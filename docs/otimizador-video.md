# Otimizador de Vídeos

## Descrição

Ferramenta para otimizar vídeos MP4, M4V e MOV reduzindo tamanho mantendo qualidade visual. Utiliza codec H.264 com CRF (Constant Rate Factor) para compressão eficiente.

## Funcionalidades

- ✅ **Otimização inteligente**: Reduz tamanho mantendo qualidade
- ✅ **Codec H.264**: Compatibilidade universal
- ✅ **Detecção de otimização**: Pula vídeos já otimizados (ou corrige se tiverem problemas)
- ✅ **Correção automática de problemas**: Detecta e corrige VFR, timestamps, dessincronia de áudio
- ✅ **Correção inteligente**: Corrige problemas mesmo em vídeos já otimizados
- ✅ **Presets pré-configurados**: 5 presets para diferentes necessidades
- ✅ **Informações detalhadas**: Mostra codec, bitrate, resolução antes/depois
- ✅ **Barra de progresso**: Acompanhamento em tempo real
- ✅ **Controle de recursos**: Limita uso de CPU, memória e threads para evitar sobrecarga
- ✅ **Proteção do sistema**: Pausa entre processamentos e monitoramento de recursos

## Requisitos

- Python 3.6+
- FFmpeg
- FFprobe
- psutil (para controle de recursos)

## Uso

### Via Menu Interativo

Execute o script `start.bat` (Windows) ou `start.sh` (Linux/macOS) e selecione a opção **Otimizar Vídeos**.

### Via Linha de Comando

```bash
python otimizador-video.py
```

#### Desabilitar Correções Automáticas

```bash
# Via argumento
python otimizador-video.py --sem-correcoes

# Via variável de ambiente
export CORRIGIR_PROBLEMAS=false
python otimizador-video.py
```

## Configuração

O script está configurado com os seguintes parâmetros padrão:

- **Preset**: medium (qualidade boa, compressão média, velocidade balanceada)
- **Deletar originais**: Sim (após otimização bem-sucedida)

### Usando Presets Pré-configurados

O otimizador oferece 5 presets pré-configurados para diferentes necessidades:

#### Listar Presets Disponíveis

```bash
python otimizador-video.py --presets
# ou
python otimizador-video.py -p
```

#### Usar um Preset Específico

```bash
# Via argumento
python otimizador-video.py --preset ultra_fast
python otimizador-video.py --preset fast
python otimizador-video.py --preset medium      # Padrão
python otimizador-video.py --preset high_quality
python otimizador-video.py --preset maximum

# Via variável de ambiente
export PRESET_VIDEO=high_quality
python otimizador-video.py
```

### Presets Disponíveis

| Preset           | CRF | Preset FFmpeg | Descrição                                         |
| ---------------- | --- | ------------- | ------------------------------------------------- |
| **ultra_fast**   | 28  | ultrafast     | Muito rápido, menor qualidade (compressão máxima) |
| **fast**         | 26  | fast          | Rápido, qualidade média-baixa                     |
| **medium**       | 23  | medium        | Balanceado, qualidade boa (padrão)                |
| **high_quality** | 20  | slow          | Alta qualidade, mais lento                        |
| **maximum**      | 18  | veryslow      | Máxima qualidade, muito lento                     |

### Personalização Avançada

Para personalização manual (sem usar presets), edite o arquivo `otimizador-video.py`:

```python
# Usando parâmetros individuais
otimizador = OtimizadorVideo(
    crf="23",           # 18-28 (menor = melhor qualidade, maior arquivo)
    preset="medium"     # ultrafast, fast, medium, slow, veryslow
)

# Ou usando preset pré-configurado
otimizador = OtimizadorVideo(
    preset_nome="high_quality"  # ultra_fast, fast, medium, high_quality, maximum
)

otimizador.processar(deletar_originais=True)  # True/False
```

## Formatos Suportados

- MP4
- M4V
- MOV

## Pastas

- **Entrada**: `entrada/videos/`
- **Saída**: `saida/videos/`

## Parâmetros CRF

| CRF | Qualidade | Uso                           |
| --- | --------- | ----------------------------- |
| 18  | Excelente | Arquivo final, alta qualidade |
| 23  | Boa       | Uso geral (padrão)            |
| 28  | Aceitável | Compressão máxima             |

## Presets FFmpeg

| Preset    | Velocidade   | Compressão   |
| --------- | ------------ | ------------ |
| ultrafast | Muito rápido | Baixa        |
| fast      | Rápido       | Média        |
| medium    | Média        | Boa (padrão) |
| slow      | Lento        | Muito boa    |
| veryslow  | Muito lento  | Máxima       |

## Como Funciona

1. Analisa cada vídeo (codec, bitrate, resolução)
2. Verifica se já está otimizado (codec H.264 + bitrate < 5 Mbps)
3. Se já otimizado:
   - **Sem problemas**: Pula o vídeo
   - **Com problemas**: Aplica correções (sem re-otimizar quando possível)
4. Se não otimizado:
   - Detecta problemas (VFR, timestamps, dessincronia de áudio) se habilitado
   - Otimiza usando H.264 com CRF
   - Aplica correções automáticas se problemas foram detectados
5. Mostra informações antes/depois
6. Deleta original se solicitado

### Detecção de Otimização

Um vídeo é considerado "já otimizado" quando:

- Codec é **H.264** (`h264`)
- Bitrate total < **5 Mbps** (indica compressão)

### Correção de Vídeos Otimizados

Vídeos já otimizados que têm problemas são corrigidos automaticamente:

- **VFR**: Re-encoda com filtro `fps` (necessário)
- **Timestamps/Áudio**: Usa `copy` mode (sem re-encodar, mais rápido)

