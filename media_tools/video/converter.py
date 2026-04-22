"""
Conversor de WebM para MP4.
"""

import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..common.paths import criar_pastas, obter_pastas_entrada_saida
from ..common.progress import ProgressBar
from ..common.validators import verificar_ffmpeg


class ConversorWebM:
    """
    Classe para converter WebM para MP4 com correção de erros.
    """

    # Perfis pré-configurados
    PERFIS = {
        "web": {"crf": "23", "preset": "fast", "fps": 30, "bitrate_audio": "128k"},
        "mobile": {"crf": "25", "preset": "medium", "fps": 30, "bitrate_audio": "96k"},
        "archive": {"crf": "18", "preset": "slow", "fps": 30, "bitrate_audio": "192k"},
    }

    def __init__(
        self,
        pasta_entrada: Path = None,
        pasta_saida: Path = None,
        manter_originais: bool = True,
        corrigir_velocidade: bool = False,
        fator_velocidade: float = 2.0,
        fps_saida: int = 30,
        qualidade_crf: str = "20",
        perfil: str = None,
        detectar_problemas: bool = True,
    ):
        """
        Inicializa o conversor.

        Args:
            pasta_entrada: Pasta de entrada (None = padrão).
            pasta_saida: Pasta de saída (None = padrão).
            manter_originais: Se True, mantém os arquivos WebM originais.
            corrigir_velocidade: Se True, aplica correção de velocidade.
            fator_velocidade: Fator de desaceleração (0.5-2.0).
            fps_saida: FPS de saída forçado.
            qualidade_crf: Qualidade CRF (0-51).
            perfil: Perfil pré-configurado ('web', 'mobile', 'archive').
            detectar_problemas: Se True, detecta problemas automaticamente.
        """
        if pasta_entrada is None or pasta_saida is None:
            entrada, saida = obter_pastas_entrada_saida("videos")
            self.pasta_entrada = pasta_entrada or entrada
            self.pasta_saida = pasta_saida or saida
        else:
            self.pasta_entrada = pasta_entrada
            self.pasta_saida = pasta_saida

        self.manter_originais = manter_originais
        self.corrigir_velocidade = corrigir_velocidade
        self.fator_velocidade = fator_velocidade
        self.detectar_problemas = detectar_problemas

        # Aplica perfil se especificado
        if perfil and perfil.lower() in self.PERFIS:
            perfil_config = self.PERFIS[perfil.lower()]
            self.qualidade_crf = perfil_config["crf"]
            self.preset = perfil_config["preset"]
            self.fps_saida = perfil_config["fps"]
            self.bitrate_audio = perfil_config["bitrate_audio"]
        else:
            self.qualidade_crf = qualidade_crf
            self.preset = "medium"
            self.fps_saida = fps_saida
            self.bitrate_audio = "192k"

    def _validar_configuracoes(self) -> bool:
        """
        Valida as configurações do conversor.

        Returns:
            bool: True se todas as configurações são válidas.
        """
        # Valida CRF
        try:
            crf_num = int(self.qualidade_crf)
            if crf_num < 0 or crf_num > 51:
                print(
                    f"❌ ERRO: qualidade_crf deve estar entre 0 e 51. Valor atual: {self.qualidade_crf}"
                )
                return False
        except ValueError:
            print(
                f"❌ ERRO: qualidade_crf deve ser um número. Valor atual: {self.qualidade_crf}"
            )
            return False

        # Valida FPS
        if self.fps_saida <= 0 or self.fps_saida > 120:
            print(
                f"❌ ERRO: fps_saida deve estar entre 1 e 120. Valor atual: {self.fps_saida}"
            )
            return False

        # Valida FATOR_VELOCIDADE se CORRIGIR_VELOCIDADE estiver ativo
        if self.corrigir_velocidade:
            if self.fator_velocidade < 0.5 or self.fator_velocidade > 2.0:
                print(
                    f"❌ ERRO: fator_velocidade deve estar entre 0.5 e 2.0 quando corrigir_velocidade=True."
                )
                return False

        return True

    def _get_duracao(self, arquivo: Path) -> Optional[float]:
        """
        Obtém duração do vídeo em segundos usando FFprobe.

        Args:
            arquivo: Caminho do arquivo de vídeo.

        Returns:
            float: Duração em segundos, ou None se não conseguir obter.
        """
        if shutil.which("ffprobe") is None:
            return None

        try:
            cmd = [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(arquivo),
            ]
            resultado = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if resultado.returncode == 0:
                return float(resultado.stdout.strip())
        except (subprocess.TimeoutExpired, ValueError, FileNotFoundError):
            pass
        except Exception:
            pass

        return None

    def _detectar_problemas(self, arquivo: Path) -> dict:
        """
        Detecta problemas no vídeo WebM (VFR, timestamps, áudio) em 1 chamada ffprobe.
        """
        problemas = {"vfr": False, "timestamps": False, "audio_desync": False}

        if not self.detectar_problemas or shutil.which("ffprobe") is None:
            return problemas

        try:
            cmd = [
                "ffprobe", "-v", "error",
                "-show_entries", "stream=codec_type,codec_name,r_frame_rate",
                "-of", "json",
                str(arquivo),
            ]
            resultado = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if resultado.returncode != 0:
                return problemas

            import json as _json
            data = _json.loads(resultado.stdout)
            streams = data.get("streams", [])

            video = next((s for s in streams if s.get("codec_type") == "video"), None)
            audio = next((s for s in streams if s.get("codec_type") == "audio"), None)

            if video:
                fps_str = video.get("r_frame_rate", "")
                if fps_str and "/" in fps_str:
                    num, den = map(int, fps_str.split("/"))
                    if den > 0:
                        fps = num / den
                        if fps < 10 or fps > 120 or fps != int(fps):
                            problemas["vfr"] = True

            if audio is None:
                problemas["audio_desync"] = True

            if problemas["vfr"] or problemas["audio_desync"]:
                problemas["timestamps"] = True

        except Exception:
            pass

        return problemas

    def _converter_video(
        self, entrada: Path, saida: Path
    ) -> subprocess.CompletedProcess:
        """
        Converte webm para mp4 com correção de erros e sincronia.

        Args:
            entrada: Caminho do arquivo de entrada (.webm).
            saida: Caminho do arquivo de saída (.mp4).

        Returns:
            subprocess.CompletedProcess: Resultado da execução do FFmpeg.
        """
        # Validações de entrada
        if not entrada.exists():
            print(f"❌ Arquivo de entrada não encontrado: {entrada}")
            return subprocess.CompletedProcess([], 1, "", "Arquivo não encontrado")

        if not entrada.is_file():
            print(f"❌ Caminho não é um arquivo: {entrada}")
            return subprocess.CompletedProcess([], 1, "", "Não é um arquivo")

        # Verifica se o arquivo de entrada tem tamanho válido
        try:
            tamanho_entrada = entrada.stat().st_size
            if tamanho_entrada == 0:
                print(f"❌ Arquivo de entrada está vazio: {entrada}")
                return subprocess.CompletedProcess([], 1, "", "Arquivo vazio")
        except OSError as e:
            print(f"❌ Erro ao verificar arquivo de entrada: {e}")
            return subprocess.CompletedProcess([], 1, "", str(e))

        # Detecta problemas automaticamente
        problemas = self._detectar_problemas(entrada)
        aplicar_correcoes = any(problemas.values())

        if aplicar_correcoes:
            print(f"   🔍 Problemas detectados:")
            if problemas["vfr"]:
                print(f"      ⚠️  Frame rate variável (VFR)")
            if problemas["timestamps"]:
                print(f"      ⚠️  Problemas com timestamps")
            if problemas["audio_desync"]:
                print(f"      ⚠️  Possível dessincronia de áudio")

        # 1. Comando base
        cmd = [
            "ffmpeg",
            "-y",
            "-err_detect",
            "ignore_err",
            "-i",
            str(entrada),
        ]

        # 2. Configurações de Filtro (Velocidade + FPS)
        filtros = []

        # Se precisar corrigir velocidade (slow motion)
        if self.corrigir_velocidade:
            filtros.append(f"setpts={self.fator_velocidade}*PTS")

        # Áudio: Sincronia (sempre aplica se detectar problemas ou corrigir velocidade)
        filtro_audio = "aresample=async=1"
        if self.corrigir_velocidade:
            filtro_audio += f",atempo={1/float(self.fator_velocidade)}"
        elif aplicar_correcoes:
            # Aplica correções automáticas se detectar problemas
            filtro_audio += ",aresample=async=1"

        # 3. Montagem dos argumentos de codificação
        cmd.extend(
            [
                "-c:v",
                "libx264",
                "-preset",
                self.preset,
                "-crf",
                self.qualidade_crf,
                "-c:a",
                "aac",
                "-b:a",
                self.bitrate_audio,
                "-r",
                str(self.fps_saida),
                "-movflags",
                "+faststart",
                "-pix_fmt",
                "yuv420p",
                "-max_muxing_queue_size",
                "4096",
                "-fflags",
                "+genpts+igndts",
                "-af",
                filtro_audio,
            ]
        )

        # Se houver filtros de vídeo (velocidade), aplica aqui
        if filtros:
            cmd.extend(["-filter:v", ",".join(filtros)])

        # Arquivo de saída
        cmd.append(str(saida))

        # Executa com timeout de 2 horas
        try:
            return subprocess.run(cmd, capture_output=True, text=True, timeout=7200)
        except subprocess.TimeoutExpired:
            print(
                f"❌ Timeout ao converter {entrada.name} (processo demorou mais de 2 horas)"
            )
            return subprocess.CompletedProcess(cmd, 1, "", "Timeout")
        except FileNotFoundError:
            print(f"❌ FFmpeg não encontrado. Verifique se está instalado e no PATH.")
            return subprocess.CompletedProcess(cmd, 1, "", "FFmpeg não encontrado")

    def processar(self) -> dict:
        """
        Processa todos os arquivos WebM na pasta de origem.

        Returns:
            dict: Estatísticas do processamento.
        """
        print("=" * 60)
        print(" 🎬 CONVERSOR WEBM → MP4 (CORREÇÃO VFR)")
        print("=" * 60)

        # Validações iniciais
        if not self._validar_configuracoes():
            return {"sucessos": 0, "falhas": 0}

        if not verificar_ffmpeg():
            return {"sucessos": 0, "falhas": 0}

        if not criar_pastas(self.pasta_entrada, self.pasta_saida):
            print(
                "\n💡 Adicione seus arquivos .webm na pasta de origem e execute o script novamente."
            )
            return {"sucessos": 0, "falhas": 0}

        pasta_entrada = Path(self.pasta_entrada).resolve()
        pasta_saida = Path(self.pasta_saida).resolve()

        # Obtém lista de arquivos válidos
        try:
            arquivos = [
                f
                for f in pasta_entrada.iterdir()
                if f.is_file() and f.suffix.lower() == ".webm"
            ]
        except OSError as e:
            print(f"❌ ERRO ao acessar pasta de origem: {e}")
            return {"sucessos": 0, "falhas": 0}

        if not arquivos:
            print(f"ℹ️  Nenhum arquivo .webm encontrado em: {pasta_entrada}")
            return {"sucessos": 0, "falhas": 0}

        print(f"\n📂 Origem: {pasta_entrada}")
        print(f"📂 Destino: {pasta_saida}")
        print(f"🎯 Meta: MP4 H.264, {self.fps_saida}fps, CRF {self.qualidade_crf}")
        print(f"⚙️  Preset: {self.preset} | Áudio: {self.bitrate_audio}")
        if self.corrigir_velocidade:
            print(f"⚙️  Correção de velocidade: {self.fator_velocidade}x")
        if self.detectar_problemas:
            print(f"🔍 Detecção automática de problemas: Ativa")
        print(f"💾 Manter originais: {'Sim' if self.manter_originais else 'Não'}")
        print("-" * 60)

        sucesso = 0
        falhas = 0

        # Barra de progresso geral
        with ProgressBar(
            total=len(arquivos), desc="Convertendo", unit="vídeo"
        ).context() as pbar:
            for i, arquivo_origem in enumerate(arquivos, 1):
                arquivo_destino = pasta_saida / (arquivo_origem.stem + ".mp4")

                # Obtém tamanho original
                try:
                    tamanho_orig = arquivo_origem.stat().st_size / (1024 * 1024)  # MB
                except OSError as e:
                    print(
                        f"\n[{i}/{len(arquivos)}] ❌ Erro ao acessar {arquivo_origem.name}: {e}"
                    )
                    falhas += 1
                    pbar.update(1)
                    continue

                # Obtém duração (opcional, para log)
                duracao = self._get_duracao(arquivo_origem)
                duracao_str = f" ({duracao:.1f}s)" if duracao else ""

                print(f"\n[{i}/{len(arquivos)}] 📹 Processando: {arquivo_origem.name}")
                print(f"   Tamanho original: {tamanho_orig:.2f} MB{duracao_str}")

                inicio = datetime.now()
                resultado = self._converter_video(arquivo_origem, arquivo_destino)
                tempo = (datetime.now() - inicio).total_seconds()

                if resultado.returncode == 0:
                    # Verifica se o arquivo de saída existe e tem tamanho maior que 0
                    try:
                        if (
                            arquivo_destino.exists()
                            and arquivo_destino.stat().st_size > 0
                        ):
                            tamanho_new = arquivo_destino.stat().st_size / (1024 * 1024)
                            reducao = (
                                100 - (tamanho_new / tamanho_orig * 100)
                                if tamanho_orig > 0
                                else 0
                            )

                            print(f"   ✅ Convertido com sucesso!")
                            print(
                                f"   📊 Original: {tamanho_orig:.2f} MB -> Novo: {tamanho_new:.2f} MB"
                            )
                            if reducao > 0:
                                print(f"   💾 Redução: {reducao:.1f}%")
                            elif reducao < 0:
                                print(
                                    f"   ⚠️  Aumento: {abs(reducao):.1f}% (arquivo ficou maior)"
                                )
                            print(f"   ⏱️  Tempo: {tempo:.1f}s")

                            # Apaga o original se configurado
                            if not self.manter_originais:
                                try:
                                    arquivo_origem.unlink()
                                    print(f"   🗑️  Arquivo original deletado.")
                                except OSError as e:
                                    print(f"   ⚠️  Erro ao deletar original: {e}")

                            sucesso += 1
                        else:
                            print(
                                f"   ❌ Falha: Arquivo de saída corrompido ou vazio. Original mantido."
                            )
                            falhas += 1
                    except OSError as e:
                        print(f"   ❌ Erro ao verificar arquivo de saída: {e}")
                        falhas += 1
                else:
                    print(f"   ❌ Erro ao converter!")
                    if resultado.stderr:
                        linhas_erro = resultado.stderr.strip().split("\n")
                        linhas_relevantes = (
                            linhas_erro[-10:] if len(linhas_erro) > 10 else linhas_erro
                        )
                        print("   Detalhes do erro:")
                        for linha in linhas_relevantes:
                            print(f"   {linha}")
                    falhas += 1

                pbar.update(1)

        # Resumo final
        print("\n" + "=" * 60)
        print("📊 RESUMO DO PROCESSAMENTO")
        print("-" * 60)
        print(f"✅ Sucessos: {sucesso}")
        print(f"❌ Falhas: {falhas}")
        print(f"📁 Total processado: {len(arquivos)}")
        print("-" * 60)
        print("✨ Processo finalizado!")

        return {"sucessos": sucesso, "falhas": falhas}
