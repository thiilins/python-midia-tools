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
echo -e "${YELLOW}   CONFIGURANDO AMBIENTE VIRTUAL${NC}"
echo -e "${YELLOW}=========================================${NC}"

# Verifica Python
if ! command -v python3 &> /dev/null; then
    erro "Python 3 nao encontrado. Instale: sudo apt-get install python3"
    exit 1
fi
sucesso "Python: $(python3 --version)"

# Verifica se venv já existe
if [ -d "venv" ]; then
    read -p "Ambiente virtual existe. Recriar? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        echo "Removendo..."
        rm -rf venv
    else
        source venv/bin/activate
        pip install -r requirements.txt --quiet
        sucesso "Dependencias atualizadas!"
        exit 0
    fi
fi

# Cria venv
echo "Criando ambiente virtual..."
python3 -m venv venv || { erro "Falha ao criar ambiente virtual"; exit 1; }

# Ativa e instala
echo "Instalando dependencias..."
source venv/bin/activate
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt || { erro "Falha ao instalar dependencias"; exit 1; }

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}   AMBIENTE VIRTUAL CONFIGURADO!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "Para usar:"
echo "  source venv/bin/activate"
echo "  python otimizador-imagens.py"
echo ""
