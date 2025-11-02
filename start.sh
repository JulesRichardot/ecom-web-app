#!/bin/bash

echo "🛍️  E-Shop - Site E-commerce Moderne"
echo "================================================"
echo ""
echo "📦 Installation des dépendances..."
pip3 install -r requirements.txt
echo ""
echo "🚀 Démarrage du serveur..."
echo "📍 URL: http://localhost:5000"
echo "👤 Client: client@shop.test / secret"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter le serveur"
echo ""
python3 app.py
