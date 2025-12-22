#!/bin/bash

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Muda para o diretório raiz do projeto
cd "$(dirname "$0")/.." || exit 1

erro() { echo -e "${RED}[ERRO]${NC} $1" >&2; }
sucesso() { echo -e "${GREEN}[OK]${NC} $1"; }
aviso() { echo -e "${YELLOW}[!]${NC} $1"; }

echo -e "${YELLOW}=========================================${NC}"
echo -e "${YELLOW}   VERIFICANDO AMBIENTE${NC}"
echo -e "${YELLOW}=========================================${NC}"

# 1. Verificar Python
if ! command -v python3 &> /dev/null; then
    erro "Python 3 nao encontrado. Instale: sudo apt-get install python3"
    exit 1
fi
sucesso "Python encontrado: $(python3 --version)"

# 2. Verificar pip
if ! python3 -m pip --version &> /dev/null; then
    aviso "Instalando pip..."
    python3 -m ensurepip --upgrade || { erro "Falha ao instalar pip"; exit 1; }
fi

# 3. Verificar dependências
echo "Verificando dependencias..."
if ! python3 -c "import tqdm, PIL, cv2, numpy" &> /dev/null; then
    aviso "Instalando dependencias..."
    python3 -m pip install -r requirements.txt --quiet || { erro "Falha ao instalar dependencias"; exit 1; }
fi

# 4. Verificar FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    aviso "FFmpeg nao encontrado (necessario apenas para videos)."
    if command -v apt-get &> /dev/null; then
        read -p "Instalar FFmpeg agora? (s/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Ss]$ ]]; then
            sudo apt-get update && sudo apt-get install -y ffmpeg
        fi
    fi
else
    sucesso "FFmpeg encontrado"
fi

# 5. Menu
clear
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}   MEDIA TOOLS - CANIVETE SUICO DE MIDIA${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "  IMAGENS:"
echo "  1. Otimizar Imagens"
echo "  2. Validar Imagens"
echo "  3. Converter WebP para JPG"
echo "  4. Detectar Duplicatas de Imagens"
echo "  5. OCR de Imagens"
echo "  6. Remover Fundo de Imagens"
echo "  7. Corretor de Cores e Filtros"
echo "  8. Gerar Thumbnails"
echo ""
echo "  VIDEOS:"
echo "  9. Otimizar Videos"
echo "  10. Converter WebM para MP4"
echo "  11. Extrair Audio de Videos"
echo "  12. Extrair Thumbnails de Videos"
echo "  13. Merge Videos"
echo "  14. Estabilizador de Video"
echo "  15. Detectar Duplicatas de Videos"
echo ""
echo "  0. Sair"
echo ""
read -p "Digite o numero da opcao: " OPCAO

declare -A SCRIPTS=(
    [1]="otimizador-imagens.py"
    [2]="validate-images.py"
    [3]="webp-to-jpg.py"
    [4]="detector-duplicatas-imagens.py"
    [5]="ocr-imagens.py"
    [6]="remover-fundo.py"
    [7]="corretor-cores.py"
    [8]="gerador-thumbnails.py"
    [9]="otimizador-video.py"
    [10]="webm-mp4.py"
    [11]="extrair-audio.py"
    [12]="extrair-thumbnails.py"
    [13]="merge-videos.py"
    [14]="estabilizador-video.py"
    [15]="detector-duplicatas-videos.py"
)

if [ "$OPCAO" = "0" ]; then
    exit 0
fi

SCRIPT="${SCRIPTS[$OPCAO]}"
if [ -z "$SCRIPT" ]; then
    erro "Opcao invalida."
    exit 1
fi

echo ""
echo -e "${GREEN}[V]${NC} Iniciando $SCRIPT..."
echo "-----------------------------------------"
python3 "$SCRIPT"
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    erro "Script retornou codigo de erro: $EXIT_CODE"
    exit $EXIT_CODE
fi
