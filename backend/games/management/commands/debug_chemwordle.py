from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from games.models import ChemicalWord, ChemWordleGame
from games.utils import ChemWordleEngine

User = get_user_model()

class Command(BaseCommand):
    help = 'Debug ChemWordle functionality'
    
    def handle(self, *args, **options):
        # Crear usuario de prueba si no existe
        user, created = User.objects.get_or_create(
            username='debug_chemwordle_user',
            defaults={'email': 'debug@chemwordle.com'}
        )
        if created:
            user.set_password('debug123')
            user.save()
            self.stdout.write('Usuario de debug creado')
        
        # Mostrar estadísticas de palabras
        total_words = ChemicalWord.objects.count()
        self.stdout.write(f'Total de palabras químicas: {total_words}')
        
        if total_words == 0:
            self.stdout.write(self.style.ERROR('❌ No hay palabras en la base de datos'))
            self.stdout.write('Ejecuta: python manage.py populate_chemwordle_words')
            return
        
        # Estadísticas por categoría
        self.stdout.write('\n📊 Distribución por categoría:')
        for category, name in ChemicalWord.CATEGORY_CHOICES:
            count = ChemicalWord.objects.filter(category=category).count()
            self.stdout.write(f'  {name}: {count} palabras')
        
        # Estadísticas por dificultad
        self.stdout.write('\n📈 Distribución por dificultad:')
        for difficulty, name in ChemicalWord.DIFFICULTY_CHOICES:
            count = ChemicalWord.objects.filter(difficulty=difficulty).count()
            self.stdout.write(f'  {name}: {count} palabras')
        
        # Probar creación de juego
        try:
            game = ChemWordleEngine.get_daily_word(user)
            self.stdout.write(f'\n✓ Juego creado: ID {game.id}')
            self.stdout.write(f'  Palabra objetivo: {game.target_word.word} ({game.target_word.category})')
            self.stdout.write(f'  Longitud: {len(game.target_word.word)} letras')
            self.stdout.write(f'  Dificultad: {game.target_word.difficulty}')
            self.stdout.write(f'  Pista: {game.target_word.hint}')
            
            # Probar pista progresiva
            hint = ChemWordleEngine.get_progressive_hint(game, 1)
            self.stdout.write(f'  Primera pista: {hint}')
            
            # Probar evaluación de adivinanza
            target = game.target_word.word
            test_guess = target[:2] + 'XX' + target[4:] if len(target) > 4 else 'XXXX'
            test_guess = test_guess[:len(target)].ljust(len(target), 'X')
            
            result = ChemWordleEngine.evaluate_guess(test_guess, target)
            self.stdout.write(f'\n🧪 Prueba de evaluación:')
            self.stdout.write(f'  Palabra objetivo: {target}')
            self.stdout.write(f'  Adivinanza: {test_guess}')
            self.stdout.write(f'  Resultado: {[r["state"] for r in result]}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error al crear juego: {e}'))
        
        # Mostrar algunas palabras de ejemplo
        self.stdout.write('\n🔤 Ejemplos de palabras por dificultad:')
        for difficulty in ['easy', 'medium', 'hard']:
            words = ChemicalWord.objects.filter(difficulty=difficulty)[:3]
            word_list = ', '.join([w.word for w in words])
            self.stdout.write(f'  {difficulty.title()}: {word_list}')