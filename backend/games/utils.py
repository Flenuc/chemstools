import random
from django.utils import timezone
from .models import QuizQuestion, QuizSession, QuizAnswer, QuizLeaderboard
from .models import ChemicalWord, ChemWordleGame, ChemWordleAttempt, ChemWordleStats
from .models import MemoryGame, MemoryStats

class QuizGameEngine:
    """Motor de juego para el quiz de química"""
    
    @staticmethod
    def create_quiz_session(user, difficulty=None, category=None, total_questions=10):
        """Crea una nueva sesión de quiz"""
        questions_query = QuizQuestion.objects.all()
        
        if difficulty:
            questions_query = questions_query.filter(difficulty=difficulty)
        if category:
            questions_query = questions_query.filter(category=category)
        
        # Verificar que hay preguntas disponibles
        total_available = questions_query.count()
        if total_available == 0:
            raise ValueError("No hay preguntas disponibles con los criterios especificados")
        
        # Ajustar el número de preguntas si es necesario
        if total_questions > total_available:
            total_questions = total_available
        
        # Seleccionar preguntas aleatorias
        all_question_ids = list(questions_query.values_list('id', flat=True))
        selected_questions = random.sample(all_question_ids, total_questions)
        
        session = QuizSession.objects.create(
            user=user,
            questions=selected_questions,
            total_questions=total_questions
        )
        
        return session
    
    @staticmethod
    def get_current_question(session):
        """Obtiene la pregunta actual de la sesión"""
        if session.current_question_index >= len(session.questions):
            return None
        
        question_id = session.questions[session.current_question_index]
        try:
            return QuizQuestion.objects.get(id=question_id)
        except QuizQuestion.DoesNotExist:
            return None
    
    @staticmethod
    def submit_answer(session, question_id, selected_option, time_taken):
        """Procesa una respuesta del usuario"""
        try:
            question = QuizQuestion.objects.get(id=question_id)
        except QuizQuestion.DoesNotExist:
            raise ValueError(f"Pregunta con ID {question_id} no encontrada")
        
        # Validar que selected_option es un índice válido
        if selected_option < 0 or selected_option >= len(question.options):
            # Manejar caso especial de tiempo agotado (-1)
            if selected_option == -1:
                is_correct = False
                points_earned = 0
                selected_option = -1  # Mantener -1 para indicar tiempo agotado
            else:
                raise ValueError(f"Opción seleccionada {selected_option} no es válida para la pregunta")
        else:
            is_correct = selected_option == question.correct_option
            points_earned = question.points if is_correct else 0
        
        # Crear la respuesta
        answer = QuizAnswer.objects.create(
            session=session,
            question=question,
            selected_option=selected_option,
            is_correct=is_correct,
            time_taken_seconds=time_taken,
            points_earned=points_earned
        )
        
        # Actualizar la sesión
        session.score += points_earned
        session.current_question_index += 1
        
        # Verificar si el quiz está completo
        if session.current_question_index >= session.total_questions:
            session.is_completed = True
            session.completed_at = timezone.now()
            QuizGameEngine._update_leaderboard(session)
        
        session.save()
        
        return answer
    
    @staticmethod
    def _update_leaderboard(session):
        """Actualiza la tabla de clasificación"""
        leaderboard, created = QuizLeaderboard.objects.get_or_create(
            user=session.user,
            defaults={
                'best_score': session.score,
                'total_games': 1,
                'average_score': float(session.score),
                'fastest_completion': (session.completed_at - session.started_at).seconds
            }
        )
        
        if not created:
            leaderboard.total_games += 1
            if session.score > leaderboard.best_score:
                leaderboard.best_score = session.score
            
            # Actualizar promedio (asegurar que sea float)
            leaderboard.average_score = float(
                (leaderboard.average_score * (leaderboard.total_games - 1) + session.score) / 
                leaderboard.total_games
            )
            
            # Actualizar tiempo más rápido
            completion_time = (session.completed_at - session.started_at).seconds
            if not leaderboard.fastest_completion or completion_time < leaderboard.fastest_completion:
                leaderboard.fastest_completion = completion_time
            
            leaderboard.save()
            
