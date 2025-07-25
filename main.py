#!/usr/bin/env python3
"""
Clonage de Chaînes Telegram - Point d'Entrée Principal
Un outil amélioré de clonage de chaînes Telegram avec gestion d'erreurs, journalisation et gestion de configuration.
"""

import argparse
import asyncio
import sys
import os
from datetime import datetime

from config import Config
from telegram_cloner import TelegramCloner
from logger_setup import setup_logger
from dotenv import load_dotenv


def check_credentials():
    """Vérifie et demande les identifiants requis."""
    load_dotenv()
    
    print("🔧 Vérification de la Configuration")
    print("=" * 50)
    
    # Vérifier les identifiants API Telegram
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    
    if not api_id or not api_hash:
        print("❌ Identifiants API Telegram manquants")
        print("\n📋 Pour obtenir vos identifiants :")
        print("1. Allez sur https://my.telegram.org/auth")
        print("2. Connectez-vous avec votre numéro de téléphone")
        print("3. Créez une nouvelle application")
        print("4. Copiez l'API ID et l'API Hash")
        print("\n⚙️ Configuration :")
        print("1. Copiez .env.example vers .env")
        print("2. Ajoutez vos identifiants dans le fichier .env")
        print("\nRedémarrez le programme après la configuration.")
        return False
    
    print("✅ Identifiants API Telegram trouvés")
    
    # Vérifier le token bot (optionnel)
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if bot_token:
        print("✅ Token de bot trouvé (mode hybride disponible)")
    else:
        print("⚠️  Token de bot non configuré (mode hybride indisponible)")
    
    return True

def get_channel_input(prompt, example):
    """Demande l'identifiant d'un canal à l'utilisateur."""
    while True:
        print(f"\n{prompt}")
        print(f"Exemples : {example}")
        channel = input("Canal : ").strip()
        
        if not channel:
            print("❌ Veuillez entrer un identifiant de canal valide")
            continue
            
        # Validation basique
        if channel.startswith('@') or channel.startswith('-') or channel.lstrip('-').isdigit():
            return channel
        elif not channel.startswith('@'):
            return f"@{channel}"
        else:
            print("❌ Format invalide. Utilisez @nom_canal ou -1001234567890")

def get_options():
    """Demande les options de clonage à l'utilisateur."""
    print("\n⚙️ Options de Clonage")
    print("=" * 30)
    
    options = {}
    
    # Limite de messages
    while True:
        limit_input = input("Limite de messages (Entrée pour tous) : ").strip()
        if not limit_input:
            options['limit'] = None
            break
        try:
            limit = int(limit_input)
            if limit > 0:
                options['limit'] = limit
                break
            else:
                print("❌ Entrez un nombre positif")
        except ValueError:
            print("❌ Entrez un nombre valide")
    
    # Mode reprise
    resume = input("Reprendre depuis le dernier message ? (o/N) : ").strip().lower()
    options['resume'] = resume in ['o', 'oui', 'y', 'yes']
    
    # Mode bot
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if bot_token:
        use_bot = input("Utiliser le mode hybride (bot) ? (o/N) : ").strip().lower()
        options['use_bot'] = use_bot in ['o', 'oui', 'y', 'yes']
    else:
        options['use_bot'] = False
    
    # Mode test
    dry_run = input("Mode test (aperçu sans envoi) ? (o/N) : ").strip().lower()
    options['dry_run'] = dry_run in ['o', 'oui', 'y', 'yes']
    
    # Niveau de log
    print("\nNiveaux de log : DEBUG, INFO, WARNING, ERROR")
    log_level = input("Niveau de log (INFO par défaut) : ").strip().upper()
    if log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
        log_level = 'INFO'
    options['log_level'] = log_level
    
    return options

def interactive_mode():
    """Mode interactif pour configurer le clonage."""
    print("🚀 Clonage de Chaînes Telegram - Mode Interactif")
    print("=" * 60)
    
    # Vérifier les identifiants
    if not check_credentials():
        return None, None, None
    
    # Demander les canaux
    source = get_channel_input(
        "📥 Canal source (d'où copier les messages)",
        "@mon_canal, mon_canal, -1001234567890"
    )
    
    target = get_channel_input(
        "📤 Canal cible (où envoyer les messages)",
        "@ma_copie, ma_copie, -1009876543210"
    )
    
    # Demander les options
    options = get_options()
    
    # Résumé
    print("\n📋 Résumé de la Configuration")
    print("=" * 40)
    print(f"Canal source  : {source}")
    print(f"Canal cible   : {target}")
    print(f"Limite        : {options['limit'] or 'Tous les messages'}")
    print(f"Reprise       : {'Oui' if options['resume'] else 'Non'}")
    print(f"Mode hybride  : {'Oui' if options['use_bot'] else 'Non'}")
    print(f"Mode test     : {'Oui' if options['dry_run'] else 'Non'}")
    print(f"Niveau de log : {options['log_level']}")
    
    # Confirmation
    confirm = input("\n✅ Confirmer le clonage ? (O/n) : ").strip().lower()
    if confirm in ['n', 'non', 'no']:
        print("❌ Clonage annulé")
        return None, None, None
    
    return source, target, options

