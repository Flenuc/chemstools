// Migration map for updating all components to the new hybrid system
// This file maps old component imports to new enhanced versions

export const COMPONENT_MIGRATION_MAP = {
  // Common components (already migrated)
  'components/common/Button': '@/components/ui',
  'components/common/Card': '@/components/ui',
  'components/common/Input': '@/components/ui/forms',
  'components/common/Modal': '@/components/ui',
  
  // Authentication (enhanced versions created)
  'components/features/LoginForm': '@/components/features/LoginFormEnhanced',
  
  // Layout components
  'components/core/Header': '@/components/layout/HeaderEnhanced',
  'components/core/NotificationItem': '@/components/layout/NotificationItemEnhanced',
  
  // Chemistry components (to be enhanced)
  'components/features/PeriodicTable': '@/components/features/PeriodicTableEnhanced',
  'components/features/MolarMassCalculator': '@/components/chemistry/MolarMassCalculatorEnhanced',
  'components/features/PHCalculator': '@/components/chemistry/PHCalculatorEnhanced',
  'components/features/LewisStructureGenerator': '@/components/chemistry/LewisStructureGeneratorEnhanced',
  
  // Game components (to be enhanced)
  'components/features/chemwordle/ChemWordle': '@/components/games/ChemWordleEnhanced',
  'components/features/BalanceChallenge/BalanceChallengeGame': '@/components/games/BalanceChallengeEnhanced',
  'components/features/games/MemoryGame': '@/components/games/MemoryGameEnhanced',
  'components/features/PeriodicSpeedGame': '@/components/games/PeriodicSpeedGameEnhanced',
  'components/features/quiz/QuizGame': '@/components/games/QuizGameEnhanced',
};

// Export utility function to get new import path
export function getNewImportPath(oldPath: string): string {
  // Remove leading slashes and @/ prefix
  const normalizedPath = oldPath.replace(/^[@\/]+/, '').replace(/\.(tsx?|jsx?)$/, '');
  
  // Check if we have a direct mapping
  if (COMPONENT_MIGRATION_MAP[normalizedPath as keyof typeof COMPONENT_MIGRATION_MAP]) {
    return COMPONENT_MIGRATION_MAP[normalizedPath as keyof typeof COMPONENT_MIGRATION_MAP];
  }
  
  // Check for partial matches
  for (const [oldImport, newImport] of Object.entries(COMPONENT_MIGRATION_MAP)) {
    if (normalizedPath.includes(oldImport)) {
      return newImport;
    }
  }
  
  // Return original if no mapping found
  return oldPath;
}

// Export list of components that need to be created
export const COMPONENTS_TO_CREATE = [
  'HeaderEnhanced',
  'NotificationItemEnhanced',
  'MolarMassCalculatorEnhanced',
  'PHCalculatorEnhanced',
  'LewisStructureGeneratorEnhanced',
  'ChemWordleEnhanced',
  'BalanceChallengeEnhanced',
  'MemoryGameEnhanced',
  'PeriodicSpeedGameEnhanced',
  'QuizGameEnhanced',
];

// Export default theme configuration
export const ENHANCED_THEME = {
  animations: {
    duration: {
      fast: 0.2,
      normal: 0.3,
      slow: 0.5,
    },
    easing: {
      default: 'ease-in-out',
      bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
      smooth: 'cubic-bezier(0.4, 0, 0.2, 1)',
    },
  },
  colors: {
    primary: {
      50: '#E6FFFA',
      100: '#B2F5EA',
      200: '#81E6D9',
      300: '#4FD1C5',
      400: '#38B2AC',
      500: '#319795',
      600: '#2C7A7B',
      700: '#285E61',
      800: '#234E52',
      900: '#1D4044',
    },
  },
};
