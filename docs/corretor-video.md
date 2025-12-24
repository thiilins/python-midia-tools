# Corretor de Vídeos

## Descrição

Ferramenta especializada para corrigir problemas comuns em vídeos MP4, M4V e MOV. Foca exclusivamente em correções de qualidade técnica, sem otimização de tamanho. Utiliza FFmpeg para detectar e corrigir problemas de framerate, timestamps e sincronização de áudio.

## Funcionalidades

- ✅ **Correção de VFR (Variable Frame Rate)**: Converte framerate variável para constante
- ✅ **Correção de Timestamps**: Corrige problemas com timestamps usando `genpts` e `igndts`
- ✅ **Correção de Dessincronia de Áudio**: Ajusta sincronia com `aresample=async=1`
- ✅ **Detecção Inteligente**: Detecta problemas antes de processar
- ✅ **Processamento em Lote**: Processa múltiplos vídeos de uma vez
- ✅ **Barra de Progresso**: Acompanhamento em tempo real
- ✅ **Controle de Recursos**: Limita uso de CPU, memória e threads para evitar sobrecarga
- ✅ **Proteção do Sistema**: Pausa entre processamentos e monitoramento de recursos
- ✅ **Seletividade**: Permite habilitar/desabilitar cada tipo de correção individualmente

## Requisitos

- Python 3.6+
- FFmpeg
- FFprobe
- psutil (para controle de recursos)

## Uso

### Via Linha de Comando

```bash
# Corrige todos os problemas detectados
python corretor-video.py

# Ver ajuda
python corretor-video.py --help
```

#### Desabilitar Correções Específicas

```bash
# Apenas correção de VFR (sem timestamps e áudio)
python corretor-video.py --sem-timestamps --sem-audio

# Apenas correção de timestamps e áudio (sem VFR)
python corretor-video.py --sem-vfr

# Apenas correção de áudio
python corretor-video.py --sem-vfr --sem-timestamps
```

#### Via Variáveis de Ambiente

```bash
# Desabilitar correção de VFR
export CORRIGIR_VFR=false
python corretor-video.py

# Desabilitar correção de timestamps
export CORRIGIR_TIMESTAMPS=false
python corretor-video.py

# Desabilitar correção de áudio
export CORRIGIR_AUDIO=false
python corretor-video.py

# Combinar múltiplas configurações
export CORRIGIR_VFR=false
export CORRIGIR_TIMESTAMPS=false
python corretor-video.py  # Apenas corrige áudio
```

### Via Código Python

```python
from media_tools.video.corrector import CorretorVideo

# Corrigir todos os problemas
corretor = CorretorVideo(
    corrigir_vfr=True,
    corrigir_timestamps=True,
    corrigir_audio=True
)
corretor.processar(deletar_originais=False)

# Apenas correção de VFR
corretor = CorretorVideo(
    corrigir_vfr=True,
    corrigir_timestamps=False,
    corrigir_audio=False
)
corretor.processar()

# Detectar problemas sem corrigir
corretor = CorretorVideo()
problemas = corretor.detectar_problemas(arquivo_video)
print(f"VFR: {problemas['vfr']}")
print(f"Timestamps: {problemas['timestamps']}")
print(f"Áudio: {problemas['audio_desync']}")
```

## Configuração

O script está configurado com os seguintes parâmetros padrão:

- **Corrigir VFR**: Habilitado
- **Corrigir Timestamps**: Habilitado
- **Corrigir Áudio**: Habilitado
- **Deletar originais**: Desabilitado (por segurança)

### Personalização

Para personalizar os parâmetros, edite o arquivo `corretor-video.py` ou use o código Python:

```python
from pathlib import Path
from media_tools.video.corrector import CorretorVideo

# Personalizar pastas
corretor = CorretorVideo(
    pasta_entrada=Path("minha_pasta/entrada"),
    pasta_saida=Path("minha_pasta/saida"),
    corrigir_vfr=True,
    corrigir_timestamps=True,
    corrigir_audio=False
)

# Processar e deletar originais
corretor.processar(deletar_originais=True)
```

## Formatos Suportados

- MP4
- M4V
- MOV

## Pastas

- **Entrada**: `entrada/videos/`
- **Saída**: `saida/videos/`

## Tipos de Problemas Corrigidos

### VFR (Variable Frame Rate)

