import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from games.models import ChemicalWord, ChemWordleGame, ChemWordleAttempt, ChemWordleStats
from games.utils import ChemWordleEngine

User = get_user_model()

class ChemWordleEngineTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Crear palabras de prueba
        self.word1 = ChemicalWord.objects.create(
            word='AGUA',
            category='compound',
            difficulty='easy',
            hint='Compuesto esencial para la vida',
            chemical_formula='H2O',
            molecular_weight=18.015,
            hints_progressive=['Es líquida a temperatura ambiente', 'Hierve a 100°C', 'Su fórmula es H2O']
        )
        
        self.word2 = ChemicalWord.objects.create(
            word='OXIGENO',
            category='element',
            difficulty='easy',
            hint='Gas esencial para respiración',
            atomic_number=8,
            chemical_formula='O',
            molecular_weight=15.999,
            hints_progressive=['Es un gas', 'Número atómico 8', 'Su símbolo es O']
        )
    
    def test_create_game(self):
        """Probar creación de juego"""
        game = ChemWordleEngine.get_daily_word(self.user)
        
        self.assertIsNotNone(game)
        self.assertEqual(game.user, self.user)
        self.assertFalse(game.is_completed)
        self.assertFalse(game.is_won)
        self.assertEqual(game.attempts_used, 0)
    
    def test_validate_guess(self):
        """Probar validación de adivinanzas"""
        # Palabra válida
        guess, error = ChemWordleEngine.validate_guess('AGUA', 'AGUA')
        self.assertEqual(guess, 'AGUA')
        self.assertIsNone(error)
        
        # Palabra muy corta
        guess, error = ChemWordleEngine.validate_guess('AG', 'AGUA')
        self.assertIsNone(guess)
        self.assertIsNotNone(error)
        
        # Palabra con números
        guess, error = ChemWordleEngine.validate_guess('AGU1', 'AGUA')
        self.assertIsNone(guess)
        self.assertIsNotNone(error)
    
    def test_evaluate_guess_correct(self):
        """Probar evaluación de adivinanza correcta"""
        result = ChemWordleEngine.evaluate_guess('AGUA', 'AGUA')
        
        self.assertEqual(len(result), 4)
        for letter_result in result:
            self.assertEqual(letter_result['state'], 'correct')
    
    def test_evaluate_guess_all_wrong(self):
        """Probar evaluación donde ninguna letra está en la palabra"""
        result = ChemWordleEngine.evaluate_guess('XYZW', 'AGUA')
        
        self.assertEqual(len(result), 4)
        for letter_result in result:
            self.assertEqual(letter_result['state'], 'absent')
    
    def test_evaluate_guess_mixed(self):
        """Probar evaluación con mezcla de estados"""
        # Target: AGUA
        # Guess: AULA  
        # A(0): correcto en posición 0 -> correct
        # U(1): correcto en posición 2 -> present  
        # L(2): no está en AGUA -> absent
        # A(3): correcto en posición 3 -> correct
        result = ChemWordleEngine.evaluate_guess('AULA', 'AGUA')
        
        print(f"Target: AGUA, Guess: AULA")
        for i, r in enumerate(result):
            print(f"Position {i}: {r['letter']} -> {r['state']}")
        
        self.assertEqual(result[0]['state'], 'correct')  # A en posición correcta
        self.assertEqual(result[1]['state'], 'present')  # U en posición incorrecta
        self.assertEqual(result[2]['state'], 'absent')   # L no está en AGUA
        self.assertEqual(result[3]['state'], 'correct')  # A en posición correcta
    
    def test_evaluate_guess_with_repeated_letters(self):
        """Probar evaluación con letras repetidas"""
        # Target: AGUA (tiene A repetida en posiciones 0 y 3)
        # Guess: ALAS
        # A(0): correcto en posición 0 -> correct
        # L(1): no está en AGUA -> absent
        # A(2): está en AGUA pero posición 0 ya usada, queda posición 3 -> present
        # S(3): no está en AGUA -> absent
        result = ChemWordleEngine.evaluate_guess('ALAS', 'AGUA')
        
        print(f"Target: AGUA, Guess: ALAS")
        for i, r in enumerate(result):
            print(f"Position {i}: {r['letter']} -> {r['state']}")
        
        self.assertEqual(result[0]['state'], 'correct')  # A en posición correcta
        self.assertEqual(result[1]['state'], 'absent')   # L no está
        self.assertEqual(result[2]['state'], 'present')  # A segunda, posición incorrecta
        self.assertEqual(result[3]['state'], 'absent')   # S no está
    
    def test_evaluate_guess_complex_repeated(self):
        """Probar caso complejo con múltiples letras repetidas"""
        # Target: MAMA
        # Guess: AMAM
        # A(0): está en MAMA posición 1, no 0 -> present
        # M(1): está en MAMA posición 0, no 1 -> present  
        # A(2): está en MAMA posición 3, no 2 -> present
        # M(3): está en MAMA posición 2, no 3 -> present
        word3 = ChemicalWord.objects.create(
            word='MAMA',
            category='compound',
            difficulty='easy',
            hint='Palabra de prueba'
        )
        
        result = ChemWordleEngine.evaluate_guess('AMAM', 'MAMA')
        
        print(f"Target: MAMA, Guess: AMAM")
        for i, r in enumerate(result):
            print(f"Position {i}: {r['letter']} -> {r['state']}")
        
        # Todas las letras están en la palabra pero en posiciones incorrectas
        for letter_result in result:
            self.assertEqual(letter_result['state'], 'present')
    
    def test_submit_guess_correct(self):
        """Probar envío de adivinanza correcta"""
        game = ChemWordleGame.objects.create(
            user=self.user,
            target_word=self.word1
        )
        
        attempt, error = ChemWordleEngine.submit_guess(game, 'AGUA', 30)
        
        self.assertIsNone(error)
        self.assertIsNotNone(attempt)
        self.assertEqual(attempt.guessed_word, 'AGUA')
        
        # Verificar que el juego está completado y ganado
        game.refresh_from_db()
        self.assertTrue(game.is_completed)
        self.assertTrue(game.is_won)
        self.assertEqual(game.attempts_used, 1)
    
    def test_submit_guess_incorrect(self):
        """Probar envío de adivinanza incorrecta"""
        game = ChemWordleGame.objects.create(
            user=self.user,
            target_word=self.word1
        )
        
        attempt, error = ChemWordleEngine.submit_guess(game, 'AULA', 45)
        
        self.assertIsNone(error)
        self.assertIsNotNone(attempt)
        self.assertEqual(attempt.guessed_word, 'AULA')
        
        # Verificar que el juego no está completado
        game.refresh_from_db()
        self.assertFalse(game.is_completed)
        self.assertFalse(game.is_won)
        self.assertEqual(game.attempts_used, 1)
    
    def test_progressive_hints(self):
        """Probar pistas progresivas"""
        game = ChemWordleGame.objects.create(
            user=self.user,
            target_word=self.word1
        )
        
        hint1 = ChemWordleEngine.get_progressive_hint(game, 1)
        hint2 = ChemWordleEngine.get_progressive_hint(game, 2)
        
        self.assertEqual(hint1, 'Es líquida a temperatura ambiente')
        self.assertEqual(hint2, 'Hierve a 100°C')
    
    def test_max_attempts_reached(self):
        """Probar límite de intentos"""
        game = ChemWordleGame.objects.create(
            user=self.user,
            target_word=self.word1,
            max_attempts=2
        )
        
        # Primer intento incorrecto
        ChemWordleEngine.submit_guess(game, 'AULA', 30)
        game.refresh_from_db()
        self.assertFalse(game.is_completed)
        
        # Segundo intento incorrecto - debería completar el juego
        ChemWordleEngine.submit_guess(game, 'SALE', 30)
        game.refresh_from_db()
        self.assertTrue(game.is_completed)
        self.assertFalse(game.is_won)
        
class ChemWordleAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Crear palabra de prueba
        self.word = ChemicalWord.objects.create(
            word='AGUA',
            category='compound',
            difficulty='easy',
            hint='Compuesto esencial para la vida',
            chemical_formula='H2O',
            molecular_weight=18.015,
            hints_progressive=['Es líquida a temperatura ambiente', 'Hierve a 100°C']
        )
    
    def test_start_game_endpoint(self):
        """Probar endpoint de inicio de juego"""
        response = self.client.get('/api/games/chemwordle/start_game/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('game', response.data)
        self.assertEqual(response.data['game']['word_length'], 4)  # AGUA
    
    def test_submit_guess_endpoint(self):
        """Probar endpoint de envío de adivinanza"""
        # Crear juego primero
        game = ChemWordleGame.objects.create(
            user=self.user,
            target_word=self.word
        )
        
        response = self.client.post('/api/games/chemwordle/submit_guess/', {
            'game_id': game.id,
            'guess': 'AGUA',
            'time_taken': 30
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertTrue(response.data['game_completed'])
        self.assertTrue(response.data['game_won'])
    
    def test_get_hint_endpoint(self):
        """Probar endpoint de pistas"""
        game = ChemWordleGame.objects.create(
            user=self.user,
            target_word=self.word
        )
        
        response = self.client.post('/api/games/chemwordle/get_hint/', {
            'game_id': game.id,
            'hint_level': 1
        }, format='json')  # CORRECCIÓN: Agregar format='json'
        
        print(f"Hint response status: {response.status_code}")
        print(f"Hint response data: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('hint', response.data)
    
    def test_stats_endpoint(self):
        """Probar endpoint de estadísticas"""
        response = self.client.get('/api/games/chemwordle/stats/')
        
        print(f"Stats response status: {response.status_code}")
        print(f"Stats response data: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        # Las estadísticas pueden ser None si no hay partidas previas
        self.assertIn('stats', response.data)
    
    def test_leaderboard_endpoint(self):
        """Probar endpoint de clasificación"""
        response = self.client.get('/api/games/chemwordle/leaderboard/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('leaderboard', response.data)
    
    def test_invalid_guess_length(self):
        """Probar adivinanza con longitud incorrecta"""
        game = ChemWordleGame.objects.create(
            user=self.user,
            target_word=self.word
        )
        
        response = self.client.post('/api/games/chemwordle/submit_guess/', {
            'game_id': game.id,
            'guess': 'AG',  # Muy corta
            'time_taken': 30
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_invalid_guess_characters(self):
        """Probar adivinanza con caracteres inválidos"""
        game = ChemWordleGame.objects.create(
            user=self.user,
            target_word=self.word
        )
        
        response = self.client.post('/api/games/chemwordle/submit_guess/', {
            'game_id': game.id,
            'guess': 'AG12',  # Con números
            'time_taken': 30
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