class ChemWordleEngine:
    """Motor de juego para ChemWordle"""
    
    LETTER_STATES = {
        'CORRECT': 'correct',      # Letra correcta en posición correcta (verde)
        'PRESENT': 'present',      # Letra correcta en posición incorrecta (amarillo)
        'ABSENT': 'absent'         # Letra no está en la palabra (gris)
    }
    
    @staticmethod
    def get_daily_word(user, difficulty=None):
        """Obtiene la palabra del día o crea una nueva partida"""
        # Verificar si ya tiene una partida activa hoy
        today = timezone.now().date()
        existing_game = ChemWordleGame.objects.filter(
            user=user,
            started_at__date=today,
            is_completed=False
        ).first()
        
        if existing_game:
            return existing_game
        
        # Seleccionar nueva palabra
        words_query = ChemicalWord.objects.all()
        if difficulty:
            words_query = words_query.filter(difficulty=difficulty)
        
        # Evitar palabras ya jugadas recientemente
        recent_games = ChemWordleGame.objects.filter(
            user=user,
            started_at__gte=timezone.now() - timezone.timedelta(days=30)
        ).values_list('target_word_id', flat=True)
        
        available_words = words_query.exclude(id__in=recent_games)
        if not available_words.exists():
            available_words = words_query  # Reset si no hay palabras disponibles
        
        target_word = random.choice(available_words)
        
        # Crear nueva partida
        game = ChemWordleGame.objects.create(
            user=user,
            target_word=target_word
        )
        
        return game
    
    @staticmethod
    def validate_guess(guess, target_word):
        """Valida una palabra adivinada contra la palabra objetivo"""
        guess = guess.upper().strip()
        target = target_word.upper().strip()
        
        if len(guess) != len(target):
            return None, "La palabra debe tener {} letras".format(len(target))
        
        if not guess.isalpha():
            return None, "La palabra solo debe contener letras"
        
        # Verificar si es una palabra química válida (opcional)
        # Esta validación se puede hacer contra una lista de palabras válidas
        
        return guess, None
    
    @staticmethod
    def evaluate_guess(guess, target_word):
        """
        Evalúa una adivinanza y devuelve el estado de cada letra
        Algoritmo Wordle estándar corregido
        """
        guess = guess.upper()
        target = target_word.upper()
        
        result = []
        target_chars = list(target)
        guess_chars = list(guess)
        
        # Inicializar resultado con todas las letras
        for i in range(len(guess)):
            result.append({
                'letter': guess_chars[i],
                'state': None  # Pendiente de evaluar
            })
        
        # Primera pasada: marcar letras correctas en posición correcta
        for i in range(len(guess)):
            if guess_chars[i] == target_chars[i]:
                result[i]['state'] = ChemWordleEngine.LETTER_STATES['CORRECT']
                target_chars[i] = None  # Marcar como usado
                guess_chars[i] = None   # Marcar como procesado
        
        # Segunda pasada: marcar letras presentes en posición incorrecta
        for i in range(len(guess)):
            if result[i]['state'] is None:  # No procesada aún
                letter = guess[i]
                if letter in target_chars:
                    result[i]['state'] = ChemWordleEngine.LETTER_STATES['PRESENT']
                    # Remover una instancia de la letra del target
                    target_chars[target_chars.index(letter)] = None
                else:
                    result[i]['state'] = ChemWordleEngine.LETTER_STATES['ABSENT']
        
        return result
    
    @staticmethod
    def submit_guess(game, guess, time_taken=0):
        """Procesa un intento de adivinanza"""
        # Validar la adivinanza
        validated_guess, error = ChemWordleEngine.validate_guess(guess, game.target_word.word)
        if error:
            return None, error
        
        # Evaluar la adivinanza
        letter_results = ChemWordleEngine.evaluate_guess(validated_guess, game.target_word.word)
        
        # Crear el intento
        attempt = ChemWordleAttempt.objects.create(
            game=game,
            attempt_number=game.attempts_used + 1,
            guessed_word=validated_guess,
            letter_results=letter_results,
            time_taken_seconds=time_taken
        )
        
        # Actualizar el juego
        game.attempts_used += 1
        game.guesses.append({
            'word': validated_guess,
            'results': letter_results,
            'attempt': game.attempts_used
        })
        
        # Verificar si ganó
        is_correct = validated_guess.upper() == game.target_word.word.upper()
        if is_correct:
            game.is_won = True
            game.is_completed = True
            game.completed_at = timezone.now()
        elif game.attempts_used >= game.max_attempts:
            game.is_completed = True
            game.completed_at = timezone.now()
        
        game.save()
        
        # Actualizar estadísticas si el juego terminó
        if game.is_completed:
            ChemWordleEngine._update_stats(game)
        
        return attempt, None
    
    @staticmethod
    def get_progressive_hint(game, hint_level):
        """Obtiene una pista progresiva basada en el nivel"""
        target_word = game.target_word
        hints = target_word.hints_progressive
        
        if hint_level <= len(hints):
            return hints[hint_level - 1]
        
        # Generar pistas automáticas si no hay predefinidas
        auto_hints = ChemWordleEngine._generate_auto_hints(target_word)
        if hint_level <= len(auto_hints):
            return auto_hints[hint_level - 1]
        
        return "No hay más pistas disponibles"
    
    @staticmethod
    def _generate_auto_hints(chemical_word):
        """Genera pistas automáticas basadas en los metadatos"""
        hints = []
        
        # Pista 1: Categoría
        category_names = {
            'element': 'elemento químico',
            'compound': 'compuesto químico',
            'ion': 'ion',
            'molecule': 'molécula'
        }
        hints.append(f"Es un {category_names.get(chemical_word.category, 'compuesto químico')}")
        
        # Pista 2: Número de letras y primera letra
        first_letter = chemical_word.word[0].upper()
        hints.append(f"Tiene {len(chemical_word.word)} letras y comienza con '{first_letter}'")
        
        # Pista 3: Información específica según categoría
        if chemical_word.category == 'element' and chemical_word.group_number:
            hints.append(f"Pertenece al grupo {chemical_word.group_number} de la tabla periódica")
        elif chemical_word.chemical_formula:
            hints.append(f"Su fórmula química es {chemical_word.chemical_formula}")
        
        # Pista 4: Estado o peso molecular
        if chemical_word.state_at_stp:
            hints.append(f"A condiciones estándar es {chemical_word.state_at_stp}")
        elif chemical_word.molecular_weight:
            hints.append(f"Su peso molecular es aproximadamente {chemical_word.molecular_weight:.1f} g/mol")
        
        # Pista 5: Pista principal del modelo
        if chemical_word.hint:
            hints.append(chemical_word.hint)
        
        return hints
    
    @staticmethod
    def _update_stats(game):
        """Actualiza las estadísticas del usuario"""
        stats, created = ChemWordleStats.objects.get_or_create(
            user=game.user,
            defaults={
                'games_played': 0,
                'games_won': 0,
                'win_percentage': 0.0,
                'current_streak': 0,
                'max_streak': 0,
                'win_distribution': {},
                'best_time_seconds': None
            }
        )
        
        stats.games_played += 1
        
        if game.is_won:
            stats.games_won += 1
            stats.current_streak += 1
            stats.max_streak = max(stats.max_streak, stats.current_streak)
            
            # Actualizar distribución de intentos
            attempts_key = str(game.attempts_used)
            if attempts_key not in stats.win_distribution:
                stats.win_distribution[attempts_key] = 0
            stats.win_distribution[attempts_key] += 1
            
            # Actualizar mejor tiempo
            total_time = sum(attempt.time_taken_seconds for attempt in game.attempts.all())
            if not stats.best_time_seconds or total_time < stats.best_time_seconds:
                stats.best_time_seconds = total_time
        else:
            stats.current_streak = 0
        
        # Calcular porcentaje de victoria
        stats.win_percentage = (stats.games_won / stats.games_played) * 100
        
        stats.save()
        
