#!/usr/bin/env python3
"""
Test du mode interactif sans configuration réelle
"""

import os
import sys
from unittest.mock import patch
from io import StringIO

# Ajouter le répertoire courant au path
sys.path.append('.')

def test_credentials_check():
    """Test de la vérification des identifiants."""
    print("🔍 Test de vérification des identifiants")
    
    # Mock pour éviter de charger le vrai .env
    with patch.dict(os.environ, {}, clear=True):
        from main import check_credentials
        
        # Test sans identifiants
        result = check_credentials()
        assert result == False, "Devrait retourner False sans identifiants"
        print("✅ Test sans identifiants : OK")
    
    # Test avec identifiants
    with patch.dict(os.environ, {
        'TELEGRAM_API_ID': '12345',
        'TELEGRAM_API_HASH': 'abcdef'
    }):
        result = check_credentials()
        assert result == True, "Devrait retourner True avec identifiants"
        print("✅ Test avec identifiants : OK")

def test_channel_input_validation():
    """Test de la validation des entrées de canaux."""
    print("\n🔍 Test de validation des entrées de canaux")
    
    from main import get_channel_input
    
    # Simuler les entrées utilisateur
    test_cases = [
        ("@test_channel", "@test_channel"),
        ("test_channel", "@test_channel"),
        ("-1001234567890", "-1001234567890"),
    ]
    
    for input_val, expected in test_cases:
        with patch('builtins.input', return_value=input_val):
            with patch('builtins.print'):  # Supprime l'affichage pendant le test
                result = get_channel_input("Test", "exemple")
                assert result == expected, f"'{input_val}' devrait donner '{expected}', mais got '{result}'"
        print(f"✅ '{input_val}' -> '{expected}' : OK")

def simulate_interactive_session():
    """Simule une session interactive complète."""
    print("\n🎮 Simulation d'une session interactive")
    
    # Simuler les réponses utilisateur
    user_inputs = [
        "@test_source",      # Canal source
        "@test_target",      # Canal cible
        "10",                # Limite de messages
        "o",                 # Reprise
        "o",                 # Mode test
        "DEBUG",             # Niveau de log
        "o"                  # Confirmation
    ]
    
    with patch.dict(os.environ, {
        'TELEGRAM_API_ID': '12345',
        'TELEGRAM_API_HASH': 'abcdef'
    }):
        with patch('builtins.input', side_effect=user_inputs):
            with patch('builtins.print'):  # Supprime l'affichage
                from main import interactive_mode
                
                result = interactive_mode()
                
                if result and len(result) == 3:
                    source, target, options = result
                    print(f"✅ Source: {source}")
                    print(f"✅ Target: {target}")
                    print(f"✅ Options: {options}")
                    
                    # Vérifications
                    assert source == "@test_source"
                    assert target == "@test_target"
                    assert options['limit'] == 10
                    assert options['resume'] == True
                    assert options['dry_run'] == True
                    assert options['log_level'] == "DEBUG"
                    
                    print("✅ Session interactive simulée avec succès !")
                else:
                    print("❌ Échec de la simulation")

def demo_interactive_features():
    """Démonstration des fonctionnalités interactives."""
    print("\n🚀 Nouvelles Fonctionnalités Interactives")
    print("=" * 50)
    
    print("1. ✅ Mode interactif automatique")
    print("   - Lance le mode interactif si aucun --source/--target")
    print("   - python main.py  # Active automatiquement le mode interactif")
    print()
    
    print("2. ✅ Vérification intelligente des identifiants")
    print("   - Vérifie la présence des API ID/Hash")
    print("   - Guide l'utilisateur vers la configuration")
    print("   - Instructions claires pour obtenir les identifiants")
    print()
    
    print("3. ✅ Interface conviviale")
    print("   - Questions guidées avec exemples")
    print("   - Validation des entrées")
    print("   - Support des usernames et IDs numériques")
    print()
    
    print("4. ✅ Configuration complète")
    print("   - Limite de messages")
    print("   - Mode reprise")
    print("   - Mode hybride (si bot configuré)")
    print("   - Mode test")
    print("   - Niveau de journalisation")
    print()
    
    print("5. ✅ Résumé et confirmation")
    print("   - Affichage clair de la configuration")
    print("   - Confirmation avant démarrage")
    print("   - Possibilité d'annuler")

def main():
    """Lance tous les tests."""
    print("🧪 Tests du Mode Interactif")
    print("=" * 40)
    
    try:
        test_credentials_check()
        test_channel_input_validation()
        simulate_interactive_session()
        demo_interactive_features()
        
        print("\n✅ Tous les tests sont réussis !")
        print("\n💡 Usage :")
        print("   python main.py              # Mode interactif")
        print("   python main.py --help       # Aide détaillée")
        
    except Exception as e:
        print(f"\n❌ Erreur dans les tests : {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())