#!/usr/bin/env python3
"""
Script de démarrage rapide pour E-Shop
"""

import subprocess
import sys
import os

def check_python_version():
    """Vérifier que Python 3.8+ est installé"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 ou supérieur est requis")
        print(f"Version actuelle: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} détecté")
    return True

def install_requirements():
    """Installer les dépendances"""
    print("📦 Installation des dépendances...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dépendances installées avec succès")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erreur lors de l'installation des dépendances")
        return False

def start_server():
    """Démarrer le serveur Flask"""
    print("🚀 Démarrage du serveur E-Shop...")
    print("📍 URL: http://localhost:5000")
    print("👤 Client: client@shop.test / secret")
    print("👨‍💼 Admin: admin@shop.test / admin")
    print("\nAppuyez sur Ctrl+C pour arrêter le serveur")
    
    try:
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Arrêt du serveur")

def main():
    """Fonction principale"""
    print("🛍️  E-Shop - Site E-commerce Moderne")
    print("=" * 50)
    
    # Vérifier Python
    if not check_python_version():
        sys.exit(1)
    
    # Installer les dépendances
    if not install_requirements():
        sys.exit(1)
    
    # Démarrer le serveur
    start_server()

if __name__ == "__main__":
    main()
