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

- **CRF**: 23 (qualidade boa, compressão média)
- **Preset**: medium (velocidade vs compressão)
- **Deletar originais**: Sim (após otimização bem-sucedida)

### Personalização

Para personalizar os parâmetros, edite o arquivo `otimizador-video.py`:

```python
otimizador = OtimizadorVideo(
    crf="23",           # 18-28 (menor = melhor qualidade, maior arquivo)
    preset="medium"     # ultrafast, fast, medium, slow, veryslow
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

### Otimizar vídeos (padrão)

```bash
python otimizador-video.py
```

### Personalizar qualidade (editar código)

```python
# Alta qualidade
otimizador = OtimizadorVideo(crf="18", preset="slow")

# Compressão máxima
otimizador = OtimizadorVideo(crf="28", preset="veryslow")

# Rápido, qualidade média
otimizador = OtimizadorVideo(crf="23", preset="fast")
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