**Problema**: Vídeo com framerate variável pode causar problemas de reprodução, especialmente em players que esperam framerate constante.

**Solução**: O corretor detecta FPS variável ou fora de faixas normais (10-120 fps) e converte para framerate constante usando o filtro `fps` do FFmpeg.

**Quando é aplicado**: Requer re-encodar o vídeo (não pode usar `copy`).

### Timestamps

**Problema**: Problemas com timestamps (PTS - Presentation Time Stamp) podem causar travamentos, pulos ou dessincronia.

**Solução**: Usa flags `+genpts+igndts` do FFmpeg para regenerar timestamps corretamente.

**Quando é aplicado**: Pode ser aplicado sem re-encodar o vídeo (usa `copy` quando não há VFR).

### Dessincronia de Áudio

**Problema**: Áudio dessincronizado com o vídeo, especialmente comum em vídeos com VFR ou problemas de timestamps.

**Solução**: Usa filtro `aresample=async=1` para ajustar sincronização do áudio.

**Quando é aplicado**: Pode ser aplicado sem re-encodar o vídeo (usa `copy` quando não há VFR).

## Como Funciona

1. **Detecção**: Analisa cada vídeo para detectar problemas (VFR, timestamps, áudio)
2. **Seleção**: Determina quais correções aplicar baseado nas configurações
3. **Processamento**:
   - **Sem problemas**: Pula o vídeo
   - **Com problemas**: Aplica correções necessárias
     - Se apenas timestamps/áudio: Usa `copy` (rápido, sem re-encodar)
     - Se VFR detectado: Re-encoda com H.264 (necessário para aplicar filtro fps)
4. **Resultado**: Mostra informações antes/depois e estatísticas

### Estratégia de Correção

O corretor usa estratégias diferentes dependendo dos problemas detectados:

- **Apenas Timestamps/Áudio**: Usa `-c:v copy` (sem re-encodar, muito rápido, tamanho praticamente igual)
- **VFR detectado**: Re-encoda com H.264 CRF 23, preset medium (necessário para aplicar filtro fps, pode aumentar tamanho)
- **Múltiplos problemas**: Aplica todas as correções necessárias

### Impacto no Tamanho do Arquivo

- **Apenas timestamps/áudio (sem VFR)**:
  - ✅ Tamanho praticamente igual (usa `copy` mode)
  - ✅ Processamento muito rápido

- **VFR detectado (requer re-encodar)**:
  - ⚠️ Pode aumentar o tamanho (depende do vídeo original)
  - ⚠️ Processamento mais lento (re-encodar)
  - 📊 Fatores que influenciam:
    - Se o original já estava bem comprimido: pode aumentar 10-30%
    - Se o original estava mal comprimido: pode até diminuir um pouco
    - O corretor usa CRF 23 (qualidade boa), que é um bom equilíbrio

## Exemplos

### Corrigir todos os problemas

```bash
python corretor-video.py
```

### Apenas correção de VFR

```bash
python corretor-video.py --sem-timestamps --sem-audio
```

### Apenas correção de timestamps e áudio

```bash
python corretor-video.py --sem-vfr
```

### Detectar problemas sem corrigir

```python
from pathlib import Path
from media_tools.video.corrector import CorretorVideo

corretor = CorretorVideo()
arquivo = Path("meu_video.mp4")

problemas = corretor.detectar_problemas(arquivo)

if problemas["vfr"]:
    print("⚠️  Vídeo tem framerate variável")
if problemas["timestamps"]:
    print("⚠️  Vídeo tem problemas com timestamps")
if problemas["audio_desync"]:
    print("⚠️  Vídeo tem dessincronia de áudio")

if not any(problemas.values()):
    print("✅ Vídeo sem problemas detectados")
```

### Corrigir vídeo específico

```python
from pathlib import Path
from media_tools.video.corrector import CorretorVideo

corretor = CorretorVideo()

arquivo_entrada = Path("video_com_problemas.mp4")
arquivo_saida = Path("video_corrigido.mp4")

sucesso, erro = corretor.corrigir_video(arquivo_entrada, arquivo_saida)

if sucesso:
    print("✅ Vídeo corrigido com sucesso!")
else:
    print(f"❌ Erro: {erro}")
```

## Controle de Recursos

O corretor inclui controle automático de recursos para evitar sobrecarga do sistema (CPU e memória). Isso é especialmente importante quando processando muitos vídeos.

