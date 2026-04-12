# Media Tools - Canivete Suíço de Mídia 🛠️

Ferramenta modular e padronizada para processamento de imagens e vídeos.

## 📋 Funcionalidades

### Imagens

- **Otimização**: Reduz tamanho de JPG, PNG, WebP, AVIF e HEIC mantendo qualidade e EXIF
- **Validação**: Separa imagens legíveis de ilegíveis (brilho, foco, uniformidade)
- **Conversão WebP → JPG**: Converte WebP para JPG, animações para GIF
- **Remoção de fundo**: Remove fundo automaticamente com IA (rembg)
- **OCR**: Detecta texto em imagens via Tesseract (pt + en)
- **Corretor de cores**: Ajusta brilho/contraste/saturação, filtros sépia/PB/vintage
- **Duplicatas**: Detecta cópias exatas via hash perceptual
- **Thumbnails**: Gera thumbnails em múltiplos tamanhos de imagens e vídeos

### Vídeos

- **Compressão H.265**: Comprime para 720p com H.265/HEVC — ~50% menor que H.264
- **Cortador (copy mode)**: Extrai segmentos por timestamp instantaneamente, sem re-encode
- **Analisador de pasta**: Inventário técnico com codec, resolução, FPS e estimativa de compressão
- **Conversor de FPS**: Reduz 60fps → 30fps (~30-40% menor antes de comprimir)
- **Otimização H.264**: Otimiza mantendo resolução original com H.264
- **Conversão WebM → MP4**: Converte WebM para MP4 corrigindo timestamps e VFR
- **Corretor**: Corrige VFR, timestamps e dessincronia de áudio (copy mode)
- **Extração de áudio**: Extrai MP3/AAC/OGG/WAV
- **Merge**: Concatena vídeos sem re-encode (copy mode)
- **Estabilizador**: Corrige vídeos tremidos via libvidstab (2 passes)
- **Duplicatas**: Detecta cópias exatas via hash MD5 de amostras

## 📚 Documentação

- **[Changelog](docs/CHANGELOG.md)** - Histórico de mudanças e melhorias
- **[Resumo da Implementação](docs/RESUMO_IMPLEMENTACAO.md)** - Visão geral das funcionalidades
- **[Estrutura do Projeto](docs/ESTRUTURA_PROJETO.md)** - Organização completa do código

## 🚀 Instalação Rápida

### Windows

```bash
# Execute o script de inicialização
scripts\start.bat
```

### Linux/macOS

```bash
# Dê permissão de execução
chmod +x scripts/start.sh

# Execute o script
./scripts/start.sh
```

Os scripts verificam e instalam automaticamente:

- Python 3.6+
- Dependências Python (pip install -r requirements.txt)
- FFmpeg (apenas para scripts de vídeo)

## 📦 Instalação com Ambiente Virtual (Recomendado)

Usar ambiente virtual (venv) é a melhor prática para isolar as dependências do projeto.

### Método Rápido (Scripts Automáticos)

#### Windows

```cmd
# Execute o script de setup
scripts\setup-venv.bat
```

#### Linux/macOS

```bash
# Dê permissão de execução (se necessário)
chmod +x scripts/setup-venv.sh

# Execute o script de setup
./scripts/setup-venv.sh
```

Os scripts criam automaticamente o ambiente virtual e instalam todas as dependências.

### Método Manual

#### Windows

#### 1. Criar o ambiente virtual

```cmd
# No PowerShell ou CMD, navegue até a pasta do projeto
cd C:\caminho\para\python-tools

# Criar o ambiente virtual
python -m venv venv
```

#### 2. Ativar o ambiente virtual

```cmd
# PowerShell
.\venv\Scripts\Activate.ps1

# CMD
.\venv\Scripts\activate.bat
```

**Nota**: Se você receber um erro no PowerShell sobre política de execução, execute:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 3. Instalar dependências

