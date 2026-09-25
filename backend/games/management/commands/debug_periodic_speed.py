from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from games.models import PeriodicSpeedGame, PeriodicSpeedStats
from games.utils import PeriodicSpeedEngine

User = get_user_model()

class Command(BaseCommand):
    help = 'Debug Periodic Speed Challenge functionality'
    
    def handle(self, *args, **options):
        # Crear usuario de prueba si no existe
        user, created = User.objects.get_or_create(
            username='debug_periodic_speed_user',
            defaults={'email': 'debug@periodicspeed.com'}
        )
        if created:
            user.set_password('debug123')
            user.save()
            self.stdout.write('Usuario de debug creado')
        
        # Probar carga de datos de tabla periódica
        try:
            elements = PeriodicSpeedEngine.get_periodic_table_data()
            self.stdout.write(f'✓ Datos de tabla periódica cargados: {len(elements)} elementos')
            
            # Mostrar algunos elementos de ejemplo
            sample_elements = elements[:5]
            self.stdout.write('\n📋 Primeros 5 elementos:')
            for element in sample_elements:
                self.stdout.write(f'  {element["number"]}. {element["name"]} ({element["symbol"]}) - {element["category"]}')
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error al cargar tabla periódica: {e}'))
            return
        
        # Probar creación de desafíos
        self.stdout.write('\n🎯 Probando creación de desafíos:')
        
        difficulties = ['random', 'common', 'rare']
        for difficulty in difficulties:
            try:
                game = PeriodicSpeedEngine.create_speed_challenge(user, difficulty)
                target = game.target_element
                self.stdout.write(f'  ✓ {difficulty.title()}: {target["name"]} ({target["symbol"]}) - Z={target["number"]}')
                
                # Limpiar juego para próxima prueba
                game.delete()
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Error en {difficulty}: {e}'))
        
        # Probar flujo completo de juego
        self.stdout.write('\n🎮 Probando flujo completo de juego:')
        
        try:
            # Crear juego
            game = PeriodicSpeedEngine.create_speed_challenge(user, 'common')
            target_number = game.target_element['number']
            self.stdout.write(f'  Juego creado: ID {game.id}')
            self.stdout.write(f'  Elemento objetivo: {game.target_element["name"]} (Z={target_number})')
            
            # Probar pista
            hint, error = PeriodicSpeedEngine.get_hint(game)
            if hint:
                self.stdout.write(f'  Pista: {hint}')
            else:
                self.stdout.write(f'  Error en pista: {error}')
            
            # Probar respuesta correcta
            result, error = PeriodicSpeedEngine.submit_selection(game, target_number, 2.5)
            if result:
                self.stdout.write(f'  ✓ Respuesta correcta procesada: {result["message"]}')
                self.stdout.write(f'  Tiempo: {result["time_taken"]}s')
            else:
                self.stdout.write(f'  ✗ Error en respuesta: {error}')
            
            # Verificar estadísticas
            stats = PeriodicSpeedStats.objects.get(user=user)
            self.stdout.write(f'  Estadísticas actualizadas:')
            self.stdout.write(f'    - Juegos jugados: {stats.games_played}')
            self.stdout.write(f'    - Juegos correctos: {stats.games_correct}')
            self.stdout.write(f'    - Precisión: {stats.accuracy_rate:.1f}%')
            self.stdout.write(f'    - Mejor tiempo: {stats.best_time_seconds}s')
            self.stdout.write(f'    - Racha actual: {stats.current_streak}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Error en flujo de juego: {e}'))
        
        # Probar elementos de práctica
        self.stdout.write('\n📚 Probando elementos de práctica:')
        
        try:
            practice_elements = PeriodicSpeedEngine.get_random_elements_for_practice(5)
            self.stdout.write('  Elementos aleatorios para práctica:')
            for element in practice_elements:
                self.stdout.write(f'    - {element["name"]} ({element["symbol"]})')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Error en elementos de práctica: {e}'))
        
        # Probar leaderboard
        self.stdout.write('\n🏆 Probando leaderboard:')
        
        try:
            leaderboard = PeriodicSpeedEngine.get_leaderboard(5)
            if leaderboard:
                self.stdout.write('  Top jugadores:')
                for i, stat in enumerate(leaderboard, 1):
                    time_str = f"{stat.best_time_seconds:.2f}s" if stat.best_time_seconds else "N/A"
                    self.stdout.write(f'    {i}. {stat.user.username} - {stat.accuracy_rate:.1f}% - {time_str}')
            else:
                self.stdout.write('  No hay suficientes jugadores en el leaderboard')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Error en leaderboard: {e}'))
        
        # Estadísticas por categoría
        self.stdout.write('\n📊 Estadísticas por categoría de elementos:')
        
        categories = ['metals', 'nonmetals', 'metalloids', 'noble_gases']
        for category in categories:
            count = getattr(stats, f'{category}_correct', 0)
            best_time = getattr(stats, f'best_time_{category}', None)
            time_str = f"{best_time:.2f}s" if best_time else "N/A"
            self.stdout.write(f'  {category.title()}: {count} correctos, mejor tiempo: {time_str}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Debug de Periodic Speed Challenge completado'))