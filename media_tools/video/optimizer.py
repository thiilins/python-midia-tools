"""
Otimizador de vídeos (MP4, M4V, MOV).
"""

import json
import multiprocessing
import os
import re
import subprocess
import shutil
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
    usar_aceleracao_hardware,
    obter_pausa_entre_videos,
    verificar_recursos_disponiveis,
    aguardar_recursos_disponiveis,
    definir_prioridade_processo,
    pausar_entre_processamentos,
)


class OtimizadorVideo:
    """
    Classe para otimizar vídeos usando FFmpeg.
    """

    # Extensões suportadas
    EXTENSOES_VALIDAS = {".mp4", ".m4v", ".mov"}

    # Configurações padrão
    CRF_VALUE = "23"
    PRESET_VALUE = "medium"

    # Presets pré-configurados
    PRESETS = {
        "ultra_fast": {
            "crf": "28",
            "preset": "ultrafast",
            "descricao": "Muito rápido, menor qualidade (compressão máxima)",
        },
        "fast": {
            "crf": "26",
            "preset": "fast",
            "descricao": "Rápido, qualidade média-baixa",
        },
        "medium": {
            "crf": "23",
            "preset": "medium",
            "descricao": "Balanceado, qualidade boa (padrão)",
        },
        "high_quality": {
            "crf": "20",
            "preset": "slow",
            "descricao": "Alta qualidade, mais lento",
        },
        "maximum": {
            "crf": "18",
            "preset": "veryslow",
            "descricao": "Máxima qualidade, muito lento",
        },
    }

    def __init__(
        self,
        pasta_entrada: Path = None,
        pasta_saida: Path = None,
        crf: str = None,
        preset: str = None,
        preset_nome: str = None,
        corrigir_problemas: bool = True,
    ):
        """
        Inicializa o otimizador.

        Args:
            pasta_entrada: Pasta de entrada (None = padrão).
            pasta_saida: Pasta de saída (None = padrão).
            crf: Valor CRF para qualidade (None = padrão ou preset).
            preset: Preset de velocidade FFmpeg (None = padrão ou preset).
            preset_nome: Nome do preset pré-configurado (None = usa crf/preset individuais).
                        Opções: "ultra_fast", "fast", "medium", "high_quality", "maximum"
            corrigir_problemas: Se True, detecta e corrige problemas (VFR, timestamps, etc).
        """
        if pasta_entrada is None or pasta_saida is None:
            entrada, saida = obter_pastas_entrada_saida("videos")
            self.pasta_entrada = pasta_entrada or entrada
            self.pasta_saida = pasta_saida or saida
        else:
            self.pasta_entrada = pasta_entrada
            self.pasta_saida = pasta_saida

        # Se preset_nome foi fornecido, usa as configurações do preset
        if preset_nome:
            if preset_nome in self.PRESETS:
                preset_config = self.PRESETS[preset_nome]
                self.crf = preset_config["crf"]
                self.preset = preset_config["preset"]
                self.preset_nome = preset_nome
            else:
                print(f"⚠️  Preset '{preset_nome}' não encontrado. Usando 'medium'.")
                preset_config = self.PRESETS["medium"]
                self.crf = preset_config["crf"]
                self.preset = preset_config["preset"]
                self.preset_nome = "medium"
        else:
            # Usa valores individuais ou padrão
            self.crf = crf or self.CRF_VALUE
            self.preset = preset or self.PRESET_VALUE
            self.preset_nome = None

        self.corrigir_problemas = corrigir_problemas

        # Configurações de controle de recursos
        self.threads = obter_configuracao_threads()
        self.limite_cpu = obter_configuracao_limite_cpu()
        self.limite_memoria = obter_configuracao_limite_memoria()
        self.usar_gpu = usar_aceleracao_hardware()
        self.pausa_entre_videos = obter_pausa_entre_videos()

        # Define prioridade do processo (menor prioridade = menos impacto no sistema)
        definir_prioridade_processo(nice=5)

    @classmethod
    def listar_presets(cls) -> dict:
        """
        Lista todos os presets disponíveis.

        Returns:
            dict: Dicionário com presets e suas descrições.
        """
        return cls.PRESETS

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

    def _ja_otimizado(self, info_original: Dict, crf_target: str) -> bool:
        """
        Verifica se o vídeo já está otimizado.

        Args:
            info_original: Informações do vídeo original.
            crf_target: CRF alvo.

        Returns:
            bool: True se já está otimizado.
        """
        # Se já é H.264 e tem resolução razoável, pode estar otimizado
        if info_original["codec"] == "h264":
            # Verifica se tem bitrate baixo (indicando compressão)
            if info_original["bitrate_total"]:
                # Bitrate muito alto pode indicar que não foi otimizado
                if info_original["bitrate_total"] > 5000:  # > 5 Mbps
                    return False
            return True
        return False

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
        problemas = {
            "vfr": False,  # Variable Frame Rate
            "timestamps": False,
            "audio_desync": False,
        }

        if not self.corrigir_problemas or shutil.which("ffprobe") is None:
            return problemas

        try:
            # Verifica frame rate variável
            cmd = [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=r_frame_rate",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(arquivo),
            ]
            resultado = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if resultado.returncode == 0:
                fps_str = resultado.stdout.strip()
                if fps_str and "/" in fps_str:
                    num, den = map(int, fps_str.split("/"))
                    if den > 0:
                        fps = num / den
                        # FPS muito variável ou não inteiro pode indicar VFR
                        if fps < 10 or fps > 120 or fps != int(fps):
                            problemas["vfr"] = True

            # Verifica se há stream de áudio e se está sincronizado
            cmd_audio = [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "a:0",
                "-show_entries",
                "stream=codec_name",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(arquivo),
            ]
            resultado_audio = subprocess.run(
                cmd_audio, capture_output=True, text=True, timeout=10
            )
            if resultado_audio.returncode != 0:
                # Sem áudio pode causar problemas de sincronia
                problemas["audio_desync"] = True

            # Timestamps: verifica se há problemas com PTS
            # Se o vídeo tem problemas de timestamps, geralmente aparece em erros do FFmpeg
            # Aqui assumimos que se VFR ou audio_desync, pode ter problemas de timestamps
            if problemas["vfr"] or problemas["audio_desync"]:
                problemas["timestamps"] = True

        except Exception:
            pass

        return problemas

    def _converter_video(
        self, arquivo_entrada: Path, arquivo_saida: Path, apenas_corrigir: bool = False
    ) -> tuple[bool, Optional[str]]:
        """
        Converte o vídeo usando FFmpeg com barra de progresso.

        Args:
            arquivo_entrada: Caminho do arquivo de entrada.
            arquivo_saida: Caminho do arquivo de saída.
            apenas_corrigir: Se True, apenas corrige problemas sem re-encodar (usa copy).

        Returns:
            Tuple[bool, Optional[str]]: (sucesso, mensagem_erro)
        """
        duracao_total = self._obter_duracao_video(arquivo_entrada)

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
        comando = [
            "ffmpeg",
            "-y",
        ]

        # Adiciona flags de correção de erros se necessário
        if aplicar_correcoes:
            comando.extend(
                [
                    "-err_detect",
                    "ignore_err",
                ]
            )

        comando.extend(
            [
                "-i",
                str(arquivo_entrada),
            ]
        )

        # Filtros de vídeo (para correção de VFR)
        filtros_video = []
        precisa_reencodar_video = False

        if aplicar_correcoes and problemas["vfr"]:
            # VFR requer re-encodar para aplicar filtro fps
            precisa_reencodar_video = True
            # Força FPS constante baseado no FPS detectado ou usa 30fps padrão
            info_video = self._obter_info_video(arquivo_entrada)
            fps_alvo = info_video.get("fps", 30)
            if fps_alvo and fps_alvo > 0:
                fps_alvo = round(fps_alvo)
            else:
                fps_alvo = 30
            filtros_video.append(f"fps={fps_alvo}")

        # Configurações de codificação
        if apenas_corrigir and not precisa_reencodar_video:
            # Se apenas corrigir e não precisa re-encodar vídeo, usa copy
            # (apenas timestamps/áudio, sem VFR)
            comando.extend(
                [
                    "-c:v",
                    "copy",
                ]
            )
        else:
            # Re-encoda com H.264 (otimização normal ou correção de VFR)
            # Não usa aceleração de hardware por padrão (pode ser fraca ou não disponível)
            if self.usar_gpu:
                # Tenta usar GPU (h264_nvenc para NVIDIA, h264_amf para AMD)
                # Nota: RX 580 pode não ter suporte adequado, então desabilitado por padrão
                comando.extend(
                    [
                        "-c:v",
                        "libx264",  # Mantém software encoding por segurança
                        "-crf",
                        self.crf,
                        "-preset",
                        self.preset,
                        "-threads",
                        str(self.threads),  # Limita threads para evitar sobrecarga
                    ]
                )
            else:
                # Encoding via software (CPU) com threads limitadas
                comando.extend(
                    [
                        "-c:v",
                        "libx264",
                        "-crf",
                        self.crf,
                        "-preset",
                        self.preset,
                        "-threads",
                        str(self.threads),  # Limita threads para evitar sobrecarga
                    ]
                )

        # Aplica filtros de vídeo se houver (requer re-encodar)
        if filtros_video:
            comando.extend(["-filter:v", ",".join(filtros_video)])

        # Áudio com correções se necessário
        filtro_audio = "aresample=async=1" if aplicar_correcoes else None

        comando.extend(
            [
                "-c:a",
                "aac",
                "-b:a",
                "128k",
            ]
        )

        if filtro_audio:
            comando.extend(["-af", filtro_audio])

        # Flags adicionais para correção
        comando.extend(
            [
                "-movflags",
                "+faststart",
                "-pix_fmt",
                "yuv420p",
            ]
        )

        if aplicar_correcoes:
            # Flags para corrigir timestamps e problemas de sincronia
            comando.extend(
                [
                    "-fflags",
                    "+genpts+igndts",
                    "-max_muxing_queue_size",
                    "4096",
                ]
            )

        comando.extend(
            [
                "-progress",
                "pipe:1",
                str(arquivo_saida),
            ]
        )

        # Regex para capturar o tempo processado
        regex_tempo = re.compile(r"out_time=(\d{2}:\d{2}:\d{2}\.\d+)")

        # Captura stderr para diagnóstico de erros
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
                        # Verifica se o processo terminou
                        if processo.poll() is not None:
                            break
                        # Se não terminou mas não há mais linhas, aguarda um pouco
                        continue

                    match = regex_tempo.search(linha)
                    if match:
                        tempo_atual_str = match.group(1)
                        tempo_atual_seg = self._converter_tempo_para_segundos(
                            tempo_atual_str
                        )

                        # Limita ao total para evitar ultrapassar 100%
                        tempo_atual_seg = min(tempo_atual_seg, duracao_total)

                        incremento = tempo_atual_seg - tempo_anterior
                        if incremento > 0:
                            # Garante que não ultrapasse o total
                            if pbar.n + incremento > int(duracao_total):
                                incremento = int(duracao_total) - pbar.n

                            if incremento > 0:
                                pbar.update(incremento)
                            tempo_anterior = tempo_atual_seg

                # Garante que a barra chegue a 100% ao finalizar
                if pbar.n < int(duracao_total):
                    pbar.update(int(duracao_total) - pbar.n)

            # Espera o processo terminar completamente
            try:
                processo.wait(timeout=30)
            except subprocess.TimeoutExpired:
                # Se exceder o timeout, mata o processo
                try:
                    processo.kill()
                    processo.wait(timeout=2)
                except Exception:
                    pass
                return False, "FFmpeg excedeu o tempo limite de espera"

            # Aguarda thread de stderr terminar
            stderr_thread.join(timeout=2)

            # Obtém o código de retorno
            returncode = processo.returncode

            # Converte stderr para string
            with stderr_lock:
                stderr_text = "".join(stderr_output)

            # Código de retorno válido no Windows/Linux é geralmente 0-255
            # Valores muito grandes indicam erro de sistema ou processo morto
            # No Windows, códigos negativos ou muito grandes podem indicar problemas
            if returncode is None:
                return False, "FFmpeg não retornou código de saída"

            # No Windows, códigos de retorno podem ser valores grandes quando o processo é morto
            # Verifica se é um código válido (0-255) ou um código de erro do Windows
            if returncode < 0 or (returncode > 255 and returncode != 0xFFFFFFFF):
                # Tenta obter mais informações do stderr
                erro_msg = "FFmpeg foi interrompido ou terminou de forma anormal"
                if stderr_text:
                    # Pega as últimas linhas de erro do FFmpeg
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
                        # Pega a última linha de erro relevante
                        erro_msg += f": {linhas_erro[-1][:200]}"
                return False, erro_msg

            if returncode == 0:
                return True, None
            else:
                # Código de erro válido do FFmpeg
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
            # Tenta obter informações do stderr se disponível
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

        print(f"\n🚀 Iniciando otimização de {len(arquivos)} vídeo(s)...")
        if self.preset_nome:
            preset_info = self.PRESETS[self.preset_nome]
            print(f"⚙️  Preset: {self.preset_nome} - {preset_info['descricao']}")
            print(f"   Configuração: CRF {self.crf} | Preset {self.preset}")
        else:
            print(f"⚙️  Configuração: CRF {self.crf} | Preset {self.preset}")
        print(f"🔧 Controle de recursos:")
        print(
            f"   Threads: {self.threads} | Limite CPU: {self.limite_cpu:.0f}% | Limite Memória: {self.limite_memoria:.0f}%"
        )
        print(
            f"   GPU: {'Habilitada' if self.usar_gpu else 'Desabilitada (uso de CPU apenas)'}"
        )
        print("-" * 60)

        sucessos = 0
        falhas = 0
        pulados = 0

        # Processamento sequencial com informações detalhadas
        for i, arquivo_origem in enumerate(arquivos, 1):
            # Verifica recursos antes de processar
            if not verificar_recursos_disponiveis(self.limite_cpu, self.limite_memoria):
                print(
                    f"\n⏸️  Aguardando recursos disponíveis (CPU < {self.limite_cpu:.0f}%, Memória < {self.limite_memoria:.0f}%)..."
                )
                if not aguardar_recursos_disponiveis(
                    self.limite_cpu, self.limite_memoria, timeout=120.0
                ):
                    print("⚠️  Timeout aguardando recursos. Continuando com cautela...")

            arquivo_destino = pasta_saida / arquivo_origem.name

            # Obtém informações antes
            info_antes = self._obter_info_video(arquivo_origem)

            # Verifica se já está otimizado
            ja_otimizado = self._ja_otimizado(info_antes, self.crf)

            # Se está otimizado, verifica se tem problemas que precisam correção
            if ja_otimizado and self.corrigir_problemas:
                problemas = self._detectar_problemas(arquivo_origem)
                tem_problemas = any(problemas.values())

                if not tem_problemas:
                    # Está otimizado E sem problemas - pode pular
                    print(
                        f"\n[{i}/{len(arquivos)}] ⏭️  {arquivo_origem.name}: já otimizado"
                    )
                    print(
                        f"   Info: {info_antes['width']}x{info_antes['height']} | "
                        f"{info_antes['codec']} | "
                        f"{info_antes['bitrate_total']:.0f}kbps"
                        if info_antes.get("bitrate_total")
                        else "N/A"
                    )
                    pulados += 1
                    continue
                else:
                    # Está otimizado MAS tem problemas - precisa corrigir
                    print(
                        f"\n[{i}/{len(arquivos)}] 🔧 {arquivo_origem.name}: otimizado, mas com problemas"
                    )
                    print(
                        f"   Info: {info_antes['width']}x{info_antes['height']} | "
                        f"{info_antes['codec']} | "
                        f"{info_antes['bitrate_total']:.0f}kbps"
                        if info_antes.get("bitrate_total")
                        else "N/A"
                    )
                    print(f"   ⚠️  Aplicando apenas correções (sem re-otimizar)")
            elif ja_otimizado and not self.corrigir_problemas:
                # Está otimizado e correções desabilitadas - pode pular
                print(f"\n[{i}/{len(arquivos)}] ⏭️  {arquivo_origem.name}: já otimizado")
                print(
                    f"   Info: {info_antes['width']}x{info_antes['height']} | "
                    f"{info_antes['codec']} | "
                    f"{info_antes['bitrate_total']:.0f}kbps"
                    if info_antes.get("bitrate_total")
                    else "N/A"
                )
                pulados += 1
                continue

            tamanho_original = arquivo_origem.stat().st_size / (1024 * 1024)

            # Determina se deve apenas corrigir (sem re-encodar)
            apenas_corrigir = ja_otimizado and self.corrigir_problemas

            if not apenas_corrigir:
                print(f"\n[{i}/{len(arquivos)}] 📹 {arquivo_origem.name}")
            print(
                f"   Antes: {info_antes['width']}x{info_antes['height']} | "
                f"{info_antes['codec']} | "
                f"{info_antes['bitrate_total']:.0f}kbps"
                if info_antes.get("bitrate_total")
                else "N/A"
            )

            sucesso, erro = self._converter_video(
                arquivo_origem, arquivo_destino, apenas_corrigir=apenas_corrigir
            )

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
            else:
                print(f"   ❌ Erro: {erro}")
                falhas += 1

            # Pausa entre processamentos para dar tempo ao sistema se recuperar
            if i < len(arquivos):  # Não pausa após o último vídeo
                pausar_entre_processamentos(self.pausa_entre_videos)

        print("\n" + "=" * 60)
        print("📊 RESUMO DO PROCESSAMENTO")
        print("-" * 60)
        print(f"✅ Sucessos: {sucessos}")
        if pulados > 0:
            print(f"⏭️  Pulados (já otimizados): {pulados}")
        print(f"❌ Falhas: {falhas}")
        print("-" * 60)
        print("✨ Processo finalizado!")

        return {"sucessos": sucessos, "falhas": falhas, "pulados": pulados}
