#!/usr/bin/env python3
"""
Script para probar el sistema de autenticación desde el frontend
"""

import time
import json
import requests
from datetime import datetime

# Colores para output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test(message):
    print(f"\n{BLUE}► {message}{RESET}")

def print_success(message):
    print(f"  {GREEN}✓ {message}{RESET}")

def print_error(message):
    print(f"  {RED}✗ {message}{RESET}")

def print_info(message):
    print(f"  {YELLOW}ℹ {message}{RESET}")

def test_registration_form():
    """Prueba el formulario de registro a través del frontend"""
    print_test("Testing Registration through Frontend Form")
    
    timestamp = int(time.time())
    test_data = {
        "username": f"frontend_user_{timestamp}",
        "email": f"frontend_{timestamp}@test.com",
        "password": "TestPassword123!",
        "confirmPassword": "TestPassword123!"
    }
    
    print_info(f"Intentando registrar usuario: {test_data['username']}")
    
    # Primero, verificar que la página de registro carga
    try:
        response = requests.get("http://localhost:3000/register")
        if response.status_code == 200:
            print_success("Página de registro cargada correctamente")
        else:
            print_error(f"Error al cargar página de registro: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"No se puede conectar al frontend: {e}")
        return None
    
    # Simular el envío del formulario (usando la API directamente ya que no podemos ejecutar JS)
    try:
        # El frontend debería enviar estos datos al backend a través del proxy
        registration_data = {
            "username": test_data["username"],
            "email": test_data["email"],
            "password": test_data["password"]
        }
        
        response = requests.post(
            "http://localhost:3000/api/auth/register/",
            json=registration_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            data = response.json()
            print_success(f"Usuario registrado exitosamente: {data['username']}")
            return test_data
        else:
            print_error(f"Error en registro: {response.status_code}")
            if response.text:
                try:
                    error_data = response.json()
                    print_info(f"Detalle del error: {json.dumps(error_data, indent=2)}")
                except:
                    print_info(f"Respuesta: {response.text[:200]}")
            return None
            
    except Exception as e:
        print_error(f"Error al enviar formulario de registro: {e}")
        return None

def test_login_form(user_data):
    """Prueba el formulario de login a través del frontend"""
    print_test("Testing Login through Frontend Form")
    
    if not user_data:
        print_error("No hay datos de usuario para probar login")
        return None
    
    print_info(f"Intentando login con usuario: {user_data['username']}")
    
    # Verificar que la página de login carga
    try:
        response = requests.get("http://localhost:3000/login")
        if response.status_code == 200:
            print_success("Página de login cargada correctamente")
        else:
            print_error(f"Error al cargar página de login: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"No se puede conectar al frontend: {e}")
        return None
    
    # Simular el envío del formulario de login
    try:
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        
        response = requests.post(
            "http://localhost:3000/api/auth/token/",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Login exitoso")
            print_info(f"Access token recibido: {data['access'][:20]}...")
            print_info(f"Refresh token recibido: {data['refresh'][:20]}...")
            return data
        else:
            print_error(f"Error en login: {response.status_code}")
            if response.text:
                print_info(f"Respuesta: {response.text[:200]}")
            return None
            
    except Exception as e:
        print_error(f"Error al enviar formulario de login: {e}")
        return None

def test_form_validation():
    """Prueba la validación de formularios en el frontend"""
    print_test("Testing Form Validation")
    
    # Probar registro con datos inválidos
    invalid_cases = [
        {
            "name": "Usuario muy corto",
            "data": {"username": "ab", "email": "test@test.com", "password": "Pass123!"},
            "expected_error": "usuario debe tener al menos 3 caracteres"
        },
        {
            "name": "Email inválido",
            "data": {"username": "testuser", "email": "invalid-email", "password": "Pass123!"},
            "expected_error": "correo válido"
        },
        {
            "name": "Contraseña muy corta",
            "data": {"username": "testuser", "email": "test@test.com", "password": "123"},
            "expected_error": "al menos 8 caracteres"
        }
    ]
    
    for case in invalid_cases:
        print_info(f"Probando: {case['name']}")
        try:
            response = requests.post(
                "http://localhost:3000/api/auth/register/",
                json=case['data'],
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 400:
                print_success(f"Validación correcta: rechazado como se esperaba")
            else:
                print_error(f"Validación incorrecta: se esperaba error 400, se recibió {response.status_code}")
                
        except Exception as e:
            print_error(f"Error en prueba de validación: {e}")

def test_auth_persistence():
    """Prueba que la autenticación persiste correctamente"""
    print_test("Testing Authentication Persistence")
    
    # Crear un usuario y hacer login
    timestamp = int(time.time())
    user_data = {
        "username": f"persist_user_{timestamp}",
        "email": f"persist_{timestamp}@test.com",
        "password": "PersistTest123!"
    }
    
    # Registrar usuario
    try:
        response = requests.post(
            "http://localhost:3000/api/auth/register/",
            json=user_data
        )
        if response.status_code != 201:
            print_error("No se pudo crear usuario de prueba")
            return
    except:
        print_error("Error al crear usuario de prueba")
        return
    
    # Login
    session = requests.Session()
    try:
        response = session.post(
            "http://localhost:3000/api/auth/token/",
            json={"username": user_data["username"], "password": user_data["password"]}
        )
        
        if response.status_code == 200:
            tokens = response.json()
            print_success("Login exitoso, tokens obtenidos")
            
            # Probar acceso a endpoint protegido
            response = session.get(
                "http://localhost:3000/api/auth/me/",
                headers={"Authorization": f"Bearer {tokens['access']}"}
            )
            
            if response.status_code == 200:
                user_info = response.json()
                print_success(f"Acceso autorizado a endpoint protegido")
                print_info(f"Usuario autenticado: {user_info['username']}")
            else:
                print_error(f"No se pudo acceder a endpoint protegido: {response.status_code}")
        else:
            print_error("Login falló")
            
    except Exception as e:
        print_error(f"Error en prueba de persistencia: {e}")

def run_frontend_tests():
    """Ejecuta todas las pruebas del frontend"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}    Frontend Authentication Tests{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Probar registro
    user_data = test_registration_form()
    
    # 2. Probar login
    if user_data:
        tokens = test_login_form(user_data)
    
    # 3. Probar validaciones
    test_form_validation()
    
    # 4. Probar persistencia de autenticación
    test_auth_persistence()
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{GREEN}✓ Pruebas del frontend completadas{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

if __name__ == "__main__":
    run_frontend_tests()
