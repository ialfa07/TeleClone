#!/usr/bin/env python3
"""
Tests des nouvelles fonctionnalités : IDs de canaux et prévention des doublons
"""

import asyncio
import os
import json
from unittest.mock import AsyncMock, MagicMock, patch
from utils import parse_channel_identifier, is_channel_id
from config import Config
from logger_setup import setup_logger

def test_parse_channel_identifier():
    """Test de l'analyse des identifiants de canaux."""
    print("🔍 Test de l'analyse des identifiants de canaux")
    
    # Test avec des usernames
    assert parse_channel_identifier("@test_channel") == "@test_channel"
    assert parse_channel_identifier("test_channel") == "@test_channel"
    
    # Test avec des IDs numériques
    assert parse_channel_identifier("-1001234567890") == -1001234567890
    assert parse_channel_identifier("-100123456789") == -100123456789
    
    # Test avec des liens t.me
    assert parse_channel_identifier("https://t.me/test_channel") == "@test_channel"
    
    print("✅ Tous les tests d'analyse des identifiants passent")

def test_is_channel_id():
    """Test de détection des IDs numériques."""
    print("🔍 Test de détection des IDs numériques")
    
    # Test avec des IDs valides
    assert is_channel_id(-1001234567890) == True
    assert is_channel_id("-1001234567890") == True
    
    # Test avec des usernames
    assert is_channel_id("@test_channel") == False
    assert is_channel_id("test_channel") == False
    
    print("✅ Tous les tests de détection d'ID passent")

async def test_duplicate_prevention():
    """Test de la prévention des doublons."""
    print("🔍 Test de la prévention des doublons")
    
    from telegram_cloner import TelegramCloner
    
    config = Config()
    logger = setup_logger('DEBUG')
    cloner = TelegramCloner(config, logger)
    
    # Simule des messages déjà copiés
    cloner.copied_messages = {1, 2, 3}
    
    # Mock message
    mock_message = MagicMock()
    mock_message.id = 2
    
    # Test : message déjà copié
    result = await cloner._clone_single_message(mock_message, None)
    assert result == True, "Le message déjà copié devrait retourner True"
    
    print("✅ Test de prévention des doublons réussi")

def test_progress_key_generation():
    """Test de génération des clés de progression."""
    print("🔍 Test de génération des clés de progression")
    
    from telegram_cloner import TelegramCloner
    
    config = Config()
    logger = setup_logger('DEBUG')
    cloner = TelegramCloner(config, logger)
    
    # Test avec des usernames
    cloner._load_progress("@source_channel", "@target_channel")
    expected_key = "source_channel_to_target_channel"
    assert cloner.progress_key == expected_key
    
    # Test avec des IDs
    cloner._load_progress("-1001234567890", "-9876543210987")
    expected_key = "_1001234567890_to__9876543210987"
    assert cloner.progress_key == expected_key
    
    print("✅ Test de génération des clés de progression réussi")

def test_examples():
    """Affiche des exemples d'utilisation avec les nouvelles fonctionnalités."""
    print("\n🚀 Exemples d'utilisation des nouvelles fonctionnalités :")
    print()
    print("1. Utilisation avec des usernames (classique) :")
    print("   python main.py --source @ma_chaine --target @ma_copie")
    print()
    print("2. Utilisation avec des IDs numériques :")
    print("   python main.py --source -1001234567890 --target -1009876543210")
    print()
    print("3. Mode hybride avec IDs :")
    print("   python main.py --source -1001234567890 --target @ma_copie --use-bot")
    print()
    print("4. Reprise avec prévention des doublons :")
    print("   python main.py --source @source --target @cible --resume")
    print()
    print("✨ La prévention des doublons est automatique et transparente")

def main():
    """Lance tous les tests."""
    print("🧪 Tests des Nouvelles Fonctionnalités")
    print("=" * 50)
    
    try:
        # Tests synchrones
        test_parse_channel_identifier()
        test_is_channel_id()
        test_progress_key_generation()
        
        # Tests asynchrones
        print("\n🔄 Lancement des tests asynchrones...")
        asyncio.run(test_duplicate_prevention())
        
        print("\n✅ Tous les tests sont passés avec succès !")
        
        # Affichage des exemples
        test_examples()
        
    except Exception as e:
        print(f"❌ Erreur dans les tests : {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())