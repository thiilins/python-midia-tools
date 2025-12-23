# Extrator de Áudio

## Descrição

Ferramenta para extrair áudio de vídeos em diversos formatos (MP3, AAC, OGG, WAV). Útil para criar podcasts, trilhas sonoras ou arquivos de áudio a partir de vídeos.

## Funcionalidades

- ✅ **Múltiplos formatos**: MP3, AAC, OGG, WAV
- ✅ **Controle de qualidade**: Ajuste de bitrate
- ✅ **Processamento em lote**: Processa múltiplos vídeos de uma vez
- ✅ **Barra de progresso**: Acompanhamento em tempo real
- ✅ **Preservação de qualidade**: Sample rate 44.1kHz

## Requisitos

- Python 3.6+
- FFmpeg
- FFprobe

## Uso

### Via Menu Interativo

Execute o script `start.bat` (Windows) ou `start.sh` (Linux/macOS) e selecione a opção **Extrair Áudio**.

### Via Linha de Comando

```bash
python extrair-audio.py
```

## Configuração

O script está configurado com os seguintes parâmetros padrão:

- **Formato**: MP3
- **Qualidade**: 192k (bitrate)
- **Sample rate**: 44.1kHz

### Personalização

Para personalizar os parâmetros, edite o arquivo `extrair-audio.py`:

```python
extrator = ExtratorAudio(
    formato="mp3",      # "mp3", "aac", "ogg", "wav"
    qualidade="192k"    # Bitrate (ex: "128k", "192k", "256k", "320k")
)
```

## Formatos Suportados

### Entrada (Vídeos)
- MP4
- M4V
- MOV
- WebM
- AVI
- MKV

### Saída (Áudio)
- **MP3**: Compatível universalmente
- **AAC**: Melhor compressão, qualidade similar
- **OGG**: Open source, boa qualidade
- **WAV**: Sem compressão, alta qualidade (arquivos grandes)

## Pastas

- **Entrada**: `entrada/videos/`
- **Saída**: `saida/audio/`

## Qualidade Recomendada

| Uso | Formato | Bitrate |
|-----|---------|---------|
| Podcast | MP3 | 128k |
| Música | MP3 | 192k-256k |
| Alta qualidade | MP3 | 320k |
| Streaming | AAC | 128k-192k |
| Edição | WAV | N/A (sem compressão) |

## Exemplos

### Extrair como MP3 192k (padrão)

```bash
python extrair-audio.py
```

### Personalizar formato e qualidade (editar código)

```python
# MP3 alta qualidade
extrator = ExtratorAudio(formato="mp3", qualidade="320k")

# AAC para streaming
extrator = ExtratorAudio(formato="aac", qualidade="192k")

# WAV sem compressão
extrator = ExtratorAudio(formato="wav", qualidade="N/A")
```

## Notas

- O áudio é extraído sem re-encodar o vídeo (processo rápido)
- Sample rate fixo em 44.1kHz (qualidade CD)
- Timeout de 1 hora por vídeo (para vídeos muito longos)
- Nomes dos arquivos: `{nome_video}.{formato}`

## Troubleshooting

**Problema**: Erro "FFmpeg não encontrado"
- **Solução**: Instale FFmpeg e verifique se está no PATH

**Problema**: Áudio sem som
- **Solução**: Verifique se o vídeo tem faixa de áudio

**Problema**: Qualidade baixa
- **Solução**: Aumente o bitrate (ex: "256k" ou "320k")

**Problema**: Arquivo muito grande (WAV)
- **Solução**: Use MP3 ou AAC para compressão

**Problema**: Timeout em vídeos longos
- **Solução**: Normal para vídeos muito longos. O timeout é de 1 hora por vídeo

