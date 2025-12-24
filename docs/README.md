# Documentação - Media Tools

Bem-vindo à documentação completa do projeto Media Tools!

## 📚 Índice da Documentação

### Documentos Principais

1. **[CHANGELOG.md](CHANGELOG.md)** - Histórico completo de mudanças, melhorias e novas funcionalidades
   - Todas as melhorias implementadas nos scripts existentes
   - Novos scripts criados
   - Detalhes técnicos de cada implementação

2. **[RESUMO_IMPLEMENTACAO.md](RESUMO_IMPLEMENTACAO.md)** - Resumo executivo da implementação
   - Visão geral de todas as funcionalidades
   - Estatísticas do projeto
   - Lista completa de scripts e módulos

3. **[ESTRUTURA_PROJETO.md](ESTRUTURA_PROJETO.md)** - Estrutura completa do projeto
   - Organização de diretórios
   - Mapeamento de scripts e módulos
   - Estrutura de pastas de entrada/saída

## 🎯 Documentação por Ferramenta

### 📸 Processamento de Imagens

1. **[Otimizador de Imagens](otimizador-imagens.md)**
   - Otimiza JPG, PNG, WebP, AVIF, HEIC
   - Preserva metadados EXIF
   - Compressão inteligente

2. **[Conversor WebP → JPG](webp-to-jpg.md)**
   - Converte WebP estático e animado
   - Análise de qualidade automática
   - Tratamento de transparência

3. **[Validador de Imagens](validate-images.md)**
   - Analisa legibilidade (escuridão, foco, bordas)
   - Separação automática (legíveis/ilegíveis)
   - Relatório HTML opcional

4. **[OCR de Imagens](ocr-imagens.md)**
   - Detecção de texto usando Tesseract
   - Suporte a português e inglês
   - Separação automática (com/sem texto)

5. **[Detector de Duplicatas de Imagens](detector-duplicatas-imagens.md)**
   - Detecta imagens idênticas (hash MD5)
   - Remoção automática opcional
   - Relatório detalhado

6. **[Removedor de Fundo](remover-fundo.md)**
   - Remoção automática usando IA
   - Gera PNG com transparência
   - Processamento em lote

7. **[Corretor de Cores](corretor-cores.md)**
   - Ajuste de brilho, contraste, saturação
   - Filtros artísticos (sépia, preto e branco, vintage)
   - Correção automática de olhos vermelhos

8. **[Gerador de Thumbnails](gerador-thumbnails.md)**
   - Gera thumbnails de imagens e vídeos
   - Múltiplos tamanhos configuráveis
   - Otimização de qualidade

### 🎬 Processamento de Vídeos

9. **[Otimizador de Vídeos](otimizador-video.md)**
   - Compressão H.264 com CRF
   - Detecção de vídeos já otimizados
   - Processamento paralelo

10. **[Conversor WebM → MP4](webm-mp4.md)**
    - Conversão com correções automáticas
    - Detecção de problemas (VFR, timestamps)
    - Perfis pré-configurados (web, mobile, archive)

11. **[Extrator de Áudio](extrair-audio.md)**
    - Extrai áudio em MP3, AAC, OGG, WAV
    - Controle de qualidade (bitrate)
    - Preservação de qualidade

12. **[Extrator de Thumbnails](extrair-thumbnails.md)**
    - Extrai múltiplas thumbnails por vídeo
    - Distribuição inteligente ao longo do vídeo
    - Tamanho configurável

13. **[Merge de Vídeos](merge-videos.md)**
    - Concatena múltiplos vídeos
    - Modo copy (sem re-encodar)
    - Ordenação automática

14. **[Estabilizador de Vídeo](estabilizador-video.md)**
    - Estabiliza vídeos tremidos
    - Correção de rotação automática
    - Análise de movimento avançada

15. **[Detector de Duplicatas de Vídeos](detector-duplicatas-videos.md)**
    - Detecta vídeos idênticos (hash MD5 de amostras)
    - Otimizado para vídeos grandes
    - Remoção automática opcional

16. **[Corretor de Vídeos](corretor-video.md)**
    - Corrige problemas de framerate (VFR)
    - Corrige problemas com timestamps
    - Corrige dessincronia de áudio
    - Focado em correções técnicas (sem otimização)

## 📖 Como Usar Esta Documentação

1. **Começando**: Leia o [README.md](../README.md) principal
2. **Histórico**: Consulte [CHANGELOG.md](CHANGELOG.md) para ver o que mudou
3. **Detalhes**: Veja [RESUMO_IMPLEMENTACAO.md](RESUMO_IMPLEMENTACAO.md) para funcionalidades específicas
4. **Estrutura**: Use [ESTRUTURA_PROJETO.md](ESTRUTURA_PROJETO.md) para entender a organização

## 🔗 Links Úteis

- [README Principal](../README.md) - Guia de instalação e uso
- [Requirements.txt](../requirements.txt) - Dependências do projeto
- [Scripts](../scripts/) - Scripts de inicialização

---

**Última atualização**: Veja [CHANGELOG.md](CHANGELOG.md) para informações sobre versões e atualizações.