```cmd
# Atualizar pip
python -m pip install --upgrade pip

# Instalar dependências do projeto
pip install -r requirements.txt
```

#### 4. Usar o projeto

```cmd
# Com o ambiente virtual ativado, execute os scripts normalmente
python otimizador-imagens.py
```

#### 5. Desativar o ambiente virtual

```cmd
deactivate
```

### Linux/macOS

#### 1. Criar o ambiente virtual

```bash
# Navegue até a pasta do projeto
cd /caminho/para/python-tools

# Criar o ambiente virtual
python3 -m venv venv
```

#### 2. Ativar o ambiente virtual

```bash
source venv/bin/activate
```

Você verá `(venv)` no início da linha do terminal quando o ambiente estiver ativo.

#### 3. Instalar dependências

```bash
# Atualizar pip
python -m pip install --upgrade pip

# Instalar dependências do projeto
pip install -r requirements.txt
```

#### 4. Usar o projeto

```bash
# Com o ambiente virtual ativado, execute os scripts normalmente
python otimizador-imagens.py
```

#### 5. Desativar o ambiente virtual

```bash
deactivate
```

## 🔧 Instalação Manual (Sem venv)

### Windows

1. **Instalar Python 3.6+**

   - Download: https://www.python.org/downloads/
   - ⚠️ **Importante**: Marque "Add Python to PATH" durante a instalação

2. **Instalar FFmpeg** (apenas para scripts de vídeo)

   - Download: https://www.gyan.dev/ffmpeg/builds/
   - Extraia e adicione `bin` ao PATH do sistema

3. **Instalar dependências Python**
   ```cmd
   pip install -r requirements.txt
   ```

### Linux/macOS

