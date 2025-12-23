# Conversor WebM → MP4

## Descrição

Ferramenta para converter vídeos WebM para MP4 corrigindo problemas comuns como timestamps, frame rate variável (VFR) e garantindo compatibilidade universal.

## Funcionalidades

- ✅ **Conversão otimizada**: Converte WebM para MP4 com correções automáticas
- ✅ **Detecção de problemas**: Identifica VFR, timestamps e problemas de sincronia
- ✅ **Correção automática**: Aplica correções baseadas em problemas detectados
- ✅ **Perfis pré-configurados**: Web, mobile e archive
- ✅ **Processamento em lote**: Processa múltiplos vídeos de uma vez
- ✅ **Barra de progresso**: Acompanhamento em tempo real
- ✅ **Informações detalhadas**: Mostra codec, bitrate, resolução antes/depois

## Requisitos

- Python 3.6+
- FFmpeg
- FFprobe

## Uso

### Via Menu Interativo

Execute o script `start.bat` (Windows) ou `start.sh` (Linux/macOS) e selecione a opção **Converter WebM → MP4**.

### Via Linha de Comando

#### Modo padrão

```bash
python webm-mp4.py
```

#### Com perfil específico

```bash
python webm-mp4.py --web      # Otimizado para web
python webm-mp4.py --mobile    # Otimizado para mobile
python webm-mp4.py --archive    # Alta qualidade para arquivo
```

#### Via Variável de Ambiente

```bash
# Linux/macOS
export PERFIL_WEBM=web
python webm-mp4.py

# Windows
set PERFIL_WEBM=mobile
python webm-mp4.py
```

## Configuração

O script está configurado com os seguintes parâmetros padrão:

- **Manter originais**: Sim
- **Corrigir velocidade**: Não
- **FPS saída**: 30
- **Qualidade CRF**: 20
- **Perfil**: None (detecta automaticamente)
- **Detectar problemas**: Sim

### Personalização

Para personalizar os parâmetros, edite o arquivo `webm-mp4.py`:

```python
conversor = ConversorWebM(
    manter_originais=True,      # True/False
    corrigir_velocidade=False,  # True/False
    fator_velocidade=2.0,       # Multiplicador de velocidade
    fps_saida=30,               # FPS de saída
    qualidade_crf="20",         # 18-28 (menor = melhor qualidade)
    perfil=None,                # None, "web", "mobile", "archive"
    detectar_problemas=True     # True/False
)
```

## Formatos Suportados

- **Entrada**: WebM
- **Saída**: MP4 (H.264)

## Pastas

- **Entrada**: `entrada/videos/`
- **Saída**: `saida/videos/`

## Perfis Pré-configurados

### Web
- Otimizado para streaming web
- Compressão balanceada
- Compatibilidade máxima

### Mobile
- Otimizado para dispositivos móveis
- Menor bitrate
- Melhor compressão

### Archive
- Alta qualidade
- Preservação máxima
- Arquivos maiores

## Problemas Detectados e Corrigidos

- **VFR (Variable Frame Rate)**: Converte para CFR (Constant Frame Rate)
- **Timestamps**: Corrige timestamps inconsistentes
- **Sincronia áudio/vídeo**: Ajusta sincronia
- **Codec incompatível**: Converte para H.264

## Exemplos

### Converter WebM (padrão)

```bash
python webm-mp4.py
```

### Converter com perfil web

```bash
python webm-mp4.py --web
```

### Personalizar (editar código)

```python
# Alta qualidade, corrigir velocidade
conversor = ConversorWebM(
    qualidade_crf="18",
    corrigir_velocidade=True,
    fator_velocidade=1.5
)
```

## Notas

- Arquivos originais são mantidos por padrão
- A detecção de problemas melhora a qualidade da conversão
- O processo pode ser demorado para vídeos longos
- Vídeos com VFR são convertidos para CFR (30fps padrão)

## Troubleshooting

**Problema**: Erro "FFmpeg não encontrado"
- **Solução**: Instale FFmpeg e verifique se está no PATH

**Problema**: Vídeo com problemas de sincronia
- **Solução**: Ative `detectar_problemas=True` e `corrigir_velocidade=True`

**Problema**: Conversão muito lenta
- **Solução**: Normal para vídeos longos. Use perfil "web" para velocidade

**Problema**: Qualidade baixa
- **Solução**: Reduza o CRF (ex: "18") e use perfil "archive"

**Problema**: Arquivo muito grande
- **Solução**: Aumente o CRF (ex: "23" ou "26") e use perfil "mobile"


