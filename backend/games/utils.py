import random
import json
from pathlib import Path
from django.utils import timezone
from .models import QuizQuestion, QuizSession, QuizAnswer, QuizLeaderboard
from .models import ChemicalWord, ChemWordleGame, ChemWordleAttempt, ChemWordleStats
from .models import MemoryGame, MemoryStats
from .models import BalanceChallengeAttempt, BalanceChallengeGame, BalanceChallengeStats
from .models import PeriodicSpeedGame, PeriodicSpeedStats
from reactions.utils import ChemicalEquationBalancer

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
        
class BalanceChallengeEngine:
    """Motor de juego para el desafío de balanceo de ecuaciones"""
    
    # Ecuaciones predefinidas por dificultad
    CHALLENGE_EQUATIONS = {
        'easy': [
            'H2 + O2 -> H2O',
            'Na + Cl2 -> NaCl',
            'Mg + O2 -> MgO',
            'Ca + H2O -> Ca(OH)2 + H2',
            'Al + O2 -> Al2O3',
            'Fe + O2 -> Fe2O3',
            'N2 + H2 -> NH3',
            'P4 + O2 -> P4O10',
        ],
        'medium': [
            'CH4 + O2 -> CO2 + H2O',
            'C2H6 + O2 -> CO2 + H2O',
            'NH3 + O2 -> NO + H2O',
            'KClO3 -> KCl + O2',
            'Ca(OH)2 + HCl -> CaCl2 + H2O',
            'Al2(SO4)3 + NaOH -> Al(OH)3 + Na2SO4',
            'H2SO4 + NaOH -> Na2SO4 + H2O',
            'CaCO3 + HCl -> CaCl2 + CO2 + H2O',
        ],
        'hard': [
            'C3H8 + O2 -> CO2 + H2O',
            'C6H12O6 + O2 -> CO2 + H2O',
            'Al + HCl -> AlCl3 + H2',
            'Fe2O3 + CO -> Fe + CO2',
            'KMnO4 + HCl -> KCl + MnCl2 + Cl2 + H2O',
            'Cr2O7^2- + Fe^2+ + H+ -> Cr^3+ + Fe^3+ + H2O',
            'NH3 + O2 -> NO2 + H2O',
            'C4H10 + O2 -> CO2 + H2O',
        ]
    }
    
    @staticmethod
    def create_balance_challenge(user, difficulty='easy'):
        """Crea un nuevo desafío de balanceo"""
        # Verificar si ya tiene un juego activo
        active_game = BalanceChallengeGame.objects.filter(
            user=user,
            is_completed=False
        ).first()
        
        if active_game:
            return active_game
        
        # Seleccionar ecuación aleatoria
        equations = BalanceChallengeEngine.CHALLENGE_EQUATIONS.get(difficulty, 
                    BalanceChallengeEngine.CHALLENGE_EQUATIONS['easy'])
        selected_equation = random.choice(equations)
        
        # Balancear la ecuación usando el motor existente
        balance_result = ChemicalEquationBalancer.balance_equation(selected_equation)
        
        if not balance_result['success']:
            raise ValueError(f"No se pudo balancear la ecuación: {selected_equation}")
        
        # Crear el juego
        game = BalanceChallengeGame.objects.create(
            user=user,
            original_equation=selected_equation,
            target_balanced_equation=balance_result['balanced_equation'],
            target_coefficients=balance_result['coefficients'],
            difficulty=difficulty
        )
        
        return game
    
    @staticmethod
    def validate_user_coefficients(game, user_coefficients):
        """Valida los coeficientes proporcionados por el usuario"""
        try:
            # Parsear la ecuación original para obtener compuestos
            reactants, products = ChemicalEquationBalancer.parse_equation(game.original_equation)
            all_compounds = reactants + products
            
            # Verificar que se proporcionaron coeficientes para todos los compuestos
            if len(user_coefficients) != len(all_compounds):
                return {
                    'is_correct': False,
                    'error': f'Se esperan {len(all_compounds)} coeficientes, se recibieron {len(user_coefficients)}',
                    'validation_details': None
                }
            
            # Verificar que todos los coeficientes sean enteros positivos
            for i, coeff in enumerate(user_coefficients):
                if not isinstance(coeff, int) or coeff <= 0:
                    return {
                        'is_correct': False,
                        'error': f'Los coeficientes deben ser enteros positivos. Coeficiente inválido en posición {i+1}: {coeff}',
                        'validation_details': None
                    }
            
            # Construir la ecuación con los coeficientes del usuario
            user_reactants = []
            user_products = []
            
            for i, compound in enumerate(reactants):
                coeff = user_coefficients[i]
                if coeff == 1:
                    user_reactants.append(compound)
                else:
                    user_reactants.append(f"{coeff}{compound}")
            
            for i, compound in enumerate(products):
                coeff = user_coefficients[len(reactants) + i]
                if coeff == 1:
                    user_products.append(compound)
                else:
                    user_products.append(f"{coeff}{compound}")
            
            user_equation = f"{' + '.join(user_reactants)} -> {' + '.join(user_products)}"
            
            # Verificar si la ecuación está balanceada
            is_balanced = BalanceChallengeEngine._verify_equation_balance(
                reactants, products, user_coefficients
            )
            
            # Comparar con la solución objetivo
            target_coefficients_list = []
            target_coeffs = game.target_coefficients['compounds']
            for compound in all_compounds:
                target_coefficients_list.append(target_coeffs[compound])
            
            is_exact_match = user_coefficients == target_coefficients_list
            
            return {
                'is_correct': is_balanced and is_exact_match,
                'is_balanced': is_balanced,
                'is_exact_match': is_exact_match,
                'user_equation': user_equation,
                'target_equation': game.target_balanced_equation,
                'validation_details': {
                    'user_coefficients': user_coefficients,
                    'target_coefficients': target_coefficients_list,
                    'compounds': all_compounds,
                    'coefficient_comparison': [
                        {
                            'compound': compound,
                            'user_coeff': user_coefficients[i],
                            'target_coeff': target_coefficients_list[i],
                            'is_correct': user_coefficients[i] == target_coefficients_list[i]
                        }
                        for i, compound in enumerate(all_compounds)
                    ]
                }
            }
            
        except Exception as e:
            return {
                'is_correct': False,
                'error': f'Error en validación: {str(e)}',
                'validation_details': None
            }
    
    @staticmethod
    def _verify_equation_balance(reactants, products, coefficients):
        """Verifica si una ecuación está balanceada con los coeficientes dados"""
        try:
            # Obtener composición de cada compuesto
            all_compounds = reactants + products
            element_balance = {}
            
            for i, compound in enumerate(all_compounds):
                composition = ChemicalEquationBalancer.parse_compound(compound)
                coefficient = coefficients[i]
                
                # Determinar el signo (positivo para reactivos, negativo para productos)
                sign = 1 if i < len(reactants) else -1
                
                for element, count in composition.items():
                    if element not in element_balance:
                        element_balance[element] = 0
                    element_balance[element] += sign * coefficient * count
            
            # Verificar que todos los elementos estén balanceados (suma = 0)
            for element, balance in element_balance.items():
                if abs(balance) > 1e-10:  # Tolerancia para errores de punto flotante
                    return False
            
            return True
            
        except Exception:
            return False
    
    @staticmethod
    def submit_attempt(game, user_coefficients, time_taken=0):
        """Procesa un intento del usuario"""
        if game.is_completed:
            return None, "El juego ya está completado"
        
        if game.attempts >= game.max_attempts:
            return None, "Se ha alcanzado el número máximo de intentos"
        
        # Validar los coeficientes
        validation_result = BalanceChallengeEngine.validate_user_coefficients(
            game, user_coefficients
        )
        
        # Si hay un error de validación, retornarlo
        if 'error' in validation_result and validation_result.get('error'):
            return None, validation_result['error']
        
        # Crear el intento
        game.attempts += 1
        attempt = BalanceChallengeAttempt.objects.create(
            game=game,
            attempt_number=game.attempts,
            coefficients_submitted=user_coefficients,
            is_correct=validation_result['is_correct'],
            validation_result=validation_result,
            time_taken_seconds=time_taken
        )
        
        # Actualizar el estado del juego
        game.user_coefficients = user_coefficients
        
        if validation_result['is_correct']:
            game.is_correct = True
            game.is_completed = True
            game.completed_at = timezone.now()
            game.time_spent_seconds = (game.completed_at - game.started_at).seconds
        elif game.attempts >= game.max_attempts:
            game.is_completed = True
            game.completed_at = timezone.now()
            game.time_spent_seconds = (game.completed_at - game.started_at).seconds
        
        game.save()
        
        # Actualizar estadísticas si el juego terminó
        if game.is_completed:
            BalanceChallengeEngine._update_stats(game)
        
        return attempt, None
    
    @staticmethod
    def get_hint(game, hint_type='element'):
        """Proporciona pistas al usuario"""
        if game.is_completed:
            return None, "El juego ya está completado"
        
        target_coeffs = game.target_coefficients['compounds']
        reactants, products = ChemicalEquationBalancer.parse_equation(game.original_equation)
        all_compounds = reactants + products
        
        if hint_type == 'element':
            # Pista sobre balanceo de un elemento específico
            return f"Consejo: Comienza balanceando un elemento que aparezca en pocos compuestos", None
        
        elif hint_type == 'coefficient':
            # Revelar un coeficiente
            if len(game.hints_used) < len(all_compounds) // 2:
                available_compounds = [c for c in all_compounds if c not in game.hints_used]
                if available_compounds:
                    compound = random.choice(available_compounds)
                    coefficient = target_coeffs[compound]
                    game.hints_used.append(compound)
                    game.save()
                    return f"Pista: El coeficiente de {compound} es {coefficient}", None
            
            return "No hay más pistas de coeficientes disponibles", None
        
        elif hint_type == 'method':
            # Pista sobre el método de balanceo
            if game.difficulty == 'easy':
                return "Consejo: Intenta el método de inspección, balanceando un elemento a la vez", None
            else:
                return "Consejo: Para ecuaciones complejas, puede ser útil usar el método algebraico", None
        
        return "Tipo de pista no válido", None
    
    @staticmethod
    def _update_stats(game):
        """Actualiza las estadísticas del usuario"""
        stats, created = BalanceChallengeStats.objects.get_or_create(
            user=game.user,
            defaults={
                'games_played': 0,
                'games_completed': 0,
                'games_correct': 0,
                'completion_rate': 0.0,
                'accuracy_rate': 0.0,
                'average_time_per_game': 0.0,
                'current_streak': 0,
                'best_streak': 0
            }
        )
        
        stats.games_played += 1
        stats.games_completed += 1
        
        if game.is_correct:
            stats.games_correct += 1
            stats.current_streak += 1
            stats.best_streak = max(stats.best_streak, stats.current_streak)
        else:
            stats.current_streak = 0
        
        # Actualizar estadísticas por dificultad
        difficulty_completed_field = f"{game.difficulty}_completed"
        difficulty_correct_field = f"{game.difficulty}_correct"
        
        setattr(stats, difficulty_completed_field, 
                getattr(stats, difficulty_completed_field) + 1)
        
        if game.is_correct:
            setattr(stats, difficulty_correct_field, 
                    getattr(stats, difficulty_correct_field) + 1)
        
        # Actualizar tiempos
        if game.time_spent_seconds:
            # Calcular promedio de tiempo
            total_time = (stats.average_time_per_game * (stats.games_completed - 1) + 
                         game.time_spent_seconds)
            stats.average_time_per_game = total_time / stats.games_completed
            
            # Actualizar mejor tiempo por dificultad (solo si es correcto)
            if game.is_correct:
                best_time_field = f"best_time_{game.difficulty}"
                current_best = getattr(stats, best_time_field)
                if not current_best or game.time_spent_seconds < current_best:
                    setattr(stats, best_time_field, game.time_spent_seconds)
        
        # Calcular tasas
        stats.completion_rate = (stats.games_completed / stats.games_played) * 100
        stats.accuracy_rate = (stats.games_correct / stats.games_completed) * 100
        
        stats.save()
        
