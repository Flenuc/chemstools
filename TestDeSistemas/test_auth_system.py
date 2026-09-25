#!/usr/bin/env python3
"""
Script de prueba integral para el sistema de autenticación de ChemsTools
Valida registro, login, tokens y la integración completa frontend-backend
"""

import requests
import json
import time
import random
import sys
from datetime import datetime

# Configuración
FRONTEND_URL = "http://localhost:3000"
BACKEND_URL = "http://localhost:8000"

# Colores para output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test(test_name):
    """Imprime el nombre del test"""
    print(f"\n{BLUE}► Testing: {test_name}{RESET}")

def print_success(message):
    """Imprime mensaje de éxito"""
    print(f"  {GREEN}✓ {message}{RESET}")

def print_error(message):
    """Imprime mensaje de error"""
    print(f"  {RED}✗ {message}{RESET}")

def print_info(message):
    """Imprime mensaje informativo"""
    print(f"  {YELLOW}ℹ {message}{RESET}")

def test_backend_health():
    """Prueba que el backend está funcionando"""
    print_test("Backend Health Check")
    try:
        # Usar el endpoint admin como health check
        response = requests.get(f"{BACKEND_URL}/admin/", timeout=5, allow_redirects=True)
        # Si recibimos 200 o 302 (redirección a login), el backend está funcionando
        if response.status_code in [200, 302]:
            print_success(f"Backend is running at {BACKEND_URL}")
            return True
        else:
            print_error(f"Backend returned status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Cannot connect to backend: {e}")
        return False

def test_frontend_health():
    """Prueba que el frontend está funcionando"""
    print_test("Frontend Health Check")
    try:
        response = requests.get(f"{FRONTEND_URL}/", timeout=5)
        if response.status_code == 200:
            print_success(f"Frontend is running at {FRONTEND_URL}")
            return True
        else:
            print_error(f"Frontend returned status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Cannot connect to frontend: {e}")
        return False

def test_user_registration(via_proxy=False):
    """Prueba el registro de usuario"""
    endpoint = "Frontend Proxy" if via_proxy else "Backend Direct"
    print_test(f"User Registration ({endpoint})")
    
    # Generar datos únicos con sufijo para diferenciar proxy
    timestamp = int(time.time())
    suffix = "_proxy" if via_proxy else ""
    username = f"testuser_{timestamp}{suffix}"
    email = f"test_{timestamp}{suffix}@example.com"
    password = "TestPassword123!"
    
    # URL según el endpoint
    url = f"{FRONTEND_URL if via_proxy else BACKEND_URL}/api/auth/register/"
    
    try:
        response = requests.post(
            url,
            json={
                "username": username,
                "email": email,
                "password": password
            },
            timeout=10
        )
        
        if response.status_code == 201:
            data = response.json()
            print_success(f"User registered: {data['username']} ({data['email']})")
            return {
                "username": username,
                "email": email,
                "password": password,
                "id": data.get("id")
            }
        elif response.status_code == 400:
            errors = response.json()
            print_error(f"Registration failed: {errors}")
            return None
        else:
            print_error(f"Unexpected status: {response.status_code}")
            print_info(f"Response: {response.text[:200]}")
            return None
    except Exception as e:
        print_error(f"Registration error: {e}")
        return None

