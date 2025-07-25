# Guide d'Utilisation - Clonage de Chaînes Telegram

## 🚀 Démarrage Rapide

### Mode Interactif (Recommandé pour les débutants)

```bash
python main.py
```

Le script vous guidera étape par étape :

1. **Vérification des identifiants** - Le script vérifie automatiquement vos identifiants API
2. **Configuration des canaux** - Saisie des canaux source et cible avec validation
3. **Options de clonage** - Configuration des paramètres selon vos besoins
4. **Résumé et confirmation** - Vérification avant démarrage

### Mode Ligne de Commande (Pour les utilisateurs avancés)

```bash
# Clonage simple
python main.py --source @ma_chaine --target @ma_copie

# Avec ID numériques
python main.py --source -1001234567890 --target -1009876543210

# Mode hybride (recommandé)
python main.py --source @source --target @cible --use-bot

# Avec options avancées
python main.py --source @source --target @cible --limit 100 --resume --dry-run
```

## 📋 Configuration Initiale

### 1. Obtenir les Identifiants API Telegram

1. Allez sur https://my.telegram.org/auth
2. Connectez-vous avec votre numéro de téléphone
3. Cliquez sur "API development tools"
4. Créez une nouvelle application
5. Notez votre `api_id` et `api_hash`

### 2. Configuration du Fichier .env

```bash
# Copiez le fichier d'exemple
cp .env.example .env

# Éditez le fichier .env avec vos identifiants
nano .env
```

Configuration minimale requise :
```env
TELEGRAM_API_ID=votre_api_id_ici
TELEGRAM_API_HASH=votre_api_hash_ici
```

Configuration complète (optionnelle) :
```env
# Identifiants requis
TELEGRAM_API_ID=votre_api_id_ici
TELEGRAM_API_HASH=votre_api_hash_ici

# Configuration bot (optionnel - recommandé pour gros canaux)
TELEGRAM_BOT_TOKEN=votre_bot_token_ici
USE_BOT_FOR_SENDING=true

# Paramètres de performance
RATE_LIMIT_DELAY=1.0
BATCH_SIZE=10
MAX_RETRIES=3

# Journalisation
LOG_LEVEL=INFO
LOG_FILE=telegram_cloner.log
```

### 3. Configuration du Bot Telegram (Optionnel)

Pour le mode hybride, configurez un bot :

1. Contactez @BotFather sur Telegram
2. Tapez `/newbot` et suivez les instructions
3. Copiez le token dans `TELEGRAM_BOT_TOKEN`
4. Ajoutez le bot comme administrateur du canal cible

## 🎯 Modes d'Utilisation

### Mode Standard
- Lecture et envoi avec votre compte personnel
- Idéal pour les petits canaux privés

```bash
python main.py --source @source --target @cible
```

### Mode Hybride (Recommandé)
- Lecture avec votre compte, envoi via bot
- Plus stable pour les gros canaux
- Moins de restrictions

```bash
python main.py --source @source --target @cible --use-bot
```

### Mode Test
- Aperçu sans envoi réel
- Parfait pour vérifier la configuration

```bash
python main.py --source @source --target @cible --dry-run
```

## 🔧 Options Avancées

### Formats de Canaux Supportés

| Format | Exemple | Description |
|--------|---------|-------------|
| Username | `@ma_chaine` | Nom public du canal |
| Username simple | `ma_chaine` | Ajout automatique du @ |
| ID numérique | `-1001234567890` | ID interne Telegram |
| Lien t.me | `https://t.me/ma_chaine` | Lien public |

### Options de Ligne de Commande

| Option | Description | Exemple |
|--------|-------------|---------|
| `--source, -s` | Canal source | `--source @ma_chaine` |
| `--target, -t` | Canal cible | `--target @ma_copie` |
| `--limit, -l` | Limite de messages | `--limit 100` |
| `--resume, -r` | Reprendre le clonage | `--resume` |
| `--use-bot` | Mode hybride | `--use-bot` |
| `--dry-run` | Mode test | `--dry-run` |
| `--delay` | Délai entre messages | `--delay 2.0` |
| `--batch-size` | Taille des lots | `--batch-size 5` |
| `--log-level` | Niveau de log | `--log-level DEBUG` |

## 🛡️ Fonctionnalités de Sécurité

### Prévention des Doublons
- Suivi automatique des messages déjà copiés
- Persistance dans fichier de progression
- Évite les duplicatas lors de reprises

### Gestion des Erreurs
- Retry automatique avec délais exponentiels
- Respect des limites de l'API Telegram
- Fallback automatique bot → compte utilisateur

### Journalisation Complète
- Logs détaillés avec rotation automatique
- Niveaux configurables (DEBUG, INFO, WARNING, ERROR)
- Suivi des performances et erreurs

## 📊 Exemples Pratiques

### Clonage Simple
```bash
# Mode interactif
python main.py

# Mode CLI
python main.py --source @tech_news --target @my_tech_copy
```

### Clonage avec ID Numérique
```bash
python main.py --source -1001234567890 --target @my_copy --limit 50
```

### Clonage Hybride Gros Volume
```bash
python main.py --source @big_channel --target @my_copy --use-bot --batch-size 5 --delay 2
```

### Reprendre un Clonage Interrompu
```bash
python main.py --source @source --target @cible --resume
```

### Test de Configuration
```bash
python main.py --source @test --target @test_copy --dry-run --limit 5
```

## 🔍 Résolution de Problèmes

### Erreurs Courantes

**"Identifiants API Telegram manquants"**
- Solution : Configurez `TELEGRAM_API_ID` et `TELEGRAM_API_HASH` dans `.env`

**"Canal non trouvé"**
- Vérifiez l'orthographe du nom du canal
- Assurez-vous d'avoir accès au canal
- Utilisez l'ID numérique si disponible

**"Permission denied"**
- Vérifiez que vous êtes membre du canal source
- Vérifiez que vous êtes admin du canal cible
- Pour le mode bot, ajoutez le bot comme admin

**"FloodWaitError"**
- Le script gère automatiquement les limites
- Attendez ou augmentez `RATE_LIMIT_DELAY`

### Optimisation des Performances

**Pour gros canaux (>1000 messages) :**
- Utilisez le mode hybride (`--use-bot`)
- Réduisez la taille des lots (`--batch-size 5`)
- Augmentez le délai (`--delay 2.0`)

**Pour reprise rapide :**
- Utilisez toujours `--resume`
- Surveillez les logs pour le point de reprise

## 🆘 Support

### Fichiers de Logs
- `telegram_cloner.log` : Logs détaillés
- `progression_*.json` : Fichiers de progression

### Tests Disponibles
```bash
# Test des nouvelles fonctionnalités
python test_nouvelles_fonctionnalites.py

# Test du mode interactif
python test_mode_interactif.py

# Exemple d'utilisation du bot
python exemple_bot.py
```

### Aide en Ligne
```bash
python main.py --help
```