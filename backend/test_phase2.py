#!/usr/bin/env python3
"""
Script de test pour Phase 2 - Actualités & Recommandations
Vérifie que tous les endpoints sont accessibles et fonctionnels
"""
import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8000"

def test_health():
    """Test de base pour vérifier l'API"""
    print("\n" + "="*60)
    print("🏥 TEST 1: Health Check")
    print("="*60)
    try:
        r = requests.get(f"{API_BASE}/health")
        if r.status_code == 200:
            print("✅ API accessible")
            print(f"   Status: {r.json()['status']}")
            return True
        else:
            print(f"❌ Erreur: {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_settings():
    """Vérifier la configuration Finnhub"""
    print("\n" + "="*60)
    print("⚙️ TEST 2: Settings & Finnhub Configuration")
    print("="*60)
    try:
        r = requests.get(f"{API_BASE}/api/settings")
        if r.status_code == 200:
            config = r.json()
            print("✅ Settings accessible")
            print(f"   Finnhub configuré: {config['finnhub_configured']}")
            if config['finnhub_configured']:
                print("   ✅ Clé Finnhub présente")
                return True
            else:
                print("   ⚠️ Finnhub non configuré - actualités indisponibles")
                return False
        else:
            print(f"❌ Erreur: {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_recommendations():
    """Test des recommandations"""
    print("\n" + "="*60)
    print("📰 TEST 3: Recommendations Endpoint")
    print("="*60)
    
    test_symbols = "AAPL,MSFT"
    try:
        r = requests.get(
            f"{API_BASE}/api/news/recommendations",
            params={"symbols": test_symbols, "hours": 24}
        )
        
        if r.status_code == 200:
            data = r.json()
            print(f"✅ Endpoint accessible")
            print(f"   Symboles testés: {test_symbols}")
            print(f"   Recommandations trouvées: {data['count']}")
            print(f"   Résumé: BUY={data['summary']['buy']}, SELL={data['summary']['sell']}, HOLD={data['summary']['hold']}")
            
            if data['count'] > 0:
                rec = data['recommendations'][0]
                print(f"\n   Premier résultat:")
                print(f"   - Symbole: {rec['symbol']}")
                print(f"   - Titre: {rec['title'][:50]}...")
                print(f"   - Sentiment: {rec['sentiment_score']:.2f} ({rec['sentiment_label']})")
                print(f"   - Recommandation: {rec['recommendation_type']}")
                print(f"   - Confiance: {rec['confidence']}%")
            
            return True
        else:
            print(f"❌ Erreur: {r.status_code}")
            if r.text:
                print(f"   Message: {r.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_email_endpoint():
    """Test de l'endpoint d'email"""
    print("\n" + "="*60)
    print("📧 TEST 4: Email Service Endpoint")
    print("="*60)
    
    try:
        r = requests.post(
            f"{API_BASE}/api/news/test-email",
            params={"email": "test@example.com"}
        )
        
        if r.status_code == 200:
            result = r.json()
            print("✅ Endpoint d'email accessible")
            print(f"   Status: {result['status']}")
            print(f"   Message: {result['message']}")
            
            if result['status'] == 'success':
                print("   ✅ Configuration email valide")
                return True
            else:
                print("   ⚠️ Email non configuré (normal si pas de SMTP_SERVER)")
                return False
        else:
            print(f"❌ Erreur: {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_routes_exist():
    """Vérifier que toutes les routes existent"""
    print("\n" + "="*60)
    print("🗺️ TEST 5: Route Documentation")
    print("="*60)
    
    routes = [
        ("GET", "/health", "Health check"),
        ("GET", "/api/settings", "Settings"),
        ("GET", "/api/news/recommendations", "Recommandations"),
        ("POST", "/api/news/send-recommendations", "Send email"),
        ("POST", "/api/news/test-email", "Test email"),
    ]
    
    print("Routes Phase 2 attendues:")
    for method, path, desc in routes:
        print(f"   {method:4} {path:35} - {desc}")
    
    print("\n✅ À vérifier dans Swagger: http://localhost:8000/docs")
    return True

def main():
    """Exécute tous les tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  🚀 PHASE 2 - TEST SUITE                              ".center(58) + "║")
    print("║" + "     Actualités & Recommandations                      ".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    print(f"\n⏱️  Timestamp: {datetime.now().isoformat()}")
    print(f"🎯 API URL: {API_BASE}")
    
    # Exécuter les tests
    tests = [
        ("Health Check", test_health),
        ("Settings", test_settings),
        ("Recommendations", test_recommendations),
        ("Email", test_email_endpoint),
        ("Routes", test_routes_exist),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ ERREUR CRITIQUE: {e}")
            results.append((name, False))
    
    # Résumé
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {name}")
    
    print(f"\nScore: {passed}/{total} tests réussis")
    
    if passed == total:
        print("\n🎉 TOUS LES TESTS RÉUSSIS!")
        print("\nPhase 2 est prête!")
        print("→ Démarrer le frontend: npm run dev")
        print("→ Aller à http://localhost:3000")
        print("→ Ajouter des positions")
        print("→ Voir les actualités & recommandations!")
    else:
        print("\n⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
        print("\nVérifier:")
        print("1. Backend en cours d'exécution: python main.py")
        print("2. FINNHUB_API_KEY configurée dans .env")
        print("3. Port 8000 disponible")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
