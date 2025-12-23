# Detector de Duplicatas de Imagens

## Descrição

Ferramenta para encontrar imagens duplicadas usando hash MD5. Identifica arquivos idênticos e permite remoção automática ou manual.

## Funcionalidades

- ✅ **Detecção por hash MD5**: Identifica arquivos idênticos
- ✅ **Remoção automática**: Opção para remover duplicatas automaticamente
- ✅ **Processamento em lote**: Analisa múltiplas imagens de uma vez
- ✅ **Barra de progresso**: Acompanhamento em tempo real
- ✅ **Relatório detalhado**: Mostra quais arquivos são duplicatas

## Requisitos

- Python 3.6+

## Uso

### Via Menu Interativo

Execute o script `start.bat` (Windows) ou `start.sh` (Linux/macOS) e selecione a opção **Detectar Duplicatas de Imagens**.

### Via Linha de Comando

#### Modo de Detecção (apenas relatório)

```bash
python detector-duplicatas-imagens.py
```

#### Modo de Remoção Automática

```bash
python detector-duplicatas-imagens.py --remover
# ou
python detector-duplicatas-imagens.py -r
```

#### Via Variável de Ambiente

```bash
# Linux/macOS
export REMOVER_DUPLICATAS=true
python detector-duplicatas-imagens.py

# Windows
set REMOVER_DUPLICATAS=true
python detector-duplicatas-imagens.py
```

## Como Funciona

1. Calcula hash MD5 de cada arquivo
2. Agrupa arquivos com o mesmo hash
3. Identifica duplicatas (grupos com mais de 1 arquivo)
4. Mantém o primeiro arquivo encontrado
5. Remove os demais (se `--remover` for usado)

## Formatos Suportados

- JPG/JPEG
- PNG
- WebP
- BMP
- GIF

## Pastas

- **Análise**: `entrada/imagens/`

## Exemplos

### Detectar duplicatas sem remover

```bash
python detector-duplicatas-imagens.py
```

### Detectar e remover automaticamente

```bash
python detector-duplicatas-imagens.py --remover
```

## Notas

- ⚠️ **Atenção**: A remoção é **permanente**. Use com cuidado!
- O primeiro arquivo encontrado é sempre mantido
- Arquivos com hash idêntico são considerados duplicatas exatas
- Requer pelo menos 2 imagens para detectar duplicatas
- O hash MD5 compara o arquivo completo, não apenas o conteúdo visual

## Troubleshooting

**Problema**: Nenhuma duplicata encontrada
- **Solução**: Verifique se há pelo menos 2 imagens na pasta

**Problema**: Arquivos visualmente iguais não são detectados
- **Solução**: O detector usa hash MD5 (arquivo idêntico). Imagens similares mas com metadados diferentes não são detectadas. Use ferramenta de comparação visual para isso.

**Problema**: Erro ao remover arquivo
- **Solução**: Verifique permissões de escrita na pasta


