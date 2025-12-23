# Removedor de Fundo

## Descrição

Ferramenta para remover fundo de imagens automaticamente usando IA (Inteligência Artificial). Utiliza a biblioteca `rembg` para detecção e remoção de fundo, gerando imagens PNG com transparência.

## Funcionalidades

- ✅ **Remoção automática**: Remove fundo usando IA
- ✅ **Transparência**: Gera imagens PNG com fundo transparente
- ✅ **Processamento em lote**: Processa múltiplas imagens de uma vez
- ✅ **Barra de progresso**: Acompanhamento em tempo real
- ✅ **Alta qualidade**: Usa modelo de IA treinado

## Requisitos

- Python 3.6+
- rembg
- Pillow (PIL)

## Instalação

O `rembg` será instalado automaticamente via `requirements.txt`. Na primeira execução, o modelo de IA será baixado automaticamente (~170MB).

## Uso

### Via Menu Interativo

Execute o script `start.bat` (Windows) ou `start.sh` (Linux/macOS) e selecione a opção **Remover Fundo**.

### Via Linha de Comando

```bash
python remover-fundo.py
```

## Configuração

O script não requer configuração adicional. Usa o modelo padrão do `rembg`.

## Formatos Suportados

### Entrada
- JPG/JPEG
- PNG
- WebP
- BMP

### Saída
- PNG (com transparência)

## Pastas

- **Entrada**: `entrada/imagens/`
- **Saída**: `saida/sem_fundo/`

## Como Funciona

1. Carrega modelo de IA (baixa na primeira execução)
2. Processa cada imagem
3. Remove fundo usando detecção de objetos
4. Salva como PNG com transparência

## Exemplos

### Remover fundo de imagens

```bash
python remover-fundo.py
```

## Notas

- ⚠️ **Primeira execução**: O modelo de IA será baixado automaticamente (~170MB) na primeira execução
- Todas as imagens são salvas como PNG com transparência
- Nomes dos arquivos: `{nome_original}.png`
- O processo pode ser demorado dependendo do tamanho das imagens
- Funciona melhor com objetos bem definidos e fundos contrastantes

## Troubleshooting

**Problema**: Erro "rembg não está instalado"
- **Solução**: Instale rembg: `pip install rembg`

**Problema**: Primeira execução muito lenta
- **Solução**: Normal - o modelo de IA está sendo baixado (~170MB)

**Problema**: Fundo não removido completamente
- **Solução**:
  - A IA funciona melhor com objetos bem definidos
  - Fundos muito similares ao objeto podem ter problemas
  - Tente ajustar contraste da imagem original primeiro

**Problema**: Erro ao processar imagem
- **Solução**: Verifique se a imagem não está corrompida e se tem formato suportado

**Problema**: Processamento muito lento
- **Solução**: Normal para imagens grandes. O processo de IA é computacionalmente intensivo

**Problema**: Arquivo PNG muito grande
- **Solução**: Use `otimizador-imagens.py` para comprimir os PNGs gerados

