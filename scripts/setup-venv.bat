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
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias.
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
