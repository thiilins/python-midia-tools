---
tags: [claude-knowledge, python-media-tools, personal]
project: python-media-tools
org: personal
version: 1.1.0
updated: 13-04-2026
---

# python-media-tools — Context

> [[../_index|personal]] · [[_moc|Docs]]

## Status
Manutenção — 20 scripts CLI para processamento de imagens e vídeos. Compressão H.265, otimização, conversão, corte de vídeo, análise de pasta, conversão de FPS, OCR, remoção de fundo e utilitários.

## Stack
| Layer | Tech |
|-------|------|
| Runtime | Python 3.6+ · pip |
| Video | FFmpeg · libx265 · libx264 · psutil |
| Image | Pillow · OpenCV · numpy |
| Opcional | pytesseract · rembg · pillow-heif · pngquant |

## Key Paths
```
media_tools/common/    → paths, progress, validators, resource_control
media_tools/image/     → optimizer, converter, validator, ocr, background_remover, color_corrector, duplicate_detector
media_tools/video/     → compressor, optimizer, converter, corrector, extractor, merger, stabilizer, duplicate_detector, cutter, analyzer, fps_converter
entrada/videos/        → input vídeos
entrada/imagens/       → input imagens
saida/clips/           → clips extraídos pelo cutter
saida/                 → demais outputs gerados
```

## Must-Know Rules
- x265 usa `-x265-params pools=N` — `-threads` é ignorado pelo encoder
- `obter_cores_encoder()` = cores_físicos − 2 (env: `FFMPEG_CPU_CORES`)
- Preset padrão: `medium` (não `slow`) — 3-5x mais rápido, ~10% arquivo maior
- `deletar_originais=False` é o padrão seguro em todos os scripts
- Todos os CLIs: instanciar classe + chamar `.processar()`
- **Checklist novo script**: módulo → CLI → `__init__.py` → `start.bat` + `start.sh` (3 lugares)
- `CortadorVideo`: copy mode (`-c copy -avoid_negative_ts make_zero`), interativo via `input()`, saída `saida/clips/`
- `AnalisadorMidia`: somente leitura, 1 ffprobe por arquivo, estima compressão por bitrate médio do preset
- `ConversorFPS`: H.264 CRF 16 como intermediate de alta qualidade, pula vídeos já em ≤ fps alvo

## Anti-patterns
- Não usar `-threads` para libx265 — usar `-x265-params pools=N`
- Não chamar `_obter_info_video()` e `_obter_duracao_video()` separados
- Não misturar vídeos de resoluções no merge sem re-encodar antes
- Não usar `rembg` sem `pip install rembg` — dependência opcional
- Não adicionar script sem registrar em `__init__.py` + `start.bat` + `start.sh`
- Vault: `related:` no frontmatter não cria links clicáveis — sempre adicionar `## Related` com `[[...]]` no corpo

## Blockers
None

## Next Steps
- Redimensionamento de imagens em lote (`redimensionar-imagens.py`) — gap identificado, não implementado

## Sessions
_Sessions aparecerão aqui via /compress-vault_
