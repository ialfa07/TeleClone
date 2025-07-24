#!/usr/bin/env python3
"""
Exemple d'utilisation du mode hybride (lecture + bot)
Démonstration de la nouvelle fonctionnalité
"""

import asyncio
import os
from dotenv import load_dotenv
from telegram_cloner import TelegramCloner
from config import Config
from logger_setup import setup_logger

async def exemple_mode_hybride():
    """Exemple d'utilisation du mode hybride."""
    print("🚀 Exemple Mode Hybride - Lecture avec compte, envoi avec bot")
    print("=" * 60)
    
    # Configuration
    load_dotenv()
    
    # Vérifications
    if not os.getenv('TELEGRAM_API_ID') or not os.getenv('TELEGRAM_API_HASH'):
        print("❌ Veuillez configurer TELEGRAM_API_ID et TELEGRAM_API_HASH dans .env")
        return
    
    if not os.getenv('TELEGRAM_BOT_TOKEN'):
        print("❌ Veuillez configurer TELEGRAM_BOT_TOKEN dans .env")
        print("💡 Créez un bot avec @BotFather et ajoutez le token")
        return
    
    # Configuration avec mode bot activé
    config = Config()
    config.use_bot_for_sending = True
    
    logger = setup_logger('INFO')
    
    # Initialisation du clonage
    cloner = TelegramCloner(config, logger)
    
    print("📋 Configuration Mode Hybride :")
    print(f"   - Lecture : Compte utilisateur")
    print(f"   - Envoi : Bot ({config.bot_token[:10]}...)")
    print()
    
    # Exemple de chaînes (à modifier selon vos besoins)
    chaine_source = input("📥 Nom de la chaîne source (ex: @ma_chaine): ").strip()
    chaine_cible = input("📤 Nom de la chaîne cible (ex: @ma_chaine_copie): ").strip()
    
    if not chaine_source or not chaine_cible:
        print("❌ Veuillez spécifier les noms des chaînes")
        return
    
    print(f"\n🔄 Démarrage du clonage hybride...")
    print(f"   Source: {chaine_source}")
    print(f"   Cible: {chaine_cible}")
    
    try:
        success = await cloner.clone_channel(
            source_channel=chaine_source,
            target_channel=chaine_cible,
            message_limit=5,  # Limité à 5 messages pour test
            resume=False,
            dry_run=False
        )
        
        if success:
            print("✅ Clonage hybride terminé avec succès !")
        else:
            print("❌ Échec du clonage hybride")
            
    except Exception as e:
        print(f"💥 Erreur: {str(e)}")

def afficher_instructions():
    """Affiche les instructions pour configurer le mode hybride."""
    print("📖 Instructions Mode Hybride :")
    print()
    print("1. 🤖 Créer un bot Telegram :")
    print("   - Allez sur @BotFather")
    print("   - Tapez /newbot")
    print("   - Suivez les instructions")
    print("   - Copiez le token dans TELEGRAM_BOT_TOKEN")
    print()
    print("2. 👑 Rendre le bot administrateur :")
    print("   - Allez sur votre canal cible")
    print("   - Paramètres > Administrateurs")
    print("   - Ajoutez votre bot comme admin")
    print()
    print("3. ⚙️ Configuration .env :")
    print("   TELEGRAM_BOT_TOKEN=votre_token_ici")
    print("   USE_BOT_FOR_SENDING=true")
    print()
    print("4. 🚀 Utilisation :")
    print("   python main.py --source @source --target @cible --use-bot")
    print()

if __name__ == '__main__':
    print("🔧 Mode Hybride - Clonage Telegram")
    print("Lecture avec votre compte + Envoi avec bot")
    print("=" * 50)
    
    choix = input("Choisissez une option:\n1. Voir les instructions\n2. Tester le mode hybride\nChoix (1/2): ").strip()
    
    if choix == '1':
        afficher_instructions()
    elif choix == '2':
        try:
            asyncio.run(exemple_mode_hybride())
        except KeyboardInterrupt:
            print("\n⛔ Test annulé par l'utilisateur")
    else:
        print("❌ Choix invalide")