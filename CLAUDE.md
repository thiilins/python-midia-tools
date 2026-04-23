# python-media-tools

> Coleção de 21 scripts CLI para processamento de mídia — compressão H.265, otimização de imagens/vídeos, conversão de formatos, corte de vídeo, fatiamento batch, análise de pasta, conversão de FPS, OCR, remoção de fundo e utilitários de áudio/vídeo.

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
│   └── video/         → compressor, optimizer, converter, corrector, extractor, merger, stabilizer, duplicate_detector, cutter, analyzer, fps_converter, slicer
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
- **Checklist novo script**: criar módulo → criar CLI → exportar em `__init__.py` → adicionar ao `start.bat` + `start.sh`
- Scripts interativos (ex: cutter) usam `input()` no `processar()` — sem arquivo de config externo
- `CortadorVideo`: copy mode via `-c copy -avoid_negative_ts make_zero`, saída em `saida/clips/`
- `FatiadorVideo`: lê `entrada/videos/cut-settings.(txt|json)` (JSON prioridade), extrai segmentos e concatena via `concat demuxer`; saída `saida/videos/` mesmo nome do original; `--delete` apaga original só após sucesso
- `AnalisadorMidia`: somente leitura, 1 ffprobe por arquivo, estima com bitrate médio do preset
- `ConversorFPS`: H.264 CRF 16 como intermediate de alta qualidade antes do H.265

## Anti-patterns

- Não usar `-threads N` para libx265 — ignorado pelo encoder (usar x265-params)
- Não chamar `_obter_info_video()` e `_obter_duracao_video()` separados — duração já vem do info
- Não usar preset `slow` como padrão no compressor — 3-5x mais lento por ~10% de diferença
- Não misturar vídeos de resoluções diferentes no merge sem re-encodar antes
- Não adicionar script sem registrar em `__init__.py` + `start.bat` + `start.sh` (3 lugares)
- Vault docs: wiki-links `related:` no frontmatter não são clicáveis — adicionar `## Related` com `[[...]]` no corpo
- `hevc_amf vbr_peak` ignora `-maxrate` mesmo com `-b:v` explícito — output pode ser 8× maior; usar `cbr`
- `bufsize 2M` hardcoded é inadequado para streams de alto bitrate (ex: 6981kbps) — calcular como `2× maxrate`
- Cap maxrate em 100% do original sem margem — overhead de container (~0.7%) já ultrapassa; usar 90%
- Não derivar bitrate de `bit_rate` do ffprobe para VFR — impreciso; calcular por `file_size×8/duração`

## Concepts

| Term | Definition |
|------|-----------|
| CRF | Constant Rate Factor — qualidade constante (23=alto, 32=menor arquivo) |
| pools=N | Parâmetro x265 que define quantos cores físicos o encoder usa |
| VFR | Variable Frame Rate — framerate variável, causa problemas em players |
| copy mode | Re-muxing sem re-encodar — rápido, sem perda de qualidade |
| vbr_peak | Modo AMF de VBR com pico controlado — NÃO garante enforcement do maxrate |
| cbr | Bitrate constante — único modo AMF com enforcement garantido do teto de bitrate |

## Decisions

| Decision | Rationale | Date |
|----------|-----------|------|
| H.265 como padrão de compressão | ~50% menor que H.264 mesma qualidade | — |
| preset medium em vez de slow | 3-5x mais rápido, ~10% arquivo maior | 12-04-2026 |
| x265-params pools em vez de -threads | -threads é ignorado pelo libx265 | 12-04-2026 |
| obter_cores_encoder() = total-2 | Deixa 2 cores livres para uso paralelo | 12-04-2026 |
| CortadorVideo em copy mode | Sem re-encode = instantâneo em 15GB, sem perda | 13-04-2026 |
| FatiadorVideo lê cut-settings.(txt\|json) | Batch de múltiplos vídeos sem interatividade; JSON prioridade quando ambos existem | 23-04-2026 |
| Concat via demuxer com temp dir por vídeo | Isolamento garante limpeza em `finally` mesmo em falha; 1 segmento = shutil.move direto | 23-04-2026 |
| GPU 0 habilitada por padrão (USAR_GPU default=1) | Usuário sempre usa RX 9060 XT; USAR_GPU=0 para desabilitar | 23-04-2026 |
| --delete padrão no compressor (--keep para manter) | Fluxo normal é sempre apagar original após compressão bem-sucedida | 23-04-2026 |
| AnalisadorMidia somente leitura | Inventário antes de decidir o que comprimir | 13-04-2026 |
| ConversorFPS usa H.264 CRF 16 | Intermediate alta qualidade para H.265 posterior | 13-04-2026 |
| Encode ≥ original → apaga encode, move original para saída | Pasta saída sempre completa independente do resultado | 23-04-2026 |
| maxrate = file_size×8/duration×0.90 (não bit_rate ffprobe) | bit_rate impreciso em VFR; 90% absorve overhead de container | 23-04-2026 |
| hevc_amf usa cbr quando maxrate definido | vbr_peak ignora maxrate mesmo com -b:v — cbr é único modo confiável | 23-04-2026 |
| bufsize = 2× maxrate (dinâmico) | bufsize 2M fixo inadequado para streams >2000kbps | 23-04-2026 |

## Next Steps

- Verificar se `saida/clips/` precisa ser criada automaticamente no setup (já cria via `criar_pastas`)
- Considerar adicionar `--preset` arg ao `converter-fps.py` para preset H.265 direto (skip intermediate)
- Redimensionamento de imagens em lote (`redimensionar-imagens.py`) — identificado como gap mas não implementado

## Blockers

None
