@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
TITLE Media Tools - Setup Ambiente Virtual

:: Muda para o diretório raiz do projeto
cd /d "%~dp0\.."

echo ========================================================
echo      CONFIGURANDO AMBIENTE VIRTUAL (WINDOWS)
echo ========================================================
echo.

:: Verifica Python
python --version >nul 2>&1
if errorlevel 1 (
    py --version >nul 2>&1
    if errorlevel 1 (
        echo [ERRO] Python nao encontrado!
        echo Instale: https://www.python.org/downloads/
        pause
        exit /b 1
    ) else (
        set "PYTHON_CMD=py"
    )
) else (
    set "PYTHON_CMD=python"
)

echo [OK] Python:
%PYTHON_CMD% --version

:: Verifica se venv já existe
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

:: Cria venv
echo.
echo Criando ambiente virtual...
%PYTHON_CMD% -m venv venv
if errorlevel 1 (
    echo [ERRO] Falha ao criar ambiente virtual.
    pause
    exit /b 1
)

:instalar
:: Ativa e instala
echo.
echo Instalando dependencias...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias.
    pause
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
pause
