import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from games.models import PeriodicSpeedGame, PeriodicSpeedStats
from games.utils import PeriodicSpeedEngine

User = get_user_model()

class PeriodicSpeedEngineTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_get_periodic_table_data(self):
        """Probar carga de datos de tabla periódica"""
        elements = PeriodicSpeedEngine.get_periodic_table_data()
        
        self.assertIsInstance(elements, list)
        self.assertGreater(len(elements), 100)  # Debería tener más de 100 elementos
        
        # Verificar estructura de elemento
        hydrogen = next((e for e in elements if e['number'] == 1), None)
        self.assertIsNotNone(hydrogen)
        self.assertEqual(hydrogen['name'], 'Hydrogen')
        self.assertEqual(hydrogen['symbol'], 'H')
        self.assertIn('category', hydrogen)
    
    def test_create_speed_challenge_random(self):
        """Probar creación de desafío aleatorio"""
        game = PeriodicSpeedEngine.create_speed_challenge(self.user, difficulty='random')
        
        self.assertIsNotNone(game)
        self.assertEqual(game.user, self.user)
        self.assertFalse(game.is_completed)
        self.assertFalse(game.is_correct)
        self.assertFalse(game.hint_used)
        self.assertIsNotNone(game.target_element)
        self.assertIn('name', game.target_element)
        self.assertIn('number', game.target_element)
    
    def test_create_speed_challenge_common(self):
        """Probar creación de desafío con elementos comunes"""
        game = PeriodicSpeedEngine.create_speed_challenge(self.user, difficulty='common')
        
        target_number = game.target_element['number']
        common_numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 26, 29, 47, 79]
        
        self.assertIn(target_number, common_numbers)
    
    def test_create_speed_challenge_rare(self):
        """Probar creación de desafío con elementos raros"""
        game = PeriodicSpeedEngine.create_speed_challenge(self.user, difficulty='rare')
        
        target_number = game.target_element['number']
        
        # Debe ser elemento pesado o lantánido/actínido
        is_rare = (target_number > 80 or 
                  (57 <= target_number <= 71) or 
                  (89 <= target_number <= 103))
        
        self.assertTrue(is_rare)
    
    def test_submit_correct_selection(self):
        """Probar selección correcta"""
        game = PeriodicSpeedGame.objects.create(
            user=self.user,
            target_element={'name': 'Hydrogen', 'symbol': 'H', 'number': 1, 'category': 'diatomic nonmetal'}
        )
        
        result, error = PeriodicSpeedEngine.submit_selection(game, 1, 2.5)
        
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        self.assertTrue(result['is_correct'])
        self.assertEqual(result['time_taken'], 2.5)
        
        # Verificar que el juego se actualizó
        game.refresh_from_db()
        self.assertTrue(game.is_completed)
        self.assertTrue(game.is_correct)
        self.assertEqual(game.time_taken_seconds, 2.5)
    
    def test_submit_incorrect_selection(self):
        """Probar selección incorrecta"""
        game = PeriodicSpeedGame.objects.create(
            user=self.user,
            target_element={'name': 'Hydrogen', 'symbol': 'H', 'number': 1, 'category': 'diatomic nonmetal'}
        )
        
        result, error = PeriodicSpeedEngine.submit_selection(game, 2, 3.0)  # Helio en lugar de Hidrógeno
        
        self.assertIsNone(error)
        self.assertIsNotNone(result)
        self.assertFalse(result['is_correct'])
        self.assertEqual(result['time_taken'], 3.0)
        
        # Verificar que el juego se actualizó
        game.refresh_from_db()
        self.assertTrue(game.is_completed)
        self.assertFalse(game.is_correct)
        self.assertEqual(game.time_taken_seconds, 3.0)
    
    def test_get_hint(self):
        """Probar sistema de pistas"""
        game = PeriodicSpeedGame.objects.create(
            user=self.user,
            target_element={'name': 'Iron', 'symbol': 'Fe', 'number': 26, 'category': 'transition metal', 'ypos': 4, 'xpos': 8}
        )
        
        hint, error = PeriodicSpeedEngine.get_hint(game)
        
        self.assertIsNone(error)
        self.assertIsNotNone(hint)
        self.assertIsInstance(hint, str)
        
        # Verificar que se marcó como usada
        game.refresh_from_db()
        self.assertTrue(game.hint_used)
        
        # Intentar obtener otra pista (debería fallar)
        hint2, error2 = PeriodicSpeedEngine.get_hint(game)
        self.assertIsNotNone(error2)
        self.assertIsNone(hint2)
    
    def test_stats_update_correct_answer(self):
        """Probar actualización de estadísticas con respuesta correcta"""
        game = PeriodicSpeedGame.objects.create(
            user=self.user,
            target_element={'name': 'Carbon', 'symbol': 'C', 'number': 6, 'category': 'diatomic nonmetal'},
            is_completed=True,
            is_correct=True,
            time_taken_seconds=1.5
        )
        
        PeriodicSpeedEngine._update_stats(game)
        
        stats = PeriodicSpeedStats.objects.get(user=self.user)
        self.assertEqual(stats.games_played, 1)
        self.assertEqual(stats.games_correct, 1)
        self.assertEqual(stats.accuracy_rate, 100.0)
        self.assertEqual(stats.best_time_seconds, 1.5)
        self.assertEqual(stats.current_streak, 1)
        self.assertEqual(stats.best_streak, 1)
        self.assertEqual(stats.nonmetals_correct, 1)  # Carbon es no metal
    
    def test_stats_update_incorrect_answer(self):
        """Probar actualización de estadísticas con respuesta incorrecta"""
        game = PeriodicSpeedGame.objects.create(
            user=self.user,
            target_element={'name': 'Oxygen', 'symbol': 'O', 'number': 8, 'category': 'diatomic nonmetal'},
            is_completed=True,
            is_correct=False,
            time_taken_seconds=3.0
        )
        
        PeriodicSpeedEngine._update_stats(game)
        
        stats = PeriodicSpeedStats.objects.get(user=self.user)
        self.assertEqual(stats.games_played, 1)
        self.assertEqual(stats.games_correct, 0)
        self.assertEqual(stats.accuracy_rate, 0.0)
        self.assertIsNone(stats.best_time_seconds)  # No hay mejor tiempo si no es correcto
        self.assertEqual(stats.current_streak, 0)
        self.assertEqual(stats.best_streak, 0)
    
    def test_prevent_game_action_when_completed(self):
        """Probar que no se pueden hacer acciones en juegos completados"""
        game = PeriodicSpeedGame.objects.create(
            user=self.user,
            target_element={'name': 'Helium', 'symbol': 'He', 'number': 2, 'category': 'noble gas'},
            is_completed=True,
            is_correct=True
        )
        
        # Intentar enviar otra selección
        result, error = PeriodicSpeedEngine.submit_selection(game, 3, 2.0)
        self.assertIsNotNone(error)
        self.assertIsNone(result)
        
        # Intentar obtener pista
        hint, error = PeriodicSpeedEngine.get_hint(game)
        self.assertIsNotNone(error)
        self.assertIsNone(hint)

