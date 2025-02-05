@echo off
setlocal

:: Obtém o caminho da pasta atual
set "currentDir=%cd%"

:: Verifica se o script está sendo executado como administrador
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    :: Se não estiver, solicita elevação
    powershell -Command "Start-Process cmd -ArgumentList '/s,/c,cd \"%currentDir%\" & start cmd' -Verb RunAs"
) else (
    :: Se já estiver como administrador, apenas abre o CMD na pasta atual
    cd /d "%currentDir%"
    start cmd
)

endlocal