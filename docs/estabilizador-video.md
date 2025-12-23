# Estabilizador de Vídeo

## Descrição

Ferramenta para estabilizar vídeos tremidos e corrigir rotação automática. Utiliza algoritmos avançados de análise de movimento para suavizar tremidas e vibrações.

## Funcionalidades

- ✅ **Estabilização de movimento**: Reduz tremidas e vibrações
- ✅ **Correção de rotação**: Corrige rotação automática de vídeos
- ✅ **Análise de movimento**: Detecta padrões de movimento antes de estabilizar
- ✅ **Processamento em lote**: Processa múltiplos vídeos de uma vez
- ✅ **Preservação de áudio**: Mantém áudio original sem re-encodar

## Requisitos

- Python 3.6+
- FFmpeg (com suporte a libvidstab recomendado)
- FFprobe

## Uso

### Via Menu Interativo

Execute o script `start.bat` (Windows) ou `start.sh` (Linux/macOS) e selecione a opção **Estabilizador de Vídeo**.

### Via Linha de Comando

```bash
python estabilizador-video.py
```

## Configuração

O script está configurado com os seguintes parâmetros padrão:

- **Correção de rotação**: Ativada

### Personalização

Para personalizar os parâmetros, edite o arquivo `estabilizador-video.py`:

```python
estabilizador = EstabilizadorVideo(
    correcao_rotacao=True  # True/False
)
```

## Formatos Suportados

- MP4
- M4V
- MOV
- WebM
- AVI

## Pastas

- **Entrada**: `entrada/videos/`
- **Saída**: `saida/videos/`

## Processo de Estabilização

O processo ocorre em duas etapas:

1. **Análise**: Detecta padrões de movimento e gera arquivo de transformação
2. **Aplicação**: Aplica estabilização baseada na análise

## Exemplos

### Estabilizar sem correção de rotação

```python
estabilizador = EstabilizadorVideo(correcao_rotacao=False)
estabilizador.processar()
```

## Notas

- ⚠️ **Importante**: A estabilização requer FFmpeg compilado com `libvidstab`
- Se `vidstab` não estiver disponível, o script usa estabilização básica
- O processo pode ser demorado para vídeos longos
- Arquivos temporários (`.trf`) são criados e removidos automaticamente
- O áudio é copiado sem re-encodar para manter qualidade

## Troubleshooting

**Problema**: Aviso "vidstab não está disponível"
- **Solução**: Instale FFmpeg com suporte a libvidstab:
  - **Linux**: `sudo apt-get install ffmpeg libvidstab-dev`
  - **macOS**: `brew install ffmpeg --with-libvidstab`
  - **Windows**: Baixe build com libvidstab de https://www.gyan.dev/ffmpeg/builds/

**Problema**: Estabilização muito lenta
- **Solução**: Normal para vídeos longos. O processo analisa cada frame

**Problema**: Vídeo fica com bordas pretas
- **Solução**: Normal - a estabilização pode cortar bordas. Ajuste o parâmetro `smoothing` no código se necessário

**Problema**: Erro ao processar
- **Solução**: Verifique se o FFmpeg está instalado e no PATH


