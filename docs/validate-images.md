# Validador de Imagens

## Descrição

Ferramenta para validar se imagens são legíveis, separando automaticamente em pastas "legíveis" e "ilegíveis". Analisa escuridão, uniformidade, foco e bordas.

## Funcionalidades

- ✅ **Análise completa**: Avalia escuridão, uniformidade, foco e bordas
- ✅ **Separação automática**: Move imagens para pastas "legíveis" e "ilegíveis"
- ✅ **Relatório HTML**: Gera relatório visual com previews e análise detalhada
- ✅ **Processamento em lote**: Processa múltiplas imagens de uma vez
- ✅ **Barra de progresso**: Acompanhamento em tempo real

## Requisitos

- Python 3.6+
- OpenCV (cv2)
- NumPy

## Uso

### Via Menu Interativo

Execute o script `start.bat` (Windows) ou `start.sh` (Linux/macOS) e selecione a opção **Validar Imagens**.

### Via Linha de Comando

#### Modo padrão (sem relatório HTML)

```bash
python validate-images.py
```

#### Com relatório HTML

```bash
python validate-images.py --html
# ou
python validate-images.py -h
```

#### Via Variável de Ambiente

```bash
# Linux/macOS
export GERAR_RELATORIO_HTML=true
python validate-images.py

# Windows
set GERAR_RELATORIO_HTML=true
python validate-images.py
```

## Configuração

O script analisa imagens usando os seguintes critérios:

- **Escuridão**: Detecta imagens muito escuras
- **Uniformidade**: Detecta imagens muito uniformes (sem detalhes)
- **Foco**: Detecta imagens desfocadas
- **Bordas**: Detecta problemas nas bordas

## Formatos Suportados

- JPG/JPEG
- PNG
- WebP
- BMP
- TIFF

## Pastas

- **Entrada**: `entrada/imagens/`
- **Saída legíveis**: `saida/legiveis/`
- **Saída ilegíveis**: `saida/ilegiveis/`

## Relatório HTML

Quando ativado, gera um arquivo HTML com:
- Preview de cada imagem
- Análise detalhada (escuridão, uniformidade, foco, bordas)
- Classificação (legível/ilegível)
- Estatísticas gerais

O relatório é salvo em: `saida/relatorio_validacao.html`

## Exemplos

### Validar imagens (padrão)

```bash
python validate-images.py
```

### Validar com relatório HTML

```bash
python validate-images.py --html
```

## Notas

- Imagens são **movidas** (não copiadas) para pastas de saída
- O relatório HTML pode ser aberto em qualquer navegador
- A análise é baseada em algoritmos de visão computacional
- Imagens muito escuras, desfocadas ou uniformes são classificadas como ilegíveis

## Troubleshooting

**Problema**: Erro "OpenCV não encontrado"
- **Solução**: Instale OpenCV: `pip install opencv-python`

**Problema**: Imagens legíveis classificadas como ilegíveis
- **Solução**: Normal - os critérios são conservadores. Ajuste os thresholds no código se necessário

**Problema**: Relatório HTML não gerado
- **Solução**: Use a flag `--html` ou configure a variável de ambiente

**Problema**: Erro ao mover arquivo
- **Solução**: Verifique permissões de escrita nas pastas de saída

**Problema**: Análise muito lenta
- **Solução**: Normal para muitas imagens grandes. O processo analisa cada imagem em detalhe

