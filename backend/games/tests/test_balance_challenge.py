# backend/games/tests/test_balance_challenge.py

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from games.models import BalanceChallengeGame, BalanceChallengeAttempt, BalanceChallengeStats
from games.utils import BalanceChallengeEngine

User = get_user_model()

class BalanceChallengeEngineTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_balance_challenge(self):
        """Probar creación de desafío de balanceo"""
        game = BalanceChallengeEngine.create_balance_challenge(self.user, difficulty='easy')
        
        self.assertIsNotNone(game)
        self.assertEqual(game.user, self.user)
        self.assertEqual(game.difficulty, 'easy')
        self.assertFalse(game.is_completed)
        self.assertFalse(game.is_correct)
        self.assertEqual(game.attempts, 0)
        self.assertIsNotNone(game.original_equation)
        self.assertIsNotNone(game.target_balanced_equation)
        self.assertIsNotNone(game.target_coefficients)
    
    def test_validate_correct_coefficients(self):
        """Probar validación con coeficientes correctos"""
        # Crear juego con ecuación conocida
        game = BalanceChallengeGame.objects.create(
            user=self.user,
            original_equation='H2 + O2 -> H2O',
            target_balanced_equation='2H2 + O2 -> 2H2O',
            target_coefficients={
                'reactants': [2, 1],
                'products': [2],
                'compounds': {'H2': 2, 'O2': 1, 'H2O': 2}
            },
            difficulty='easy'
        )
        
        # Coeficientes correctos: H2=2, O2=1, H2O=2
        user_coefficients = [2, 1, 2]
        
        result = BalanceChallengeEngine.validate_user_coefficients(game, user_coefficients)
        
        self.assertTrue(result['is_correct'])
        self.assertTrue(result['is_balanced'])
        self.assertTrue(result['is_exact_match'])
        self.assertEqual(result['user_equation'], '2H2 + O2 -> 2H2O')
    
    def test_validate_incorrect_coefficients(self):
        """Probar validación con coeficientes incorrectos"""
        game = BalanceChallengeGame.objects.create(
            user=self.user,
            original_equation='H2 + O2 -> H2O',
            target_balanced_equation='2H2 + O2 -> 2H2O',
            target_coefficients={
                'reactants': [2, 1],
                'products': [2],
                'compounds': {'H2': 2, 'O2': 1, 'H2O': 2}
            },
            difficulty='easy'
        )
        
        # Coeficientes incorrectos: H2=1, O2=1, H2O=1
        user_coefficients = [1, 1, 1]
        
        result = BalanceChallengeEngine.validate_user_coefficients(game, user_coefficients)
        
        self.assertFalse(result['is_correct'])
        self.assertFalse(result['is_balanced'])
        self.assertFalse(result['is_exact_match'])
    
    def test_validate_balanced_but_not_exact(self):
        """Probar validación con ecuación balanceada pero no exacta"""
        game = BalanceChallengeGame.objects.create(
            user=self.user,
            original_equation='H2 + O2 -> H2O',
            target_balanced_equation='2H2 + O2 -> 2H2O',
            target_coefficients={
                'reactants': [2, 1],
                'products': [2],
                'compounds': {'H2': 2, 'O2': 1, 'H2O': 2}
            },
            difficulty='easy'
        )
        
        # Coeficientes balanceados pero múltiplos: H2=4, O2=2, H2O=4
        user_coefficients = [4, 2, 4]
        
        result = BalanceChallengeEngine.validate_user_coefficients(game, user_coefficients)
        
        # Debería estar balanceada pero no ser la respuesta exacta esperada
        self.assertFalse(result['is_correct'])  # No es exacta
        self.assertTrue(result['is_balanced'])   # Pero está balanceada
        self.assertFalse(result['is_exact_match'])
    
    def test_submit_correct_attempt(self):
        """Probar envío de intento correcto"""
        game = BalanceChallengeGame.objects.create(
            user=self.user,
            original_equation='H2 + O2 -> H2O',
            target_balanced_equation='2H2 + O2 -> 2H2O',
            target_coefficients={
                'reactants': [2, 1],
                'products': [2],
                'compounds': {'H2': 2, 'O2': 1, 'H2O': 2}
            },
            difficulty='easy'
        )
        
        user_coefficients = [2, 1, 2]
        attempt, error = BalanceChallengeEngine.submit_attempt(game, user_coefficients, 30)
        
        self.assertIsNone(error)
        self.assertIsNotNone(attempt)
        self.assertTrue(attempt.is_correct)
        
        # Verificar que el juego está completado
        game.refresh_from_db()
        self.assertTrue(game.is_completed)
        self.assertTrue(game.is_correct)
        self.assertEqual(game.attempts, 1)
    
    def test_submit_incorrect_attempt(self):
        """Probar envío de intento incorrecto"""
        game = BalanceChallengeGame.objects.create(
            user=self.user,
            original_equation='H2 + O2 -> H2O',
            target_balanced_equation='2H2 + O2 -> 2H2O',
            target_coefficients={
                'reactants': [2, 1],
                'products': [2],
                'compounds': {'H2': 2, 'O2': 1, 'H2O': 2}
            },
            difficulty='easy'
        )
        
        user_coefficients = [1, 1, 1]
        attempt, error = BalanceChallengeEngine.submit_attempt(game, user_coefficients, 45)
        
        self.assertIsNone(error)
        self.assertIsNotNone(attempt)
        self.assertFalse(attempt.is_correct)
        
        # Verificar que el juego no está completado
        game.refresh_from_db()
        self.assertFalse(game.is_completed)
        self.assertFalse(game.is_correct)
        self.assertEqual(game.attempts, 1)
    
    def test_max_attempts_reached(self):
        """Probar límite de intentos"""
        game = BalanceChallengeGame.objects.create(
            user=self.user,
            original_equation='H2 + O2 -> H2O',
            target_balanced_equation='2H2 + O2 -> 2H2O',
            target_coefficients={
                'reactants': [2, 1],
                'products': [2],
                'compounds': {'H2': 2, 'O2': 1, 'H2O': 2}
            },
            difficulty='easy',
            max_attempts=2
        )
        
        # Primer intento incorrecto
        BalanceChallengeEngine.submit_attempt(game, [1, 1, 1], 30)
        game.refresh_from_db()
        self.assertFalse(game.is_completed)
        
        # Segundo intento incorrecto - debería completar el juego
        BalanceChallengeEngine.submit_attempt(game, [3, 1, 1], 30)
        game.refresh_from_db()
        self.assertTrue(game.is_completed)
        self.assertFalse(game.is_correct)
        
        # Tercer intento - debería fallar
        attempt, error = BalanceChallengeEngine.submit_attempt(game, [2, 1, 2], 30)
        self.assertIsNone(attempt)
        self.assertIsNotNone(error)
    
    def test_get_hints(self):
        """Probar sistema de pistas"""
        game = BalanceChallengeGame.objects.create(
            user=self.user,
            original_equation='H2 + O2 -> H2O',
            target_balanced_equation='2H2 + O2 -> 2H2O',
            target_coefficients={
                'reactants': [2, 1],
                'products': [2],
                'compounds': {'H2': 2, 'O2': 1, 'H2O': 2}
            },
            difficulty='easy'
        )
        
        # Pista de elemento
        hint, error = BalanceChallengeEngine.get_hint(game, 'element')
        self.assertIsNone(error)
        self.assertIsNotNone(hint)
        
        # Pista de coeficiente
        hint, error = BalanceChallengeEngine.get_hint(game, 'coefficient')
        self.assertIsNone(error)
        self.assertIsNotNone(hint)
        self.assertGreater(len(game.hints_used), 0)
        
        # Pista de método
        hint, error = BalanceChallengeEngine.get_hint(game, 'method')
        self.assertIsNone(error)
        self.assertIsNotNone(hint)

class BalanceChallengeAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_start_challenge_endpoint(self):
        """Probar endpoint de inicio de desafío"""
        response = self.client.post('/api/games/balance-challenge/start_challenge/', {
            'difficulty': 'easy'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('game', response.data)
        self.assertEqual(response.data['game']['difficulty'], 'easy')
    
    def test_start_challenge_existing_game(self):
        """Probar continuación de desafío existente"""
        # Crear juego existente
        game = BalanceChallengeEngine.create_balance_challenge(self.user, 'medium')
        
        response = self.client.post('/api/games/balance-challenge/start_challenge/', {
            'difficulty': 'hard'  # Diferente dificultad
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('Continuando desafío existente', response.data['message'])
        # Debería devolver el juego existente, no crear uno nuevo
        self.assertEqual(response.data['game']['id'], game.id)
        self.assertEqual(response.data['game']['difficulty'], 'medium')  # No cambió
    
    def test_submit_coefficients_endpoint(self):
        """Probar endpoint de envío de coeficientes"""
        # Crear juego
        game = BalanceChallengeGame.objects.create(
            user=self.user,
            original_equation='H2 + O2 -> H2O',
            target_balanced_equation='2H2 + O2 -> 2H2O',
            target_coefficients={
                'reactants': [2, 1],
                'products': [2],
                'compounds': {'H2': 2, 'O2': 1, 'H2O': 2}
            },
            difficulty='easy'
        )
        
        response = self.client.post('/api/games/balance-challenge/submit_coefficients/', {
            'game_id': game.id,
            'coefficients': [2, 1, 2],
            'time_taken': 30
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertTrue(response.data['is_correct'])
        self.assertTrue(response.data['game_completed'])
    
    def test_submit_incorrect_coefficients(self):
        """Probar envío de coeficientes incorrectos"""
        game = BalanceChallengeGame.objects.create(
            user=self.user,
            original_equation='H2 + O2 -> H2O',
            target_balanced_equation='2H2 + O2 -> 2H2O',
            target_coefficients={
                'reactants': [2, 1],
                'products': [2],
                'compounds': {'H2': 2, 'O2': 1, 'H2O': 2}
            },
            difficulty='easy'
        )
        
        response = self.client.post('/api/games/balance-challenge/submit_coefficients/', {
            'game_id': game.id,
            'coefficients': [1, 1, 1],
            'time_taken': 45
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertFalse(response.data['is_correct'])
        self.assertFalse(response.data['game_completed'])
    
    def test_get_hint_endpoint(self):
        """Probar endpoint de pistas"""
        game = BalanceChallengeGame.objects.create(
            user=self.user,
            original_equation='H2 + O2 -> H2O',
            target_balanced_equation='2H2 + O2 -> 2H2O',
            target_coefficients={
                'reactants': [2, 1],
                'products': [2],
                'compounds': {'H2': 2, 'O2': 1, 'H2O': 2}
            },
            difficulty='easy'
        )
        
        response = self.client.post('/api/games/balance-challenge/get_hint/', {
            'game_id': game.id,
            'hint_type': 'element'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('hint', response.data)
        self.assertEqual(response.data['hint_type'], 'element')
    
    def test_current_challenge_endpoint(self):
        """Probar endpoint de desafío actual"""
        # Sin desafío activo
        response = self.client.get('/api/games/balance-challenge/current_challenge/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIsNone(response.data['game'])
        
        # Con desafío activo
        game = BalanceChallengeEngine.create_balance_challenge(self.user, 'easy')
        
        response = self.client.get('/api/games/balance-challenge/current_challenge/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIsNotNone(response.data['game'])
        self.assertEqual(response.data['game']['id'], game.id)
    
    def test_stats_endpoint(self):
        """Probar endpoint de estadísticas"""
        response = self.client.get('/api/games/balance-challenge/stats/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('stats', response.data)
        
        # Verificar estructura de estadísticas
        stats = response.data['stats']
        self.assertEqual(stats['games_played'], 0)
        self.assertEqual(stats['accuracy_rate'], 0.0)
    
    def test_leaderboard_endpoint(self):
        """Probar endpoint de clasificación"""
        response = self.client.get('/api/games/balance-challenge/leaderboard/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('leaderboard', response.data)
        self.assertIsInstance(response.data['leaderboard'], list)
    
    def test_end_challenge_endpoint(self):
        """Probar endpoint de terminar desafío"""
        # Sin desafío activo
        response = self.client.delete('/api/games/balance-challenge/end_challenge/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])
        
        # Con desafío activo
        game = BalanceChallengeEngine.create_balance_challenge(self.user, 'easy')
        
        response = self.client.delete('/api/games/balance-challenge/end_challenge/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verificar que el juego se marcó como completado
        game.refresh_from_db()
        self.assertTrue(game.is_completed)
    
    def test_invalid_game_id(self):
        """Probar con ID de juego inválido"""
        response = self.client.post('/api/games/balance-challenge/submit_coefficients/', {
            'game_id': 99999,
            'coefficients': [2, 1, 2],
            'time_taken': 30
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])
    
    def test_invalid_coefficients_data(self):
        """Probar con datos de coeficientes inválidos"""
        game = BalanceChallengeEngine.create_balance_challenge(self.user, 'easy')
        
        # Coeficientes con valores inválidos (negativos)
        response = self.client.post('/api/games/balance-challenge/submit_coefficients/', {
            'game_id': game.id,
            'coefficients': [-1, 1, 2],
            'time_taken': 30
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        
        # Coeficientes con longitud incorrecta
        response = self.client.post('/api/games/balance-challenge/submit_coefficients/', {
            'game_id': game.id,
            'coefficients': [1, 2],  # Muy pocos coeficientes
            'time_taken': 30
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

class BalanceChallengeStatsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_stats_creation(self):
        """Probar creación de estadísticas"""
        stats, created = BalanceChallengeStats.objects.get_or_create(
            user=self.user,
            defaults={
                'games_played': 0,
                'games_completed': 0,
                'games_correct': 0
            }
        )
        
        self.assertTrue(created)
        self.assertEqual(stats.games_played, 0)
        self.assertEqual(stats.accuracy_rate, 0.0)
        self.assertEqual(stats.current_streak, 0)
    
    def test_stats_update_after_correct_game(self):
        """Probar actualización de estadísticas después de juego correcto"""
        # Crear y completar un juego correctamente
        game = BalanceChallengeGame.objects.create(
            user=self.user,
            original_equation='H2 + O2 -> H2O',
            target_balanced_equation='2H2 + O2 -> 2H2O',
            target_coefficients={
                'reactants': [2, 1],
                'products': [2],
                'compounds': {'H2': 2, 'O2': 1, 'H2O': 2}
            },
            difficulty='easy',
            is_completed=True,
            is_correct=True,
            attempts=1,
            time_spent_seconds=60
        )
        
        BalanceChallengeEngine._update_stats(game)
        
        # Verificar estadísticas
        stats = BalanceChallengeStats.objects.get(user=self.user)
        self.assertEqual(stats.games_played, 1)
        self.assertEqual(stats.games_completed, 1)
        self.assertEqual(stats.games_correct, 1)
        self.assertEqual(stats.completion_rate, 100.0)
        self.assertEqual(stats.accuracy_rate, 100.0)
        self.assertEqual(stats.current_streak, 1)
        self.assertEqual(stats.best_streak, 1)
        self.assertEqual(stats.easy_completed, 1)
        self.assertEqual(stats.easy_correct, 1)
        self.assertEqual(stats.best_time_easy, 60)
    
    def test_stats_update_after_incorrect_game(self):
        """Probar actualización de estadísticas después de juego incorrecto"""
        game = BalanceChallengeGame.objects.create(
            user=self.user,
            original_equation='H2 + O2 -> H2O',
            target_balanced_equation='2H2 + O2 -> 2H2O',
            target_coefficients={
                'reactants': [2, 1],
                'products': [2],
                'compounds': {'H2': 2, 'O2': 1, 'H2O': 2}
            },
            difficulty='medium',
            is_completed=True,
            is_correct=False,
            attempts=3,
            time_spent_seconds=120
        )
        
        BalanceChallengeEngine._update_stats(game)
        
        # Verificar estadísticas
        stats = BalanceChallengeStats.objects.get(user=self.user)
        self.assertEqual(stats.games_played, 1)
        self.assertEqual(stats.games_completed, 1)
        self.assertEqual(stats.games_correct, 0)
        self.assertEqual(stats.completion_rate, 100.0)
        self.assertEqual(stats.accuracy_rate, 0.0)
        self.assertEqual(stats.current_streak, 0)
        self.assertEqual(stats.best_streak, 0)
        self.assertEqual(stats.medium_completed, 1)
        self.assertEqual(stats.medium_correct, 0)
        self.assertIsNone(stats.best_time_medium)  # No hay mejor tiempo para juegos incorrectos
    
    def test_streak_management(self):
        """Probar manejo de rachas"""
        # Primer juego correcto
        game1 = BalanceChallengeGame.objects.create(
            user=self.user,
            original_equation='H2 + O2 -> H2O',
            target_balanced_equation='2H2 + O2 -> 2H2O',
            target_coefficients={'compounds': {'H2': 2, 'O2': 1, 'H2O': 2}},
            difficulty='easy',
            is_completed=True,
            is_correct=True,
            time_spent_seconds=60
        )
        BalanceChallengeEngine._update_stats(game1)
        
        stats = BalanceChallengeStats.objects.get(user=self.user)
        self.assertEqual(stats.current_streak, 1)
        self.assertEqual(stats.best_streak, 1)
        
        # Segundo juego correcto
        game2 = BalanceChallengeGame.objects.create(
            user=self.user,
            original_equation='Na + Cl2 -> NaCl',
            target_balanced_equation='2Na + Cl2 -> 2NaCl',
            target_coefficients={'compounds': {'Na': 2, 'Cl2': 1, 'NaCl': 2}},
            difficulty='easy',
            is_completed=True,
            is_correct=True,
            time_spent_seconds=45
        )
        BalanceChallengeEngine._update_stats(game2)
        
        stats.refresh_from_db()
        self.assertEqual(stats.current_streak, 2)
        self.assertEqual(stats.best_streak, 2)
        
        # Tercer juego incorrecto (rompe la racha)
        game3 = BalanceChallengeGame.objects.create(
            user=self.user,
            original_equation='CH4 + O2 -> CO2 + H2O',
            target_balanced_equation='CH4 + 2O2 -> CO2 + 2H2O',
            target_coefficients={'compounds': {'CH4': 1, 'O2': 2, 'CO2': 1, 'H2O': 2}},
            difficulty='medium',
            is_completed=True,
            is_correct=False,
            time_spent_seconds=90
        )
        BalanceChallengeEngine._update_stats(game3)
        
        stats.refresh_from_db()
        self.assertEqual(stats.current_streak, 0)  # Se rompió la racha
        self.assertEqual(stats.best_streak, 2)     # La mejor se mantiene