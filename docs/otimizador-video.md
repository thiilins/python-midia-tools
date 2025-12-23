# Otimizador de Vídeos

## Descrição

Ferramenta para otimizar vídeos MP4, M4V e MOV reduzindo tamanho mantendo qualidade visual. Utiliza codec H.264 com CRF (Constant Rate Factor) para compressão eficiente.

## Funcionalidades

- ✅ **Otimização inteligente**: Reduz tamanho mantendo qualidade
- ✅ **Codec H.264**: Compatibilidade universal
- ✅ **Detecção de otimização**: Pula vídeos já otimizados
- ✅ **Processamento paralelo**: Processa até 2 vídeos simultaneamente
- ✅ **Informações detalhadas**: Mostra codec, bitrate, resolução antes/depois
- ✅ **Barra de progresso**: Acompanhamento em tempo real

## Requisitos

- Python 3.6+
- FFmpeg
- FFprobe

## Uso

### Via Menu Interativo

Execute o script `start.bat` (Windows) ou `start.sh` (Linux/macOS) e selecione a opção **Otimizar Vídeos**.

### Via Linha de Comando

```bash
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

| Preset | CRF | Preset FFmpeg | Descrição |
|--------|-----|---------------|-----------|
| **ultra_fast** | 28 | ultrafast | Muito rápido, menor qualidade (compressão máxima) |
| **fast** | 26 | fast | Rápido, qualidade média-baixa |
| **medium** | 23 | medium | Balanceado, qualidade boa (padrão) |
| **high_quality** | 20 | slow | Alta qualidade, mais lento |
| **maximum** | 18 | veryslow | Máxima qualidade, muito lento |

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
2. Verifica se já está otimizado
3. Se não, otimiza usando H.264 com CRF
4. Mostra informações antes/depois
5. Deleta original se solicitado

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

### Personalizar qualidade (editar código)

```python
# Usando preset
otimizador = OtimizadorVideo(preset_nome="high_quality")

# Ou parâmetros individuais
otimizador = OtimizadorVideo(crf="18", preset="slow")
```

## Notas

- ⚠️ **Atenção**: Com `deletar_originais=True`, os arquivos originais são **permanentemente deletados** após otimização
- Vídeos já otimizados são automaticamente pulados
- Processamento paralelo limitado a 2 vídeos simultaneamente
- O script mostra informações detalhadas de cada vídeo

## Troubleshooting

**Problema**: Erro "FFmpeg não encontrado"

- **Solução**: Instale FFmpeg e verifique se está no PATH

**Problema**: Vídeo não otimizado (já otimizado)

- **Solução**: Normal - vídeos já otimizados são pulados automaticamente

**Problema**: Processamento muito lento

- **Solução**: Use preset mais rápido (ex: "fast" ou "ultrafast")

**Problema**: Qualidade baixa

- **Solução**: Reduza o CRF (ex: "20" ou "18") e use preset "slow"

**Problema**: Arquivo muito grande

- **Solução**: Aumente o CRF (ex: "26" ou "28") para maior compressão
