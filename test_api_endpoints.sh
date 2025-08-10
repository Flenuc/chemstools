#!/bin/bash

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Testing ChemsTools API Endpoints${NC}"
echo "===================================="

# Primero, vamos a hacer login para obtener un token
echo -e "\n${YELLOW}1. Testing Login...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test1234"}')

if echo "$LOGIN_RESPONSE" | grep -q "access"; then
  echo -e "${GREEN}✓ Login successful${NC}"
  ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access":"[^"]*' | grep -o '[^"]*$')
  echo "Token obtained: ${ACCESS_TOKEN:0:20}..."
else
  echo -e "${RED}✗ Login failed${NC}"
  echo "$LOGIN_RESPONSE"
  exit 1
fi

# Test Memory Game endpoints
echo -e "\n${YELLOW}2. Testing Memory Game Current Game...${NC}"
CURRENT_GAME=$(curl -s -X GET http://localhost:8000/api/games/memory/current_game/ \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if echo "$CURRENT_GAME" | grep -q "success"; then
  echo -e "${GREEN}✓ Current game endpoint working${NC}"
else
  echo -e "${RED}✗ Current game endpoint failed${NC}"
  echo "$CURRENT_GAME"
fi

echo -e "\n${YELLOW}3. Testing Memory Game Stats...${NC}"
STATS=$(curl -s -X GET http://localhost:8000/api/games/memory/stats/ \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if echo "$STATS" | grep -q "success"; then
  echo -e "${GREEN}✓ Stats endpoint working${NC}"
else
  echo -e "${RED}✗ Stats endpoint failed${NC}"
  echo "$STATS"
fi

echo -e "\n${YELLOW}4. Testing Memory Game Leaderboard...${NC}"
LEADERBOARD=$(curl -s -X GET http://localhost:8000/api/games/memory/leaderboard/ \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if echo "$LEADERBOARD" | grep -q "success"; then
  echo -e "${GREEN}✓ Leaderboard endpoint working${NC}"
else
  echo -e "${RED}✗ Leaderboard endpoint failed${NC}"
  echo "$LEADERBOARD"
fi

echo -e "\n${YELLOW}5. Testing Start New Memory Game...${NC}"
START_GAME=$(curl -s -X POST http://localhost:8000/api/games/memory/start_game/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"difficulty": "easy", "total_pairs": 6}')

if echo "$START_GAME" | grep -q "success"; then
  echo -e "${GREEN}✓ Start game endpoint working${NC}"
  GAME_ID=$(echo "$START_GAME" | grep -o '"id":[0-9]*' | grep -o '[0-9]*')
  echo "Game ID: $GAME_ID"
else
  echo -e "${RED}✗ Start game endpoint failed${NC}"
  echo "$START_GAME"
fi

echo -e "\n${GREEN}All tests completed!${NC}"
