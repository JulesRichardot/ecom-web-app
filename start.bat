@echo off
echo 🛍️  E-Shop - Site E-commerce Moderne
echo ================================================
echo.
echo 📦 Installation des dépendances...
pip install -r requirements.txt
echo.
echo 🚀 Démarrage du serveur...
echo 📍 URL: http://localhost:5000
echo 👤 Client: client@shop.test / Secret123!
echo.
echo Appuyez sur Ctrl+C pour arrêter le serveur
echo.
python app.py
pause