1. **Instalar Python 3.6+**

   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install python3 python3-pip

   # macOS (com Homebrew)
   brew install python3
   ```

2. **Instalar FFmpeg** (apenas para scripts de vídeo)

   ```bash
   # Ubuntu/Debian
   sudo apt-get install ffmpeg

   # macOS
   brew install ffmpeg
   ```

3. **Instalar dependências Python**
   ```bash
   pip3 install -r requirements.txt
   ```

## 📦 Estrutura do Projeto

```
python-media-tools/
├── media_tools/              # Módulos principais
│   ├── common/              # Utilitários compartilhados
│   │   ├── paths.py         # Gerenciamento de caminhos
│   │   ├── progress.py      # Barras de progresso
│   │   ├── validators.py    # Validações de dependências
│   │   └── resource_control.py  # Controle de CPU/memória/threads
│   ├── image/               # Processamento de imagens (8 módulos)
│   │   ├── optimizer.py     # Otimizador JPG/PNG/WebP/AVIF/HEIC
│   │   ├── converter.py     # Conversor WebP→JPG
│   │   ├── validator.py     # Validador de legibilidade
│   │   ├── color_corrector.py   # Corretor de cores e filtros
│   │   ├── background_remover.py # Remoção de fundo com IA
│   │   ├── ocr.py           # OCR via Tesseract
│   │   └── duplicate_detector.py # Detector de duplicatas
│   └── video/               # Processamento de vídeos (11 módulos)
│       ├── compressor.py    # Compressor H.265 com presets
│       ├── optimizer.py     # Otimizador H.264
│       ├── converter.py     # Conversor WebM→MP4
│       ├── corrector.py     # Corretor VFR/timestamps/áudio
│       ├── extractor.py     # Extrator de áudio e thumbnails
│       ├── merger.py        # Merge de vídeos (copy mode)
│       ├── stabilizer.py    # Estabilizador via libvidstab
│       ├── duplicate_detector.py # Detector de duplicatas
│       ├── cutter.py        # Cortador por timestamp (copy mode)
│       ├── analyzer.py      # Analisador de pasta com estimativas
│       └── fps_converter.py # Conversor de FPS
├── entrada/
│   ├── imagens/            # Imagens para processar
│   └── videos/             # Vídeos para processar
├── saida/                   # Resultados gerados
├── scripts/
│   ├── start.bat           # Menu interativo (Windows)
│   ├── start.sh            # Menu interativo (Linux/macOS)
│   ├── setup-venv.bat      # Setup venv (Windows)
│   └── setup-venv.sh       # Setup venv (Linux/macOS)
├── docs/                   # Documentação local
│── otimizador-imagens.py         # Otimizar imagens
├── validate-images.py            # Validar imagens
├── webp-to-jpg.py                # Converter WebP→JPG
├── detector-duplicatas-imagens.py # Duplicatas de imagens
├── ocr-imagens.py                # OCR de imagens
├── remover-fundo.py              # Remover fundo
├── corretor-cores.py             # Corretor de cores
├── gerador-thumbnails.py         # Gerar thumbnails
├── otimizador-compressor-video.py # Comprimir H.265
├── otimizador-video.py           # Otimizar H.264
├── webm-mp4.py                   # Converter WebM→MP4
├── corretor-video.py             # Corrigir VFR/timestamps
├── extrair-audio.py              # Extrair áudio
├── extrair-thumbnails.py         # Extrair thumbnails
├── merge-videos.py               # Merge vídeos
├── estabilizador-video.py        # Estabilizar vídeos
├── detector-duplicatas-videos.py # Duplicatas de vídeos
├── cortar-video.py               # Cortar clips (copy mode)
├── analisar-pasta.py             # Analisar pasta de vídeos
├── converter-fps.py              # Converter FPS
├── requirements.txt
└── README.md
```

## 🎯 Uso

### Via Menu Interativo

Execute `scripts/start.bat` (Windows) ou `scripts/start.sh` (Linux/macOS) e escolha uma opção:

**Imagens:**

1. **Otimizar Imagens**: Processa JPG, PNG, WebP, AVIF, HEIC na pasta `entrada/imagens/`
2. **Validar Imagens**: Analisa imagens em `entrada/downloads/` e separa em legíveis/ilegíveis
3. **Converter WebP → JPG**: Converte WebP para JPG na pasta `entrada/imagens/`
4. **Detectar Duplicatas de Imagens**: Encontra imagens duplicadas
5. **OCR de Imagens**: Detecta texto em imagens usando Tesseract
6. **Remover Fundo**: Remove fundo de imagens automaticamente
7. **Corretor de Cores**: Ajusta brilho, contraste e aplica filtros
8. **Gerar Thumbnails**: Gera thumbnails de imagens e vídeos

**Vídeos:**

9. **Comprimir Vídeos (H.265)**: Comprime para 720p com H.265 — pasta `entrada/videos/`
10. **Otimizar Vídeos (H.264)**: Processa MP4, M4V e MOV na pasta `entrada/videos/`
11. **Converter WebM → MP4**: Converte WebM para MP4 na pasta `entrada/videos/`
12. **Extrair Áudio**: Extrai áudio de vídeos (MP3, AAC, OGG, WAV)
13. **Extrair Thumbnails**: Extrai thumbnails de vídeos
14. **Merge Vídeos**: Concatena múltiplos vídeos
15. **Corretor de Vídeo**: Corrige VFR, timestamps e áudio
16. **Estabilizador**: Estabiliza vídeos tremidos
17. **Detectar Duplicatas de Vídeos**: Encontra vídeos duplicados
18. **Cortar Vídeo**: Extrai segmentos por timestamp (copy mode, instantâneo)
19. **Analisar Pasta**: Inventário técnico com estimativas de compressão
20. **Converter FPS**: Reduz framerate (60fps → 30fps, ~30-40% menor)

### Via Linha de Comando

#### Com ambiente virtual ativado:

**Windows:**

```cmd
.\venv\Scripts\activate
python otimizador-imagens.py
```

**Linux/macOS:**

```bash
source venv/bin/activate
python otimizador-imagens.py
```

#### Sem ambiente virtual:

**Windows:**

```cmd
python otimizador-imagens.py
```

**Linux/macOS:**

```bash
python3 otimizador-imagens.py
```

### Scripts Disponíveis

**Imagens:**

```bash
python otimizador-imagens.py          # Otimizar imagens (JPG, PNG, WebP, AVIF, HEIC)
python validate-images.py              # Validar imagens (separar legíveis/ilegíveis)
python webp-to-jpg.py                 # Converter WebP para JPG
python detector-duplicatas-imagens.py # Detectar duplicatas
python ocr-imagens.py                 # OCR de texto em imagens
python remover-fundo.py               # Remover fundo de imagens
python corretor-cores.py              # Corrigir cores e aplicar filtros
python gerador-thumbnails.py          # Gerar thumbnails
```

**Vídeos:**

```bash
# Analisar antes de comprimir (recomendado)
python analisar-pasta.py              # inventário: codec, FPS, tamanho, estimativas

