from rest_framework import serializers
from .models import QuizQuestion, QuizSession, QuizAnswer, QuizLeaderboard
from .models import ChemicalWord, ChemWordleGame, ChemWordleAttempt, ChemWordleStats
from .models import MemoryGame, MemoryStats
from .models import BalanceChallengeGame, BalanceChallengeAttempt, BalanceChallengeStats
from .models import PeriodicSpeedGame, PeriodicSpeedStats 
from django.utils import timezone

class QuizQuestionSerializer(serializers.ModelSerializer):
    """Serializer para preguntas sin mostrar la respuesta correcta"""
    class Meta:
        model = QuizQuestion
        fields = ['id', 'question_text', 'options', 'difficulty', 'category', 'points']

class QuizQuestionWithAnswerSerializer(serializers.ModelSerializer):
    """Serializer completo para mostrar después de responder"""
    class Meta:
        model = QuizQuestion
        fields = '__all__'

class QuizSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizSession
        fields = '__all__'
        read_only_fields = ['user']

class QuizAnswerSerializer(serializers.ModelSerializer):
    question_data = QuizQuestionWithAnswerSerializer(source='question', read_only=True)
    
    class Meta:
        model = QuizAnswer
        fields = ['id', 'selected_option', 'is_correct', 'time_taken_seconds', 'points_earned', 'question_data']

class QuizLeaderboardSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = QuizLeaderboard
        fields = ['username', 'best_score', 'total_games', 'average_score', 'fastest_completion']
        
class ChemicalWordSerializer(serializers.ModelSerializer):
    """Serializer para palabras químicas (sin revelar la palabra)"""
    class Meta:
        model = ChemicalWord
        fields = ['id', 'category', 'difficulty', 'hint', 'atomic_number', 
                 'group_number', 'period_number', 'state_at_stp', 'chemical_formula',
                 'molecular_weight']

class ChemicalWordFullSerializer(serializers.ModelSerializer):
    """Serializer completo para palabras químicas"""
    class Meta:
        model = ChemicalWord
        fields = '__all__'

class ChemWordleGameSerializer(serializers.ModelSerializer):
    target_word = ChemicalWordSerializer(read_only=True)
    word_length = serializers.SerializerMethodField()
    
    class Meta:
        model = ChemWordleGame
        fields = ['id', 'target_word', 'is_completed', 'is_won', 'attempts_used', 
                 'max_attempts', 'guesses', 'hints_revealed', 'started_at', 'word_length']
        read_only_fields = ['user']
    
    def get_word_length(self, obj):
        return len(obj.target_word.word)

class ChemWordleGameCompleteSerializer(ChemWordleGameSerializer):
    """Serializer para juegos completados que incluye la palabra correcta"""
    target_word = ChemicalWordFullSerializer(read_only=True)

class ChemWordleAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChemWordleAttempt
        fields = ['id', 'attempt_number', 'guessed_word', 'letter_results', 'time_taken_seconds']

class ChemWordleStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChemWordleStats
        fields = ['games_played', 'games_won', 'win_percentage', 'current_streak', 
                 'max_streak', 'win_distribution', 'best_time_seconds']
        
        
class MemoryGameSerializer(serializers.ModelSerializer):
    """Serializer para partidas de Memory Molecular"""
    cards = serializers.SerializerMethodField()
    time_elapsed = serializers.SerializerMethodField()
    
    class Meta:
        model = MemoryGame
        fields = [
            'id', 'difficulty', 'is_completed', 'pairs_found', 'total_pairs',
            'attempts', 'score', 'started_at', 'completed_at', 'total_time_seconds',
            'cards', 'time_elapsed'
        ]
        read_only_fields = ['user']
    
    def get_cards(self, obj):
        """Retorna las cartas sin revelar información sensible si el juego está activo"""
        cards = obj.cards_data.copy()
        
        # Si el juego no está completado, ocultar el contenido de cartas no reveladas
        if not obj.is_completed:
            for card in cards:
                if not card['is_revealed'] and not card['is_matched']:
                    # Mantener estructura pero ocultar contenido
                    safe_card = {
                        'id': card['id'],
                        'position': card['position'],
                        'type': 'hidden',
                        'is_revealed': False,
                        'is_matched': False,
                        'compound_type': card.get('compound_type', 'unknown')
                    }
                    cards[card['position']] = safe_card
        
        return cards
    
    def get_time_elapsed(self, obj):
        """Calcula el tiempo transcurrido en segundos"""
        if obj.completed_at:
            return obj.total_time_seconds
        else:
            return int((timezone.now() - obj.started_at).total_seconds())

class MemoryStatsSerializer(serializers.ModelSerializer):
    """Serializer para estadísticas de Memory Molecular"""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = MemoryStats
        fields = [
            'username', 'games_played', 'games_completed', 'completion_rate',
            'best_time_easy', 'best_time_medium', 'best_time_hard',
            'total_pairs_found', 'total_attempts', 'average_accuracy'
        ]

