# python-media-tools

> Coleção de 17 scripts CLI para processamento de mídia — compressão H.265, otimização de imagens/vídeos, conversão de formatos, OCR, remoção de fundo e utilitários de áudio/vídeo.

## Project Info

| Field | Value |
|-------|-------|
| Status | Manutenção |
| Stack | Python 3.6+ · FFmpeg · Pillow · OpenCV · numpy · psutil |
| Vault | `E:\Documentos\Obsidian\Projetos` |
| Vault Org | personal |
| Vault Path | personal/python-media-tools |
| Package Manager | pip |

## Structure

```
python-media-tools/
├── media_tools/
│   ├── common/        → paths, progress, validators, resource_control
│   ├── image/         → optimizer, converter, validator, ocr, background_remover, color_corrector, duplicate_detector
│   └── video/         → compressor, optimizer, converter, corrector, extractor, merger, stabilizer, duplicate_detector
├── entrada/
│   ├── imagens/       → imagens para processar
│   └── videos/        → vídeos para processar
├── saida/             → resultados gerados
├── docs/              → documentação local por feature
└── scripts/           → start.bat / start.sh / setup-venv.bat
```

## Key Patterns & Conventions

- Todos os scripts CLI instanciam a classe do módulo e chamam `.processar()`
- `obter_pastas_entrada_saida("videos")` retorna `(entrada/videos, saida/videos)` — convenção padrão
- x265 usa `-x265-params pools=N` (não `-threads`) para paralelismo real
- `deletar_originais=False` é o padrão seguro em todos os processamentos

## Anti-patterns

- Não usar `-threads N` para libx265 — ignorado pelo encoder (usar x265-params)
- Não chamar `_obter_info_video()` e `_obter_duracao_video()` separados — duração já vem do info
- Não usar preset `slow` como padrão no compressor — 3-5x mais lento por ~10% de diferença
- Não misturar vídeos de resoluções diferentes no merge sem re-encodar antes

## Concepts

| Term | Definition |
|------|-----------|
| CRF | Constant Rate Factor — qualidade constante (23=alto, 32=menor arquivo) |
| pools=N | Parâmetro x265 que define quantos cores físicos o encoder usa |
| VFR | Variable Frame Rate — framerate variável, causa problemas em players |
| copy mode | Re-muxing sem re-encodar — rápido, sem perda de qualidade |

## Decisions

| Decision | Rationale | Date |
|----------|-----------|------|
| H.265 como padrão de compressão | ~50% menor que H.264 mesma qualidade | — |
| preset medium em vez de slow | 3-5x mais rápido, ~10% arquivo maior | 12-04-2026 |
| x265-params pools em vez de -threads | -threads é ignorado pelo libx265 | 12-04-2026 |
| obter_cores_encoder() = total-2 | Deixa 2 cores livres para uso paralelo | 12-04-2026 |

## Next Steps

- Pendente

## Blockers

None
