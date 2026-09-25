import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState, AppDispatch } from '@/store';
import {
  startQuizSession,
  getCurrentQuestion,
  submitAnswer,
  updateTimeRemaining,
  resetQuiz,
  clearError
} from '@/store/quizSlice';

interface QuizGameProps {
  onComplete?: () => void;
}

const QuizGame: React.FC<QuizGameProps> = ({ onComplete }) => {
  const dispatch = useDispatch<AppDispatch>();
  const {
    currentSession,
    currentQuestion,
    currentQuestionIndex,
    totalQuestions,
    score,
    timeRemaining,
    gameState,
    lastAnswer,
    loading,
    error
  } = useSelector((state: RootState) => state.quiz);

  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [questionStartTime, setQuestionStartTime] = useState<number>(Date.now());
  const [showFeedback, setShowFeedback] = useState(false);

  // Timer effect
  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (gameState === 'playing' && timeRemaining > 0) {
      interval = setInterval(() => {
        dispatch(updateTimeRemaining(timeRemaining - 1));
      }, 1000);
    } else if (timeRemaining === 0 && gameState === 'playing') {
      // Tiempo agotado
      handleTimeUp();
    }

    return () => clearInterval(interval);
  }, [gameState, timeRemaining, dispatch]);

  // Load current question when session starts
  useEffect(() => {
    if (currentSession && gameState === 'playing' && !currentQuestion) {
      console.log('Loading current question for session:', currentSession.id);
      dispatch(getCurrentQuestion(currentSession.id));
      setQuestionStartTime(Date.now());
    }
  }, [currentSession, gameState, currentQuestion, dispatch]);

  // Reset selected option when new question loads
  useEffect(() => {
    if (currentQuestion) {
      setSelectedOption(null);
      setShowFeedback(false);
      setQuestionStartTime(Date.now());
    }
  }, [currentQuestion]);

  const handleStartQuiz = (difficulty?: string, category?: string) => {
    console.log('Starting quiz with params:', { difficulty, category });
    dispatch(resetQuiz());
    dispatch(startQuizSession({ difficulty, category, total_questions: 10 }));
  };

  const handleTimeUp = () => {
    if (currentSession && currentQuestion) {
      // Auto-submit with no selection (time up)
      const timeTaken = Math.floor((Date.now() - questionStartTime) / 1000);
      dispatch(submitAnswer({
        session_id: currentSession.id,
        question_id: currentQuestion.id,
        selected_option: -1, // Indica que se agotó el tiempo
        time_taken: timeTaken
      }));
    }
  };

  const handleAnswerSubmit = () => {
    if (selectedOption === null || !currentSession || !currentQuestion) return;

    const timeTaken = Math.floor((Date.now() - questionStartTime) / 1000);
    
    console.log('Submitting answer:', {
      session_id: currentSession.id,
      question_id: currentQuestion.id,
      selected_option: selectedOption,
      time_taken: timeTaken
    });

    dispatch(submitAnswer({
      session_id: currentSession.id,
      question_id: currentQuestion.id,
      selected_option: selectedOption,
      time_taken: timeTaken
    })).then((result) => {
      console.log('Answer submitted, result:', result);
      setShowFeedback(true);
      
      // Mostrar feedback por 3 segundos antes de continuar
      setTimeout(() => {
        if (currentQuestionIndex + 1 < totalQuestions) {
          dispatch(getCurrentQuestion(currentSession.id));
        } else {
          onComplete?.();
        }
      }, 3000);
    }).catch((error) => {
      console.error('Error submitting answer:', error);
    });
  };

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const getProgressPercentage = () => {
    return ((currentQuestionIndex + 1) / totalQuestions) * 100;
  };

  // Componente para mostrar feedback de respuesta
  const FeedbackDisplay = () => {
    if (!lastAnswer) return null;

    return (
      <div className={`p-4 rounded-lg ${lastAnswer.is_correct ? 'bg-green-100 border-green-500' : 'bg-red-100 border-red-500'} border-2`}>
        <div className="flex items-center mb-2">
          {lastAnswer.is_correct ? (
            <div className="text-green-600 font-bold">¡Correcto! +{lastAnswer.points_earned} puntos</div>
          ) : (
            <div className="text-red-600 font-bold">Incorrecto</div>
          )}
        </div>
        
        <div className="text-sm text-gray-700">
          <p><strong>Respuesta correcta:</strong> {lastAnswer.question_data.options[lastAnswer.question_data.correct_option]}</p>
          {lastAnswer.question_data.explanation && (
            <p className="mt-2"><strong>Explicación:</strong> {lastAnswer.question_data.explanation}</p>
          )}
        </div>
      </div>
    );
  };

  // Estado de carga inicial
  if (gameState === 'idle') {
    return (
      <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-blue-600 mb-4">Quiz Rápido de Química</h2>
          <p className="text-gray-600 mb-6">Pon a prueba tus conocimientos químicos</p>
          
          <div className="space-y-4">
            <button
              onClick={() => handleStartQuiz()}
              className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 px-6 rounded-lg transition-colors"
            >
              Comenzar Quiz Aleatorio
            </button>
            
            <div className="grid grid-cols-2 gap-4">
              <button
                onClick={() => handleStartQuiz('easy')}
                className="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded transition-colors"
              >
                Nivel Fácil
              </button>
              <button
                onClick={() => handleStartQuiz('medium')}
                className="bg-yellow-500 hover:bg-yellow-600 text-white font-bold py-2 px-4 rounded transition-colors"
              >
                Nivel Medio
              </button>
            </div>
            
            <button
              onClick={() => handleStartQuiz('hard')}
              className="w-full bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded transition-colors"
            >
              Nivel Difícil
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Estado de carga
  if (loading || gameState === 'starting') {
    return (
      <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Preparando tu quiz...</p>
        </div>
      </div>
    );
  }

  // Estado de error
  if (gameState === 'error') {
    return (
      <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
        <div className="text-center">
          <div className="text-red-500 text-xl mb-4">❌ Error</div>
          <p className="text-gray-600 mb-4">{error}</p>
          <div className="space-y-2">
            <button
              onClick={() => dispatch(clearError())}
              className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded mr-2"
            >
              Reintentar
            </button>
            <button
              onClick={() => dispatch(resetQuiz())}
              className="bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded"
            >
              Volver al Inicio
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Quiz completado
  if (gameState === 'completed') {
    return (
      <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-green-600 mb-4">🎉 ¡Quiz Completado!</h2>
          <div className="text-6xl font-bold text-blue-600 mb-2">{score}</div>
          <p className="text-gray-600 mb-6">puntos totales</p>
          
          <div className="bg-gray-100 rounded-lg p-4 mb-6">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-semibold">Preguntas respondidas:</span>
                <div className="text-lg">{totalQuestions}</div>
              </div>
              <div>
                <span className="font-semibold">Puntuación final:</span>
                <div className="text-lg">{score}</div>
              </div>
            </div>
          </div>
          
          <div className="space-y-2">
            <button
              onClick={() => dispatch(resetQuiz())}
              className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded transition-colors"
            >
              Jugar de Nuevo
            </button>
            <button
              onClick={onComplete}
              className="w-full bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded transition-colors"
            >
              Volver al Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Jugando quiz
  if (!currentQuestion) {
    return (
      <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p>Cargando pregunta...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      {/* Header con información del quiz */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <div className="text-sm text-gray-600">
            Pregunta {currentQuestionIndex + 1} de {totalQuestions}
          </div>
          <div className="text-sm font-semibold text-blue-600">
            Puntuación: {score}
          </div>
        </div>
        
        {/* Barra de progreso */}
        <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
          <div 
            className="bg-blue-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${getProgressPercentage()}%` }}
          ></div>
        </div>
        
        {/* Timer */}
        <div className="text-center">
          <div className={`text-2xl font-bold ${timeRemaining <= 30 ? 'text-red-500' : 'text-gray-700'}`}>
            ⏱️ {formatTime(timeRemaining)}
          </div>
        </div>
      </div>

      {/* Mostrar feedback si existe */}
      {showFeedback && lastAnswer ? (
        <FeedbackDisplay />
      ) : (
        <>
          {/* Pregunta */}
          <div className="mb-6">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-xl font-semibold text-gray-800 flex-1">
                {currentQuestion.question_text}
              </h3>
              <div className="ml-4 text-sm">
                <span className={`px-2 py-1 rounded text-white ${
                  currentQuestion.difficulty === 'easy' ? 'bg-green-500' :
                  currentQuestion.difficulty === 'medium' ? 'bg-yellow-500' : 'bg-red-500'
                }`}>
                  {currentQuestion.difficulty === 'easy' ? 'Fácil' : 
                   currentQuestion.difficulty === 'medium' ? 'Medio' : 'Difícil'}
                </span>
                <div className="text-xs text-gray-500 mt-1">
                  {currentQuestion.points} pts
                </div>
              </div>
            </div>
          </div>

          {/* Opciones */}
          <div className="space-y-3 mb-6">
            {currentQuestion.options.map((option: string, index: number) => (
              <button
                key={index}
                onClick={() => setSelectedOption(index)}
                className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                  selectedOption === index
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
                disabled={gameState === 'answering'}
              >
                <div className="flex items-center">
                  <div className={`w-6 h-6 rounded-full border-2 mr-3 flex items-center justify-center ${
                    selectedOption === index ? 'border-blue-500 bg-blue-500' : 'border-gray-300'
                  }`}>
                    {selectedOption === index && (
                      <div className="w-2 h-2 bg-white rounded-full"></div>
                    )}
                  </div>
                  <span className="text-gray-800">{option}</span>
                </div>
              </button>
            ))}
          </div>

          {/* Botón de enviar */}
          <div className="text-center">
            <button
              onClick={handleAnswerSubmit}
              disabled={selectedOption === null || gameState === 'answering'}
              className={`px-8 py-3 rounded-lg font-semibold transition-all ${
                selectedOption !== null && gameState !== 'answering'
                  ? 'bg-blue-500 hover:bg-blue-600 text-white'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }`}
            >
              {gameState === 'answering' ? 'Enviando...' : 'Enviar Respuesta'}
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default QuizGame;