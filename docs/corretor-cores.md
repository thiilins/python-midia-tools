# Corretor de Cores

## Descrição

Ferramenta para ajustar brilho, contraste, saturação e aplicar filtros artísticos em imagens. Ideal para correção automática de cores e aplicação de efeitos visuais.

## Funcionalidades

- ✅ **Ajuste automático**: Melhora brilho e contraste automaticamente
- ✅ **Ajustes manuais**: Controle fino de brilho, contraste e saturação
- ✅ **Filtros artísticos**: Sépia, preto e branco, vintage
- ✅ **Correção de olhos vermelhos**: Redução automática de olhos vermelhos
- ✅ **Processamento em lote**: Processa múltiplas imagens de uma vez
- ✅ **Barra de progresso**: Acompanhamento em tempo real

## Requisitos

- Python 3.6+
- Pillow (PIL)
- NumPy

## Uso

### Via Menu Interativo

Execute o script `start.bat` (Windows) ou `start.sh` (Linux/macOS) e selecione a opção **Corretor de Cores**.

### Via Linha de Comando

```bash
python corretor-cores.py
```

## Configuração

O script está configurado com os seguintes parâmetros padrão:

- **Ajuste automático**: Ativado
- **Brilho**: 1.0 (normal)
- **Contraste**: 1.0 (normal)
- **Saturação**: 1.0 (normal)
- **Filtro**: Nenhum

### Personalização

Para personalizar os parâmetros, edite o arquivo `corretor-cores.py`:

```python
corretor = CorretorCores(
    ajuste_automatico=True,    # True/False
    brilho=1.2,                # 0.5-2.0 (1.0 = normal)
    contraste=1.1,             # 0.5-2.0 (1.0 = normal)
    saturacao=1.3,             # 0.0-2.0 (1.0 = normal)
    filtro="sepia",            # None, "sepia", "bw", "vintage"
)
```

## Formatos Suportados

- JPG/JPEG
- PNG
- WebP
- BMP

## Pastas

- **Entrada**: `entrada/imagens/`
- **Saída**: `saida/corrigidas/`

## Exemplos

### Aplicar filtro sépia

```python
corretor = CorretorCores(filtro="sepia")
corretor.processar()
```

### Aumentar brilho e contraste

```python
corretor = CorretorCores(
    ajuste_automatico=False,
    brilho=1.3,
    contraste=1.2
)
corretor.processar()
```

### Preto e branco com alto contraste

```python
corretor = CorretorCores(
    filtro="bw",
    contraste=1.5
)
corretor.processar()
```

## Notas

- As imagens são salvas com qualidade 95% para manter alta fidelidade
- A correção de olhos vermelhos é aplicada automaticamente em todas as imagens
- O ajuste automático aumenta levemente brilho e contraste (10%)
- Filtros podem ser combinados com ajustes manuais

## Troubleshooting

**Problema**: Imagens ficam muito escuras/claras

- **Solução**: Ajuste o parâmetro `brilho` (valores entre 0.8-1.5 geralmente funcionam bem)

**Problema**: Cores ficam saturadas demais

- **Solução**: Reduza o parâmetro `saturacao` para valores entre 0.7-0.9

**Problema**: Filtro não aplica corretamente

- **Solução**: Verifique se a imagem está em modo RGB (conversão automática)
