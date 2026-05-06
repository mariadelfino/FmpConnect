@echo off
TITLE Rodando o Projeto Python
setlocal

REM 
ECHO "Configurando e iniciando o projeto..."
ECHO.

REM 
py -3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py -3
) else (
    REM 
    python --version >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=python
    ) else (
        ECHO ============================================================
        ECHO ERRO: Python nao encontrado no PATH!
        ECHO ============================================================
        ECHO.
        ECHO Python instalado via Microsoft Store nao e compativel.
        ECHO Instale do site https://www.python.org/downloads/ 
        ECHO.
        ECHO e marque [x] Add Python to PATH.
        ECHO.
        ECHO Execute este script novamente apos a instalacao.
        ECHO ============================================================
        ECHO.
        pause
        exit /b
    )
)

ECHO "Usando o comando: %PYTHON_CMD%"

if not exist .venv (
    ECHO "Criando ambiente virtual (.venv)..."
    %PYTHON_CMD% -m venv .venv
)

ECHO "Ativando ambiente..."
call .venv\Scripts\activate.bat

ECHO "Instalando dependencias do requirements.txt (isso pode levar um minuto)..."
ECHO "--------------------------------------------------------------------------"
pip install -r requirements.txt
ECHO "--------------------------------------------------------------------------"
ECHO "Instalacao concluida."
ECHO.
ECHO.

REM 
ECHO ******************************************************
ECHO.
ECHO    SERVIDOR PRONTO E RODANDO!
ECHO.
ECHO    Acesse no seu navegador: http://127.0.0.1:5000
ECHO.
ECHO ******************************************************
ECHO.
ECHO (Pressione CTRL+C neste terminal para parar o servidor)
ECHO.

REM 
python app.py

REM 
