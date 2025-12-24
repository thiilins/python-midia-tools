@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
TITLE Media Tools - Canivete Suico de Midia

REM Muda para o diretorio raiz do projeto
pushd "%~dp0\.."

echo ========================================================
echo      MEDIA TOOLS - VERIFICACAO DE AMBIENTE
echo ========================================================
echo.

set "NEED_RESTART=0"
set "PYTHON_CMD="

REM --- 1. VERIFICAR PYTHON ---
python --version >nul 2>&1
if errorlevel 1 (
    py --version >nul 2>&1
    if errorlevel 1 (
        echo [X] Python nao encontrado!
        winget --version >nul 2>&1
        if errorlevel 1 (
            echo [ERRO] Instale Python manualmente: https://www.python.org/downloads/
            pause
            popd
            exit /b 1
        )
        echo Instalando Python via Winget...
        winget install -e --id Python.Python.3 --accept-package-agreements --accept-source-agreements
        if errorlevel 1 (
            echo [ERRO] Falha ao instalar Python. Instale manualmente.
            pause
            popd
            exit /b 1
        )
        echo [OK] Python instalado. Reinicie o script.
        pause
        popd
        exit /b 0
    ) else (
        set "PYTHON_CMD=py"
    )
) else (
    set "PYTHON_CMD=python"
)

REM --- 2. VERIFICAR PIP ---
call %PYTHON_CMD% -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [X] pip nao encontrado. Instalando...
    call %PYTHON_CMD% -m ensurepip --upgrade
    if errorlevel 1 (
        echo [ERRO] Falha ao instalar pip.
        pause
        popd
        exit /b 1
    )
)

REM --- 3. VERIFICAR DEPENDENCIAS ---
echo Verificando dependencias...
call %PYTHON_CMD% -c "import tqdm, PIL, cv2, numpy" >nul 2>&1
if errorlevel 1 (
    echo [X] Instalando dependencias...
    call %PYTHON_CMD% -m pip install -r requirements.txt --quiet
    if errorlevel 1 (
        echo [ERRO] Falha ao instalar dependencias.
        pause
        popd
        exit /b 1
    )
)

REM --- 4. VERIFICAR FFMPEG ---
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo [AVISO] FFmpeg nao encontrado (necessario apenas para videos).
    winget --version >nul 2>&1
    if not errorlevel 1 (
        echo Tentando instalar FFmpeg...
        winget install -e --id Gyan.FFmpeg --accept-package-agreements --accept-source-agreements
    )
)

REM --- 5. MENU ---
cls
echo ========================================================
echo      MEDIA TOOLS - CANIVETE SUICO DE MIDIA
echo ========================================================
echo.
echo   IMAGENS:
echo   1. Otimizar Imagens
echo   2. Validar Imagens
echo   3. Converter WebP para JPG
echo   4. Detectar Duplicatas de Imagens
echo   5. OCR de Imagens
echo   6. Remover Fundo de Imagens
echo   7. Corretor de Cores e Filtros
echo   8. Gerar Thumbnails
echo.
echo   VIDEOS:
echo   9. Otimizar Videos
echo   10. Converter WebM para MP4
echo   11. Extrair Audio de Videos
echo   12. Extrair Thumbnails de Videos
echo   13. Merge Videos
echo   14. Estabilizador de Video
echo   15. Detectar Duplicatas de Videos
echo.
echo   0. Sair
echo.
set /p OPCAO="Digite o numero da opcao: "

set "SCRIPTS[1]=otimizador-imagens.py"
set "SCRIPTS[2]=validate-images.py"
set "SCRIPTS[3]=webp-to-jpg.py"
set "SCRIPTS[4]=detector-duplicatas-imagens.py"
set "SCRIPTS[5]=ocr-imagens.py"
set "SCRIPTS[6]=remover-fundo.py"
set "SCRIPTS[7]=corretor-cores.py"
set "SCRIPTS[8]=gerador-thumbnails.py"
set "SCRIPTS[9]=otimizador-video.py"
set "SCRIPTS[10]=webm-mp4.py"
set "SCRIPTS[11]=extrair-audio.py"
set "SCRIPTS[12]=extrair-thumbnails.py"
set "SCRIPTS[13]=merge-videos.py"
set "SCRIPTS[14]=estabilizador-video.py"
set "SCRIPTS[15]=detector-duplicatas-videos.py"

if "%OPCAO%"=="0" (
    popd
    exit /b 0
)

set "SCRIPT=!SCRIPTS[%OPCAO%]!"
if not defined SCRIPT (
    echo [ERRO] Opcao invalida.
    pause
    popd
    exit /b 1
)

echo.
echo [V] Iniciando !SCRIPT!...
echo --------------------------------------------------------
call %PYTHON_CMD% !SCRIPT!
if errorlevel 1 (
    echo.
    echo [ERRO] Script retornou codigo de erro.
)
echo.
popd
pause
