import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from games.models import MemoryGame, MemoryStats
from games.utils import MemoryGameEngine

User = get_user_model()

class MemoryGameEngineTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_memory_game(self):
        """Probar creación de juego Memory"""
        game = MemoryGameEngine.create_memory_game(self.user, difficulty='easy', total_pairs=4)
        
        self.assertIsNotNone(game)
        self.assertEqual(game.user, self.user)
        self.assertEqual(game.difficulty, 'easy')
        self.assertEqual(game.total_pairs, 4)
        self.assertFalse(game.is_completed)
        self.assertEqual(game.pairs_found, 0)
        
        # Verificar que se crearon 8 cartas (4 pares)
        self.assertEqual(len(game.cards_data), 8)
        
        # Verificar que hay 4 cartas de nombre y 4 de fórmula
        name_cards = [card for card in game.cards_data if card['type'] == 'name']
        formula_cards = [card for card in game.cards_data if card['type'] == 'formula']
        
        self.assertEqual(len(name_cards), 4)
        self.assertEqual(len(formula_cards), 4)
    
    def test_reveal_card_basic(self):
        """Probar revelado básico de carta"""
        game = MemoryGameEngine.create_memory_game(self.user, difficulty='easy', total_pairs=3)
        
        # Revelar primera carta
        result, error = MemoryGameEngine.reveal_card(game, 0)
        
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        self.assertIn('card', result)
        self.assertTrue(result['card']['is_revealed'])
        self.assertFalse(result['is_match'])
    
    def test_reveal_card_match(self):
        """Probar coincidencia de cartas"""
        game = MemoryGameEngine.create_memory_game(self.user, difficulty='easy', total_pairs=2)
        
        # Encontrar dos cartas que forman un par
        pair_id = game.cards_data[0]['pair_id']
        matching_cards = [
            i for i, card in enumerate(game.cards_data) 
            if card['pair_id'] == pair_id
        ]
        
        self.assertEqual(len(matching_cards), 2)
        
        # Revelar primera carta del par
        result1, error1 = MemoryGameEngine.reveal_card(game, matching_cards[0])
        self.assertIsNone(error1)
        self.assertFalse(result1['is_match'])
        
        # Revelar segunda carta del par
        result2, error2 = MemoryGameEngine.reveal_card(game, matching_cards[1])
        self.assertIsNone(error2)
        self.assertTrue(result2['is_match'])
        
        # Verificar que el juego se actualizó
        game.refresh_from_db()
        self.assertEqual(game.pairs_found, 1)
        self.assertEqual(game.attempts, 1)
        self.assertGreater(game.score, 0)
    
    def test_game_completion(self):
        """Probar finalización del juego"""
        game = MemoryGameEngine.create_memory_game(self.user, difficulty='easy', total_pairs=1)
        
        # Encontrar el único par
        pair_id = game.cards_data[0]['pair_id']
        matching_cards = [
            i for i, card in enumerate(game.cards_data) 
            if card['pair_id'] == pair_id
        ]
        
        # Revelar ambas cartas
        MemoryGameEngine.reveal_card(game, matching_cards[0])
        result, error = MemoryGameEngine.reveal_card(game, matching_cards[1])
        
        self.assertIsNone(error)
        self.assertTrue(result['is_match'])
        self.assertTrue(result['game_completed'])
        
        # Verificar que el juego está completo
        game.refresh_from_db()
        self.assertTrue(game.is_completed)
        self.assertIsNotNone(game.completed_at)
        self.assertIsNotNone(game.total_time_seconds)
    
    def test_hide_revealed_cards(self):
        """Probar ocultado de cartas reveladas"""
        game = MemoryGameEngine.create_memory_game(self.user, difficulty='easy', total_pairs=3)
        
        # Revelar una carta
        MemoryGameEngine.reveal_card(game, 0)
        
        # Verificar que está revelada
        game.refresh_from_db()
        self.assertTrue(game.cards_data[0]['is_revealed'])
        
        # Ocultar cartas
        MemoryGameEngine.hide_revealed_cards(game)
        
        # Verificar que se ocultó
        game.refresh_from_db()
        self.assertFalse(game.cards_data[0]['is_revealed'])
    
    def test_score_calculation(self):
        """Probar cálculo de puntuación por dificultad"""
        easy_score = MemoryGameEngine._calculate_pair_score('easy')
        medium_score = MemoryGameEngine._calculate_pair_score('medium')
        hard_score = MemoryGameEngine._calculate_pair_score('hard')
        
        self.assertEqual(easy_score, 100)
        self.assertEqual(medium_score, 200)
        self.assertEqual(hard_score, 300)
    
    def test_prevent_reveal_matched_card(self):
        """Probar que no se pueden revelar cartas ya emparejadas"""
        game = MemoryGameEngine.create_memory_game(self.user, difficulty='easy', total_pairs=2)
        
        # Marcar una carta como emparejada manualmente
        cards = game.cards_data.copy()
        cards[0]['is_matched'] = True
        game.cards_data = cards
        game.save()
        
        # Intentar revelar carta emparejada
        result, error = MemoryGameEngine.reveal_card(game, 0)
        
        self.assertIsNotNone(error)
        self.assertIsNone(result)
        self.assertIn("ya está revelada o emparejada", error)

class MemoryGameAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_start_game_endpoint(self):
        """Probar endpoint de inicio de juego"""
        response = self.client.post('/api/games/memory/start_game/', {
            'difficulty': 'easy',
            'total_pairs': 4
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('game', response.data)
        self.assertEqual(response.data['game']['difficulty'], 'easy')
        self.assertEqual(response.data['game']['total_pairs'], 4)
    
    def test_start_game_default_values(self):
        """Probar valores por defecto al iniciar juego"""
        response = self.client.post('/api/games/memory/start_game/', {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['game']['difficulty'], 'easy')
        self.assertEqual(response.data['game']['total_pairs'], 6)
    
    def test_reveal_card_endpoint(self):
        """Probar endpoint de revelar carta"""
        # Crear juego primero
        game = MemoryGameEngine.create_memory_game(self.user, difficulty='easy', total_pairs=3)
        
        response = self.client.post('/api/games/memory/reveal_card/', {
            'game_id': game.id,
            'card_position': 0
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('result', response.data)
        self.assertIn('game', response.data)
    
    def test_hide_cards_endpoint(self):
        """Probar endpoint de ocultar cartas"""
        game = MemoryGameEngine.create_memory_game(self.user, difficulty='easy', total_pairs=3)
        
        response = self.client.post('/api/games/memory/hide_cards/', {
            'game_id': game.id
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_current_game_endpoint(self):
        """Probar endpoint de juego actual"""
        # Sin juego activo
        response = self.client.get('/api/games/memory/current_game/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIsNone(response.data['game'])
        
        # Con juego activo
        game = MemoryGameEngine.create_memory_game(self.user, difficulty='medium', total_pairs=4)
        
        response = self.client.get('/api/games/memory/current_game/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIsNotNone(response.data['game'])
        self.assertEqual(response.data['game']['id'], game.id)
    
    def test_stats_endpoint(self):
        """Probar endpoint de estadísticas"""
        response = self.client.get('/api/games/memory/stats/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('stats', response.data)
        
        # Verificar estructura de estadísticas
        stats = response.data['stats']
        self.assertEqual(stats['games_played'], 0)
        self.assertEqual(stats['games_completed'], 0)
        self.assertEqual(stats['completion_rate'], 0.0)
    
    def test_leaderboard_endpoint(self):
        """Probar endpoint de clasificación"""
        response = self.client.get('/api/games/memory/leaderboard/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('leaderboard', response.data)
        self.assertIsInstance(response.data['leaderboard'], list)
    
    def test_end_game_endpoint(self):
        """Probar endpoint de terminar juego"""
        # Sin juego activo
        response = self.client.delete('/api/games/memory/end_game/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])
        
        # Con juego activo
        game = MemoryGameEngine.create_memory_game(self.user, difficulty='easy', total_pairs=3)
        
        response = self.client.delete('/api/games/memory/end_game/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verificar que el juego se marcó como completado
        game.refresh_from_db()
        self.assertTrue(game.is_completed)
    
    def test_invalid_game_id(self):
        """Probar con ID de juego inválido"""
        response = self.client.post('/api/games/memory/reveal_card/', {
            'game_id': 99999,
            'card_position': 0
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])
    
    def test_invalid_card_position(self):
        """Probar con posición de carta inválida"""
        game = MemoryGameEngine.create_memory_game(self.user, difficulty='easy', total_pairs=3)
        
        response = self.client.post('/api/games/memory/reveal_card/', {
            'game_id': game.id,
            'card_position': 999  # Posición inválida
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_continue_existing_game(self):
        """Probar continuación de juego existente"""
        # Crear juego
        game = MemoryGameEngine.create_memory_game(self.user, difficulty='easy', total_pairs=3)
        
        # Intentar crear otro juego
        response = self.client.post('/api/games/memory/start_game/', {
            'difficulty': 'medium',
            'total_pairs': 5
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('Continuando partida existente', response.data['message'])
        # Debería devolver el juego existente, no crear uno nuevo
        self.assertEqual(response.data['game']['id'], game.id)
        self.assertEqual(response.data['game']['difficulty'], 'easy')  # No cambió

class MemoryStatsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_stats_creation(self):
        """Probar creación de estadísticas"""
        stats, created = MemoryStats.objects.get_or_create(
            user=self.user,
            defaults={
                'games_played': 0,
                'games_completed': 0
            }
        )
        
        self.assertTrue(created)
        self.assertEqual(stats.games_played, 0)
        self.assertEqual(stats.completion_rate, 0.0)
        self.assertEqual(stats.average_accuracy, 0.0)
    
    def test_stats_update_after_game(self):
        """Probar actualización de estadísticas después del juego"""
        # Crear y completar un juego
        game = MemoryGameEngine.create_memory_game(self.user, difficulty='easy', total_pairs=1)
        
        # Simular finalización del juego
        game.is_completed = True
        game.pairs_found = 1
        game.attempts = 2
        game.total_time_seconds = 60
        
        MemoryGameEngine._update_stats(game)
        
        # Verificar estadísticas
        stats = MemoryStats.objects.get(user=self.user)
        self.assertEqual(stats.games_played, 1)
        self.assertEqual(stats.games_completed, 1)
        self.assertEqual(stats.completion_rate, 100.0)
        self.assertEqual(stats.total_pairs_found, 1)
        self.assertEqual(stats.total_attempts, 2)
        self.assertEqual(stats.average_accuracy, 50.0)  # 1/2 * 100
        self.assertEqual(stats.best_time_easy, 60)