class MemoryCardRevealSerializer(serializers.Serializer):
    """Serializer para revelar cartas"""
    game_id = serializers.IntegerField()
    card_position = serializers.IntegerField(min_value=0)
    
    def validate_card_position(self, value):
        """Validar que la posición de la carta sea válida"""
        if value < 0:
            raise serializers.ValidationError("La posición de la carta debe ser positiva")
        return value

class MemoryGameCreateSerializer(serializers.Serializer):
    """Serializer para crear nuevas partidas"""
    difficulty = serializers.ChoiceField(
        choices=['easy', 'medium', 'hard'],
        default='easy'
    )
    total_pairs = serializers.IntegerField(
        min_value=3,
        max_value=12,
        default=6
    )
    
    def validate_total_pairs(self, value):
        """Validar que el número de pares sea apropiado para la dificultad"""
        difficulty = self.initial_data.get('difficulty', 'easy')
        max_pairs = {
            'easy': 8,
            'medium': 8,
            'hard': 8
        }
        
        if value > max_pairs.get(difficulty, 8):
            raise serializers.ValidationError(
                f"Máximo {max_pairs.get(difficulty, 8)} pares para dificultad {difficulty}"
            )
        
        return value
    
class BalanceChallengeGameSerializer(serializers.ModelSerializer):
    """Serializer para el juego de balanceo de ecuaciones"""
    compounds = serializers.SerializerMethodField()
    time_elapsed = serializers.SerializerMethodField()
    
    class Meta:
        model = BalanceChallengeGame
        fields = [
            'id', 'original_equation', 'difficulty', 'is_completed', 'is_correct',
            'attempts', 'max_attempts', 'user_coefficients', 'hints_used',
            'started_at', 'completed_at', 'time_elapsed', 'compounds'
        ]
        read_only_fields = ['user']
    
    def get_compounds(self, obj):
        """Obtiene la lista de compuestos en orden"""
        from reactions.utils import ChemicalEquationBalancer
        try:
            reactants, products = ChemicalEquationBalancer.parse_equation(obj.original_equation)
            return {
                'reactants': reactants,
                'products': products,
                'all_compounds': reactants + products
            }
        except:
            return {'reactants': [], 'products': [], 'all_compounds': []}
    
    def get_time_elapsed(self, obj):
        """Calcula el tiempo transcurrido"""
        if obj.completed_at:
            return obj.time_spent_seconds
        else:
            return int((timezone.now() - obj.started_at).total_seconds())

class BalanceChallengeGameCompleteSerializer(BalanceChallengeGameSerializer):
    """Serializer completo que incluye la solución"""
    target_balanced_equation = serializers.CharField(read_only=True)
    target_coefficients = serializers.JSONField(read_only=True)
    
    class Meta(BalanceChallengeGameSerializer.Meta):
        fields = BalanceChallengeGameSerializer.Meta.fields + [
            'target_balanced_equation', 'target_coefficients'
        ]

class BalanceChallengeAttemptSerializer(serializers.ModelSerializer):
    """Serializer para intentos de balanceo"""
    class Meta:
        model = BalanceChallengeAttempt
        fields = '__all__'

class BalanceChallengeStatsSerializer(serializers.ModelSerializer):
    """Serializer para estadísticas de balanceo"""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = BalanceChallengeStats
        fields = [
            'username', 'games_played', 'games_completed', 'games_correct',
            'completion_rate', 'accuracy_rate', 'easy_completed', 'easy_correct',
            'medium_completed', 'medium_correct', 'hard_completed', 'hard_correct',
            'average_time_per_game', 'best_time_easy', 'best_time_medium', 
            'best_time_hard', 'current_streak', 'best_streak'
        ]

class BalanceChallengeSubmitSerializer(serializers.Serializer):
    """Serializer para envío de coeficientes"""
    game_id = serializers.IntegerField()
    coefficients = serializers.ListField(
        child=serializers.IntegerField(min_value=1, max_value=50),
        min_length=1,
        max_length=20
    )
    time_taken = serializers.IntegerField(min_value=0, default=0)

class BalanceChallengeCreateSerializer(serializers.Serializer):
    """Serializer para crear nuevo desafío"""
    difficulty = serializers.ChoiceField(
        choices=['easy', 'medium', 'hard'],
        default='easy'
    )

