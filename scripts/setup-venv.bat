@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
TITLE Media Tools - Setup Ambiente Virtual

REM Muda para o diretorio raiz do projeto
pushd "%~dp0\.."

echo ========================================================
echo      CONFIGURANDO AMBIENTE VIRTUAL (WINDOWS)
echo ========================================================
echo.

REM Verifica Python
set "PYTHON_CMD="
python --version >nul 2>&1
if errorlevel 1 (
    py --version >nul 2>&1
    if errorlevel 1 (
        echo [ERRO] Python nao encontrado!
        echo Instale: https://www.python.org/downloads/
        pause
        popd
        exit /b 1
    ) else (
        set "PYTHON_CMD=py"
    )
) else (
    set "PYTHON_CMD=python"
)

echo [OK] Python:
call %PYTHON_CMD% --version

REM Verifica se venv ja existe
if exist "venv" (
    echo.
    set /p RESPOSTA="Ambiente virtual existe. Recriar? (S/N): "
    if /i "!RESPOSTA!"=="S" (
        echo Removendo...
        rmdir /s /q venv
    ) else (
        goto :instalar
    )
)

REM Cria venv
echo.
echo Criando ambiente virtual...
call %PYTHON_CMD% -m venv venv
if errorlevel 1 (
    echo [ERRO] Falha ao criar ambiente virtual.
    pause
    popd
    exit /b 1
)

:instalar
REM Ativa e instala
echo.
echo Instalando dependencias...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet

REM Tenta instalar NumPy primeiro (Python 3.14 pode precisar de versao especifica)
echo.
echo [INFO] Instalando NumPy primeiro (Python 3.14 pode precisar de versao especifica)...
python -m pip install numpy --only-binary :all: --quiet 2>nul
if errorlevel 1 (
    echo [AVISO] NumPy nao encontrou wheel pre-compilada para Python 3.14.
    echo [AVISO] Tentando instalar versao mais recente disponivel (pode demorar)...
    python -m pip install numpy --upgrade --quiet
    if errorlevel 1 (
        echo [ERRO] Falha ao instalar NumPy.
        echo.
        echo [INFO] Python 3.14 e muito novo e nao tem wheels pre-compiladas do NumPy.
        echo [INFO] Solucoes:
        echo   1. Instale Visual Studio Build Tools: https://visualstudio.microsoft.com/downloads/
        echo   2. Use Python 3.11 ou 3.12 (melhor suporte de wheels)
        echo   3. Instale NumPy manualmente: pip install numpy
        pause
        popd
        exit /b 1
    )
)

REM Cria requirements temporario sem NumPy para evitar conflito
echo [INFO] Instalando demais dependencias...
findstr /v /i "^numpy" requirements.txt > requirements_temp.txt 2>nul
if exist requirements_temp.txt (
    pip install -r requirements_temp.txt
    del requirements_temp.txt
) else (
    REM Se findstr nao funcionar, tenta instalar tudo (NumPy ja esta instalado)
    pip install -r requirements.txt --no-deps
    pip install -r requirements.txt
)

if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao instalar algumas dependencias.
    echo [INFO] Tente instalar manualmente: pip install -r requirements.txt
    pause
    popd
    exit /b 1
)

echo.
echo ========================================================
echo      AMBIENTE VIRTUAL CONFIGURADO COM SUCESSO!
echo ========================================================
echo.
echo Para usar:
echo   venv\Scripts\activate.bat
echo   python otimizador-imagens.py
echo.
popd
pause
