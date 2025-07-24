#!/usr/bin/env python3
"""
Version française simple du clonage de chaînes Telegram
Basée sur votre code original mais améliorée et traduite
"""

from telethon import TelegramClient
import asyncio
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Configuration API Telegram
api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')

# Chaînes à configurer
chaine_source = 'nom_chaine_source'  # ex: 'ma_chaine_source'
chaine_cible = 'nom_chaine_cible'   # ex: 'ma_chaine_cible'

async def cloner_chaine():
    """Fonction principale de clonage de chaîne."""
    print("🚀 Démarrage du clonage de chaîne Telegram...")
    
    # Vérification des identifiants
    if not api_id or not api_hash:
        print("❌ Erreur: Veuillez configurer vos identifiants API dans le fichier .env")
        return
    
    # Création du client Telegram
    client = TelegramClient('session_clonage', api_id, api_hash)
    
    try:
        await client.start()
        print("✅ Connecté à Telegram")
        
        # Obtention des entités des chaînes
        print(f"📥 Récupération de la chaîne source: {chaine_source}")
        source = await client.get_entity(chaine_source)
        
        print(f"📤 Récupération de la chaîne cible: {chaine_cible}")
        cible = await client.get_entity(chaine_cible)
        
        print("📋 Récupération des messages...")
        
        # Parcours des messages dans l'ordre chronologique
        compteur = 0
        async for message in client.iter_messages(source, reverse=True):
            try:
                compteur += 1
                
                # Si c'est un message texte
                if message.message and not message.media:
                    await client.send_message(cible, message.message)
                    print(f"✅ Message texte {compteur} envoyé")
                
                # Si c'est un message avec média
                elif message.media:
                    await client.send_file(
                        cible, 
                        message.media, 
                        caption=message.message or ""
                    )
                    print(f"🖼️ Message avec média {compteur} envoyé")
                
                # Sinon, on passe au suivant
                else:
                    print(f"⏭️ Message {compteur} ignoré (vide)")
                
                # Petite pause pour éviter les limites
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"❌ Erreur avec le message {compteur}: {str(e)}")
                continue
        
        print(f"🎉 Clonage terminé ! {compteur} messages traités")
        
    except Exception as e:
        print(f"❌ Erreur générale: {str(e)}")
    
    finally:
        await client.disconnect()
        print("👋 Déconnecté de Telegram")


if __name__ == '__main__':
    print("🔧 Clonage de Chaînes Telegram - Version Simple Française")
    print("=" * 60)
    
    try:
        asyncio.run(cloner_chaine())
    except KeyboardInterrupt:
        print("\n⛔ Opération annulée par l'utilisateur")
    except Exception as e:
        print(f"💥 Erreur fatale: {str(e)}")