class PeriodicSpeedAPITests(TestCase):
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
        response = self.client.post('/api/games/periodic-speed/start_challenge/', {
            'difficulty': 'common'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('game', response.data)
        self.assertIn('target_element', response.data['game'])
    
    def test_start_challenge_with_existing_game(self):
        """Probar inicio con juego existente"""
        # Crear juego existente
        game = PeriodicSpeedEngine.create_speed_challenge(self.user, 'random')
        
        response = self.client.post('/api/games/periodic-speed/start_challenge/', {
            'difficulty': 'rare'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('Continuando desafío existente', response.data['message'])
        self.assertEqual(response.data['game']['id'], game.id)
    
    def test_submit_selection_endpoint(self):
        """Probar endpoint de envío de selección"""
        game = PeriodicSpeedGame.objects.create(
            user=self.user,
            target_element={'name': 'Lithium', 'symbol': 'Li', 'number': 3, 'category': 'alkali metal'}
        )
        
        response = self.client.post('/api/games/periodic-speed/submit_selection/', {
            'game_id': game.id,
            'selected_element_number': 3,
            'time_taken': 2.1
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertTrue(response.data['is_correct'])
        self.assertEqual(response.data['time_taken'], 2.1)
    
    def test_submit_incorrect_selection(self):
        """Probar envío de selección incorrecta"""
        game = PeriodicSpeedGame.objects.create(
            user=self.user,
            target_element={'name': 'Lithium', 'symbol': 'Li', 'number': 3, 'category': 'alkali metal'}
        )
        
        response = self.client.post('/api/games/periodic-speed/submit_selection/', {
            'game_id': game.id,
            'selected_element_number': 4,  # Berilio en lugar de Litio
            'time_taken': 3.5
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertFalse(response.data['is_correct'])
        self.assertIn('Incorrecto', response.data['message'])
    
    def test_get_hint_endpoint(self):
        """Probar endpoint de pistas"""
        game = PeriodicSpeedGame.objects.create(
            user=self.user,
            target_element={'name': 'Sodium', 'symbol': 'Na', 'number': 11, 'category': 'alkali metal', 'ypos': 3, 'xpos': 1}
        )
        
        response = self.client.post('/api/games/periodic-speed/get_hint/', {
            'game_id': game.id
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('hint', response.data)
        self.assertTrue(response.data['hint_used'])
    
    def test_current_challenge_endpoint(self):
        """Probar endpoint de desafío actual"""
        # Sin desafío activo
        response = self.client.get('/api/games/periodic-speed/current_challenge/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIsNone(response.data['game'])
        
        # Con desafío activo
        game = PeriodicSpeedEngine.create_speed_challenge(self.user, 'common')
        
        response = self.client.get('/api/games/periodic-speed/current_challenge/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIsNotNone(response.data['game'])
        self.assertEqual(response.data['game']['id'], game.id)
    
    def test_stats_endpoint(self):
        """Probar endpoint de estadísticas"""
        response = self.client.get('/api/games/periodic-speed/stats/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('stats', response.data)
        
        # Verificar estructura de estadísticas
        stats = response.data['stats']
        self.assertEqual(stats['games_played'], 0)
        self.assertEqual(stats['accuracy_rate'], 0.0)
    
    def test_leaderboard_endpoint(self):
        """Probar endpoint de clasificación"""
        response = self.client.get('/api/games/periodic-speed/leaderboard/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('leaderboard', response.data)
        self.assertIsInstance(response.data['leaderboard'], list)
    
    def test_periodic_table_endpoint(self):
        """Probar endpoint de tabla periódica"""
        response = self.client.get('/api/games/periodic-speed/periodic_table/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('elements', response.data)
        self.assertGreater(response.data['total_elements'], 100)
    
    def test_practice_elements_endpoint(self):
        """Probar endpoint de elementos de práctica"""
        response = self.client.get('/api/games/periodic-speed/practice_elements/?count=5&difficulty=common')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('elements', response.data)
        self.assertEqual(len(response.data['elements']), 5)
        self.assertEqual(response.data['difficulty'], 'common')
    
    def test_end_challenge_endpoint(self):
        """Probar endpoint de terminar desafío"""
        # Sin desafío activo
        response = self.client.delete('/api/games/periodic-speed/end_challenge/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])
        
        # Con desafío activo
        game = PeriodicSpeedEngine.create_speed_challenge(self.user, 'random')
        
        response = self.client.delete('/api/games/periodic-speed/end_challenge/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verificar que el juego se marcó como completado
        game.refresh_from_db()
        self.assertTrue(game.is_completed)
    
    def test_invalid_game_id(self):
        """Probar con ID de juego inválido"""
        response = self.client.post('/api/games/periodic-speed/submit_selection/', {
            'game_id': 99999,
            'selected_element_number': 1,
            'time_taken': 2.0
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])
    
    def test_invalid_element_number(self):
        """Probar con número de elemento inválido"""
        game = PeriodicSpeedEngine.create_speed_challenge(self.user, 'random')
        
        response = self.client.post('/api/games/periodic-speed/submit_selection/', {
            'game_id': game.id,
            'selected_element_number': 150,  # No existe
            'time_taken': 2.0
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_invalid_time_values(self):
        """Probar con valores de tiempo inválidos"""
        game = PeriodicSpeedEngine.create_speed_challenge(self.user, 'random')
        
        # Tiempo negativo
        response = self.client.post('/api/games/periodic-speed/submit_selection/', {
            'game_id': game.id,
            'selected_element_number': 1,
            'time_taken': -1.0
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        
        # Tiempo demasiado largo
        response = self.client.post('/api/games/periodic-speed/submit_selection/', {
            'game_id': game.id,
            'selected_element_number': 1,
            'time_taken': 400.0  # Más de 5 minutos
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])