# Workflow streams longas (ex: 15GB, 60fps)
python converter-fps.py --fps 30      # 1. reduz 60→30fps (~30-40% menor)
python otimizador-compressor-video.py --preset stream_720p  # 2. H.265 720p

# Cortar clips antes de comprimir
python cortar-video.py                # extrai segmentos por timestamp (instantâneo)

# Compressor H.265 (padrão recomendado)
python otimizador-compressor-video.py                           # Perfil Master 720p (padrão)
python otimizador-compressor-video.py --preset stream_720p      # Streams longas — 720p
python otimizador-compressor-video.py --preset stream_540p      # Streams longas — 540p
python otimizador-compressor-video.py --preset stream_480p      # Streams longas — 480p mínimo
python otimizador-compressor-video.py --preset ultra_compression_720p  # CRF 32 agressivo 720p
python otimizador-compressor-video.py --preset maximum_compression     # Sem reduzir resolução
python otimizador-compressor-video.py --presets                        # Lista todos os perfis

# Controle de CPU (não travar o PC durante uso paralelo)
set FFMPEG_CPU_CORES=6 && python otimizador-compressor-video.py --preset stream_540p

# Outros processamentos
python corretor-video.py              # Corrigir VFR, timestamps, áudio
python otimizador-video.py            # Otimizar vídeos com H.264
python webm-mp4.py                    # Converter WebM para MP4
python extrair-audio.py               # Extrair áudio de vídeos
python extrair-thumbnails.py          # Extrair thumbnails de vídeos
python merge-videos.py                # Concatenar múltiplos vídeos
python estabilizador-video.py         # Estabilizar vídeos tremidos
python detector-duplicatas-videos.py  # Detectar vídeos duplicados
```

📖 **Documentação completa**: Veja [docs/RESUMO_IMPLEMENTACAO.md](docs/RESUMO_IMPLEMENTACAO.md) para detalhes de cada funcionalidade.

## ⚙️ Configurações

### Otimizador de Imagens

- **Qualidade JPG**: 85% (padrão) - ajustável no código
- **Conversão automática**: WebP → JPG
- **Pasta de entrada**: `entrada/imagens/`
- **Pasta de saída**: `saida/imagens/`

### Compressor de Vídeos (otimizador-compressor-video.py)

Perfil padrão **Master 720p** — melhor equilíbrio qualidade/tamanho:

| Parâmetro | Valor | Motivo |
| :--- | :--- | :--- |
| **Codec** | H.265 (libx265) | ~50% menor que H.264 mesma qualidade |
| **Resolução** | 720p (1280×720) | Reduz apenas se o original for maior |
| **CRF** | 23 | Sweet spot qualidade/compressão |
| **Preset encoder** | medium | Equilíbrio velocidade/compressão |
| **Áudio** | AAC 96kbps stereo | Eficiente para 720p |
| **Saída** | sempre `.mp4` | Independente do formato de entrada |

**Pasta de entrada**: `entrada/videos/`
**Pasta de saída**: `saida/videos/`

Perfis disponíveis (use `--preset <nome>`):

| Preset | CRF | Resolução | Bitrate máx | Indicado para |
| :--- | :--- | :--- | :--- | :--- |
| `master_720p` **(padrão)** | 23 | 720p | — | Qualidade + tamanho equilibrados |
| `stream_720p` | 28 | 720p | 1.5M | Streams e gravações longas (15GB+) |
| `stream_540p` | 28 | 540p | 1M | Streams longas — 35% menor que 720p |
| `stream_480p` | 28 | 480p | 800k | Streams longas — arquivo mínimo |
| `balanced_compression` | 28 | original | — | Compressão leve sem reduzir |
| `high_compression` | 30 | original | 3M | Alta compressão, boa qualidade |
| `maximum_compression` | 32 | original | 2M | Máxima compressão sem reduzir |
| `ultra_compression_1080p` | 32 | 1080p | 1.5M | Arquivo mínimo em 1080p |
| `ultra_compression_720p` | 32 | 720p | 1M | Arquivo mínimo agressivo em 720p |
| `extreme_compression` | 35 | original | 1.5M | Extremo (perda visível) |

**Estimativa de saída para arquivos de 15GB (streams ~4-8h):**

| Preset | Estimativa |
| :--- | :--- |
| `stream_720p` | ~800MB – 2GB |
| `stream_540p` | ~500MB – 1.2GB |
| `stream_480p` | ~300MB – 700MB |

**Variáveis de ambiente para controle de recursos:**

```bat
set FFMPEG_CPU_CORES=8      # Cores físicos para o encoder x265 (padrão: total-2)
set FFMPEG_THREADS=12       # Threads I/O do FFmpeg (padrão: 50% dos lógicos)
set ENCODER_VELOCIDADE=rapido  # faster | normal (padrão) | lento
set USAR_GPU=1              # Tenta GPU: AMD AMF / NVIDIA NVENC / Intel QSV
set LIMITE_CPU=85           # Limite de uso de CPU em % (padrão: 85%)
set LIMITE_MEMORIA=85       # Limite de uso de memória em % (padrão: 85%)
```

### Cortador de Vídeo (cortar-video.py)

Modo interativo — lista vídeos disponíveis e solicita timestamps via terminal.

- **Modo**: copy mode — sem re-encode, instantâneo mesmo em arquivos de 15GB
- **Pasta de entrada**: `entrada/videos/`
- **Pasta de saída**: `saida/clips/`
- **Formatos de tempo**: `HH:MM:SS`, `MM:SS` ou segundos
- Permite cortar múltiplos segmentos em sequência

### Analisador de Pasta (analisar-pasta.py)

Exibe inventário técnico completo antes de decidir o que/como comprimir.

- **Informações por arquivo**: codec, resolução, FPS, bitrate, duração, tamanho
- **Estimativa**: tamanho pós-compressão H.265 stream_720p
- **Recomendação**: preset/workflow sugerido por arquivo
- **Pasta padrão**: `entrada/videos/` (ou path via argumento)

```bash
python analisar-pasta.py                    # analisa entrada/videos/
python analisar-pasta.py /minha/pasta       # analisa pasta específica
```

### Conversor de FPS (converter-fps.py)

Pré-processamento para streams: reduz FPS antes de comprimir.

| Passo | Script | Redução estimada |
| :--- | :--- | :--- |
| 1. Reduzir FPS | `converter-fps.py --fps 30` | ~30-40% |
| 2. Comprimir H.265 | `otimizador-compressor-video.py --preset stream_720p` | ~60-70% adicional |

- **FPS padrão**: 30 (configurável via `--fps N`)
- **Codec saída**: H.264 CRF 16 (alta qualidade intermediária)
- **Arquivos já em ≤ fps alvo**: pulados automaticamente
- **Pasta de entrada**: `entrada/videos/`
- **Pasta de saída**: `saida/videos/` (sufixo `_{fps}fps.mp4`)

```bash
python converter-fps.py            # converte para 30fps
python converter-fps.py --fps 24   # converte para 24fps
```

### Otimizador de Vídeos (otimizador-video.py)

- **CRF**: 23 (padrão) - qualidade constante (18-28 recomendado)
- **Preset**: medium (padrão) - velocidade de codificação
- **Codec**: H.264 (libx264)
- **Pasta de entrada**: `entrada/videos/`
- **Pasta de saída**: `saida/videos/`

### Conversor WebM → MP4

- **FPS**: 30 (padrão)
- **CRF**: 20 (padrão)
- **Correção de velocidade**: Desativada por padrão
- **Manter originais**: True (padrão)

### Validador de Imagens

- **Limiares configuráveis** para brilho, foco, uniformidade e bordas
- **Log detalhado**: `historico_processamento.log`
- **Pasta de entrada**: `entrada/downloads/`
- **Pastas de saída**: `saida/legiveis/` e `saida/ilegiveis/`

## 📝 Dependências

### Python (requirements.txt)

- **Pillow** >= 10.2.0 - Processamento de imagens
- **opencv-python** >= 4.12.0 - Análise de imagens
- **numpy** >= 2.2.0 - Computação numérica
- **tqdm** >= 4.66.1 - Barras de progresso
- **python-dotenv** >= 1.0.0 - Variáveis de ambiente
- **requests** >= 2.31.0 - Requisições HTTP

### Sistema

- **FFmpeg**: Necessário apenas para scripts de vídeo
  - Windows: https://www.gyan.dev/ffmpeg/builds/
  - Linux: `sudo apt-get install ffmpeg`
  - macOS: `brew install ffmpeg`

## 🔧 Desenvolvimento

### Estrutura Modular

O projeto foi modularizado para facilitar manutenção e extensão:

- **Módulos compartilhados** (`common/`): Funções reutilizáveis
- **Módulos específicos** (`image/`, `video/`): Lógica de processamento
- **Scripts CLI**: Interfaces simples que usam os módulos

### Adicionar Nova Funcionalidade

1. Crie um novo módulo em `media_tools/` (ex: `media_tools/audio/`)
2. Use os utilitários de `common/` (paths, progress, validators)
3. Crie um script CLI que usa o módulo
4. Adicione a opção no menu de `start.bat` e `start.sh`

### Executar Testes

```bash
# Com ambiente virtual ativado
python -m pytest tests/  # Se houver testes
```

## 🐛 Solução de Problemas

### Erro: "ModuleNotFoundError: No module named 'media_tools'"

**Solução**: Certifique-se de estar executando o script na pasta raiz do projeto:

```bash
cd /caminho/para/python-tools
python otimizador-imagens.py
```

### Erro: "FFmpeg não encontrado"

**Solução**:

- Verifique se o FFmpeg está instalado: `ffmpeg -version`
- Adicione o FFmpeg ao PATH do sistema
- Este erro só afeta scripts de vídeo

### Erro: "Permission denied" no Linux/macOS

**Solução**:

```bash
chmod +x start.sh
chmod +x *.py
```

### Ambiente virtual não ativa no Windows PowerShell

**Solução**:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Dependências não instalam

**Solução**:

```bash
# Atualizar pip primeiro
python -m pip install --upgrade pip

# Instalar dependências
pip install -r requirements.txt
```

## 📄 Licença

Este projeto é de código aberto. Sinta-se livre para usar e modificar.

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se livre para abrir issues ou pull requests.

## 📞 Suporte

Se encontrar problemas ou tiver dúvidas:

1. Verifique a seção "Solução de Problemas" acima
2. Abra uma issue no repositório
3. Consulte a documentação dos módulos em `media_tools/`

---

**Desenvolvido com ❤️ para facilitar o processamento de mídia**
