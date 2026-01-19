@echo off
echo ========================================
echo    Build do Sistema de Reservas
echo ========================================
echo.

echo Limpando builds anteriores...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del "*.spec"

echo.
echo Combinando icones...
python combinar_icones.py

echo.
echo Instalando dependencias...
pip install pyinstaller
pip install tkcalendar
pip install mysql-connector-python
pip install pillow

echo.
echo Criando executavel...
pyinstaller --onedir --noconsole --icon=resources/icone_completo.ico --add-data "resources;resources" --exclude-module pkg_resources --exclude-module setuptools --name "Reservas de Salas" sala_reservas.py

echo.
echo ========================================
echo    Build concluido!
echo ========================================
echo.
echo O executavel foi criado em: dist\Reservas de Salas.exe
echo.
echo Para atualizar o cache de icones do Windows:
echo Execute o arquivo atualizar_icones.bat
echo.
pause 
