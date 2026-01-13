@echo off
echo ========================================
echo    Corrigindo Icone do Executavel
echo ========================================
echo.

echo Verificando se o executavel existe...
if not exist "dist\Reservas de Salas.exe" (
    echo ERRO: Executavel nao encontrado!
    echo Execute primeiro o build_exe.bat
    pause
    exit /b 1
)

echo.
echo Limpando cache de icones do Windows...
ie4uinit.exe -show
ie4uinit.exe -ClearIconCache
ie4uinit.exe -show

echo.
echo Parando o Explorer...
taskkill /f /im explorer.exe /t >nul 2>&1

echo.
echo Aguardando 3 segundos...
timeout /t 3 /nobreak >nul

echo.
echo Iniciando o Explorer novamente...
start explorer.exe

echo.
echo ========================================
echo    Processo concluido!
echo ========================================
echo.
echo Se o icone ainda nao aparecer:
echo 1. Clique com botao direito no executavel
echo 2. Selecione "Propriedades"
echo 3. Clique em "Alterar icone"
echo 4. Navegue ate a pasta resources
echo 5. Selecione icone.reservas.ico
echo.
pause 