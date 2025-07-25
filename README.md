# Clonage de Chaînes Telegram

Un outil amélioré de clonage de chaînes Telegram avec gestion d'erreurs complète, journalisation, gestion de configuration et fonctionnalité de reprise.

## Fonctionnalités

- **Clonage Complet de Messages**: Clone les messages texte, fichiers médias et contenu mixte
- **Support IDs de Canaux**: Accepte les noms (@chaine) et IDs numériques (-1001234567890)
- **Mode Hybride**: Lire avec votre compte, envoyer via un bot (recommandé pour les gros canaux)
- **Prévention des Doublons**: Évite automatiquement les messages déjà copiés
- **Gestion d'Erreurs et Récupération**: Gestion d'erreurs robuste avec mécanismes de retry automatiques
- **Limitation de Taux**: Limitation de taux intégrée pour respecter les limites de l'API Telegram
- **Suivi de Progression**: Reprendre les transferts interrompus là où ils se sont arrêtés
- **Journalisation Complète**: Journalisation détaillée avec sortie fichier et console
- **Gestion de Configuration**: Configuration basée sur l'environnement pour la sécurité
- **Traitement par Lots**: Traiter les messages par lots configurables
- **Mode Test**: Prévisualiser ce qui sera cloné sans envoyer de messages
- **Interface en Ligne de Commande**: Interface CLI facile à utiliser avec plusieurs options

## Installation

1. Clonez ou téléchargez ce projet
2. Installez les packages Python requis:
   ```bash
   pip install telethon python-dotenv
   ```

3. Configurez vos identifiants API Telegram:
   - Allez sur https://my.telegram.org/auth
   - Créez une nouvelle application pour obtenir votre `api_id` et `api_hash`
   - Copiez `.env.example` vers `.env` et remplissez vos identifiants

## Configuration

Copiez `.env.example` vers `.env` et configurez ce qui suit:

```env
# Requis - Obtenez depuis https://my.telegram.org/auth
TELEGRAM_API_ID=votre_api_id_ici
TELEGRAM_API_HASH=votre_api_hash_ici

# Optionnel - Personnalisez selon vos besoins
TELEGRAM_SESSION_NAME=clonage_telegram

# Configuration Bot (optionnel - recommandé pour gros canaux)
TELEGRAM_BOT_TOKEN=votre_bot_token_ici
USE_BOT_FOR_SENDING=false

# Autres paramètres
RATE_LIMIT_DELAY=1.0
BATCH_SIZE=10
MAX_RETRIES=3
RETRY_DELAY=5.0
LOG_FILE=clonage_telegram.log
LOG_LEVEL=INFO
PROGRESS_FILE=progression_clonage.json
SAVE_PROGRESS_INTERVAL=50
DOWNLOAD_MEDIA=true
MEDIA_TIMEOUT=300
```

## Mode Hybride (Lecture + Bot)

Cette fonctionnalité innovante permet de :
- **Lire les messages** avec votre compte personnel (accès complet aux chaînes privées)
- **Envoyer les messages** via un bot (moins de restrictions, plus stable pour gros volumes)

### Avantages du mode hybride :
1. **Accès étendu** : Votre compte peut lire les chaînes privées
2. **Stabilité** : Le bot gère mieux les gros volumes d'envois
3. **Sécurité** : Moins de risque de restrictions sur votre compte personnel
4. **Fallback automatique** : Si le bot échoue, l'outil utilise votre compte

### Configuration du bot :
1. Créez un bot avec @BotFather sur Telegram
2. Copiez le token dans `TELEGRAM_BOT_TOKEN`
3. Ajoutez le bot comme **administrateur** du canal cible
4. Activez `USE_BOT_FOR_SENDING=true` ou utilisez `--use-bot`

## Utilisation

### Mode Interactif (Recommandé pour débutants)

```bash
# Lance le mode interactif guidé
python main.py
```

Le script vous guide étape par étape :
- Vérification automatique des identifiants API
- Configuration des canaux avec validation des formats
- Options de clonage personnalisées
- Résumé complet et confirmation

### Mode Ligne de Commande

#### Formats de canaux supportés :
- **Usernames** : `@ma_chaine`, `ma_chaine`
- **IDs numériques** : `-1001234567890`
- **Liens t.me** : `https://t.me/ma_chaine`

#### Exemples d'utilisation :

```bash
# Mode Standard (compte uniquement)
python main.py --source @chaine_source --target @chaine_cible

# Avec IDs numériques
python main.py --source -1001234567890 --target -1009876543210

# Mode Hybride (recommandé pour gros canaux)
python main.py --source @chaine_source --target @chaine_cible --use-bot