def parse_arguments():
    """Analyse les arguments de ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Clone les messages d'une chaîne Telegram source vers une chaîne cible",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python main.py                                    # Mode interactif
  python main.py --source @chaine_source --target @chaine_cible
  python main.py --source -1001234567890 --target -1009876543210 --limit 100
  python main.py --source @chaine_source --target @chaine_cible --resume --use-bot
        """
    )
    
    parser.add_argument(
        '--source', '-s',
        required=False,
        help='Nom ou ID de la chaîne source (ex: @chaine, -1001234567890)'
    )
    
    parser.add_argument(
        '--target', '-t',
        required=False,
        help='Nom ou ID de la chaîne cible (ex: @chaine, -1001234567890)'
    )
    
    parser.add_argument(
        '--limit', '-l',
        type=int,
        default=None,
        help='Limiter le nombre de messages à cloner (défaut: tous les messages)'
    )
    
    parser.add_argument(
        '--resume', '-r',
        action='store_true',
        help='Reprendre depuis le dernier message cloné'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=None,
        help='Délai entre les messages en secondes (remplace la config)'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=None,
        help='Nombre de messages à traiter par lot (remplace la config)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Définir le niveau de journalisation (défaut: INFO)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Afficher ce qui serait cloné sans envoyer les messages'
    )
    
    parser.add_argument(
        '--use-bot',
        action='store_true',
        help='Utiliser un bot pour envoyer les messages (nécessite TELEGRAM_BOT_TOKEN)'
    )
    
    return parser.parse_args()


async def main():
    """Point d'entrée principal de l'application."""
    args = parse_arguments()
    
    try:
        # Si aucun argument source/target, lancer le mode interactif
        if not args.source or not args.target:
            result = interactive_mode()
            if not result or result[0] is None or result[1] is None:
                return 0
            
            source, target, options = result
            
            # Appliquer les options du mode interactif
            args.source = source
            args.target = target
            args.limit = options['limit']
            args.resume = options['resume']
            args.use_bot = options['use_bot']
            args.dry_run = options['dry_run']
            args.log_level = options['log_level']
        else:
            # Vérifier les identifiants en mode CLI
            if not check_credentials():
                return 1
        
        # Configuration de la journalisation
        logger = setup_logger(args.log_level)
        
        # Chargement de la configuration
        config = Config()
        
        # Remplacer la config avec les arguments de ligne de commande si fournis
        if args.delay is not None:
            config.rate_limit_delay = args.delay
        if args.batch_size is not None:
            config.batch_size = args.batch_size
        if hasattr(args, 'use_bot') and args.use_bot:
            config.use_bot_for_sending = True
            
        # Validation de la configuration
        if not config.validate():
            logger.error("Échec de validation de la configuration. Veuillez vérifier votre fichier .env.")
            return 1
            
        # Initialisation du clonage Telegram
        cloner = TelegramCloner(config, logger)
        
        logger.info("Démarrage du Clonage de Chaînes Telegram")
        logger.info(f"Chaîne Source: {args.source}")
        logger.info(f"Chaîne Cible: {args.target}")
        logger.info(f"Limite de Messages: {args.limit or 'Aucune limite'}")
        logger.info(f"Mode Reprise: {'Activé' if args.resume else 'Désactivé'}")
        logger.info(f"Mode Test: {'Activé' if args.dry_run else 'Désactivé'}")
        logger.info(f"Mode Bot: {'Activé' if config.use_bot_for_sending else 'Désactivé'}")
        
        # Démarrage du processus de clonage
        start_time = datetime.now()
        
        success = await cloner.clone_channel(
            source_channel=args.source,
            target_channel=args.target,
            message_limit=args.limit,
            resume=args.resume,
            dry_run=args.dry_run
        )
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        if success:
            logger.info(f"Clonage terminé avec succès en {duration}")
            print("\n🎉 Clonage terminé avec succès !")
            return 0
        else:
            logger.error(f"Échec du clonage après {duration}")
            print("\n❌ Échec du clonage ! Consultez les logs pour plus de détails.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⛔ Opération annulée par l'utilisateur")
        return 130
    except Exception as e:
        print(f"💥 Erreur inattendue : {str(e)}")
        return 1


if __name__ == '__main__':
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nOpération annulée par l'utilisateur")
        sys.exit(130)
