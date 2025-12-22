# Estrutura Completa do Projeto

## 📁 Estrutura de Diretórios

```
python-tools/
├── media_tools/                    # Biblioteca modular principal
│   ├── __init__.py
│   ├── common/                    # Utilitários compartilhados
│   │   ├── __init__.py
│   │   ├── paths.py               # Gerenciamento de caminhos
│   │   ├── progress.py            # Barras de progresso
│   │   └── validators.py          # Validações de dependências
│   ├── image/                     # Processamento de imagens
│   │   ├── __init__.py
│   │   ├── optimizer.py           # Otimizador (melhorado)
│   │   ├── converter.py           # Conversor WebP→JPG (melhorado)
│   │   ├── validator.py           # Validador (melhorado)
│   │   ├── duplicate_detector.py  # Detector de duplicatas
│   │   ├── ocr.py                 # OCR de imagens
│   │   ├── background_remover.py  # Remoção de fundo
│   │   └── color_corrector.py     # Correção de cores
│   └── video/                     # Processamento de vídeos
│       ├── __init__.py
│       ├── optimizer.py           # Otimizador (melhorado)
│       ├── converter.py           # Conversor WebM→MP4 (melhorado)
│       ├── extractor.py           # Extrator de áudio e thumbnails
│       ├── merger.py              # Merge de vídeos
│       ├── stabilizer.py          # Estabilizador
│       └── duplicate_detector.py  # Detector de duplicatas
│
├── entrada/                       # Pasta de entrada
│   ├── imagens/                  # Imagens para processar
│   ├── videos/                   # Vídeos para processar
│   └── downloads/                # Imagens para validação
│
├── saida/                         # Pasta de saída
│   ├── imagens/                  # Imagens processadas
│   ├── videos/                   # Vídeos processados
│   ├── legiveis/                 # Imagens legíveis
│   ├── ilegiveis/                # Imagens ilegíveis
│   ├── com_texto/                # Imagens com texto (OCR)
│   ├── sem_texto/                # Imagens sem texto (OCR)
│   ├── sem_fundo/                # Imagens sem fundo
│   ├── corrigidas/               # Imagens corrigidas
│   ├── thumbnails/               # Thumbnails geradas
│   └── audio/                    # Áudio extraído
│
├── Scripts CLI (15 scripts):
│   ├── otimizador-imagens.py
│   ├── otimizador-video.py
│   ├── validate-images.py
│   ├── webm-mp4.py
│   ├── webp-to-jpg.py
│   ├── extrair-audio.py
│   ├── extrair-thumbnails.py
│   ├── merge-videos.py
│   ├── estabilizador-video.py
│   ├── detector-duplicatas-videos.py
│   ├── ocr-imagens.py
│   ├── detector-duplicatas-imagens.py
│   ├── remover-fundo.py
│   ├── corretor-cores.py
│   └── gerador-thumbnails.py
│
├── Scripts de Setup:
│   ├── start.bat                  # Menu Windows
│   ├── start.sh                   # Menu Linux/macOS
│   ├── setup-venv.bat             # Setup venv Windows
│   └── setup-venv.sh              # Setup venv Linux/macOS
│
└── Documentação:
    ├── README.md                  # Documentação completa
    ├── CHANGELOG.md               # Histórico de mudanças
    ├── RESUMO_IMPLEMENTACAO.md    # Resumo da implementação
    ├── ESTRUTURA_PROJETO.md       # Este arquivo
    └── requirements.txt           # Dependências
```

## 🎯 Scripts por Categoria

### Imagens (8 scripts)
1. `otimizador-imagens.py` - Otimiza e converte imagens
2. `validate-images.py` - Valida legibilidade
3. `webp-to-jpg.py` - Converte WebP para JPG
4. `detector-duplicatas-imagens.py` - Detecta duplicatas
5. `ocr-imagens.py` - OCR de texto
6. `remover-fundo.py` - Remove fundo
7. `corretor-cores.py` - Corrige cores e filtros
8. `gerador-thumbnails.py` - Gera thumbnails

### Vídeos (7 scripts)
9. `otimizador-video.py` - Otimiza vídeos
10. `webm-mp4.py` - Converte WebM para MP4
11. `extrair-audio.py` - Extrai áudio
12. `extrair-thumbnails.py` - Extrai thumbnails
13. `merge-videos.py` - Concatena vídeos
14. `estabilizador-video.py` - Estabiliza vídeos
15. `detector-duplicatas-videos.py` - Detecta duplicatas

## 📦 Módulos Criados

### Common (3 módulos)
- `paths.py` - Gerenciamento de caminhos
- `progress.py` - Barras de progresso
- `validators.py` - Validações

### Image (7 módulos)
- `optimizer.py` - Otimização
- `converter.py` - Conversão WebP
- `validator.py` - Validação
- `duplicate_detector.py` - Duplicatas
- `ocr.py` - OCR
- `background_remover.py` - Remoção de fundo
- `color_corrector.py` - Correção de cores

### Video (6 módulos)
- `optimizer.py` - Otimização
- `converter.py` - Conversão WebM
- `extractor.py` - Extração (áudio/thumbnails)
- `merger.py` - Merge
- `stabilizer.py` - Estabilização
- `duplicate_detector.py` - Duplicatas

## ✨ Total: 16 Módulos + 15 Scripts CLI

