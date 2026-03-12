#!/usr/bin/env python3
"""Test script per l'API Backed Research Agent"""

import requests
import time
import subprocess
import sys
from pathlib import Path

API_URL = "http://127.0.0.1:8000"
HEALTH_ENDPOINT = f"{API_URL}/v1/health"
ANALYZE_ENDPOINT = f"{API_URL}/v1/analyze"

# API key di default
API_KEY = "GIT3PRIVATE"

def test_health():
    """Test dell'endpoint di health"""
    print("Testing /v1/health endpoint...")
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("[ERRORE] Server non raggiungibile. Assicurati che l'API sia avviata.")
        return False
    except Exception as e:
        print(f"[ERRORE] Errore: {e}")
        return False

def test_analyze():
    """Test dell'endpoint di analisi"""
    print("\nTesting /v1/analyze endpoint...")
    payload = {
        "source": "https://www.futard.io/launch/6JSEvdUfQuo8rh3M18Wex5xmSacUuBozz9uQEgFC81pX",
        "mode": "rules"
    }
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    try:
        print(f"Invio richiesta a {ANALYZE_ENDPOINT}...")
        response = requests.post(ANALYZE_ENDPOINT, json=payload, headers=headers, timeout=120)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Analisi completata!")
            print(f"Request ID: {result.get('request_id')}")
            print(f"Score: {result.get('result', {}).get('score', {}).get('value', 'N/A')}")
            return True
        else:
            print(f"[ERRORE] Errore: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("[ERRORE] Server non raggiungibile.")
        return False
    except Exception as e:
        print(f"[ERRORE] Errore: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Test API Backed Research Agent")
    print("=" * 60)
    
    # Test health
    if not test_health():
        print("\n[AVVISO] Avvio del server...")
        print("Esegui in un altro terminale:")
        print("  uvicorn investment_agent.api:app --host 127.0.0.1 --port 8000")
        sys.exit(1)
    
    # Test analyze
    test_analyze()
    
    print("\n" + "=" * 60)
    print("Test completati!")
    print("=" * 60)
