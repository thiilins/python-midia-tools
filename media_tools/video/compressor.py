"""
Compressor de vídeos com H.265/HEVC para máxima redução de tamanho.
"""

import json
import os
import re
import subprocess
import threading
from pathlib import Path
from typing import Optional, Dict

from ..common.paths import criar_pastas, obter_pastas_entrada_saida
from ..common.progress import ProgressBar
from ..common.validators import verificar_ffmpeg
from ..common.resource_control import (
    obter_configuracao_threads,
    obter_configuracao_limite_cpu,
    obter_configuracao_limite_memoria,
    obter_pausa_entre_videos,
    verificar_recursos_disponiveis,
    aguardar_recursos_disponiveis,
    definir_prioridade_processo,
    pausar_entre_processamentos,
    usar_aceleracao_hardware,
    obter_cores_fisicos,
    obter_cores_encoder,
)
from .corrector import CorretorVideo


class CompressorVideo:
    """
    Classe para comprimir vídeos usando FFmpeg com H.265/HEVC.
    Ideal para compressão máxima de vídeos longos.
    """

    # Extensões suportadas
    EXTENSOES_VALIDAS = {".mp4", ".m4v", ".mov"}

    # Presets de compressão otimizados para H.265
    PRESETS = {
        "balanced_compression": {
            "crf": "28",
            "preset": "medium",
            "codec": "libx265",
            "descricao": "Compressão balanceada com H.265 (padrão)",
            "max_resolution": None,
            "max_bitrate": None,
        },
        "high_compression": {
            "crf": "30",
            "preset": "medium",
            "codec": "libx265",
            "descricao": "Alta compressão, boa qualidade",
            "max_resolution": None,
            "max_bitrate": "3M",
        },
        "maximum_compression": {
            "crf": "32",
            "preset": "medium",
            "codec": "libx265",
            "descricao": "Compressão máxima mantendo resolução original",
            "max_resolution": None,
            "max_bitrate": "2M",
        },
        "ultra_compression_1080p": {
            "crf": "32",
            "preset": "medium",
            "codec": "libx265",
            "descricao": "Compressão máxima reduzindo para 1080p",
            "max_resolution": "1920x1080",
            "max_bitrate": "1.5M",
        },
        "master_720p": {
            "crf": "23",
            "preset": "medium",
            "codec": "libx265",
            "descricao": "Perfil Master 720p — melhor equilíbrio qualidade/tamanho (padrão)",
            "max_resolution": "1280x720",
            "max_bitrate": None,
        },
        "ultra_compression_720p": {
            "crf": "32",
            "preset": "medium",
            "codec": "libx265",
            "descricao": "Compressão máxima reduzindo para 720p",
            "max_resolution": "1280x720",
            "max_bitrate": "1M",
        },
        "extreme_compression": {
            "crf": "35",
            "preset": "slow",
            "codec": "libx265",
            "descricao": "Compressão extrema (pode perder qualidade visível)",
            "max_resolution": None,
            "max_bitrate": "1.5M",
        },
        "stream_720p": {
            "crf": "28",
            "preset": "medium",
            "codec": "libx265",
            "descricao": "Streams e gravações longas — 720p boa qualidade (recomendado para 15GB+)",
            "max_resolution": "1280x720",
            "max_bitrate": "1.5M",
        },
        "stream_540p": {
            "crf": "28",
            "preset": "medium",
            "codec": "libx265",
            "descricao": "Streams e gravações longas — 540p (meio-termo 720p/480p, ~35% menor que 720p)",
            "max_resolution": "960x540",
            "max_bitrate": "1M",
        },
        "stream_480p": {
            "crf": "28",
            "preset": "medium",
            "codec": "libx265",
            "descricao": "Streams e gravações longas — 480p arquivo mínimo",
            "max_resolution": "854x480",
            "max_bitrate": "800k",
        },
    }

    # Encoders GPU suportados para H.265 (em ordem de preferência)
    GPU_ENCODERS = ["hevc_nvenc", "hevc_qsv", "hevc_amf", "hevc_videotoolbox"]

    def __init__(
        self,
        pasta_entrada: Path = None,
        pasta_saida: Path = None,
        preset_nome: str = None,
        corrigir_problemas: bool = True,
    ):
        """
        Inicializa o compressor.

        Args:
            pasta_entrada: Pasta de entrada (None = padrão).
            pasta_saida: Pasta de saída (None = padrão).
            preset_nome: Nome do preset pré-configurado.
            corrigir_problemas: Se True, detecta e corrige problemas (VFR, timestamps, etc).
        """
        if pasta_entrada is None or pasta_saida is None:
            entrada, saida = obter_pastas_entrada_saida("videos")
            self.pasta_entrada = pasta_entrada or entrada
            self.pasta_saida = pasta_saida or saida
        else:
            self.pasta_entrada = pasta_entrada
            self.pasta_saida = pasta_saida

        # Carrega configurações do preset
        if preset_nome and preset_nome in self.PRESETS:
            preset_config = self.PRESETS[preset_nome]
            self.preset_nome = preset_nome
        else:
            if preset_nome:
                print(f"⚠️  Preset '{preset_nome}' não encontrado. Usando 'balanced_compression'.")
            preset_config = self.PRESETS["balanced_compression"]
            self.preset_nome = "balanced_compression"

        self.crf = preset_config["crf"]
        self.codec = preset_config["codec"]
        self.max_resolution = preset_config.get("max_resolution")
        self.max_bitrate = preset_config.get("max_bitrate")
        self.corrigir_problemas = corrigir_problemas

        # Permite sobrescrever o preset de velocidade via env var
        # ENCODER_VELOCIDADE=rapido → faster | normal → medium | lento → slow
        velocidade_map = {"rapido": "faster", "normal": "medium", "lento": "slow"}
        env_velocidade = os.getenv("ENCODER_VELOCIDADE", "").lower()
        if env_velocidade in velocidade_map:
            self.preset = velocidade_map[env_velocidade]
        else:
            self.preset = preset_config["preset"]

        # Detecção de encoder GPU (se USAR_GPU=1)
        self.encoder_gpu = None
        # Índice do adaptador D3D11: 0=GPU dedicada (padrão para RX 9060 XT)
        # Sobrescrever com GPU_DEVICE=N se necessário (usar ffmpeg -init_hw_device list para verificar)
        env_device = os.getenv("GPU_DEVICE", "").strip()
        self.gpu_device_idx = int(env_device) if env_device.isdigit() else 0
        if usar_aceleracao_hardware():
            self.encoder_gpu = self._detectar_encoder_gpu()

        # Instancia o corretor de vídeo
        self.corretor = CorretorVideo(
            pasta_entrada=self.pasta_entrada,
            pasta_saida=self.pasta_saida,
            corrigir_vfr=corrigir_problemas,
            corrigir_timestamps=corrigir_problemas,
            corrigir_audio=corrigir_problemas,
        )

        # Configurações de controle de recursos
        self.threads = obter_configuracao_threads()
        self.cores_fisicos = obter_cores_fisicos()
        self.cores_encoder = obter_cores_encoder()  # cores dedicados ao x265
        self.limite_cpu = obter_configuracao_limite_cpu()
        self.limite_memoria = obter_configuracao_limite_memoria()
        self.pausa_entre_videos = obter_pausa_entre_videos()

        # Define prioridade do processo (nice=0 = prioridade normal, usar CPU ao máximo)
        definir_prioridade_processo(nice=0)

    @classmethod
    def listar_presets(cls) -> dict:
        """
        Lista todos os presets disponíveis.

        Returns:
            dict: Dicionário com presets e suas descrições.
        """
        return cls.PRESETS

    def _detectar_encoder_gpu(self) -> Optional[str]:
        """
        Detecta encoder GPU para H.265.
        Respeita GPU_ENCODER env var para forçar um encoder específico.

        Returns:
            str: Nome do encoder GPU (ex: 'hevc_amf'), ou None se não disponível.
        """
        # Permite forçar encoder específico via env var (ex: GPU_ENCODER=hevc_amf)
        encoder_forcado = os.getenv("GPU_ENCODER", "").strip().lower()
        if encoder_forcado:
            if encoder_forcado in self.GPU_ENCODERS:
                return encoder_forcado
            # Aceita atalhos: amd/amf → hevc_amf, nvidia/nvenc → hevc_nvenc, intel/qsv → hevc_qsv
            aliases = {"amd": "hevc_amf", "amf": "hevc_amf", "nvidia": "hevc_nvenc",
                       "nvenc": "hevc_nvenc", "intel": "hevc_qsv", "qsv": "hevc_qsv"}
            if encoder_forcado in aliases:
                return aliases[encoder_forcado]

        try:
            resultado = subprocess.run(
                ["ffmpeg", "-encoders"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5,
            )
            output = resultado.stdout + resultado.stderr
            for encoder in self.GPU_ENCODERS:
                if encoder in output:
                    return encoder
        except Exception:
            pass
        return None

    def _obter_info_video(self, arquivo: Path) -> Dict:
        """
        Obtém informações detalhadas do vídeo usando ffprobe.

        Args:
            arquivo: Caminho do arquivo de vídeo.

        Returns:
            dict: Informações do vídeo (codec, resolução, bitrate, duração, etc.)
        """
        comando = [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=codec_name,width,height,bit_rate,r_frame_rate",
            "-show_entries",
            "format=duration,bit_rate,size",
            "-of",
            "json",
            str(arquivo),
        ]

        try:
            resultado = subprocess.run(
                comando,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
                timeout=10,
            )
            data = json.loads(resultado.stdout)

            info = {
                "codec": None,
                "width": None,
                "height": None,
                "bitrate_video": None,
                "bitrate_total": None,
                "fps": None,
                "duracao": None,
                "tamanho": None,
            }

            # Extrai informações do stream de vídeo
            if "streams" in data and len(data["streams"]) > 0:
                stream = data["streams"][0]
                info["codec"] = stream.get("codec_name", "unknown")
                info["width"] = stream.get("width", 0)
                info["height"] = stream.get("height", 0)
                info["bitrate_video"] = stream.get("bit_rate")
                if info["bitrate_video"]:
                    info["bitrate_video"] = int(info["bitrate_video"]) / 1000  # kbps

                # Calcula FPS
                r_frame_rate = stream.get("r_frame_rate", "")
                if r_frame_rate and "/" in r_frame_rate:
                    num, den = map(int, r_frame_rate.split("/"))
                    if den > 0:
                        info["fps"] = round(num / den, 2)

            # Extrai informações do formato
            if "format" in data:
                format_info = data["format"]
                info["duracao"] = float(format_info.get("duration", 0))
                info["bitrate_total"] = format_info.get("bit_rate")
                if info["bitrate_total"]:
                    info["bitrate_total"] = int(info["bitrate_total"]) / 1000  # kbps
                info["tamanho"] = int(format_info.get("size", 0))

            return info
        except Exception as e:
            return {
                "codec": "unknown",
                "width": 0,
                "height": 0,
                "bitrate_video": None,
                "bitrate_total": None,
                "fps": None,
                "duracao": 0,
                "tamanho": 0,
            }

    def _obter_duracao_video(self, arquivo: Path) -> float:
        """
        Obtém a duração do vídeo em segundos usando ffprobe.

        Args:
            arquivo: Caminho do arquivo de vídeo.

        Returns:
            float: Duração em segundos, ou 0.0 se não conseguir obter.
        """
        comando = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(arquivo),
        ]
        try:
            resultado = subprocess.run(
                comando,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
                timeout=10,
            )
            return float(resultado.stdout.strip())
        except (subprocess.CalledProcessError, ValueError):
            return 0.0

    def _converter_tempo_para_segundos(self, tempo_str: str) -> float:
        """
        Converte o formato HH:MM:SS.mm do FFmpeg para segundos totais.

        Args:
            tempo_str: String no formato HH:MM:SS.mm.

        Returns:
            float: Tempo em segundos.
        """
        try:
            h, m, s = tempo_str.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
        except ValueError:
            return 0.0

    def _detectar_problemas(self, arquivo: Path) -> Dict:
        """
        Detecta problemas no vídeo (VFR, timestamps, áudio).

        Args:
            arquivo: Caminho do arquivo de vídeo.

        Returns:
            dict: Problemas detectados.
        """
        if not self.corrigir_problemas:
            return {"vfr": False, "timestamps": False, "audio_desync": False}

        return self.corretor.detectar_problemas(arquivo)

    def _construir_filtro_resolucao(self, info_video: Dict) -> Optional[str]:
        """
        Constrói o filtro de resolução se necessário.

        Args:
            info_video: Informações do vídeo original.

        Returns:
            str: Filtro de resolução ou None se não precisa reduzir.
        """
        if not self.max_resolution:
            return None

        largura_original = info_video.get("width", 0)
        altura_original = info_video.get("height", 0)

        if not largura_original or not altura_original:
            return None

        # Parse resolução máxima
        largura_max, altura_max = map(int, self.max_resolution.split("x"))

        # Se o vídeo já está dentro do limite, não reduz
        if largura_original <= largura_max and altura_original <= altura_max:
            return None

        # Dois passes:
        # 1) scale com aspect ratio mantido dentro do limite
        # 2) trunc garante dimensões pares na saída real (force_original_aspect_ratio
        #    pode gerar largura ímpar, ex: 720x1280 → 405x720 → quebra hevc_amf e libx265)
        return (
            f"scale='min({largura_max},iw)':'min({altura_max},ih)'"
            f":force_original_aspect_ratio=decrease"
            f",scale=trunc(iw/2)*2:trunc(ih/2)*2"
        )

    def _construir_comando_gpu(
        self, encoder: str, crf: str, max_bitrate: Optional[str]
    ) -> list:
        """
        Constrói os argumentos de codec para encoder GPU.

        Args:
            encoder: Nome do encoder GPU (ex: 'hevc_nvenc').
            crf: Valor de qualidade CRF.
            max_bitrate: Bitrate máximo ou None.

        Returns:
            list: Argumentos FFmpeg para o encoder GPU.
        """
        args = ["-c:v", encoder]
        if encoder == "hevc_nvenc":
            # p4 = preset balanceado velocidade/qualidade no NVENC
            args += ["-preset", "p4", "-rc:v", "vbr", "-cq", crf, "-b:v", "0"]
            if max_bitrate:
                args += ["-maxrate", max_bitrate]
        elif encoder == "hevc_qsv":
            args += ["-preset", "medium", "-global_quality", crf]
            if max_bitrate:
                args += ["-maxrate", max_bitrate]
        elif encoder == "hevc_amf":
            # AMD AMF HEVC encoder
            # qp_p e qp_b ligeiramente maiores que qp_i = melhor equilíbrio qualidade/tamanho
            qp = int(crf)
            if max_bitrate:
                # VBR com cap de bitrate quando preset define max_bitrate
                args += [
                    "-rc", "vbr_peak",
                    "-b:v", "0",
                    "-maxrate", max_bitrate,
                    "-qp_i", str(qp),
                    "-qp_p", str(qp + 2),
                    "-qp_b", str(qp + 4),
                    "-quality", "quality",
                ]
            else:
                # CQP (qualidade constante) — equivalente ao CRF do libx265
                args += [
                    "-rc", "cqp",
                    "-qp_i", str(qp),
                    "-qp_p", str(qp + 2),
                    "-qp_b", str(qp + 4),
                    "-quality", "quality",
                    "-b:v", "0",
                ]
        elif encoder == "hevc_videotoolbox":
            # VideoToolbox usa escala 0-100, mapear CRF 18-35 → qualidade ~85-40
            qualidade = max(40, min(85, int(100 - (int(crf) - 18) * 2.5)))
            args += ["-q:v", str(qualidade), "-allow_sw", "1"]
        return args

    def _converter_video(
        self, arquivo_entrada: Path, arquivo_saida: Path, info_video: Optional[Dict] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Converte o vídeo usando FFmpeg com H.265/HEVC.

        Args:
            arquivo_entrada: Caminho do arquivo de entrada.
            arquivo_saida: Caminho do arquivo de saída.
            info_video: Informações do vídeo já obtidas (evita chamada ffprobe extra).

        Returns:
            Tuple[bool, Optional[str]]: (sucesso, mensagem_erro)
        """
        # Reutiliza info_video passado (evita ffprobe redundante)
        if info_video is None:
            info_video = self._obter_info_video(arquivo_entrada)

        duracao_total = info_video.get("duracao") or 0
        if duracao_total == 0:
            duracao_total = 100  # Fallback

        # Detecta problemas se habilitado
        problemas = self._detectar_problemas(arquivo_entrada)
        aplicar_correcoes = self.corrigir_problemas and any(problemas.values())

        if aplicar_correcoes:
            print(f"   🔍 Problemas detectados:")
            if problemas["vfr"]:
                print(f"      ⚠️  Frame rate variável (VFR) - será corrigido")
            if problemas["timestamps"]:
                print(f"      ⚠️  Problemas com timestamps - será corrigido")
            if problemas["audio_desync"]:
                print(f"      ⚠️  Possível dessincronia de áudio - será corrigido")

        # Comando FFmpeg base
        comando = ["ffmpeg", "-y"]

        # Decode + encode no mesmo adaptador (força GPU dedicada, evita iGPU)
        # -init_hw_device d3d11va=dx:N cria contexto no adaptador N (1 = dGPU dedicada)
        # -hwaccel_device dx vincula decode a esse contexto
        # hevc_amf herda automaticamente o mesmo contexto D3D11
        if self.encoder_gpu and "amf" in self.encoder_gpu:
            # Cria contexto AMF no adaptador correto (GPU dedicada)
            # Decode fica no CPU para evitar conflito de formato com filtros de escala
            comando.extend([
                "-init_hw_device", f"d3d11va=dx:{self.gpu_device_idx}",
                "-init_hw_device", "amf=amf@dx",
            ])

        # Adiciona flags de correção de erros se necessário
        if aplicar_correcoes:
            comando.extend(["-err_detect", "ignore_err"])

        comando.extend(["-i", str(arquivo_entrada)])

        # Filtros de vídeo
        filtros_video = []

        # Correção de VFR
        if aplicar_correcoes and problemas["vfr"]:
            fps_alvo = info_video.get("fps", 30)
            if fps_alvo and fps_alvo > 0:
                fps_alvo = round(fps_alvo)
            else:
                fps_alvo = 30
            filtros_video.append(f"fps={fps_alvo}")

        # Filtro de resolução
        filtro_resolucao = self._construir_filtro_resolucao(info_video)
        if filtro_resolucao:
            filtros_video.append(filtro_resolucao)
            print(f"   📐 Reduzindo resolução para: {self.max_resolution}")

        # Configurações de codificação
        if self.encoder_gpu:
            # GPU: usa encoder AMF/NVENC/QSV
            print(f"   ⚡ Usando GPU: {self.encoder_gpu}")
            comando.extend(self._construir_comando_gpu(self.encoder_gpu, self.crf, self.max_bitrate))
        else:
            # CPU: libx265 com paralelismo máximo via x265-params
            # pools=N diz ao x265 quantos threads usar (usa cores físicos, não lógicos)
            # wpp=1 = wavefront parallel processing (padrão, deixa ligado)
            x265_params = f"pools={self.cores_encoder}:wpp=1"
            comando.extend([
                "-c:v", "libx265",
                "-crf", self.crf,
                "-preset", self.preset,
                "-x265-params", x265_params,
            ])
            if self.max_bitrate:
                comando.extend(["-maxrate", self.max_bitrate, "-bufsize", "2M"])

        # Aplica filtros de vídeo se houver
        if filtros_video:
            comando.extend(["-filter:v", ",".join(filtros_video)])

        # Configurações de áudio
        filtro_audio = "aresample=async=1" if aplicar_correcoes else None

        comando.extend(["-c:a", "aac", "-b:a", "96k", "-ac", "2"])  # stereo

        if filtro_audio:
            comando.extend(["-af", filtro_audio])

        # Flags adicionais
        comando.extend(["-movflags", "+faststart", "-pix_fmt", "yuv420p"])

        if aplicar_correcoes:
            comando.extend([
                "-fflags",
                "+genpts+igndts",
                "-max_muxing_queue_size",
                "4096",
            ])

        comando.extend(["-progress", "pipe:1", str(arquivo_saida)])

        # Regex para capturar o tempo processado
        regex_tempo = re.compile(r"out_time=(\d{2}:\d{2}:\d{2}\.\d+)")

        # Captura stderr
        stderr_output = []
        stderr_lock = threading.Lock()

        def ler_stderr():
            """Thread para ler stderr sem bloquear."""
            nonlocal stderr_output
            try:
                for linha in processo.stderr:
                    with stderr_lock:
                        stderr_output.append(linha)
            except Exception:
                pass

        try:
            processo = subprocess.Popen(
                comando,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )

            # Inicia thread para ler stderr
            stderr_thread = threading.Thread(target=ler_stderr, daemon=True)
            stderr_thread.start()

            with ProgressBar(
                total=int(duracao_total),
                unit="s",
                desc=f"🎬 {arquivo_entrada.name[:20]}...",
            ).context() as pbar:
                tempo_anterior = 0.0

                # Lê stdout linha por linha
                while True:
                    linha = processo.stdout.readline()
                    if not linha:
                        if processo.poll() is not None:
                            break
                        continue

                    match = regex_tempo.search(linha)
                    if match:
                        tempo_atual_str = match.group(1)
                        tempo_atual_seg = self._converter_tempo_para_segundos(
                            tempo_atual_str
                        )

                        tempo_atual_seg = min(tempo_atual_seg, duracao_total)

                        incremento = tempo_atual_seg - tempo_anterior
                        if incremento > 0:
                            if pbar.n + incremento > int(duracao_total):
                                incremento = int(duracao_total) - pbar.n

                            if incremento > 0:
                                pbar.update(incremento)
                            tempo_anterior = tempo_atual_seg

                # Garante que a barra chegue a 100%
                if pbar.n < int(duracao_total):
                    pbar.update(int(duracao_total) - pbar.n)

            # Espera o processo terminar
            try:
                processo.wait(timeout=30)
            except subprocess.TimeoutExpired:
                try:
                    processo.kill()
                    processo.wait(timeout=2)
                except Exception:
                    pass
                return False, "FFmpeg excedeu o tempo limite de espera"

            stderr_thread.join(timeout=2)
            returncode = processo.returncode

            with stderr_lock:
                stderr_text = "".join(stderr_output)

            if returncode is None:
                return False, "FFmpeg não retornou código de saída"

            if returncode < 0 or (returncode > 255 and returncode != 0xFFFFFFFF):
                erro_msg = "FFmpeg foi interrompido ou terminou de forma anormal"
                if stderr_text:
                    linhas_erro = [
                        linha.strip()
                        for linha in stderr_text.split("\n")
                        if linha.strip()
                        and (
                            "error" in linha.lower()
                            or "failed" in linha.lower()
                            or "cannot" in linha.lower()
                        )
                    ]
                    if linhas_erro:
                        erro_msg += f": {linhas_erro[-1][:200]}"
                return False, erro_msg

            if returncode == 0:
                return True, None
            else:
                erro_msg = f"FFmpeg retornou código {returncode}"
                if stderr_text:
                    linhas_erro = [
                        linha.strip()
                        for linha in stderr_text.split("\n")
                        if linha.strip()
                        and (
                            "error" in linha.lower()
                            or "failed" in linha.lower()
                            or "cannot" in linha.lower()
                        )
                    ]
                    if linhas_erro:
                        erro_msg += f": {linhas_erro[-1][:200]}"
                return False, erro_msg

        except Exception as e:
            erro_msg = f"Erro ao executar FFmpeg: {str(e)}"
            with stderr_lock:
                if stderr_output:
                    stderr_text = "".join(stderr_output)
                    linhas_erro = [
                        linha.strip()
                        for linha in stderr_text.split("\n")
                        if linha.strip()
                        and ("error" in linha.lower() or "failed" in linha.lower())
                    ]
                    if linhas_erro:
                        erro_msg += f" | FFmpeg: {linhas_erro[-1][:200]}"
            return False, erro_msg

    def processar(self, deletar_originais: bool = True) -> dict:
        """
        Processa todos os vídeos na pasta de entrada.

        Args:
            deletar_originais: Se True, deleta os arquivos originais após processar.

        Returns:
            dict: Estatísticas do processamento.
        """
        if not verificar_ffmpeg():
            return {"sucessos": 0, "falhas": 0, "pulados": 0}

        if not criar_pastas(self.pasta_entrada, self.pasta_saida):
            print(f"ℹ️  Pasta '{self.pasta_entrada}' criada. Adicione vídeos nela.")
            return {"sucessos": 0, "falhas": 0, "pulados": 0}

        pasta_entrada = Path(self.pasta_entrada).resolve()
        pasta_saida = Path(self.pasta_saida).resolve()

        arquivos = [
            f
            for f in pasta_entrada.iterdir()
            if f.is_file() and f.suffix.lower() in self.EXTENSOES_VALIDAS
        ]

        if not arquivos:
            print("ℹ️  Nenhum vídeo encontrado.")
            return {"sucessos": 0, "falhas": 0, "pulados": 0}

        print(f"\n🚀 Iniciando compressão de {len(arquivos)} vídeo(s) com H.265/HEVC...")
        preset_info = self.PRESETS[self.preset_nome]
        print(f"⚙️  Preset: {self.preset_nome} - {preset_info['descricao']}")
        print(f"   Configuração: CRF {self.crf} | Preset {self.preset} | Codec {self.codec}")
        if self.max_resolution:
            print(f"   Resolução máxima: {self.max_resolution}")
        if self.max_bitrate:
            print(f"   Bitrate máximo: {self.max_bitrate}")
        if self.encoder_gpu:
            encoder_info = f"{self.encoder_gpu} (adapter {self.gpu_device_idx} — GPU dedicada)"
        else:
            encoder_info = f"libx265 (pools={self.cores_encoder}/{self.cores_fisicos} cores)"
        print(f"🔧 Encoder: {encoder_info}")
        if not self.encoder_gpu:
            print(f"   Limite CPU: {self.limite_cpu:.0f}% | Limite Memória: {self.limite_memoria:.0f}%")
        print("-" * 60)

        sucessos = 0
        falhas = 0
        pulados = 0

        # Processamento sequencial
        for i, arquivo_origem in enumerate(arquivos, 1):
            # Verifica recursos antes de processar (apenas em modo CPU — GPU não tem esse gargalo)
            if not self.encoder_gpu and not verificar_recursos_disponiveis(self.limite_cpu, self.limite_memoria):
                print(
                    f"\n⏸️  Aguardando recursos disponíveis (CPU < {self.limite_cpu:.0f}%, Memória < {self.limite_memoria:.0f}%)..."
                )
                if not aguardar_recursos_disponiveis(
                    self.limite_cpu, self.limite_memoria, timeout=120.0
                ):
                    print("⚠️  Timeout aguardando recursos. Continuando com cautela...")

            arquivo_destino = pasta_saida / (arquivo_origem.stem + ".mp4")

            # Obtém informações antes
            info_antes = self._obter_info_video(arquivo_origem)
            tamanho_original = arquivo_origem.stat().st_size / (1024 * 1024)

            print(f"\n[{i}/{len(arquivos)}] 📹 {arquivo_origem.name}")
            print(
                f"   Antes: {info_antes['width']}x{info_antes['height']} | "
                f"{info_antes['codec']} | "
                f"{info_antes['bitrate_total']:.0f}kbps | {tamanho_original:.2f}MB"
                if info_antes.get("bitrate_total")
                else f"{tamanho_original:.2f}MB"
            )

            sucesso, erro = self._converter_video(arquivo_origem, arquivo_destino, info_antes)

            # Fallback para CPU quando GPU falha (dimensões incomuns, VFR, etc.)
            if not sucesso and self.encoder_gpu:
                # Remove arquivo corrompido gerado pela tentativa falha
                if arquivo_destino.exists():
                    try:
                        arquivo_destino.unlink()
                    except OSError:
                        pass
                print(f"   🔄 GPU falhou, tentando CPU (libx265)...")
                encoder_backup = self.encoder_gpu
                self.encoder_gpu = None
                sucesso, erro = self._converter_video(arquivo_origem, arquivo_destino, info_antes)
                self.encoder_gpu = encoder_backup

            if sucesso and arquivo_destino.exists():
                info_depois = self._obter_info_video(arquivo_destino)
                tamanho_novo = arquivo_destino.stat().st_size / (1024 * 1024)
                reducao = 100 - (tamanho_novo / tamanho_original * 100)

                print(f"   ✅ Finalizado.")
                print(
                    f"   📊 Redução: {reducao:.1f}% ({tamanho_original:.2f}MB -> {tamanho_novo:.2f}MB)"
                )
                print(
                    f"   Depois: {info_depois['width']}x{info_depois['height']} | "
                    f"{info_depois['codec']} | "
                    f"{info_depois['bitrate_total']:.0f}kbps"
                    if info_depois.get("bitrate_total")
                    else "N/A"
                )

                if deletar_originais:
                    try:
                        arquivo_origem.unlink()
                        print("   🗑️  Original removido.")
                    except OSError:
                        pass
                sucessos += 1

                # Pausa entre vídeos
                if i < len(arquivos):
                    pausar_entre_processamentos(self.pausa_entre_videos)
            else:
                # Remove arquivo corrompido/incompleto gerado pela falha
                if arquivo_destino.exists():
                    try:
                        arquivo_destino.unlink()
                    except OSError:
                        pass
                print(f"   ❌ Erro: {erro}")
                falhas += 1

        print("\n" + "=" * 60)
        print(f"✅ Compressão concluída!")
        print(f"   Sucessos: {sucessos} | Falhas: {falhas} | Pulados: {pulados}")

        return {"sucessos": sucessos, "falhas": falhas, "pulados": pulados}