### Configuração Padrão

- **Threads**: 50% dos cores disponíveis (máximo 8 threads)
- **Limite CPU**: 85% (aguarda se exceder)
- **Limite Memória**: 85% (aguarda se exceder)
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

# Executar com as configurações
python corretor-video.py
```

### Recomendações

- **CPU potente (ex: Ryzen 9)**: Pode aumentar `FFMPEG_THREADS` se necessário
- **Sistema com pouca RAM**: Reduza `LIMITE_MEMORIA` (ex: 70%)
- **Processamento em background**: Aumente `PAUSA_ENTRE_VIDEOS` (ex: 2.0 ou 3.0)

### Funcionamento do Controle de Recursos

1. **Antes de cada vídeo**: Verifica uso de CPU e memória
2. **Se recursos excederem limites**: Aguarda até ficarem disponíveis (timeout: 120s)
3. **Durante processamento**: Usa número limitado de threads
4. **Entre vídeos**: Pausa para dar tempo ao sistema se recuperar
5. **Prioridade do processo**: Reduzida (nice=5) para menor impacto no sistema

## Diferenças do Otimizador

O **Corretor de Vídeos** é diferente do **Otimizador de Vídeos**:

| Característica | Corretor | Otimizador |
| -------------- | -------- | ---------- |
| **Objetivo** | Corrigir problemas técnicos | Otimizar tamanho mantendo qualidade |
| **Re-encodar** | Apenas quando necessário (VFR) | Sempre (otimização) |
| **Tamanho** | Pode aumentar (correções) | Sempre reduz |
| **Velocidade** | Rápido (usa `copy` quando possível) | Mais lento (sempre re-encoda) |
| **Uso** | Vídeos com problemas técnicos | Vídeos grandes que precisam compressão |

**Quando usar cada um:**

- **Corretor**: Vídeos com problemas de reprodução, framerate variável, dessincronia
- **Otimizador**: Vídeos grandes que precisam ser reduzidos mantendo qualidade

**Nota**: O otimizador já inclui correções automáticas, então você pode usar apenas o otimizador se precisar de ambos (otimização + correção).

## Notas

- ⚠️ **Atenção**: Com `deletar_originais=True`, os arquivos originais são **permanentemente deletados** após correção
- Vídeos sem problemas detectados são automaticamente pulados
- Correções de VFR requerem re-encodar (mais lento)
- Correções de timestamps/áudio podem usar `copy` (muito rápido)
- O script mostra informações detalhadas de cada vídeo
- **Controle de recursos**: O corretor protege automaticamente o sistema contra sobrecarga

## Troubleshooting

**Problema**: Erro "FFmpeg não encontrado"

- **Solução**: Instale FFmpeg e verifique se está no PATH

**Problema**: Vídeo pulado (sem problemas)

- **Solução**: Normal - vídeos sem problemas são pulados automaticamente. Se quiser forçar correção, desabilite a detecção no código

**Problema**: Processamento muito lento

- **Solução**: Normal quando VFR é detectado (requer re-encodar). Para acelerar, desabilite correção de VFR se não for necessária

**Problema**: Arquivo maior após correção

- **Solução**:
  - **Apenas timestamps/áudio**: O tamanho deve permanecer praticamente igual (usa `copy` mode)
  - **VFR corrigido**: Pode aumentar o tamanho porque requer re-encodar. O aumento depende do vídeo original:
    - Se o original já estava bem comprimido: pode aumentar 10-30%
    - Se o original estava mal comprimido: pode até diminuir um pouco
    - O corretor usa CRF 23 (qualidade boa), que é um bom equilíbrio

**Problema**: Sistema desliga ou trava durante processamento

- **Solução**: O corretor controla recursos automaticamente. Se ainda ocorrer:
  - Reduza `FFMPEG_THREADS` (ex: `export FFMPEG_THREADS=2`)
  - Reduza `LIMITE_CPU` (ex: `export LIMITE_CPU=70`)
  - Aumente `PAUSA_ENTRE_VIDEOS` (ex: `export PAUSA_ENTRE_VIDEOS=3.0`)

**Problema**: Correção não resolveu o problema

- **Solução**:
  - Verifique se o tipo de correção está habilitado
  - Alguns problemas podem requerer correção manual ou ferramentas especializadas
  - Tente usar o otimizador que tem correções mais agressivas

