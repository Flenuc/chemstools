#!/bin/bash

echo "=== Probando API del Simulador de Reacciones ==="
echo ""

# 1. Health Check
echo "1. Health Check:"
curl -X GET http://localhost:8000/api/reactions/health/
echo -e "\n"

# 2. Reacción de Síntesis (H2 + O2 -> H2O)
echo "2. Reacción de Síntesis:"
curl -X POST -H "Content-Type: application/json" -d '{"equation": "H2 + O2 -> H2O"}' http://localhost:8000/api/reactions/balance-equation/
echo -e "\n"

# 3. Reacción de Descomposición (H2O2 -> H2O + O2)
echo "3. Reacción de Descomposición:"
curl -X POST -H "Content-Type: application/json" -d '{"equation": "H2O2 -> H2O + O2"}' http://localhost:8000/api/reactions/balance-equation/
echo -e "\n"

# 4. Reacción de Combustión (CH4 + O2 -> CO2 + H2O)
echo "4. Reacción de Combustión:"
curl -X POST -H "Content-Type: application/json" -d '{"equation": "CH4 + O2 -> CO2 + H2O"}' http://localhost:8000/api/reactions/balance-equation/
echo -e "\n"

echo "=== Pruebas Completadas ==="

