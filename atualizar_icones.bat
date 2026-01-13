@echo off
echo ========================================
echo    Atualizando Cache de Icones
echo ========================================
echo.

echo Parando o Explorer...
taskkill /f /im explorer.exe

echo.
echo Aguardando 3 segundos...
timeout /t 3 /nobreak >nul

echo.
echo Iniciando o Explorer novamente...
start explorer.exe

echo.
echo ========================================
echo    Cache de icones atualizado!
echo ========================================
echo.
echo Agora o icone do executavel deve aparecer
echo corretamente na area de trabalho.
echo.
pause 