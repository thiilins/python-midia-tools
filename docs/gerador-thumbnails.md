# Gerador de Thumbnails

## Descrição

Ferramenta para gerar thumbnails (miniaturas) de imagens e vídeos em múltiplos tamanhos. Útil para criar previews, galerias e otimizar carregamento de páginas web.

## Funcionalidades

- ✅ **Thumbnails de imagens**: Gera miniaturas de JPG, PNG, WebP
- ✅ **Thumbnails de vídeos**: Extrai frames de vídeos
- ✅ **Múltiplos tamanhos**: Gera 3 tamanhos por padrão (320x240, 640x480, 1280x720)
- ✅ **Processamento em lote**: Processa múltiplos arquivos de uma vez
- ✅ **Barra de progresso**: Acompanhamento em tempo real
- ✅ **Qualidade otimizada**: Thumbnails com qualidade 85% e otimização

## Requisitos

- Python 3.6+
- Pillow (PIL)
- FFmpeg (para vídeos)
- FFprobe (para vídeos)

## Uso

### Via Menu Interativo

Execute o script `start.bat` (Windows) ou `start.sh` (Linux/macOS) e selecione a opção **Gerar Thumbnails**.

### Via Linha de Comando

```bash
python gerador-thumbnails.py
```

## Configuração

O script está configurado com os seguintes tamanhos padrão:

- **320x240**: Pequeno (mobile, preview)
- **640x480**: Médio (tablet, galeria)
- **1280x720**: Grande (desktop, HD)

### Personalização

Para personalizar os tamanhos, edite o arquivo `gerador-thumbnails.py`:

```python
# Tamanhos padrão
tamanhos = ["320x240", "640x480", "1280x720"]
```

## Formatos Suportados

### Imagens
- JPG/JPEG
- PNG
- WebP

### Vídeos
- MP4
- M4V
- MOV
- WebM
- AVI

## Pastas

- **Entrada Imagens**: `entrada/imagens/`
- **Entrada Vídeos**: `entrada/videos/`
- **Saída**: `saida/thumbnails/`

## Como Funciona

### Para Imagens

1. Reduz imagem se muito grande (máx 1920x1920)
2. Gera thumbnail para cada tamanho solicitado
3. Salva como JPG com qualidade 85%

### Para Vídeos

1. Obtém duração do vídeo
2. Extrai frame do meio do vídeo
3. Redimensiona para cada tamanho solicitado
4. Salva como JPG

## Exemplos

### Gerar thumbnails padrão

```bash
python gerador-thumbnails.py
```

### Personalizar tamanhos (editar código)

```python
# No arquivo gerador-thumbnails.py
tamanhos = ["150x150", "300x300", "600x600"]  # Quadrados
```

## Notas

- Thumbnails de imagens usam algoritmo LANCZOS para alta qualidade
- Thumbnails de vídeos extraem frame do meio (50% da duração)
- Todos os thumbnails são salvos como JPG
- Nomes dos arquivos: `{nome_original}_{tamanho}.jpg`
- Se nenhum arquivo for encontrado, o script retorna erro

## Troubleshooting

**Problema**: Thumbnails de vídeos não são geradas
- **Solução**: Verifique se FFmpeg está instalado e no PATH

**Problema**: Thumbnails ficam distorcidas
- **Solução**: O script mantém proporção. Thumbnails podem ter dimensões ligeiramente diferentes do solicitado

**Problema**: Erro "Nenhum arquivo encontrado"
- **Solução**: Verifique se há imagens ou vídeos nas pastas de entrada

**Problema**: Thumbnails muito grandes
- **Solução**: Ajuste os tamanhos no código ou use ferramenta de otimização de imagens


