---
tags: [claude-session, python-media-tools, personal, ffmpeg, hevc-amf, rtk, gpu-encoding]
date: 16-04-2026
topic: portrait-scale-fix-rtk-hook
keywords: portrait, scale filter, hevc_amf, bounds swap, rtk-hook, settings.json, d3d11va, vbr_peak
project: python-media-tools
org: personal
area: infra
impact: high
---

# Session: 16-04-2026 — Portrait Scale Fix + RTK Hook

> Projeto: [[python-media-tools/python-media-tools|python-media-tools]] · [[personal/_index|personal]]

## Quick Reference

**Keywords:** portrait video, scale bounds swap, hevc_amf, rtk-hook.py, PreToolUse hook, settings.json, 1080x1920, 720x1280
**Outcome:** Corrigido bug crítico de escala em vídeos portrait + configurado RTK global hook
**Impact:** high — 1198 vídeos processados com risco de escala errada (1080x1920 → 404x720 ao invés de 720x1280)

## Solutions & Fixes

### Portrait Scale Bug (compressor.py:401)
**Problema:** Preset `1280x720` (landscape bounds) aplicado a portrait 1080x1920 gerava 404x720.
**Causa:** `scale='min(1280,iw)':'min(720,ih)'` com `force_original_aspect_ratio=decrease` limitava pela altura 720px.
**Fix:** Detectar portrait (ih > iw) e trocar as bounds no Python antes de montar o filtro FFmpeg.

```python
# media_tools/video/compressor.py ~line 421
if altura_original > largura_original:
    largura_max, altura_max = altura_max, largura_max
```

Resultado: 1080x1920 com preset `1280x720` → bounds viram `720x1280` → saída correta 720x1280.

### RTK Global Hook
**Problema:** Queria prefixar automaticamente comandos como git, grep, ls, gh com `rtk`.
**Solução:** Script externo `C:/Users/thiil/.claude/rtk-hook.py` + PreToolUse hook em `settings.json`.

Inline Python no JSON era inviável (escaping de aspas). Script externo resolve:
```json
"hooks": {
  "PreToolUse": [{
    "matcher": "Bash",
    "hooks": [{"type": "command", "command": "python3 C:/Users/thiil/.claude/rtk-hook.py"}]
  }]
}
```

O script detecta o primeiro token do comando e adiciona `rtk ` se ainda não tiver.
RTK é binário local Rust (`/c/bin/rtk/rtk`) — não envia dados para lugar algum.

## Decisions Made

| Decisão | Racional |
|---------|---------|
| Swap bounds no Python (não no filtro FFmpeg) | Código mais limpo, sem expressão `if(gt(iw,ih),...)` no filtro |
| Script externo para RTK hook | JSON não suporta bem Python inline com aspas aninhadas |
| AMD (hevc_amf) como padrão do compressor | GPU RX 9060 XT confirmada no adapter 0 via d3d11va |
| vbr_peak > vbr_latency para AMF | Melhor qualidade com controle de bitrate máximo |

## Files Modified

| Arquivo | Mudança |
|---------|---------|
| `media_tools/video/compressor.py:401` | Swap de bounds para portrait antes de construir filtro |
| `C:/Users/thiil/.claude/rtk-hook.py` | Criado — script hook RTK para PreToolUse Bash |
| `C:/Users/thiil/.claude/settings.json` | Adicionado `hooks.PreToolUse` com comando externo RTK |

## Pending Tasks

- [ ] Fazer commit do fix portrait em `compressor.py`
- [ ] Abrir `/hooks` no Claude Code para recarregar settings.json (watcher não detecta mudanças em sessão ativa)
- [ ] Testar hook RTK após reload — confirmar que `git status` vira `rtk git status` automaticamente

---

## Quick Resume Context

Fix de portrait aplicado em `_construir_filtro_resolucao()` (`compressor.py:421`): quando `altura_original > largura_original`, as bounds `largura_max` e `altura_max` são trocadas antes de montar o filtro. RTK hook criado em `C:/Users/thiil/.claude/rtk-hook.py` e registrado em `settings.json` como PreToolUse Bash — requer `/hooks` reload para ativar. Commit do fix portrait ainda pendente. AMD GPU (hevc_amf, adapter 0 = RX 9060 XT) já é o padrão do compressor.

Related: [[python-media-tools/python-media-tools|python-media-tools]]

---

## Raw Session Log

- Continuação de sessão anterior sobre GPU AMD RX 9060 XT
- Portrait bug: 1080x1920 → 404x720 (errado) em vez de 720x1280
- Fix: swap bounds em Python detectando portrait pela comparação ih > iw
- RTK hook: tentativa inline JSON falhou por escaping; solução com script externo
- Usuário perguntou se RTK é seguro — confirmado que é binário local Rust sem rede
- Usuário pediu "volte ao sonnet" — modelo já estava em sonnet, não foi alterado
