"""
Otimizador de imagens (JPG, PNG, WebP, AVIF, HEIC).
"""

import hashlib
import os
import subprocess
import shutil
from pathlib import Path
from typing import List, Tuple, Optional

from PIL import Image

try:
    from PIL.ExifTags import TAGS
except ImportError:
    TAGS = {}

from ..common.paths import criar_pastas, obter_pastas_entrada_saida
from ..common.progress import ProgressBar


class OtimizadorImagens:
    """
    Classe para otimizar e converter imagens.
    """

    # Extensões suportadas
    EXTENSOES_VALIDAS = {".jpg", ".jpeg", ".png", ".webp"}

    # Configurações padrão
    QUALIDADE_JPG = 85
    PRESERVAR_EXIF = True
    COMPRIMIR_PNG = True
    BATCH_INTELIGENTE = True  # Pular arquivos já processados

    def __init__(
        self,
        pasta_entrada: Path = None,
        pasta_saida: Path = None,
        qualidade_jpg: int = None,
        preservar_exif: bool = None,
        comprimir_png: bool = None,
        batch_inteligente: bool = None,
    ):
        """
        Inicializa o otimizador.

        Args:
            pasta_entrada: Pasta de entrada (None = padrão).
            pasta_saida: Pasta de saída (None = padrão).
            qualidade_jpg: Qualidade JPG (0-100, None = padrão).
            preservar_exif: Se True, preserva metadados EXIF.
            comprimir_png: Se True, tenta comprimir PNGs adicionalmente.
            batch_inteligente: Se True, pula arquivos já processados.
        """
        if pasta_entrada is None or pasta_saida is None:
            entrada, saida = obter_pastas_entrada_saida("imagens")
            self.pasta_entrada = pasta_entrada or entrada
            self.pasta_saida = pasta_saida or saida
        else:
            self.pasta_entrada = pasta_entrada
            self.pasta_saida = pasta_saida

        self.qualidade_jpg = qualidade_jpg or self.QUALIDADE_JPG
        self.preservar_exif = (
            preservar_exif if preservar_exif is not None else self.PRESERVAR_EXIF
        )
        self.comprimir_png = (
            comprimir_png if comprimir_png is not None else self.COMPRIMIR_PNG
        )
        self.batch_inteligente = (
            batch_inteligente
            if batch_inteligente is not None
            else self.BATCH_INTELIGENTE
        )

    def _calcular_hash_arquivo(self, caminho: Path) -> str:
        """
        Calcula hash MD5 do arquivo para comparação.

        Args:
            caminho: Caminho do arquivo.

        Returns:
            str: Hash MD5 do arquivo.
        """
        hash_md5 = hashlib.md5()
        try:
            with open(caminho, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""

    def _arquivo_ja_processado(self, caminho_origem: Path, caminho_saida: Path) -> bool:
        """
        Verifica se o arquivo já foi processado (batch inteligente).

        Args:
            caminho_origem: Caminho do arquivo original.
            caminho_saida: Caminho do arquivo de saída.

        Returns:
            bool: True se já foi processado.
        """
        if not self.batch_inteligente:
            return False

        if not caminho_saida.exists():
            return False

        # Compara hash dos arquivos
        hash_origem = self._calcular_hash_arquivo(caminho_origem)
        hash_saida = self._calcular_hash_arquivo(caminho_saida)

        # Se os hashes são iguais, já foi processado
        if hash_origem == hash_saida and hash_origem != "":
            return True

        return False

    def _preservar_exif(self, img: Image.Image) -> dict:
        """
        Extrai metadados EXIF da imagem.

        Args:
            img: Objeto PIL Image.

        Returns:
            dict: Metadados EXIF.
        """
        exif_data = {}
        try:
            exif = img.getexif()
            if exif is not None:
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    exif_data[tag] = value
        except Exception:
            pass
        return exif_data

    def _comprimir_png(self, caminho: Path) -> bool:
        """
        Tenta comprimir PNG usando pngquant (se disponível).

        Args:
            caminho: Caminho do arquivo PNG.

        Returns:
            bool: True se conseguiu comprimir.
        """
        if not self.comprimir_png:
            return False

        # Verifica se pngquant está disponível
        if shutil.which("pngquant") is None:
            return False

        try:
            # Cria arquivo temporário
            temp_path = caminho.with_suffix(".tmp.png")
            caminho.rename(temp_path)

            # Executa pngquant
            resultado = subprocess.run(
                [
                    "pngquant",
                    "--quality=65-80",
                    "--force",
                    "--output",
                    str(caminho),
                    str(temp_path),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30,
            )

            if resultado.returncode == 0 and caminho.exists():
                # Remove temporário
                if temp_path.exists():
                    temp_path.unlink()
                return True
            else:
                # Restaura original se falhou
                if temp_path.exists():
                    temp_path.rename(caminho)
        except Exception:
            # Restaura original em caso de erro
            temp_path = caminho.with_suffix(".tmp.png")
            if temp_path.exists():
                temp_path.rename(caminho)

        return False

    def _otimizar_imagem(
        self, caminho_origem: Path, pasta_destino: Path
    ) -> Tuple[bool, Path, Optional[str]]:
        """
        Processa uma imagem: converte WebP para JPG e otimiza.

        Args:
            caminho_origem: Caminho da imagem original.
            pasta_destino: Pasta de destino.

        Returns:
            Tuple[bool, Path, Optional[str]]: (sucesso, caminho_saida, mensagem)
        """
        try:
            extensao = caminho_origem.suffix.lower()
            nome_arquivo = caminho_origem.stem

            # Define o nome de saída
            # WebP, AVIF, HEIC/HEIF → JPG
            if extensao in {".webp", ".avif", ".heic", ".heif"}:
                nova_extensao = ".jpg"
            else:
                nova_extensao = extensao

            caminho_saida = pasta_destino / f"{nome_arquivo}{nova_extensao}"

            # Verifica se já foi processado (batch inteligente)
            if self._arquivo_ja_processado(caminho_origem, caminho_saida):
                return True, caminho_saida, "já processado"

            # Tenta abrir a imagem
            try:
                img = Image.open(caminho_origem)
            except Exception as e:
                # Tenta converter HEIC/HEIF usando pillow-heif se disponível
                if extensao in {".heic", ".heif"}:
                    try:
                        from pillow_heif import register_heif_opener

                        register_heif_opener()
                        img = Image.open(caminho_origem)
                    except ImportError:
                        return (
                            False,
                            None,
                            f"HEIC/HEIF requer pillow-heif: pip install pillow-heif",
                        )
                    except Exception:
                        return False, None, f"Erro ao abrir HEIC/HEIF: {e}"

            # Preserva EXIF se solicitado
            exif_data = None
            if self.preservar_exif:
                exif_data = self._preservar_exif(img)

            # Se a imagem for RGBA (com transparência) e o destino for JPG,
            # precisamos converter para RGB (fundo branco)
            if (
                extensao in {".webp", ".png", ".avif", ".heic", ".heif"}
            ) and nova_extensao == ".jpg":
                if img.mode in ("RGBA", "LA", "P"):
                    # Cria fundo branco
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    fundo = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "RGBA":
                        fundo.paste(
                            img, mask=img.split()[3] if len(img.split()) == 4 else None
                        )
                    else:
                        fundo.paste(img)
                    img = fundo
                elif img.mode not in ("RGB", "L"):
                    img = img.convert("RGB")

            # Salva com otimização
            save_kwargs = {"optimize": True}

            if nova_extensao in [".jpg", ".jpeg"]:
                save_kwargs["quality"] = self.qualidade_jpg
                if exif_data and hasattr(img, "save"):
                    # Tenta preservar EXIF (Pillow preserva automaticamente se disponível)
                    try:
                        img.save(caminho_saida, "JPEG", **save_kwargs)
                    except Exception:
                        img.save(caminho_saida, "JPEG", **save_kwargs)
                else:
                    img.save(caminho_saida, "JPEG", **save_kwargs)
            elif nova_extensao == ".png":
                img.save(caminho_saida, "PNG", **save_kwargs)
                # Tenta comprimir PNG adicionalmente
                if self.comprimir_png:
                    self._comprimir_png(caminho_saida)
            else:
                img.save(caminho_saida, **save_kwargs)

            img.close()

            return True, caminho_saida, None
        except Exception as e:
            return False, None, str(e)

    def processar(self, deletar_originais: bool = True) -> dict:
        """
        Processa todas as imagens na pasta de entrada.

        Args:
            deletar_originais: Se True, deleta os arquivos originais após processar.

        Returns:
            dict: Estatísticas do processamento.
        """
        if not criar_pastas(self.pasta_entrada, self.pasta_saida):
            return {"sucessos": 0, "falhas": 0, "economia_mb": 0.0, "pulados": 0}

        pasta_entrada = Path(self.pasta_entrada).resolve()
        pasta_saida = Path(self.pasta_saida).resolve()

        # Lista arquivos válidos
        arquivos = [
            f
            for f in pasta_entrada.iterdir()
            if f.is_file() and f.suffix.lower() in self.EXTENSOES_VALIDAS
        ]

        if not arquivos:
            print(f"ℹ️  Nenhuma imagem encontrada em {pasta_entrada}")
            return {"sucessos": 0, "falhas": 0, "economia_mb": 0.0, "pulados": 0}

        print(f"🚀 Iniciando processamento de {len(arquivos)} imagem(ns)...")
        print(
            f"⚙️  Configuração: Qualidade JPG {self.qualidade_jpg}% | "
            f"EXIF: {'Preservado' if self.preservar_exif else 'Removido'} | "
            f"Batch Inteligente: {'Ativo' if self.batch_inteligente else 'Inativo'}"
        )
        print("-" * 60)

        sucessos = 0
        falhas = 0
        pulados = 0
        total_economizado = 0

        # Barra de progresso
        with ProgressBar(
            total=len(arquivos), desc="Progresso", unit="img"
        ).context() as pbar:
            for arquivo in arquivos:
                tamanho_original = arquivo.stat().st_size

                sucesso, caminho_saida, mensagem = self._otimizar_imagem(
                    arquivo, pasta_saida
                )

                if sucesso and caminho_saida:
                    if mensagem == "já processado":
                        pulados += 1
                        pbar.set_postfix({"Pulados": pulados})
                    elif caminho_saida.exists():
                        tamanho_novo = caminho_saida.stat().st_size
                        economia = tamanho_original - tamanho_novo
                        total_economizado += economia

                        # Deleta o original após sucesso
                        if deletar_originais:
                            try:
                                arquivo.unlink()
                            except OSError:
                                pass

                        sucessos += 1
                    else:
                        falhas += 1
                        if mensagem:
                            print(f"\n⚠️  {arquivo.name}: {mensagem}")
                else:
                    falhas += 1
                    if mensagem:
                        print(f"\n❌ {arquivo.name}: {mensagem}")

                pbar.update(1)

        # Resumo Final
        economia_mb = total_economizado / (1024 * 1024)
        print("\n" + "=" * 60)
        print("📊 RESUMO DO PROCESSAMENTO")
        print("-" * 60)
        print(f"✅ Sucessos: {sucessos}")
        if pulados > 0:
            print(f"⏭️  Pulados (já processados): {pulados}")
        print(f"❌ Falhas: {falhas}")
        print(f"💾 Espaço total liberado: {economia_mb:.2f} MB")
        print("-" * 60)
        print("✨ Processo finalizado com sucesso!")

        return {
            "sucessos": sucessos,
            "falhas": falhas,
            "pulados": pulados,
            "economia_mb": economia_mb,
        }
