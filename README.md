# Projet E-Commerce - Site de Vente en Ligne

Projet réalisé dans le cadre du cours "Qualité de développement". Application e-commerce complète avec Flask, permettant de gérer un catalogue de produits, un panier, des commandes et un support client.

## 📋 Fonctionnalités Implémentées

### Pour les Utilisateurs
- ✅ **Catalogue de produits** avec recherche en temps réel
- ✅ **Filtrage par catégorie** (Homme / Femme)
- ✅ **Panier d'achat** avec gestion des quantités
- ✅ **Création de compte** et authentification
- ✅ **Passage de commande** avec formulaire de paiement
- ✅ **Suivi des commandes** dans le compte utilisateur
- ✅ **Support client** avec système de tickets
- ✅ **Mode sombre** pour l'interface

### Gestion
- ✅ **Gestion du stock** : réservation uniquement après paiement réussi
- ✅ **Synchronisation** : compteur de panier en temps réel
- ✅ **Validation** : vérification des données côté client et serveur

## 🛠️ Technologies Utilisées

- **Backend** : Python 3.8+, Flask
- **Frontend** : HTML5, CSS3, JavaScript (vanilla)
- **Tests** : pytest, pytest-cov
- **Qualité** : flake8, pylint
- **CI/CD** : GitHub Actions

## 🚀 Installation et Lancement

### Prérequis
- Python 3.8 ou supérieur
- pip installé

### Installation

1. **Cloner ou télécharger le projet**
   ```bash
   cd ecom-web-app-main
   ```

2. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

3. **Lancer l'application**

   **Sur Windows :**
   ```bash
   python app.py
   ```
   ou double-cliquer sur `start.bat`

   **Sur Linux/Mac :**
   ```bash
   python3 app.py
   ```
   ou exécuter `start.sh`

4. **Accéder au site**
   Ouvrir votre navigateur et aller sur : **http://localhost:5000**

## 👤 Compte de Test

Un compte de test est créé automatiquement au démarrage :
- **Email** : `client@shop.test`
- **Mot de passe** : `secret`

## 📁 Structure du Projet

```
ecom-web-app-main/
├── app.py                    # Application Flask (routes, endpoints)
├── main.py                   # Logique métier (services, modèles)
├── requirements.txt          # Dépendances production
├── requirements-dev.txt      # Dépendances développement/test
├── pytest.ini               # Configuration des tests
├── setup.cfg                # Configuration linters
│
├── static/                   # Fichiers statiques
│   ├── css/style.css        # Styles de l'application
│   ├── js/main.js           # JavaScript (panier, recherche, etc.)
│   └── images/              # Images produits et bannière
│
├── templates/                # Templates HTML
│   ├── base.html            # Template de base
│   ├── index.html           # Page d'accueil (catalogue)
│   ├── product.html         # Page détail produit
│   ├── cart.html            # Panier
│   ├── login.html           # Connexion
│   ├── register.html        # Inscription
│   ├── dashboard.html       # Compte utilisateur
│   ├── orders.html          # Historique des commandes
│   └── support.html         # Support client
│
└── tests/                    # Tests automatisés
    ├── unit/                 # Tests unitaires (services)
    └── functional/           # Tests fonctionnels (routes)
```

## 🧪 Tests

Ce projet inclut des tests pour valider le bon fonctionnement de l'application.

### Installation des dépendances de test
```bash
pip install -r requirements-dev.txt
```

### Exécuter les tests
```bash
# Tous les tests
pytest

# Tests unitaires seulement
pytest tests/unit/ -v

# Tests fonctionnels seulement
pytest tests/functional/ -v

# Avec rapport de couverture
pytest --cov=main --cov=app --cov-report=html
```

Le rapport de couverture HTML sera généré dans `htmlcov/index.html`.

### Qualité de code
```bash
flake8 main.py app.py        # Vérification du style
pylint main.py app.py        # Analyse statique
```

**Objectif** : Maintenir une couverture de code ≥ 70%

## 🔧 Fonctionnement

### Flux d'une commande

1. **Navigation** : L'utilisateur parcourt le catalogue et peut filtrer par catégorie ou rechercher
2. **Panier** : Ajout de produits au panier avec gestion des quantités
3. **Checkout** : Création d'une commande (le stock est vérifié mais pas encore réservé)
4. **Paiement** : Saisie des informations de carte bancaire
5. **Validation** : Si le paiement réussit, le stock est réservé et le panier vidé
6. **Suivi** : L'utilisateur peut voir ses commandes dans son compte

### Points Importants

- **Stock** : La réservation se fait uniquement après un paiement réussi (évite les problèmes si l'utilisateur abandonne)
- **Synchronisation** : Le compteur de panier est mis à jour en temps réel via le serveur
- **Validation** : Les données sont validées côté client (JavaScript) et serveur (Python)

## 📝 Utilisation de Git

Ce projet utilise Git pour le versioning. Les commits suivent une convention :
- `feat:` Nouvelle fonctionnalité
- `fix:` Correction de bug
- `test:` Ajout/modification de tests
- `docs:` Documentation
- `refactor:` Refactorisation du code

## 🔍 Points d'Attention / Améliorations Possibles

- Les données sont stockées en mémoire (redémarrer = perte des données)
- Les mots de passe utilisent SHA256 (pas optimal, mais suffisant pour ce projet)
- Le paiement est simulé (pas de vraie transaction)
- Pas de base de données persistante (toutefois prévu pour amélioration future)

## 📚 Contexte Pédagogique

Ce projet a été développé pour appliquer les concepts vus en cours de **Qualité de développement** :
- ✅ Tests unitaires et fonctionnels
- ✅ Commentaires et documentation
- ✅ Utilisation de Git avec workflow approprié
- ✅ Intégration continue (CI/CD) via GitHub Actions
- ✅ Standards de code (PEP 8, linters)
- ✅ Structure de projet claire

## 🤝 Contributions

Les suggestions d'amélioration sont les bienvenues ! Pour contribuer :
1. Créer une branche : `git checkout -b feature/nouvelle-fonctionnalite`
2. Développer et tester votre code
3. Créer une Pull Request

## 📞 Support

Pour toute question sur le projet, créer une issue sur le dépôt GitHub.

---

**Note** : Ce projet est à but pédagogique et démontre l'application des bonnes pratiques de développement.
