"""
Detector de vídeos duplicados.
"""

import hashlib
from pathlib import Path
from typing import Dict, List

from ..common.paths import obter_pastas_entrada_saida
from ..common.progress import ProgressBar


class DetectorDuplicatasVideos:
    """
    Classe para detectar vídeos duplicados.
    """

    EXTENSOES_VALIDAS = {".mp4", ".m4v", ".mov", ".webm", ".avi", ".mkv"}

    def __init__(
        self,
        pasta_origem: Path = None,
        remover_automaticamente: bool = False,
    ):
        """
        Inicializa o detector.

        Args:
            pasta_origem: Pasta com vídeos para verificar (None = padrão).
            remover_automaticamente: Se True, remove duplicatas automaticamente.
        """
        if pasta_origem is None:
            entrada, _ = obter_pastas_entrada_saida("videos")
            self.pasta_origem = entrada
        else:
            self.pasta_origem = pasta_origem

        self.remover_automaticamente = remover_automaticamente

    def _calcular_hash_arquivo(self, caminho: Path) -> str:
        """
        Calcula hash MD5 do arquivo (amostra para vídeos grandes).

        Args:
            caminho: Caminho do arquivo.

        Returns:
            str: Hash MD5.
        """
        hash_md5 = hashlib.md5()
        try:
            tamanho = caminho.stat().st_size
            # Para vídeos grandes, usa amostra (primeiros 10MB + últimos 10MB)
            with open(caminho, "rb") as f:
                # Primeiros 10MB
                chunk_size = 10 * 1024 * 1024
                chunk = f.read(chunk_size)
                hash_md5.update(chunk)

                # Últimos 10MB se o arquivo for grande
                if tamanho > chunk_size * 2:
                    f.seek(tamanho - chunk_size)
                    chunk = f.read(chunk_size)
                    hash_md5.update(chunk)

            return hash_md5.hexdigest()
        except Exception:
            return ""

    def processar(self) -> dict:
        """
        Processa e detecta duplicatas.

        Returns:
            dict: Estatísticas do processamento.
        """
        pasta_origem = Path(self.pasta_origem).resolve()

        if not pasta_origem.exists():
            print(f"❌ Erro: Pasta não encontrada: {pasta_origem}")
            return {"duplicatas": 0, "removidos": 0}

        arquivos = [
            f
            for f in pasta_origem.iterdir()
            if f.is_file() and f.suffix.lower() in self.EXTENSOES_VALIDAS
        ]

        if len(arquivos) < 2:
            print("ℹ️  É necessário pelo menos 2 vídeos para detectar duplicatas.")
            return {"duplicatas": 0, "removidos": 0}

        print(f"🚀 Analisando {len(arquivos)} vídeo(s) para duplicatas...")
        print("   (Usando amostra de arquivos grandes para velocidade)")
        print("-" * 60)

        # Mapa de hash -> lista de arquivos
        hash_map: Dict[str, List[Path]] = {}

        # Calcula hashes
        with ProgressBar(
            total=len(arquivos), desc="Calculando hashes", unit="vídeo"
        ).context() as pbar:
            for arquivo in arquivos:
                hash_val = self._calcular_hash_arquivo(arquivo)
                if hash_val:
                    if hash_val not in hash_map:
                        hash_map[hash_val] = []
                    hash_map[hash_val].append(arquivo)
                pbar.update(1)

        # Encontra duplicatas
        duplicatas_encontradas = 0
        removidos = 0

        print("\n📊 Analisando resultados...")
        print("-" * 60)

        for hash_val, arquivos_duplicados in hash_map.items():
            if len(arquivos_duplicados) > 1:
                duplicatas_encontradas += len(arquivos_duplicados) - 1

                # Mantém o primeiro, remove os outros
                original = arquivos_duplicados[0]
                duplicados = arquivos_duplicados[1:]

                print(f"\n🔍 Duplicatas encontradas ({len(arquivos_duplicados)} arquivos):")
                print(f"   ✅ Mantido: {original.name} ({original.stat().st_size / (1024*1024):.2f} MB)")

                for dup in duplicados:
                    tamanho_mb = dup.stat().st_size / (1024 * 1024)
                    print(f"   ❌ Duplicata: {dup.name} ({tamanho_mb:.2f} MB)")

                    if self.remover_automaticamente:
                        try:
                            dup.unlink()
                            print(f"      🗑️  Removido")
                            removidos += 1
                        except Exception as e:
                            print(f"      ⚠️  Erro ao remover: {e}")

        print("\n" + "=" * 60)
        print("📊 RESUMO")
        print("-" * 60)
        print(f"🔍 Duplicatas encontradas: {duplicatas_encontradas}")
        if self.remover_automaticamente:
            print(f"🗑️  Arquivos removidos: {removidos}")
        else:
            print("💡 Use --remover para remover duplicatas automaticamente")
        print("-" * 60)

        return {"duplicatas": duplicatas_encontradas, "removidos": removidos}

