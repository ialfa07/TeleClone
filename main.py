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


def parse_arguments():
    """Analyse les arguments de ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Clone les messages d'une chaîne Telegram source vers une chaîne cible",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python main.py --source @chaine_source --target @chaine_cible
  python main.py --source -1001234567890 --target -1009876543210 --limit 100
  python main.py --source @chaine_source --target @chaine_cible --resume --use-bot
        """
    )
    
    parser.add_argument(
        '--source', '-s',
        required=True,
        help='Nom ou ID de la chaîne source (ex: @chaine, -1001234567890)'
    )
    
    parser.add_argument(
        '--target', '-t',
        required=True,
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
    
    # Configuration de la journalisation
    logger = setup_logger(args.log_level)
    
    try:
        # Chargement de la configuration
        config = Config()
        logger.info("Chargement de la configuration...")
        
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
            return 0
        else:
            logger.error(f"Échec du clonage après {duration}")
            return 1
            
    except KeyboardInterrupt:
        logger.info("Opération annulée par l'utilisateur")
        return 130
    except Exception as e:
        logger.error(f"Erreur inattendue: {str(e)}", exc_info=True)
        return 1


if __name__ == '__main__':
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nOpération annulée par l'utilisateur")
        sys.exit(130)
