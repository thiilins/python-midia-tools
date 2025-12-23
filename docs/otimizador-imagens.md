# Otimizador de Imagens

## Descrição

Ferramenta para otimizar imagens JPG, PNG, WebP, AVIF e HEIC reduzindo tamanho mantendo qualidade visual. Inclui conversão automática de formatos e preservação de metadados EXIF.

## Funcionalidades

- ✅ **Otimização inteligente**: Reduz tamanho mantendo qualidade
- ✅ **Múltiplos formatos**: JPG, PNG, WebP, AVIF, HEIC
- ✅ **Conversão automática**: Converte WebP para JPG
- ✅ **Preservação EXIF**: Mantém metadados originais
- ✅ **Detecção de duplicatas**: Pula arquivos já processados (hash MD5)
- ✅ **Compressão PNG avançada**: Usa pngquant se disponível
- ✅ **Processamento em lote**: Processa múltiplas imagens de uma vez
- ✅ **Barra de progresso**: Acompanhamento em tempo real

## Requisitos

- Python 3.6+
- Pillow (PIL)
- pillow-heif (para HEIC/AVIF)
- pngquant (opcional, para compressão PNG avançada)

## Uso

### Via Menu Interativo

Execute o script `start.bat` (Windows) ou `start.sh` (Linux/macOS) e selecione a opção **Otimizar Imagens**.

### Via Linha de Comando

```bash
python otimizador-imagens.py
```

## Configuração

O script está configurado com os seguintes parâmetros padrão:

- **Qualidade JPG**: 85%
- **Deletar originais**: Sim (após otimização bem-sucedida)

### Personalização

Para personalizar os parâmetros, edite o arquivo `otimizador-imagens.py`:

```python
otimizador = OtimizadorImagens(
    qualidade_jpg=85  # 0-100 (maior = melhor qualidade, maior arquivo)
)
otimizador.processar(deletar_originais=True)  # True/False
```

## Formatos Suportados

### Entrada
- JPG/JPEG
- PNG
- WebP
- AVIF (requer pillow-heif)
- HEIC/HEIF (requer pillow-heif)

### Saída
- JPG (para WebP, AVIF, HEIC)
- PNG (otimizado)
- JPG (otimizado)

## Pastas

- **Entrada**: `entrada/imagens/`
- **Saída**: `saida/imagens/`

## Como Funciona

1. Analisa cada imagem
2. Verifica se já foi processada (hash MD5)
3. Extrai metadados EXIF
4. Otimiza ou converte conforme necessário
5. Preserva EXIF na imagem otimizada
6. Deleta original se solicitado

## Otimizações Aplicadas

### JPG
- Redução de qualidade (85% padrão)
- Otimização de compressão
- Preservação de EXIF

### PNG
- Compressão otimizada
- Uso de pngquant se disponível (compressão adicional)
- Preservação de transparência

### WebP → JPG
- Conversão automática
- Tratamento de transparência (fundo branco)
- Preservação de qualidade

### AVIF/HEIC → JPG
- Conversão automática
- Preservação de qualidade
- Requer pillow-heif

## Exemplos

### Otimizar imagens (padrão)

```bash
python otimizador-imagens.py
```

### Personalizar qualidade (editar código)

```python
# Alta qualidade
otimizador = OtimizadorImagens(qualidade_jpg=95)

# Compressão máxima
otimizador = OtimizadorImagens(qualidade_jpg=75)
```

## Notas

- ⚠️ **Atenção**: Com `deletar_originais=True`, os arquivos originais são **permanentemente deletados** após otimização
- Imagens já processadas são automaticamente puladas (baseado em hash MD5)
- Metadados EXIF são preservados quando possível
- WebP com transparência é convertido para JPG com fundo branco
- PNG usa compressão otimizada, pngquant se disponível

## Troubleshooting

**Problema**: Erro "PIL não encontrado"
- **Solução**: Instale Pillow: `pip install Pillow`

**Problema**: Erro ao processar HEIC/AVIF
- **Solução**: Instale pillow-heif: `pip install pillow-heif`

**Problema**: PNG não comprime bem
- **Solução**: Instale pngquant para compressão adicional:
  - Windows: `choco install pngquant`
  - Linux: `sudo apt-get install pngquant`
  - macOS: `brew install pngquant`

**Problema**: Imagem não otimizada (já processada)
- **Solução**: Normal - imagens já processadas são puladas automaticamente

**Problema**: Qualidade baixa
- **Solução**: Aumente a qualidade JPG (ex: 90 ou 95)

**Problema**: Arquivo muito grande
- **Solução**: Reduza a qualidade JPG (ex: 75 ou 80)


