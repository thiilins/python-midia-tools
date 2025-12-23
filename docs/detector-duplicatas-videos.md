# Detector de Duplicatas de Vídeos

## Descrição

Ferramenta para encontrar vídeos duplicados usando hash MD5 de amostras. Identifica arquivos idênticos e permite remoção automática ou manual.

## Funcionalidades

- ✅ **Detecção por hash MD5**: Identifica arquivos idênticos usando amostras
- ✅ **Otimizado para vídeos grandes**: Usa amostra (primeiros e últimos 10MB)
- ✅ **Remoção automática**: Opção para remover duplicatas automaticamente
- ✅ **Processamento em lote**: Analisa múltiplos vídeos de uma vez
- ✅ **Barra de progresso**: Acompanhamento em tempo real
- ✅ **Relatório detalhado**: Mostra tamanho e quais arquivos são duplicatas

## Requisitos

- Python 3.6+

## Uso

### Via Menu Interativo

Execute o script `start.bat` (Windows) ou `start.sh` (Linux/macOS) e selecione a opção **Detectar Duplicatas de Vídeos**.

### Via Linha de Comando

#### Modo de Detecção (apenas relatório)

```bash
python detector-duplicatas-videos.py
```

#### Modo de Remoção Automática

```bash
python detector-duplicatas-videos.py --remover
# ou
python detector-duplicatas-videos.py -r
```

#### Via Variável de Ambiente

```bash
# Linux/macOS
export REMOVER_DUPLICATAS=true
python detector-duplicatas-videos.py

# Windows
set REMOVER_DUPLICATAS=true
python detector-duplicatas-videos.py
```

## Como Funciona

1. Calcula hash MD5 usando amostra do arquivo:
   - Primeiros 10MB
   - Últimos 10MB (se arquivo > 20MB)
2. Agrupa arquivos com o mesmo hash
3. Identifica duplicatas (grupos com mais de 1 arquivo)
4. Mantém o primeiro arquivo encontrado
5. Remove os demais (se `--remover` for usado)

## Formatos Suportados

- MP4
- M4V
- MOV
- WebM
- AVI
- MKV

## Pastas

- **Análise**: `entrada/videos/`

## Exemplos

### Detectar duplicatas sem remover

```bash
python detector-duplicatas-videos.py
```

### Detectar e remover automaticamente

```bash
python detector-duplicatas-videos.py --remover
```

## Notas

- ⚠️ **Atenção**: A remoção é **permanente**. Use com cuidado!
- O primeiro arquivo encontrado é sempre mantido
- Usa amostra para velocidade (primeiros e últimos 10MB)
- Arquivos com hash idêntico são considerados duplicatas exatas
- Requer pelo menos 2 vídeos para detectar duplicatas
- A amostra é suficiente para detectar arquivos idênticos, mas pode não detectar vídeos similares com diferenças no meio

## Troubleshooting

**Problema**: Nenhuma duplicata encontrada
- **Solução**: Verifique se há pelo menos 2 vídeos na pasta

**Problema**: Vídeos visualmente iguais não são detectados
- **Solução**: O detector usa hash MD5 de amostras (arquivo idêntico). Vídeos similares mas com metadados diferentes não são detectados.

**Problema**: Erro ao remover arquivo
- **Solução**: Verifique permissões de escrita na pasta

**Problema**: Processamento lento
- **Solução**: Normal para muitos vídeos grandes. O processo usa amostras para otimizar velocidade.


