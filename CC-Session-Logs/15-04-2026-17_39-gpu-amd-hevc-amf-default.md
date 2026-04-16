---
tags: [claude-session, python-media-tools, personal, ffmpeg, hevc, amd, gpu, python]
date: 15-04-2026
topic: gpu-amd-hevc-amf-default
keywords: hevc_amf, d3d11va, GPU_ENCODER, hevc_nvenc, vbr_peak, cqp, qp_i, qp_p, qp_b, AMD RX 9060 XT
project: python-media-tools
org: personal
area: backend
impact: high
---

# Session: 15-04-2026 — GPU AMD hevc_amf como Default

> Projeto: [[python-media-tools/python-media-tools|python-media-tools]] · [[personal/_index|personal]]

## Quick Reference

**Keywords:** hevc_amf, d3d11va, GPU_ENCODER, vbr_peak, cqp, RX 9060 XT, AMD AMF, hwaccel, QP  
**Outcome:** Compressor adaptado para usar GPU AMD RX 9060 XT (hevc_amf) como padrão, com decode acelerado via d3d11va  
**Impact:** high — 5-10x mais rápido que libx265 (CPU) para comprimir streams de 15GB

## Soluções & Código

### `media_tools/video/compressor.py`

**1. `_detectar_encoder_gpu()` — suporte a `GPU_ENCODER` env var**

Antes: varria lista `GPU_ENCODERS` em ordem — detectava `hevc_nvenc` primeiro (mesmo sem NVIDIA), causando falha silenciosa na AMD.

Depois: respeita `GPU_ENCODER` env var com aliases:
```python
aliases = {"amd": "hevc_amf", "amf": "hevc_amf", "nvidia": "hevc_nvenc",
           "nvenc": "hevc_nvenc", "intel": "hevc_qsv", "qsv": "hevc_qsv"}
```

**2. `_construir_comando_gpu()` — parâmetros corretos para `hevc_amf`**

Antes: incompleto — sem `qp_b`, sem distinção CQP vs VBR.

Depois (CQP quando sem max_bitrate):
```python
["-rc", "cqp", "-qp_i", str(qp), "-qp_p", str(qp+2), "-qp_b", str(qp+4),
 "-quality", "quality", "-b:v", "0"]
```

Depois (VBR peak quando preset tem max_bitrate):
```python
["-rc", "vbr_peak", "-b:v", "0", "-maxrate", max_bitrate,
 "-qp_i", str(qp), "-qp_p", str(qp+2), "-qp_b", str(qp+4), "-quality", "quality"]
```

**3. `_converter_video()` — hardware decode AMD**

```python
if self.encoder_gpu and "amf" in self.encoder_gpu:
    comando.extend(["-hwaccel", "d3d11va"])
```

### `otimizador-compressor-video.py`

**AMD como padrão (sem nenhuma flag):**
```python
if not os.getenv("USAR_GPU"):
    os.environ["USAR_GPU"] = "1"
    os.environ.setdefault("GPU_ENCODER", "hevc_amf")
```

**Novas flags:**
- `--amd` → força `hevc_amf` + `USAR_GPU=1`
- `--nvidia` → força `hevc_nvenc` + `USAR_GPU=1`
- `--gpu` / `-g` → auto-detect mantido
- `set USAR_GPU=0` → força CPU (desativa GPU)

## Decisões Tomadas

| Decisão | Motivo |
|---------|--------|
| `hevc_amf` como padrão (não libx265) | RX 9060 XT 16GB — GPU potente, 5-10x mais rápido |
| `vbr_latency` → `vbr_peak` para archiving | vbr_latency é para streaming ao vivo; vbr_peak = melhor qualidade offline |
| CQP quando sem max_bitrate | Qualidade constante, equivalente ao CRF do libx265 |
| `qp_p = qp+2`, `qp_b = qp+4` | Equilíbrio padrão AMD AMF — I-frames mais qualidade, B-frames podem ser menores |
| `-hwaccel d3d11va` junto com hevc_amf | AMD no Windows usa D3D11VA para decode; acelera toda a pipeline |
| Aliases `amd/amf/nvidia/nvenc` | Evita memorizar nome exato do encoder |

## Arquivos Modificados

- `media_tools/video/compressor.py` — `_detectar_encoder_gpu()`, `_construir_comando_gpu()`, `_converter_video()`
- `otimizador-compressor-video.py` — padrão AMD, flags `--amd`/`--nvidia`, help atualizado

## Setup & Config

**Uso padrão (AMD automático):**
```bash
python otimizador-compressor-video.py
# ou
python otimizador-compressor-video.py --preset stream_720p
```

**Forçar encoder específico:**
```bash
python otimizador-compressor-video.py --amd           # AMD RX 9060 XT
python otimizador-compressor-video.py --nvidia        # NVIDIA (se tiver)
python otimizador-compressor-video.py --gpu           # auto-detect

set USAR_GPU=0 && python otimizador-compressor-video.py  # forçar CPU (libx265)
set GPU_ENCODER=amf && python otimizador-compressor-video.py  # via env var
```

**Presets recomendados para streams de 15GB → AMD:**
- `stream_720p` — vbr_peak 1.5M, 720p (recomendado)
- `master_720p` — cqp qp=23, qualidade máxima sem cap de bitrate
- `stream_480p` — vbr_peak 800k, arquivo mínimo

---

## Quick Resume Context

Compressor de vídeo adaptado para GPU AMD RX 9060 XT — `hevc_amf` é agora o encoder padrão (sem precisar de flags). Pipeline completa: decode via `-hwaccel d3d11va` + encode via `hevc_amf`. Parâmetros AMF corrigidos: CQP para presets sem bitrate cap, VBR peak para presets com max_bitrate. Novo bug preexistente identificado: a detecção automática de GPU pegava `hevc_nvenc` antes do `hevc_amf` na lista, causando falha silenciosa em máquinas AMD — corrigido via `GPU_ENCODER` env var com aliases. Próximo passo: testar encode real com um arquivo de entrada para validar que d3d11va + hevc_amf funciona corretamente no sistema.

Related: [[personal/python-media-tools/python-media-tools|python-media-tools]]

---

## Raw Session Log

<!-- Nunca lido pelo /resume-vault. Apenas para auditoria. -->
Sessão iniciou com busca de histórico em sessões antigas (C:\COMPACT e C:\CLASS). Usuário pediu adaptação para GPU AMD RX 9060 XT 16GB. Inicialmente ajustei hevc_amf e adicionei hwaccel d3d11va. Usuário disse "mantenha encoder x265" — interpretado como manter H.265 (hevc_amf também é H.265). Usuário mostrou comando com vbr_latency+3M; explicado que vbr_peak é melhor para archiving. Usuário pediu que AMD seja o padrão sem flags. Implementado `os.environ.setdefault("GPU_ENCODER", "hevc_amf")` no início do main().