class PeriodicSpeedGameSerializer(serializers.ModelSerializer):
    """Serializer para el juego de velocidad periódica"""
    time_elapsed = serializers.SerializerMethodField()
    target_hint = serializers.SerializerMethodField()
    
    class Meta:
        model = PeriodicSpeedGame
        fields = [
            'id', 'target_element', 'is_completed', 'is_correct', 
            'time_taken_seconds', 'selected_element', 'hint_used',
            'started_at', 'completed_at', 'time_elapsed', 'target_hint'
        ]
        read_only_fields = ['user']
    
    def get_time_elapsed(self, obj):
        """Calcula el tiempo transcurrido"""
        if obj.completed_at:
            return obj.time_taken_seconds
        else:
            return (timezone.now() - obj.started_at).total_seconds()
    
    def get_target_hint(self, obj):
        """Proporciona información básica del elemento sin revelarlo"""
        if obj.is_completed:
            return obj.target_element
        
        # Solo mostrar información básica mientras el juego está activo
        target = obj.target_element
        return {
            'name': target.get('name', ''),
            'category_hint': self._get_category_hint(target.get('category', '')),
            'period_hint': f"Período {target.get('ypos', '?')}",
            'group_hint': f"Grupo {target.get('xpos', '?')}" if target.get('xpos', 0) <= 18 else "Lantánido/Actínido"
        }
    
    def _get_category_hint(self, category):
        """Convierte categoría técnica en pista comprensible"""
        if 'metal' in category.lower() and 'nonmetal' not in category.lower():
            return "Metal"
        elif 'nonmetal' in category.lower():
            return "No metal"
        elif 'noble gas' in category.lower():
            return "Gas noble"
        elif 'metalloid' in category.lower():
            return "Metaloide"
        else:
            return "Elemento químico"

class PeriodicSpeedGameCompleteSerializer(PeriodicSpeedGameSerializer):
    """Serializer completo que incluye toda la información"""
    target_element = serializers.JSONField(read_only=True)
    
    def get_target_hint(self, obj):
        """Para juegos completados, retorna toda la información"""
        return obj.target_element

class PeriodicSpeedStatsSerializer(serializers.ModelSerializer):
    """Serializer para estadísticas de velocidad periódica"""
    username = serializers.CharField(source='user.username', read_only=True)
    best_time_formatted = serializers.SerializerMethodField()
    average_time_formatted = serializers.SerializerMethodField()
    category_breakdown = serializers.SerializerMethodField()
    
    class Meta:
        model = PeriodicSpeedStats
        fields = [
            'username', 'games_played', 'games_correct', 'accuracy_rate',
            'best_time_seconds', 'average_time_seconds', 'current_streak', 'best_streak',
            'metals_correct', 'nonmetals_correct', 'metalloids_correct', 'noble_gases_correct',
            'best_time_metals', 'best_time_nonmetals', 'best_time_metalloids', 'best_time_noble_gases',
            'best_time_formatted', 'average_time_formatted', 'category_breakdown'
        ]
    
    def get_best_time_formatted(self, obj):
        """Formatea el mejor tiempo para mostrar"""
        if obj.best_time_seconds:
            return f"{obj.best_time_seconds:.2f}s"
        return "N/A"
    
    def get_average_time_formatted(self, obj):
        """Formatea el tiempo promedio para mostrar"""
        if obj.average_time_seconds:
            return f"{obj.average_time_seconds:.2f}s"
        return "N/A"
    
    def get_category_breakdown(self, obj):
        """Proporciona desglose por categorías"""
        return {
            'metals': {
                'correct': obj.metals_correct,
                'best_time': obj.best_time_metals,
                'best_time_formatted': f"{obj.best_time_metals:.2f}s" if obj.best_time_metals else "N/A"
            },
            'nonmetals': {
                'correct': obj.nonmetals_correct,
                'best_time': obj.best_time_nonmetals,
                'best_time_formatted': f"{obj.best_time_nonmetals:.2f}s" if obj.best_time_nonmetals else "N/A"
            },
            'metalloids': {
                'correct': obj.metalloids_correct,
                'best_time': obj.best_time_metalloids,
                'best_time_formatted': f"{obj.best_time_metalloids:.2f}s" if obj.best_time_metalloids else "N/A"
            },
            'noble_gases': {
                'correct': obj.noble_gases_correct,
                'best_time': obj.best_time_noble_gases,
                'best_time_formatted': f"{obj.best_time_noble_gases:.2f}s" if obj.best_time_noble_gases else "N/A"
            }
        }

class PeriodicSpeedCreateSerializer(serializers.Serializer):
    """Serializer para crear nuevo desafío de velocidad"""
    difficulty = serializers.ChoiceField(
        choices=['random', 'common', 'rare'],
        default='random'
    )

class PeriodicSpeedSubmitSerializer(serializers.Serializer):
    """Serializer para envío de selección"""
    game_id = serializers.IntegerField()
    selected_element_number = serializers.IntegerField(min_value=1, max_value=118)
    time_taken = serializers.FloatField(min_value=0.1, max_value=300.0)  # Entre 0.1s y 5 minutos