class PeriodicSpeedEngine:
    """Motor de juego para el desafío de velocidad de tabla periódica"""
    
    # Categorías de elementos para stats
    ELEMENT_CATEGORIES = {
        'alkali metal': 'metals',
        'alkaline earth metal': 'metals',
        'transition metal': 'metals',
        'post-transition metal': 'metals',
        'diatomic nonmetal': 'nonmetals',
        'polyatomic nonmetal': 'nonmetals',
        'metalloid': 'metalloids',
        'noble gas': 'noble_gases',
        'lanthanide': 'metals',
        'actinide': 'metals',
        'unknown, probably transition metal': 'metals',
        'unknown, probably post-transition metal': 'metals',
        'unknown, probably metalloid': 'metalloids',
        'unknown, predicted to be noble gas': 'noble_gases'
    }
    
    @staticmethod
    def get_periodic_table_data():
        """Obtiene los datos de la tabla periódica"""
        try:
            json_file_path = Path(__file__).parent.parent / 'data' / 'static' / 'data' / 'periodic_table.json'
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data['elements']
        except Exception as e:
            raise ValueError(f"Error al cargar datos de la tabla periódica: {str(e)}")
    
    @staticmethod
    def create_speed_challenge(user, difficulty='random'):
        """Crea un nuevo desafío de velocidad"""
        # Verificar si ya tiene un juego activo
        active_game = PeriodicSpeedGame.objects.filter(
            user=user,
            is_completed=False
        ).first()
        
        if active_game:
            return active_game
        
        # Obtener elementos de la tabla periódica
        elements = PeriodicSpeedEngine.get_periodic_table_data()
        
        # Filtrar elementos según dificultad
        if difficulty == 'common':
            # Elementos más comunes (primeros 20 + algunos otros conocidos)
            common_numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 26, 29, 47, 79]
            filtered_elements = [e for e in elements if e['number'] in common_numbers]
        elif difficulty == 'rare':
            # Elementos menos comunes (número atómico > 80 o lantánidos/actínidos)
            filtered_elements = [e for e in elements if e['number'] > 80 or (57 <= e['number'] <= 71) or (89 <= e['number'] <= 103)]
        else:  # random - todos los elementos
            filtered_elements = elements
        
        # Seleccionar elemento aleatorio
        target_element = random.choice(filtered_elements)
        
        # Crear el juego
        game = PeriodicSpeedGame.objects.create(
            user=user,
            target_element=target_element
        )
        
        return game
    
    @staticmethod
    def submit_selection(game, selected_element_number, time_taken):
        """Procesa la selección del usuario"""
        if game.is_completed:
            return None, "El juego ya está completado"
        
        # Obtener todos los elementos para encontrar el seleccionado
        elements = PeriodicSpeedEngine.get_periodic_table_data()
        selected_element = next((e for e in elements if e['number'] == selected_element_number), None)
        
        if not selected_element:
            return None, f"Elemento con número atómico {selected_element_number} no encontrado"
        
        # Verificar si es correcto
        target_number = game.target_element['number']
        is_correct = selected_element_number == target_number
        
        # Actualizar el juego
        game.selected_element = selected_element
        game.is_correct = is_correct
        game.is_completed = True
        game.time_taken_seconds = time_taken
        game.completed_at = timezone.now()
        game.save()
        
        # Actualizar estadísticas
        PeriodicSpeedEngine._update_stats(game)
        
        result = {
            'is_correct': is_correct,
            'target_element': game.target_element,
            'selected_element': selected_element,
            'time_taken': time_taken,
            'message': '¡Correcto!' if is_correct else f'Incorrecto. El elemento era {game.target_element["name"]} ({game.target_element["symbol"]})'
        }
        
        return result, None
    
    @staticmethod
    def get_hint(game):
        """Proporciona una pista sobre el elemento objetivo"""
        if game.is_completed:
            return None, "El juego ya está completado"
        
        if game.hint_used:
            return None, "Ya se utilizó la pista para este juego"
        
        target = game.target_element
        
        # Generar pista basada en las propiedades del elemento
        hints = []
        
        # Pista sobre la categoría
        category = target.get('category', '')
        if 'metal' in category.lower():
            hints.append("Es un metal")
        elif 'nonmetal' in category.lower():
            hints.append("Es un no metal")
        elif 'noble gas' in category.lower():
            hints.append("Es un gas noble")
        elif 'metalloid' in category.lower():
            hints.append("Es un metaloide")
        
        # Pista sobre la posición
        if target.get('ypos', 0) <= 3:
            hints.append("Está en los primeros 3 períodos")
        elif target.get('ypos', 0) <= 5:
            hints.append("Está en los períodos 4-5")
        else:
            hints.append("Está en los períodos 6-7")
        
        # Pista específica según número atómico
        number = target.get('number', 0)
        if number <= 10:
            hints.append("Es uno de los primeros 10 elementos")
        elif number <= 20:
            hints.append("Su número atómico está entre 11 y 20")
        elif number <= 36:
            hints.append("Su número atómico está entre 21 y 36")
        elif number <= 54:
            hints.append("Su número atómico está entre 37 y 54")
        else:
            hints.append("Es un elemento pesado (Z > 54)")
        
        # Seleccionar una pista aleatoria
        hint = random.choice(hints) if hints else "Es un elemento químico de la tabla periódica"
        
        # Marcar pista como usada
        game.hint_used = True
        game.save()
        
        return hint, None
    
    @staticmethod
    def _update_stats(game):
        """Actualiza las estadísticas del usuario"""
        stats, created = PeriodicSpeedStats.objects.get_or_create(
            user=game.user,
            defaults={
                'games_played': 0,
                'games_correct': 0,
                'accuracy_rate': 0.0,
                'best_time_seconds': None,
                'average_time_seconds': 0.0,
                'total_time_seconds': 0.0,
                'current_streak': 0,
                'best_streak': 0
            }
        )
        
        stats.games_played += 1
        
        if game.is_correct and game.time_taken_seconds:
            stats.games_correct += 1
            stats.current_streak += 1
            stats.best_streak = max(stats.best_streak, stats.current_streak)
            
            # Actualizar tiempos
            stats.total_time_seconds += game.time_taken_seconds
            stats.average_time_seconds = stats.total_time_seconds / stats.games_correct
            
            if not stats.best_time_seconds or game.time_taken_seconds < stats.best_time_seconds:
                stats.best_time_seconds = game.time_taken_seconds
            
            # Actualizar estadísticas por categoría
            element_category = game.target_element.get('category', '')
            category_key = PeriodicSpeedEngine.ELEMENT_CATEGORIES.get(element_category, 'metals')
            
            # Incrementar contador de la categoría
            category_field = f"{category_key}_correct"
            setattr(stats, category_field, getattr(stats, category_field) + 1)
            
            # Actualizar mejor tiempo por categoría
            best_time_field = f"best_time_{category_key}"
            current_best = getattr(stats, best_time_field)
            if not current_best or game.time_taken_seconds < current_best:
                setattr(stats, best_time_field, game.time_taken_seconds)
        else:
            stats.current_streak = 0
        
        # Calcular tasa de precisión
        stats.accuracy_rate = (stats.games_correct / stats.games_played) * 100
        
        stats.save()
    
    @staticmethod
    def get_leaderboard(limit=10):
        """Obtiene la tabla de clasificación"""
        return PeriodicSpeedStats.objects.filter(
            games_played__gte=5  # Mínimo 5 juegos
        ).order_by('best_time_seconds', '-accuracy_rate')[:limit]
    
    @staticmethod
    def get_random_elements_for_practice(count=10):
        """Obtiene elementos aleatorios para práctica"""
        elements = PeriodicSpeedEngine.get_periodic_table_data()
        return random.sample(elements, min(count, len(elements)))