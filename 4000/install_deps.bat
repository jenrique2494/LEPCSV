@echo off
echo 🚀 Instalando dependencias para Clasificador CEFR Local
echo.

echo 📦 Instalando paquetes de Python...
pip install cefrpy spacy transformers torch numpy pandas

echo.
echo 📥 Descargando modelo de spaCy...
python -m spacy download en_core_web_sm

echo.
echo ✅ Verificando instalación...
python -c "import cefrpy, spacy, transformers, torch; print('✅ Todas las dependencias instaladas correctamente')"

echo.
echo 🎉 ¡Instalación completada!
echo 🚀 Puedes ejecutar: python cerf_local.py
echo.
pause
