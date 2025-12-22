# Media Tools - Canivete Suíço de Mídia 🛠️

Ferramenta modular e padronizada para processamento de imagens e vídeos.

## 📋 Funcionalidades

### Imagens

- **Otimização**: Reduz tamanho de JPG, PNG e WebP mantendo qualidade
- **Conversão WebP → JPG**: Converte WebP para JPG com alta qualidade
- **Validação**: Separa imagens legíveis de ilegíveis (análise de brilho, foco, uniformidade)

### Vídeos

- **Otimização**: Otimiza MP4, M4V e MOV usando H.264
- **Conversão WebM → MP4**: Converte WebM para MP4 corrigindo timestamps e VFR

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
python-tools/
├── media_tools/              # Módulos principais
│   ├── __init__.py
│   ├── common/              # Utilitários compartilhados
│   │   ├── __init__.py
│   │   ├── paths.py         # Gerenciamento de caminhos
│   │   ├── progress.py      # Barras de progresso
│   │   └── validators.py     # Validações de dependências
│   ├── image/               # Processamento de imagens
│   │   ├── __init__.py
│   │   ├── optimizer.py     # Otimizador de imagens
│   │   ├── converter.py     # Conversor WebP→JPG
│   │   └── validator.py      # Validador de legibilidade
│   └── video/               # Processamento de vídeos
│       ├── __init__.py
│       ├── optimizer.py     # Otimizador de vídeos
│       └── converter.py      # Conversor WebM→MP4
├── entrada/                 # Pasta de entrada
│   ├── imagens/            # Imagens para processar
│   ├── videos/             # Vídeos para processar
│   └── downloads/          # Imagens para validação
├── saida/                   # Pasta de saída
│   ├── imagens/            # Imagens processadas
│   ├── videos/             # Vídeos processados
│   ├── legiveis/           # Imagens legíveis
│   └── ilegiveis/          # Imagens ilegíveis
├── venv/                    # Ambiente virtual (criado pelo usuário)
├── scripts/                # Scripts de inicialização
│   ├── start.bat          # Menu interativo (Windows)
│   ├── start.sh            # Menu interativo (Linux/macOS)
│   ├── setup-venv.bat      # Setup venv (Windows)
│   └── setup-venv.sh       # Setup venv (Linux/macOS)
├── docs/                   # Documentação
│   ├── CHANGELOG.md       # Histórico de mudanças
│   ├── RESUMO_IMPLEMENTACAO.md  # Resumo das funcionalidades
│   └── ESTRUTURA_PROJETO.md     # Estrutura completa
├── otimizador-imagens.py   # Script CLI: Otimizar imagens
├── otimizador-video.py     # Script CLI: Otimizar vídeos
├── validate-images.py       # Script CLI: Validar imagens
├── webm-mp4.py            # Script CLI: Converter WebM→MP4
├── webp-to-jpg.py         # Script CLI: Converter WebP→JPG
├── extrair-audio.py        # Script CLI: Extrair áudio
├── extrair-thumbnails.py   # Script CLI: Extrair thumbnails
├── merge-videos.py         # Script CLI: Merge vídeos
├── estabilizador-video.py  # Script CLI: Estabilizar vídeo
├── detector-duplicatas-videos.py  # Script CLI: Detectar duplicatas vídeos
├── ocr-imagens.py          # Script CLI: OCR de imagens
├── detector-duplicatas-imagens.py # Script CLI: Detectar duplicatas imagens
├── remover-fundo.py        # Script CLI: Remover fundo
├── corretor-cores.py       # Script CLI: Corretor de cores
├── gerador-thumbnails.py   # Script CLI: Gerar thumbnails
├── requirements.txt        # Dependências Python
└── README.md               # Este arquivo
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

**Vídeos:** 9. **Otimizar Vídeos**: Processa MP4, M4V e MOV na pasta `entrada/videos/` 10. **Converter WebM → MP4**: Converte WebM para MP4 na pasta `entrada/videos/` 11. **Extrair Áudio**: Extrai áudio de vídeos (MP3, AAC, OGG, WAV) 12. **Extrair Thumbnails**: Extrai thumbnails de vídeos 13. **Merge Vídeos**: Concatena múltiplos vídeos 14. **Estabilizador**: Estabiliza vídeos tremidos 15. **Detectar Duplicatas de Vídeos**: Encontra vídeos duplicados

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
python otimizador-video.py            # Otimizar vídeos (MP4, M4V, MOV)
python webm-mp4.py                    # Converter WebM para MP4
python extrair-audio.py                # Extrair áudio de vídeos
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

### Otimizador de Vídeos

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
