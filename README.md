# 🛍️ E-Shop - Application E-Commerce

Application web e-commerce complète développée avec Flask, permettant la gestion d'un catalogue de produits, d'un panier d'achat, de commandes et d'un système de support client.

## 📋 Table des matières

- [À propos](#-à-propos)
- [Fonctionnalités](#-fonctionnalités)
- [Technologies](#-technologies)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [Tests](#-tests)
- [Sécurité](#-sécurité)
- [Structure du projet](#-structure-du-projet)
- [Développement](#-développement)
- [CI/CD](#-cicd)
- [Contexte pédagogique](#-contexte-pédagogique)

## 🎯 À propos

Ce projet a été développé dans le cadre d'un cours universitaire sur la **Qualité de développement**. Il démontre l'application des bonnes pratiques de développement logiciel, incluant :

- Architecture modulaire et séparation des responsabilités
- Tests automatisés (unitaires et fonctionnels)
- Intégration continue (CI/CD)
- Standards de code et linters
- Documentation complète
- Gestion de version avec Git
- Pratiques de sécurité

## ✨ Fonctionnalités

### 👤 Espace Utilisateur

- **Catalogue de produits**
  - Affichage de tous les produits disponibles
  - Recherche en temps réel par nom ou description
  - Filtrage par catégorie (Homme / Femme)
  - Pages détaillées pour chaque produit

- **Panier d'achat**
  - Ajout/suppression de produits
  - Gestion des quantités
  - Mise à jour en temps réel (AJAX)
  - Calcul automatique du total

- **Authentification**
  - Inscription avec validation de force du mot de passe
  - Connexion sécurisée
  - Gestion de session

- **Gestion du profil**
  - Modification des informations personnelles
  - Changement d'email avec confirmation
  - Changement de mot de passe sécurisé
  - Validation complète des champs

- **Commandes**
  - Passage de commande depuis le panier
  - Formulaire de paiement sécurisé
  - Validation de carte bancaire (algorithme de Luhn)
  - Suivi des commandes dans le compte utilisateur
  - Annulation de commandes (si non expédiées)

- **Support client**
  - Création de tickets de support
  - Système de messages
  - Historique des conversations

- **Interface utilisateur**
  - Design moderne et responsive
  - Mode sombre/clair
  - Notifications en temps réel
  - Navigation intuitive

### 🔒 Sécurité

- **Authentification sécurisée**
  - Hachage des mots de passe avec bcrypt (12 rounds)
  - Migration automatique des anciens hash SHA256
  - Validation de force des mots de passe
  - Protection contre les attaques par énumération

- **Validation des données**
  - Validation côté client (JavaScript)
  - Validation côté serveur (Python)
  - Protection contre l'injection SQL (pas de SQL utilisé)
  - Protection contre XSS (échappement des données)

- **Gestion des sessions**
  - Tokens de session uniques
  - Destruction propre lors de la déconnexion
  - Vérification d'authentification sur les routes protégées

### 🛠️ Gestion Technique

- **Stock**
  - Vérification de disponibilité en temps réel
  - Réservation uniquement après paiement réussi
  - Restitution du stock en cas d'annulation

- **Paiements**
  - Simulation de paiement par carte bancaire
  - Validation du numéro de carte (Luhn)
  - Gestion des transactions

## 🛠️ Technologies

### Backend
- **Python 3.8+** - Langage de programmation
- **Flask 2.3.3** - Framework web
- **bcrypt 4.1.2** - Hachage sécurisé des mots de passe
- **Werkzeug 2.3.7** - Utilitaires WSGI

### Frontend
- **HTML5** - Structure
- **CSS3** - Styles et design responsive
- **JavaScript (ES6+)** - Interactivité et AJAX
- **Font Awesome** - Icônes

### Tests & Qualité
- **pytest 7.4.3** - Framework de tests
- **pytest-cov 4.1.0** - Couverture de code
- **pytest-flask 1.3.0** - Tests Flask
- **flake8 6.1.0** - Linter Python
- **pylint 3.0.3** - Analyse statique
- **black 23.12.1** - Formateur de code

### CI/CD
- **GitHub Actions** - Intégration continue
- Automatisation des tests
- Vérification de la qualité de code
- Génération de rapports de couverture

## 🏗️ Architecture

Le projet suit une architecture en couches avec séparation des responsabilités :

```
┌─────────────────────────────────────┐
│         Templates (Vue)              │
│      (HTML + Jinja2)                 │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Routes Flask (Contrôleur)       │
│           (app.py)                   │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│    Services (Logique Métier)        │
│         (main.py)                    │
│  - AuthService                      │
│  - CartService                      │
│  - OrderService                     │
│  - CustomerService                  │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│    Repositories (Accès Données)     │
│         (main.py)                    │
│  - UserRepository                   │
│  - ProductRepository                │
│  - CartRepository                   │
│  - OrderRepository                  │
└─────────────────────────────────────┘
```

### Principes appliqués

- **Séparation des responsabilités** : Routes, services et repositories sont distincts
- **Inversion de dépendances** : Les services dépendent d'abstractions (repositories)
- **Single Responsibility** : Chaque classe a une responsabilité unique
- **Testabilité** : Architecture facilitant l'écriture de tests

## 🚀 Installation

### Prérequis

- **Python 3.8** ou supérieur
- **pip** (gestionnaire de paquets Python)
- **Git** (optionnel, pour cloner le dépôt)

### Étapes d'installation

1. **Cloner le dépôt** (ou télécharger le projet)
   ```bash
   git clone <url-du-depot>
   cd ecom-web-app-main
   ```

2. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

3. **Installer les dépendances de développement** (pour les tests)
   ```bash
   pip install -r requirements-dev.txt
   ```

## 💻 Utilisation

### Lancement de l'application

#### Option 1 : Scripts de démarrage

**Windows :**
```bash
start.bat
```

**Linux/Mac :**
```bash
chmod +x start.sh
./start.sh
```

**Python :**
```bash
python start.py
```

#### Option 2 : Lancement manuel

```bash
python app.py
```

L'application sera accessible à l'adresse : **http://localhost:5000**

### Compte de test

Un compte de test est créé automatiquement au démarrage :

- **Email** : `client@shop.test`
- **Mot de passe** : `Secret123!`

### Workflow utilisateur

1. **Navigation** : Parcourir le catalogue, rechercher ou filtrer par catégorie
2. **Panier** : Ajouter des produits au panier avec les quantités souhaitées
3. **Connexion** : Se connecter ou créer un compte
4. **Checkout** : Créer une commande depuis le panier
5. **Paiement** : Saisir les informations de carte bancaire
6. **Suivi** : Consulter les commandes dans le tableau de bord

## 🧪 Tests

### Exécution des tests

```bash
# Tous les tests
pytest

# Tests unitaires uniquement
pytest tests/unit/ -v

# Tests fonctionnels uniquement
pytest tests/functional/ -v

# Tests de sécurité
pytest tests/unit/test_security.py -v

# Avec rapport de couverture
pytest --cov=main --cov=app --cov-report=html
```

Le rapport de couverture HTML sera généré dans `htmlcov/index.html`.

### Types de tests

- **Tests unitaires** (`tests/unit/`) : Testent les services et la logique métier de manière isolée
- **Tests fonctionnels** (`tests/functional/`) : Testent les routes Flask et les interactions utilisateur
- **Tests de sécurité** (`tests/unit/test_security.py`) : Testent les mécanismes de sécurité

### Objectif de couverture

**Objectif** : Maintenir une couverture de code ≥ 70%

### Qualité de code

```bash
# Vérification du style (PEP 8)
flake8 main.py app.py

# Analyse statique complète
pylint main.py app.py

# Formatage automatique
black main.py app.py
```

## 🔐 Sécurité

### Mesures de sécurité implémentées

1. **Hachage des mots de passe**
   - Utilisation de bcrypt avec 12 rounds
   - Salt unique pour chaque mot de passe
   - Migration automatique des anciens hash SHA256

2. **Validation de force des mots de passe**
   - Minimum 8 caractères
   - Au moins une majuscule
   - Au moins une minuscule
   - Au moins un chiffre
   - Au moins un caractère spécial

3. **Protection des sessions**
   - Tokens de session uniques
   - Destruction propre lors de la déconnexion
   - Vérification d'authentification sur les routes protégées

4. **Validation des entrées**
   - Validation côté client et serveur
   - Protection contre l'injection SQL
   - Échappement des données pour prévenir XSS

5. **Tests de sécurité**
   - 22 tests de sécurité couvrant les vulnérabilités courantes
   - Tests de hachage, validation, authentification, autorisation

## 📁 Structure du projet

```
ecom-web-app-main/
├── app.py                    # Application Flask (routes, endpoints)
├── main.py                   # Logique métier (services, modèles, repositories)
├── requirements.txt          # Dépendances production
├── requirements-dev.txt      # Dépendances développement/test
├── pytest.ini               # Configuration pytest
├── setup.cfg                # Configuration linters (flake8, pylint)
├── config.env.example        # Exemple de configuration
│
├── static/                   # Fichiers statiques
│   ├── css/
│   │   └── style.css        # Styles de l'application
│   ├── js/
│   │   └── main.js          # JavaScript (panier, recherche, etc.)
│   └── images/              # Images produits et bannière
│
├── templates/                # Templates HTML (Jinja2)
│   ├── base.html            # Template de base
│   ├── index.html           # Page d'accueil (catalogue)
│   ├── product.html         # Page détail produit
│   ├── cart.html            # Panier
│   ├── login.html           # Connexion
│   ├── register.html        # Inscription
│   ├── dashboard.html       # Compte utilisateur
│   ├── orders.html          # Historique des commandes
│   ├── support.html         # Support client
│   └── admin/               # Interface administrateur
│       └── dashboard.html
│
├── tests/                    # Tests automatisés
│   ├── conftest.py          # Configuration et fixtures pytest
│   ├── unit/                 # Tests unitaires
│   │   ├── test_auth_service.py
│   │   ├── test_cart_service.py
│   │   ├── test_order_service.py
│   │   └── test_security.py
│   └── functional/           # Tests fonctionnels
│       └── test_routes.py
│
├── .github/                  # GitHub Actions (CI/CD)
│   └── workflows/
│       └── ci.yml
│
├── htmlcov/                  # Rapports de couverture (générés)
├── start.bat                 # Script de démarrage Windows
├── start.sh                  # Script de démarrage Linux/Mac
└── start.py                 # Script de démarrage Python
```

## 🔧 Développement

### Workflow Git

Le projet suit une convention de commits :

- `feat:` - Nouvelle fonctionnalité
- `fix:` - Correction de bug
- `test:` - Ajout/modification de tests
- `docs:` - Documentation
- `refactor:` - Refactorisation du code
- `security:` - Amélioration de sécurité
- `style:` - Formatage du code

### Branches

- `main` - Branche principale (production)
- `develop` - Branche de développement
- `feature/*` - Nouvelles fonctionnalités
- `fix/*` - Corrections de bugs

### Ajout de nouvelles fonctionnalités

1. Créer une branche : `git checkout -b feature/nouvelle-fonctionnalite`
2. Développer et tester le code
3. Écrire les tests correspondants
4. Vérifier la couverture de code
5. Soumettre une Pull Request

## 🔄 CI/CD

Le projet utilise GitHub Actions pour l'intégration continue.

### Pipeline CI

Le pipeline automatique exécute :

1. **Tests unitaires** avec rapport de couverture
2. **Tests fonctionnels**
3. **Linters** (flake8, pylint)
4. **Vérification de la couverture** (minimum 70%)

Fichier de configuration : `.github/workflows/ci.yml`

## 📚 Contexte pédagogique

Ce projet a été développé pour appliquer les concepts vus en cours de **Qualité de développement** :

### Concepts appliqués

- ✅ **Tests automatisés** : Tests unitaires et fonctionnels avec pytest
- ✅ **Couverture de code** : Mesure et objectif de couverture ≥ 70%
- ✅ **Intégration continue** : Pipeline CI/CD avec GitHub Actions
- ✅ **Standards de code** : PEP 8, utilisation de linters (flake8, pylint)
- ✅ **Documentation** : Docstrings, commentaires, README complet
- ✅ **Gestion de version** : Git avec workflow approprié
- ✅ **Architecture** : Séparation des responsabilités, design patterns
- ✅ **Sécurité** : Hachage bcrypt, validation, tests de sécurité

### Objectifs pédagogiques

- Comprendre l'importance des tests dans le développement
- Appliquer les bonnes pratiques de développement
- Maîtriser les outils de qualité de code
- Mettre en place un pipeline CI/CD
- Implémenter des mesures de sécurité

## 🚧 Limitations et améliorations futures

### Limitations actuelles

- **Stockage en mémoire** : Les données sont perdues au redémarrage
- **Paiement simulé** : Pas de vraie transaction bancaire
- **Pas de base de données** : Utilisation de repositories en mémoire

### Améliorations possibles

- Intégration d'une base de données (PostgreSQL, MySQL)
- Authentification OAuth (Google, Facebook)
- Envoi d'emails de confirmation
- Système de gestion des images
- Interface administrateur complète
- API REST complète
- Déploiement en production (Heroku, AWS, etc.)


---

**Note** : Ce projet est un projet universitaire et sert de démonstration des compétences en développement logiciel de qualité.
