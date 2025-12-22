"""
Validador de imagens (verifica se são legíveis).
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Tuple

import cv2
import numpy as np

from ..common.paths import obter_diretorio_base, obter_pastas_entrada_saida
from ..common.progress import ProgressBar


class ValidadorImagens:
    """
    Classe para validar se imagens são legíveis.
    """

    # Limiares de validação
    CROP_TOP_PCT = 0.15
    LIMIAR_ESCURO = 40
    LIMIAR_UNIFORMIDADE_CRITICO = 20
    LIMIAR_UNIFORMIDADE_ALERTA = 36
    LIMIAR_FOCO = 110
    LIMIAR_BORDAS_PCT = 0.005

    def __init__(
        self,
        pasta_origem: Path = None,
        pasta_legiveis: Path = None,
        pasta_ilegiveis: Path = None,
        arquivo_log: Path = None,
        gerar_relatorio_html: bool = False,
    ):
        """
        Inicializa o validador.

        Args:
            pasta_origem: Pasta com imagens para validar (None = padrão).
            pasta_legiveis: Pasta para imagens legíveis (None = padrão).
            pasta_ilegiveis: Pasta para imagens ilegíveis (None = padrão).
            arquivo_log: Caminho do arquivo de log (None = padrão).
            gerar_relatorio_html: Se True, gera relatório HTML com previews.
        """
        if pasta_origem is None:
            base = obter_diretorio_base()
            self.pasta_origem = base / "entrada" / "downloads"
        else:
            self.pasta_origem = pasta_origem

        if pasta_legiveis is None or pasta_ilegiveis is None:
            base = obter_diretorio_base()
            self.pasta_legiveis = pasta_legiveis or (base / "saida" / "legiveis")
            self.pasta_ilegiveis = pasta_ilegiveis or (base / "saida" / "ilegiveis")
        else:
            self.pasta_legiveis = pasta_legiveis
            self.pasta_ilegiveis = pasta_ilegiveis

        if arquivo_log is None:
            base = obter_diretorio_base()
            self.arquivo_log = base / "historico_processamento.log"
        else:
            self.arquivo_log = arquivo_log

        self.gerar_relatorio_html = gerar_relatorio_html
        self.resultados = []  # Armazena resultados para relatório HTML

    def _analisar_imagem(self, caminho_imagem: Path) -> Dict:
        """
        Analisa uma imagem e determina se é legível.

        Args:
            caminho_imagem: Caminho da imagem a analisar.

        Returns:
            dict: Resultado da análise com status e motivo.
        """
        try:
            img = cv2.imread(str(caminho_imagem))
            if img is None:
                return {"status": False, "motivo": "Erro Leitura"}

            gray_full = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            h, w = gray_full.shape

            # CROP (Recorte do Topo)
            crop_start = int(h * self.CROP_TOP_PCT)
            gray = gray_full[crop_start:, :]

            h_crop, w_crop = gray.shape
            total_pixels = h_crop * w_crop
            if total_pixels == 0:
                return {"status": False, "motivo": "Erro crop"}

            # MÉTRICAS
            brilho_medio = np.mean(gray)
            desvio_padrao = np.std(gray)
            foco = cv2.Laplacian(gray, cv2.CV_64F).var()

            # Detecção de Bordas
            bordas = cv2.Canny(gray, 50, 150)
            pixels_borda = np.count_nonzero(bordas)
            ratio_bordas = pixels_borda / total_pixels

            motivos = []
            is_legivel = True

            # 1. Checagem de Escuridão
            if brilho_medio < self.LIMIAR_ESCURO:
                is_legivel = False
                motivos.append(f"Muito escura ({brilho_medio:.1f})")

            # 2. Checagem de Uniformidade
            elif desvio_padrao < self.LIMIAR_UNIFORMIDADE_ALERTA:
                if desvio_padrao < self.LIMIAR_UNIFORMIDADE_CRITICO:
                    is_legivel = False
                    motivos.append(f"Imagem lisa/sólida (StdDev: {desvio_padrao:.1f})")
                else:
                    if ratio_bordas < self.LIMIAR_BORDAS_PCT:
                        is_legivel = False
                        motivos.append(
                            f"Uniforme e sem texto (StdDev: {desvio_padrao:.1f}, Bordas: {ratio_bordas:.4f})"
                        )

            # 3. Checagem de Foco
            if is_legivel and foco < self.LIMIAR_FOCO:
                if ratio_bordas < self.LIMIAR_BORDAS_PCT:
                    is_legivel = False
                    motivos.append(f"Desfocada (Foco: {foco:.1f})")
                else:
                    motivos.append(f"AVISO: Foco baixo ({foco:.1f}) mas legível.")

            # 4. Checagem final de conteúdo
            if is_legivel and ratio_bordas < (self.LIMIAR_BORDAS_PCT / 3):
                is_legivel = False
                motivos.append(f"Imagem vazia (Bordas: {ratio_bordas:.4f})")

            return {
                "status": is_legivel,
                "motivo": ", ".join(motivos) if motivos else "Ok",
                "metricas": (brilho_medio, desvio_padrao, foco, ratio_bordas),
            }

        except Exception as e:
            return {"status": False, "motivo": f"Erro: {str(e)}"}

    def processar(self) -> dict:
        """
        Processa todas as imagens na pasta de origem.

        Returns:
            dict: Estatísticas do processamento.
        """
        import logging

        # Configuração do Logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(message)s",
            datefmt="%d/%m/%Y %H:%M:%S",
            handlers=[logging.FileHandler(self.arquivo_log, encoding="utf-8")],
        )

        pasta_origem = Path(self.pasta_origem).resolve()
        pasta_legiveis = Path(self.pasta_legiveis).resolve()
        pasta_ilegiveis = Path(self.pasta_ilegiveis).resolve()

        # Cria pastas
        pasta_legiveis.mkdir(parents=True, exist_ok=True)
        pasta_ilegiveis.mkdir(parents=True, exist_ok=True)

        if not pasta_origem.exists():
            print(f"❌ Erro: Pasta downloads não encontrada: {pasta_origem}")
            logging.error("Pasta downloads nao encontrada")
            return {"legiveis": 0, "ilegiveis": 0}

        # Lista arquivos válidos
        arquivos = [
            f
            for f in pasta_origem.iterdir()
            if f.is_file() and f.suffix.lower() in (".jpg", ".jpeg", ".png")
        ]

        total_arquivos = len(arquivos)
        if total_arquivos == 0:
            print("⚠️  Nenhum arquivo para processar.")
            return {"legiveis": 0, "ilegiveis": 0}

        logging.info("=" * 60)
        logging.info("INICIANDO PROCESSAMENTO COM BARRA DE PROGRESSO")
        logging.info(f"Arquivos na fila: {total_arquivos}")

        c_leg = 0
        c_ileg = 0

        print(f"🚀 Iniciando análise de {total_arquivos} imagens...")
        print("-" * 60)

        # Barra de progresso
        with ProgressBar(
            total=total_arquivos, desc="Analisando", unit="img"
        ).context() as pbar:
            for arq in arquivos:
                res = self._analisar_imagem(arq)

                if res["status"]:
                    dest = pasta_legiveis / arq.name
                    c_leg += 1
                    st_txt = "LEGÍVEL"
                else:
                    dest = pasta_ilegiveis / arq.name
                    c_ileg += 1
                    st_txt = "ILEGÍVEL"

                # Armazena resultado para relatório HTML
                if self.gerar_relatorio_html:
                    self.resultados.append({
                        "arquivo": arq.name,
                        "status": res["status"],
                        "motivo": res["motivo"],
                        "caminho": str(dest),
                        "metricas": res.get("metricas", (0, 0, 0, 0)),
                    })

                # Movimentação dos arquivos
                if dest.exists():
                    dest.unlink()
                shutil.move(str(arq), str(dest))

                # Grava no log
                logging.info(f"{arq.name:<35} | {st_txt:<10} | {res['motivo']}")

                # Atualiza contadores na barra
                pbar.set_postfix({"✅ Legíveis": c_leg, "❌ Ilegíveis": c_ileg})
                pbar.update(1)

        # Relatório Final
        relatorio = (
            f"\n{'='*50}\n"
            f"✅ PROCESSAMENTO CONCLUÍDO\n"
            f"{'='*50}\n"
            f"📸 Total Processado: {total_arquivos}\n"
            f"👍 Legíveis:         {c_leg}\n"
            f"👎 Ilegíveis:        {c_ileg}\n"
            f"📝 Log detalhado:    {self.arquivo_log}\n"
            f"{'='*50}"
        )

        print(relatorio)
        logging.info(relatorio)

        # Gera relatório HTML se solicitado
        if self.gerar_relatorio_html:
            self._gerar_relatorio_html(c_leg, c_ileg, total_arquivos)

        return {"legiveis": c_leg, "ilegiveis": c_ileg}

    def _gerar_relatorio_html(self, legiveis: int, ilegiveis: int, total: int):
        """
        Gera relatório HTML com previews das imagens.

        Args:
            legiveis: Número de imagens legíveis.
            ilegiveis: Número de imagens ilegíveis.
            total: Total de imagens processadas.
        """
        base = obter_diretorio_base()
        html_path = base / "relatorio_validacao.html"

        html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Validação de Imagens</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .stats {{
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            flex: 1;
        }}
        .stat-card h3 {{
            margin: 0 0 10px 0;
            color: #333;
        }}
        .stat-card .number {{
            font-size: 2em;
            font-weight: bold;
        }}
        .legivel {{ color: #28a745; }}
        .ilegivel {{ color: #dc3545; }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
        }}
        .image-card {{
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .image-card img {{
            width: 100%;
            height: 150px;
            object-fit: cover;
        }}
        .image-info {{
            padding: 10px;
        }}
        .image-info .nome {{
            font-weight: bold;
            margin-bottom: 5px;
            word-break: break-word;
        }}
        .image-info .status {{
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            display: inline-block;
        }}
        .status-legivel {{
            background: #d4edda;
            color: #155724;
        }}
        .status-ilegivel {{
            background: #f8d7da;
            color: #721c24;
        }}
        .motivo {{
            font-size: 0.85em;
            color: #666;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Relatório de Validação de Imagens</h1>
        <p>Gerado em: {__import__('datetime').datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
    </div>

    <div class="stats">
        <div class="stat-card">
            <h3>Total Processado</h3>
            <div class="number">{total}</div>
        </div>
        <div class="stat-card">
            <h3>✅ Legíveis</h3>
            <div class="number legivel">{legiveis}</div>
        </div>
        <div class="stat-card">
            <h3>❌ Ilegíveis</h3>
            <div class="number ilegivel">{ilegiveis}</div>
        </div>
    </div>

    <h2>Imagens Processadas</h2>
    <div class="grid">
"""

        for resultado in self.resultados:
            status_class = "status-legivel" if resultado["status"] else "status-ilegivel"
            status_text = "✅ LEGÍVEL" if resultado["status"] else "❌ ILEGÍVEL"

            # Tenta criar caminho relativo para a imagem
            img_path = resultado["caminho"]
            if not Path(img_path).is_absolute():
                img_path = str(Path(img_path).resolve())

            html_content += f"""
        <div class="image-card">
            <img src="file://{img_path}" alt="{resultado['arquivo']}" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\\'http://www.w3.org/2000/svg\\'%3E%3Ctext y=\\'50%25\\'%3EErro ao carregar%3C/text%3E%3C/svg%3E'">
            <div class="image-info">
                <div class="nome">{resultado['arquivo']}</div>
                <span class="status {status_class}">{status_text}</span>
                <div class="motivo">{resultado['motivo']}</div>
            </div>
        </div>
"""

        html_content += """
    </div>
</body>
</html>
"""

        try:
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"\n📄 Relatório HTML gerado: {html_path}")
        except Exception as e:
            print(f"\n⚠️  Erro ao gerar relatório HTML: {e}")
