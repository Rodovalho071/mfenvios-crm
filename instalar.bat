@echo off
echo Decodificando patch_mascara_moeda.py...
certutil -decode patch.b64 patch_mascara_moeda.py
if errorlevel 1 (
    echo ERRO ao decodificar!
    pause
    exit /b 1
)
echo Executando patch...
python patch_mascara_moeda.py
echo.
echo === Concluido! ===
echo Agora rode:
echo   git add -A ^&^& git commit -m "fix: mascara moeda" ^&^& git push origin main
pause