## Correção Automática de Problemas

O otimizador detecta e corrige automaticamente os seguintes problemas:

- **VFR (Variable Frame Rate)**: Converte para FPS constante
- **Timestamps**: Corrige problemas com timestamps usando `genpts` e `igndts`
- **Dessincronia de áudio**: Ajusta sincronia com `aresample=async=1`

A correção é **habilitada por padrão**. Para desabilitar:

```bash
# Via linha de comando
python otimizador-video.py --sem-correcoes

# Via variável de ambiente
export CORRIGIR_PROBLEMAS=false
python otimizador-video.py

# Ou editando o código
otimizador = OtimizadorVideo(corrigir_problemas=False)
```

## Exemplos

### Otimizar vídeos (padrão - preset medium)

```bash
python otimizador-video.py
```

### Usar preset específico

```bash
# Compressão máxima (muito rápido)
python otimizador-video.py --preset ultra_fast

# Alta qualidade (mais lento)
python otimizador-video.py --preset high_quality

# Máxima qualidade (muito lento)
python otimizador-video.py --preset maximum
```

### Desabilitar correções automáticas

```bash
# Apenas otimizar, sem corrigir problemas
python otimizador-video.py --sem-correcoes

# Combinar com preset
python otimizador-video.py --preset fast --sem-correcoes
```

### Personalizar qualidade (editar código)

```python
# Usando preset
otimizador = OtimizadorVideo(preset_nome="high_quality")

# Ou parâmetros individuais
otimizador = OtimizadorVideo(crf="18", preset="slow")
```

## Controle de Recursos

O otimizador agora inclui controle automático de recursos para evitar sobrecarga do sistema (CPU, memória e GPU). Isso é especialmente importante para sistemas com GPU fraca ou quando processando muitos vídeos.

### Configuração Padrão

- **Threads**: 50% dos cores disponíveis (máximo 8 threads)
- **Limite CPU**: 85% (aguarda se exceder)
- **Limite Memória**: 85% (aguarda se exceder)
- **GPU**: Desabilitada por padrão (usa apenas CPU)
- **Pausa entre vídeos**: 1 segundo

### Variáveis de Ambiente

Você pode personalizar o controle de recursos usando variáveis de ambiente:

```bash
# Limitar threads do FFmpeg (padrão: 50% dos cores, máx 8)
export FFMPEG_THREADS=4

# Limite de uso de CPU em % (padrão: 85%)
export LIMITE_CPU=80

# Limite de uso de memória em % (padrão: 85%)
export LIMITE_MEMORIA=80

# Pausa entre vídeos em segundos (padrão: 1.0)
export PAUSA_ENTRE_VIDEOS=2.0

# Usar GPU (padrão: false - desabilitado)
# ⚠️ ATENÇÃO: Para GPUs fracas (ex: RX 580), mantenha false
export USAR_GPU=false

# Executar com as configurações
python otimizador-video.py
```

### Recomendações

- **GPU fraca (ex: RX 580)**: Mantenha `USAR_GPU=false` (padrão)
- **CPU potente (ex: Ryzen 9)**: Pode aumentar `FFMPEG_THREADS` se necessário
- **Sistema com pouca RAM**: Reduza `LIMITE_MEMORIA` (ex: 70%)
- **Processamento em background**: Aumente `PAUSA_ENTRE_VIDEOS` (ex: 2.0 ou 3.0)

### Funcionamento do Controle de Recursos

1. **Antes de cada vídeo**: Verifica uso de CPU e memória
2. **Se recursos excederem limites**: Aguarda até ficarem disponíveis (timeout: 120s)
3. **Durante processamento**: Usa número limitado de threads
4. **Entre vídeos**: Pausa para dar tempo ao sistema se recuperar
5. **Prioridade do processo**: Reduzida (nice=5) para menor impacto no sistema

## Notas

- ⚠️ **Atenção**: Com `deletar_originais=True`, os arquivos originais são **permanentemente deletados** após otimização
- Vídeos já otimizados **sem problemas** são automaticamente pulados
- Vídeos já otimizados **com problemas** são corrigidos (sem re-otimizar quando possível)
- Correções automáticas são habilitadas por padrão
- O script mostra informações detalhadas de cada vídeo
- **Controle de recursos**: O otimizador agora protege automaticamente o sistema contra sobrecarga

## Troubleshooting

**Problema**: Erro "FFmpeg não encontrado"

- **Solução**: Instale FFmpeg e verifique se está no PATH

**Problema**: Vídeo não otimizado (já otimizado)

- **Solução**: Normal - vídeos já otimizados sem problemas são pulados. Se tiver problemas, será corrigido automaticamente

**Problema**: Processamento muito lento

- **Solução**: Use preset mais rápido (ex: "fast" ou "ultrafast")

**Problema**: Qualidade baixa

- **Solução**: Reduza o CRF (ex: "20" ou "18") e use preset "slow"

**Problema**: Arquivo muito grande

- **Solução**: Aumente o CRF (ex: "26" ou "28") para maior compressão

**Problema**: Sistema desliga ou trava durante processamento

- **Solução**: O otimizador agora controla recursos automaticamente. Se ainda ocorrer:
  - Reduza `FFMPEG_THREADS` (ex: `export FFMPEG_THREADS=2`)
  - Reduza `LIMITE_CPU` (ex: `export LIMITE_CPU=70`)
  - Aumente `PAUSA_ENTRE_VIDEOS` (ex: `export PAUSA_ENTRE_VIDEOS=3.0`)
  - Mantenha `USAR_GPU=false` (padrão) para GPUs fracas
