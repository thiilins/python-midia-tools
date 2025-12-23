# Conversor WebP para JPG

## Descrição

Ferramenta para converter imagens WebP para JPG com alta qualidade. Suporta WebP estático e animado (converte animações para GIF).

## Funcionalidades

- ✅ **Conversão de alta qualidade**: Converte WebP para JPG mantendo qualidade
- ✅ **Suporte a animações**: Detecta e converte WebP animado para GIF
- ✅ **Análise de qualidade**: Analisa resolução e recomenda qualidade JPG
- ✅ **Tratamento de transparência**: Converte transparência para fundo branco
- ✅ **Processamento em lote**: Processa múltiplas imagens de uma vez
- ✅ **Barra de progresso**: Acompanhamento em tempo real

## Requisitos

- Python 3.6+
- Pillow (PIL)

## Uso

### Via Menu Interativo

Execute o script `start.bat` (Windows) ou `start.sh` (Linux/macOS) e selecione a opção **Converter WebP → JPG**.

### Via Linha de Comando

```bash
python webp-to-jpg.py
```

## Configuração

O script está configurado com os seguintes parâmetros padrão:

- **Qualidade**: 100% (máxima)
- **Apagar original**: Sim
- **Preservar qualidade**: Sim (analisa e ajusta)
- **Suporte a animações**: Sim

### Personalização

Para personalizar os parâmetros, edite o arquivo `webp-to-jpg.py`:

```python
conversor = ConversorWebP(
    qualidade=100,              # 0-100 (maior = melhor qualidade)
    apagar_original=True,       # True/False
    preservar_qualidade=True,   # True/False (analisa e ajusta)
    suporte_animacoes=True      # True/False
)
```

## Formatos Suportados

- **Entrada**: WebP (estático e animado)
- **Saída**: JPG (estático) ou GIF (animado)

## Pastas

- **Entrada**: `entrada/imagens/`
- **Saída**: `saida/imagens/`

## Como Funciona

### WebP Estático

1. Detecta se é animado ou estático
2. Analisa qualidade e resolução (se `preservar_qualidade=True`)
3. Converte transparência para fundo branco (se necessário)
4. Converte para JPG com qualidade otimizada
5. Apaga original (se `apagar_original=True`)

### WebP Animado

1. Detecta se é animado
2. Extrai todos os frames
3. Converte para GIF mantendo duração e loop
4. Salva como GIF

## Análise de Qualidade

Quando `preservar_qualidade=True`, o script:
- Analisa resolução (megapixels)
- Recomenda qualidade JPG baseada no tamanho
- Imagens grandes (>10MP): qualidade 95%
- Imagens médias (5-10MP): qualidade 90%
- Imagens pequenas (<5MP): qualidade 100%

## Exemplos

### Converter WebP (padrão)

```bash
python webp-to-jpg.py
```

### Personalizar qualidade (editar código)

```python
# Qualidade média, manter original
conversor = ConversorWebP(
    qualidade=85,
    apagar_original=False
)
```

## Notas

- WebP com transparência é convertido para JPG com fundo branco
- WebP animado é convertido para GIF (não JPG)
- A análise de qualidade ajusta automaticamente a qualidade JPG
- Arquivos originais são apagados por padrão após conversão bem-sucedida

## Troubleshooting

**Problema**: Erro "PIL não encontrado"
- **Solução**: Instale Pillow: `pip install Pillow`

**Problema**: WebP animado não converte
- **Solução**: WebP animado é convertido para GIF, não JPG. Isso é esperado.

**Problema**: Qualidade baixa
- **Solução**: Aumente a qualidade (ex: 95 ou 100) ou desative `preservar_qualidade`

**Problema**: Transparência vira fundo preto
- **Solução**: O script converte transparência para fundo branco. Se precisar de transparência, mantenha como PNG.

**Problema**: Arquivo muito grande
- **Solução**: Reduza a qualidade (ex: 85 ou 90) ou ative `preservar_qualidade=True` para análise automática

