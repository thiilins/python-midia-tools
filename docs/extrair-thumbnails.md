# Extrator de Thumbnails

## Descrição

Ferramenta para extrair thumbnails (miniaturas) de vídeos. Extrai múltiplos frames de cada vídeo distribuídos ao longo da duração.

## Funcionalidades

- ✅ **Múltiplas thumbnails**: Extrai várias thumbnails por vídeo
- ✅ **Distribuição inteligente**: Distribui frames ao longo do vídeo
- ✅ **Tamanho configurável**: Define tamanho das thumbnails
- ✅ **Processamento em lote**: Processa múltiplos vídeos de uma vez
- ✅ **Barra de progresso**: Acompanhamento em tempo real

## Requisitos

- Python 3.6+
- FFmpeg
- FFprobe

## Uso

### Via Menu Interativo

Execute o script `start.bat` (Windows) ou `start.sh` (Linux/macOS) e selecione a opção **Extrair Thumbnails**.

### Via Linha de Comando

```bash
python extrair-thumbnails.py
```

## Configuração

O script está configurado com os seguintes parâmetros padrão:

- **Quantidade**: 3 thumbnails por vídeo
- **Tamanho**: 320x240

### Personalização

Para personalizar os parâmetros, edite o arquivo `extrair-thumbnails.py`:

```python
extrator = ExtratorThumbnails(
    quantidade=3,        # Número de thumbnails por vídeo
    tamanho="320x240"    # Tamanho (ex: "640x480", "1280x720")
)
```

## Formatos Suportados

- MP4
- M4V
- MOV
- WebM
- AVI
- MKV

## Pastas

- **Entrada**: `entrada/videos/`
- **Saída**: `saida/thumbnails/`

## Como Funciona

1. Obtém duração do vídeo
2. Calcula intervalos para distribuir as thumbnails
3. Extrai frame em cada intervalo
4. Redimensiona para o tamanho especificado
5. Salva como JPG

### Exemplo de Distribuição

Para um vídeo de 60 segundos com 3 thumbnails:
- Thumbnail 1: 15s (25%)
- Thumbnail 2: 30s (50%)
- Thumbnail 3: 45s (75%)

## Exemplos

### Extrair 3 thumbnails 320x240 (padrão)

```bash
python extrair-thumbnails.py
```

### Personalizar quantidade e tamanho (editar código)

```python
# 5 thumbnails grandes
extrator = ExtratorThumbnails(quantidade=5, tamanho="1280x720")

# 1 thumbnail média
extrator = ExtratorThumbnails(quantidade=1, tamanho="640x480")
```

## Nomenclatura

Os arquivos são nomeados como:
```
{nome_video}_thumb_01.jpg
{nome_video}_thumb_02.jpg
{nome_video}_thumb_03.jpg
...
```

## Notas

- Thumbnails são extraídas distribuídas ao longo do vídeo (não todas no início)
- Timeout de 30 segundos por thumbnail
- Todas as thumbnails são salvas como JPG
- Se o vídeo não tiver duração válida, nenhuma thumbnail é extraída

## Troubleshooting

**Problema**: Erro "FFmpeg não encontrado"
- **Solução**: Instale FFmpeg e verifique se está no PATH

**Problema**: Nenhuma thumbnail extraída
- **Solução**: Verifique se o vídeo tem duração válida e se FFprobe consegue ler

**Problema**: Thumbnails muito pequenas
- **Solução**: Aumente o tamanho (ex: "640x480" ou "1280x720")

**Problema**: Poucas thumbnails
- **Solução**: Aumente a quantidade no código

**Problema**: Timeout
- **Solução**: Normal para vídeos muito longos ou corrompidos. Verifique o vídeo