class MemoryGameEngine:
    """Motor de juego para Memory Molecular"""
    
    # Datos químicos para diferentes dificultades
    CHEMICAL_DATA = {
        'easy': [
            {'name': 'Agua', 'formula': 'H₂O', 'type': 'compound'},
            {'name': 'Metano', 'formula': 'CH₄', 'type': 'compound'},
            {'name': 'Amoníaco', 'formula': 'NH₃', 'type': 'compound'},
            {'name': 'Dióxido de carbono', 'formula': 'CO₂', 'type': 'compound'},
            {'name': 'Hidrógeno', 'formula': 'H₂', 'type': 'element'},
            {'name': 'Oxígeno', 'formula': 'O₂', 'type': 'element'},
            {'name': 'Sal común', 'formula': 'NaCl', 'type': 'compound'},
            {'name': 'Ácido clorhídrico', 'formula': 'HCl', 'type': 'compound'},
        ],
        'medium': [
            {'name': 'Glucosa', 'formula': 'C₆H₁₂O₆', 'type': 'compound'},
            {'name': 'Etanol', 'formula': 'C₂H₅OH', 'type': 'compound'},
            {'name': 'Ácido sulfúrico', 'formula': 'H₂SO₄', 'type': 'compound'},
            {'name': 'Hidróxido de sodio', 'formula': 'NaOH', 'type': 'compound'},
            {'name': 'Carbonato de calcio', 'formula': 'CaCO₃', 'type': 'compound'},
            {'name': 'Peróxido de hidrógeno', 'formula': 'H₂O₂', 'type': 'compound'},
            {'name': 'Ácido acético', 'formula': 'CH₃COOH', 'type': 'compound'},
            {'name': 'Bicarbonato de sodio', 'formula': 'NaHCO₃', 'type': 'compound'},
        ],
        'hard': [
            {'name': 'Cafeína', 'formula': 'C₈H₁₀N₄O₂', 'type': 'compound'},
            {'name': 'Aspirina', 'formula': 'C₉H₈O₄', 'type': 'compound'},
            {'name': 'Vitamina C', 'formula': 'C₆H₈O₆', 'type': 'compound'},
            {'name': 'Adenosina trifosfato', 'formula': 'C₁₀H₁₆N₅O₁₃P₃', 'type': 'compound'},
            {'name': 'Colesterol', 'formula': 'C₂₇H₄₆O', 'type': 'compound'},
            {'name': 'Morfina', 'formula': 'C₁₇H₁₉NO₃', 'type': 'compound'},
            {'name': 'Penicilina G', 'formula': 'C₁₆H₁₈N₂O₄S', 'type': 'compound'},
            {'name': 'Adrenalina', 'formula': 'C₉H₁₃NO₃', 'type': 'compound'},
        ]
    }
    
    @staticmethod
    def create_memory_game(user, difficulty='easy', total_pairs=6):
        """Crea una nueva partida de Memory Molecular"""
        available_data = MemoryGameEngine.CHEMICAL_DATA.get(difficulty, MemoryGameEngine.CHEMICAL_DATA['easy'])
        
        if total_pairs > len(available_data):
            total_pairs = len(available_data)
        
        # Seleccionar compuestos aleatorios
        selected_compounds = random.sample(available_data, total_pairs)
        
        # Crear cartas (cada compuesto genera 2 cartas: nombre y fórmula)
        cards = []
        card_id = 0
        
        for compound in selected_compounds:
            # Carta con nombre
            cards.append({
                'id': card_id,
                'content': compound['name'],
                'type': 'name',
                'pair_id': len(cards) // 2,
                'compound_type': compound['type'],
                'is_revealed': False,
                'is_matched': False
            })
            card_id += 1
            
            # Carta con fórmula
            cards.append({
                'id': card_id,
                'content': compound['formula'],
                'type': 'formula',
                'pair_id': (len(cards) - 1) // 2,
                'compound_type': compound['type'],
                'is_revealed': False,
                'is_matched': False
            })
            card_id += 1
        
        # Mezclar las cartas
        random.shuffle(cards)
        
        # Reasignar IDs después del shuffle para mantener posiciones
        for i, card in enumerate(cards):
            card['position'] = i
        
        game = MemoryGame.objects.create(
            user=user,
            difficulty=difficulty,
            total_pairs=total_pairs,
            cards_data=cards
        )
        
        return game
    
    @staticmethod
    def reveal_card(game, card_position):
        """Revela una carta y verifica si hay coincidencia"""
        cards = game.cards_data.copy()
        
        if card_position >= len(cards):
            return None, "Posición de carta inválida"
        
        card = cards[card_position]
        
        # No permitir revelar cartas ya emparejadas o ya reveladas
        if card['is_matched'] or card['is_revealed']:
            return None, "Esta carta ya está revelada o emparejada"
        
        # Revelar la carta
        card['is_revealed'] = True
        cards[card_position] = card
        
        # Contar cartas reveladas no emparejadas
        revealed_cards = [c for c in cards if c['is_revealed'] and not c['is_matched']]
        
        result = {
            'card': card,
            'is_match': False,
            'matched_pair': None,
            'game_completed': False
        }
        
        # Si hay 2 cartas reveladas, verificar coincidencia
        if len(revealed_cards) == 2:
            game.attempts += 1
            
            card1, card2 = revealed_cards
            
            # Verificar si forman un par (mismo pair_id)
            if card1['pair_id'] == card2['pair_id']:
                # ¡Coincidencia!
                for i, c in enumerate(cards):
                    if c['id'] == card1['id'] or c['id'] == card2['id']:
                        cards[i]['is_matched'] = True
                
                game.pairs_found += 1
                game.score += MemoryGameEngine._calculate_pair_score(game.difficulty)
                
                result['is_match'] = True
                result['matched_pair'] = [card1, card2]
                
                # Verificar si el juego está completo
                if game.pairs_found >= game.total_pairs:
                    game.is_completed = True
                    game.completed_at = timezone.now()
                    game.total_time_seconds = (game.completed_at - game.started_at).seconds
                    MemoryGameEngine._update_stats(game)
                    result['game_completed'] = True
            else:
                # No coinciden - se ocultarán automáticamente en el frontend
                pass
        
        # Actualizar datos del juego
        game.cards_data = cards
        game.save()
        
        return result, None
    
    @staticmethod
    def hide_revealed_cards(game):
        """Oculta las cartas reveladas que no fueron emparejadas"""
        cards = game.cards_data.copy()
        
        for i, card in enumerate(cards):
            if card['is_revealed'] and not card['is_matched']:
                cards[i]['is_revealed'] = False
        
        game.cards_data = cards
        game.save()
        
        return True
    
    @staticmethod
    def _calculate_pair_score(difficulty):
        """Calcula puntos por par encontrado según dificultad"""
        score_map = {
            'easy': 100,
            'medium': 200,
            'hard': 300
        }
        return score_map.get(difficulty, 100)
    
    @staticmethod
    def _update_stats(game):
        """Actualiza las estadísticas del usuario"""
        stats, created = MemoryStats.objects.get_or_create(
            user=game.user,
            defaults={
                'games_played': 0,
                'games_completed': 0,
                'completion_rate': 0.0,
                'total_pairs_found': 0,
                'total_attempts': 0,
                'average_accuracy': 0.0
            }
        )
        
        stats.games_played += 1
        if game.is_completed:
            stats.games_completed += 1
        
        stats.total_pairs_found += game.pairs_found
        stats.total_attempts += game.attempts
        
        # Calcular tasa de finalización
        stats.completion_rate = (stats.games_completed / stats.games_played) * 100
        
        # Calcular precisión promedio
        if stats.total_attempts > 0:
            stats.average_accuracy = (stats.total_pairs_found / stats.total_attempts) * 100
        
        # Actualizar mejor tiempo por dificultad
        if game.is_completed and game.total_time_seconds:
            time_field = f'best_time_{game.difficulty}'
            current_best = getattr(stats, time_field)
            if not current_best or game.total_time_seconds < current_best:
                setattr(stats, time_field, game.total_time_seconds)
        
        stats.save()
    
    @staticmethod
    def get_game_state(game):
        """Obtiene el estado actual del juego para el frontend"""
        return {
            'id': game.id,
            'difficulty': game.difficulty,
            'is_completed': game.is_completed,
            'pairs_found': game.pairs_found,
            'total_pairs': game.total_pairs,
            'attempts': game.attempts,
            'score': game.score,
            'cards': game.cards_data,
            'started_at': game.started_at,
            'total_time_seconds': game.total_time_seconds
        }