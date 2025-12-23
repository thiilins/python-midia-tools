# OCR de Imagens

## Descrição

Ferramenta para detectar texto em imagens usando OCR (Optical Character Recognition). Separa imagens com texto legível das imagens sem texto.

## Funcionalidades

- ✅ **Detecção de texto**: Identifica texto em imagens
- ✅ **Múltiplos idiomas**: Suporta português e inglês
- ✅ **Separação automática**: Move imagens para pastas "com_texto" e "sem_texto"
- ✅ **Análise de confiança**: Calcula nível de confiança do OCR
- ✅ **Processamento em lote**: Processa múltiplas imagens de uma vez
- ✅ **Barra de progresso**: Acompanhamento em tempo real

## Requisitos

- Python 3.6+
- pytesseract
- Tesseract OCR (instalado no sistema)

## Instalação do Tesseract

### Windows
1. Baixe o instalador: https://github.com/UB-Mannheim/tesseract/wiki
2. Instale incluindo idiomas português e inglês
3. Adicione ao PATH ou configure `pytesseract.pytesseract.tesseract_cmd`

### Linux
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-por tesseract-ocr-eng
```

### macOS
```bash
brew install tesseract tesseract-lang
```

## Uso

### Via Menu Interativo

Execute o script `start.bat` (Windows) ou `start.sh` (Linux/macOS) e selecione a opção **OCR de Imagens**.

### Via Linha de Comando

```bash
python ocr-imagens.py
```

## Configuração

O script detecta automaticamente texto usando Tesseract OCR com suporte a português e inglês.

### Critérios de Detecção

- **Com texto**: Mais de 10 caracteres detectados
- **Sem texto**: Menos de 10 caracteres ou nenhum texto

## Formatos Suportados

- JPG/JPEG
- PNG
- WebP
- BMP
- TIFF

## Pastas

- **Entrada**: `entrada/imagens/`
- **Saída com texto**: `saida/com_texto/`
- **Saída sem texto**: `saida/sem_texto/`

## Como Funciona

1. Analisa cada imagem usando Tesseract OCR
2. Extrai texto detectado
3. Calcula confiança média
4. Classifica como "com texto" ou "sem texto"
5. Move imagem para pasta correspondente

## Exemplos

### Analisar imagens (padrão)

```bash
python ocr-imagens.py
```

## Notas

- Requer Tesseract OCR instalado no sistema
- Suporta português e inglês por padrão
- Imagens são **movidas** (não copiadas) para pastas de saída
- Confiança é calculada baseada na qualidade do OCR
- Texto muito pequeno ou de baixa qualidade pode não ser detectado

## Troubleshooting

**Problema**: Erro "Tesseract OCR não está disponível"
- **Solução**: Instale Tesseract OCR no sistema (veja seção Instalação)

**Problema**: Texto não detectado em imagens com texto
- **Solução**:
  - Verifique qualidade da imagem (resolução, contraste)
  - Texto muito pequeno ou distorcido pode não ser detectado
  - Imagens muito escuras ou claras podem ter problemas

**Problema**: Falsos positivos (imagens sem texto classificadas como "com texto")
- **Solução**: Normal - padrões visuais podem ser interpretados como texto. Ajuste o threshold no código se necessário

**Problema**: Erro ao mover arquivo
- **Solução**: Verifique permissões de escrita nas pastas de saída

**Problema**: OCR muito lento
- **Solução**: Normal para muitas imagens grandes. O processo pode demorar

