@echo off
chcp 65001 >nul
echo =====================================================
echo   GymSystem — Build completo
echo =====================================================
 
:: 1) Limpiar builds anteriores
echo [1/3] Limpiando dist\ y build\ anteriores...
if exist dist   rmdir /s /q dist
if exist build  rmdir /s /q build
if exist installer_output rmdir /s /q installer_output
 
:: 2) PyInstaller
echo [2/3] Empaquetando con PyInstaller...
pyinstaller GymSystem.spec
if errorlevel 1 (
    echo ERROR: PyInstaller fallo. Revisa el log anterior.
    pause
    exit /b 1
)
 
:: 3) Inno Setup (ajusta la ruta si lo tienes en otro lugar)
echo [3/3] Creando instalador con Inno Setup...
set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist %ISCC% set ISCC="C:\Program Files\Inno Setup 6\ISCC.exe"
 
%ISCC% GymSystem.iss
if errorlevel 1 (
    echo ERROR: Inno Setup fallo.
    pause
    exit /b 1
)
 
echo.
echo =====================================================
echo   Listo!  installer_output\GymSystem_Installer.exe
echo =====================================================
pause