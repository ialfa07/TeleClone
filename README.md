# Clonage de Chaînes Telegram

Un outil amélioré de clonage de chaînes Telegram avec gestion d'erreurs complète, journalisation, gestion de configuration et fonctionnalité de reprise.

## Fonctionnalités

- **Clonage Complet de Messages**: Clone les messages texte, fichiers médias et contenu mixte
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