def test_user_login(user_data, via_proxy=False):
    """Prueba el login de usuario"""
    endpoint = "Frontend Proxy" if via_proxy else "Backend Direct"
    print_test(f"User Login ({endpoint})")
    
    if not user_data:
        print_error("No user data provided")
        return None
    
    # URL según el endpoint
    url = f"{FRONTEND_URL if via_proxy else BACKEND_URL}/api/auth/token/"
    
    try:
        response = requests.post(
            url,
            json={
                "username": user_data["username"],
                "password": user_data["password"]
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Login successful for {user_data['username']}")
            if "access" in data and "refresh" in data:
                print_info(f"Access token: {data['access'][:20]}...")
                print_info(f"Refresh token: {data['refresh'][:20]}...")
                return data
            else:
                print_error("Tokens not found in response")
                return None
        else:
            print_error(f"Login failed with status: {response.status_code}")
            print_info(f"Response: {response.text[:200]}")
            return None
    except Exception as e:
        print_error(f"Login error: {e}")
        return None

def test_token_refresh(tokens, via_proxy=False):
    """Prueba el refresh de tokens"""
    endpoint = "Frontend Proxy" if via_proxy else "Backend Direct"
    print_test(f"Token Refresh ({endpoint})")
    
    if not tokens or "refresh" not in tokens:
        print_error("No refresh token provided")
        return None
    
    # URL según el endpoint
    url = f"{FRONTEND_URL if via_proxy else BACKEND_URL}/api/auth/token/refresh/"
    
    try:
        response = requests.post(
            url,
            json={"refresh": tokens["refresh"]},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Token refreshed successfully")
            print_info(f"New access token: {data['access'][:20]}...")
            return data
        else:
            print_error(f"Token refresh failed with status: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Token refresh error: {e}")
        return None

def test_protected_endpoint(tokens, via_proxy=False):
    """Prueba un endpoint protegido"""
    endpoint = "Frontend Proxy" if via_proxy else "Backend Direct"
    print_test(f"Protected Endpoint Access ({endpoint})")
    
    if not tokens or "access" not in tokens:
        print_error("No access token provided")
        return False
    
    # URL según el endpoint
    url = f"{FRONTEND_URL if via_proxy else BACKEND_URL}/api/auth/me/"
    
    try:
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {tokens['access']}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Protected endpoint accessed successfully")
            print_info(f"User data: {data}")
            return True
        elif response.status_code == 401:
            print_error("Unauthorized - token may be invalid")
            return False
        else:
            print_error(f"Unexpected status: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Protected endpoint error: {e}")
        return False

def run_full_test_suite():
    """Ejecuta todas las pruebas"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}    ChemsTools Authentication System Test Suite{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "backend_health": False,
        "frontend_health": False,
        "registration_direct": False,
        "registration_proxy": False,
        "login_direct": False,
        "login_proxy": False,
        "token_refresh": False,
        "protected_endpoint": False
    }
    
    # 1. Health checks
    results["backend_health"] = test_backend_health()
    results["frontend_health"] = test_frontend_health()
    
    if not results["backend_health"]:
        print(f"\n{RED}Backend is not running. Please start it first.{RESET}")
        return results
    
    # 2. Test registration directly to backend
    user_data = test_user_registration(via_proxy=False)
    results["registration_direct"] = user_data is not None
    
    # 3. Test login directly to backend
    if user_data:
        tokens = test_user_login(user_data, via_proxy=False)
        results["login_direct"] = tokens is not None
        
        # 4. Test token refresh
        if tokens:
            new_tokens = test_token_refresh(tokens, via_proxy=False)
            results["token_refresh"] = new_tokens is not None
            
            # 5. Test protected endpoint
            test_tokens = new_tokens if new_tokens else tokens
            results["protected_endpoint"] = test_protected_endpoint(test_tokens, via_proxy=False)
    
    # 6. Test through frontend proxy
    if results["frontend_health"]:
        # Registration via proxy
        proxy_user = test_user_registration(via_proxy=True)
        results["registration_proxy"] = proxy_user is not None
        
        # Login via proxy
        if proxy_user:
            proxy_tokens = test_user_login(proxy_user, via_proxy=True)
            results["login_proxy"] = proxy_tokens is not None
    
    # Print summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}    TEST RESULTS SUMMARY{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, passed_test in results.items():
        status = f"{GREEN}PASS{RESET}" if passed_test else f"{RED}FAIL{RESET}"
        test_display = test_name.replace("_", " ").title()
        print(f"  {test_display:.<40} [{status}]")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"\n{GREEN}✓ All tests passed! The authentication system is working correctly.{RESET}")
    elif passed > total // 2:
        print(f"\n{YELLOW}⚠ Some tests failed. Please check the errors above.{RESET}")
    else:
        print(f"\n{RED}✗ Most tests failed. There may be a configuration issue.{RESET}")
    
    return results

if __name__ == "__main__":
    results = run_full_test_suite()
    
    # Exit with error code if any test failed
    sys.exit(0 if all(results.values()) else 1)
