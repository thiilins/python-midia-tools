# Merge de Vídeos

## Descrição

Ferramenta para concatenar (juntar) múltiplos vídeos em um único arquivo. Útil para unir gravações, criar compilações ou combinar vídeos curtos.

## Funcionalidades

- ✅ **Concatenação rápida**: Usa copy mode (sem re-encodar)
- ✅ **Múltiplos vídeos**: Concatena quantos vídeos necessário
- ✅ **Ordenação automática**: Ordena arquivos por nome
- ✅ **Processamento eficiente**: Copia streams sem re-encodar
- ✅ **Preservação de qualidade**: Mantém qualidade original

## Requisitos

- Python 3.6+
- FFmpeg
- FFprobe

## Uso

### Via Menu Interativo

Execute o script `start.bat` (Windows) ou `start.sh` (Linux/macOS) e selecione a opção **Merge Vídeos**.

### Via Linha de Comando

```bash
python merge-videos.py
```

## Configuração

O script está configurado com os seguintes parâmetros padrão:

- **Nome de saída**: `video_merged.mp4`

### Personalização

Para personalizar os parâmetros, edite o arquivo `merge-videos.py`:

```python
merger = MergerVideos(
    nome_saida="meu_video_unido.mp4"  # Nome do arquivo de saída
)
```

## Formatos Suportados

- MP4
- M4V
- MOV
- WebM

## Pastas

- **Entrada**: `entrada/videos/`
- **Saída**: `saida/videos/`

## Como Funciona

1. Lista todos os vídeos na pasta de entrada
2. Ordena por nome (alfabeticamente)
3. Cria arquivo de lista temporário para FFmpeg
4. Concatena usando modo copy (sem re-encodar)
5. Remove arquivo temporário
6. Salva vídeo concatenado

## Requisitos para Concatenação

⚠️ **Importante**: Para concatenação eficiente, os vídeos devem ter:
- Mesmo codec de vídeo
- Mesma resolução (recomendado)
- Mesmo frame rate (recomendado)
- Mesmo codec de áudio (recomendado)

Se os vídeos forem diferentes, o FFmpeg pode falhar ou o resultado pode ter problemas.

## Exemplos

### Concatenar vídeos (padrão)

```bash
python merge-videos.py
```

### Personalizar nome de saída (editar código)

```python
merger = MergerVideos(nome_saida="compilacao_final.mp4")
merger.processar()
```

## Notas

- ⚠️ Requer pelo menos 2 vídeos para concatenar
- Os vídeos são ordenados alfabeticamente antes de concatenar
- Usa modo copy (sem re-encodar) para velocidade
- Timeout de 2 horas para vídeos muito longos
- Arquivo temporário (`concat_list.txt`) é criado e removido automaticamente

## Troubleshooting

**Problema**: Erro "É necessário pelo menos 2 vídeos"
- **Solução**: Adicione pelo menos 2 vídeos na pasta de entrada

**Problema**: Erro ao concatenar (codecs diferentes)
- **Solução**: Os vídeos precisam ter codecs compatíveis. Re-encode os vídeos primeiro usando `otimizador-video.py`

**Problema**: Vídeo concatenado com problemas de sincronia
- **Solução**: Verifique se os vídeos têm mesmo frame rate e codec

**Problema**: Timeout
- **Solução**: Normal para muitos vídeos muito longos. O timeout é de 2 horas

**Problema**: Vídeo final com resolução diferente
- **Solução**: Normal se os vídeos originais têm resoluções diferentes. FFmpeg usa a resolução do primeiro vídeo

