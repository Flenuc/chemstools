/**
 * Central export file for all migrated components
 * This file serves as the main entry point for importing enhanced components
 */

// ============= UI Components (Base) =============
export * from '@/components/ui';
export * from '@/components/ui/forms';

// ============= Animations =============
export * from '@/lib/animations';

// ============= Authentication =============
export { default as LoginForm } from '@/components/features/LoginFormEnhanced';

// ============= Chemistry Components =============
export { default as PeriodicTable } from '@/components/features/PeriodicTableEnhanced';
export { default as MolarMassCalculator } from '@/components/chemistry/MolarMassCalculatorEnhanced';

// ============= Common Components (Re-exports) =============
// These are now aliases to the enhanced UI components
export { Button } from '@/components/ui';
export { Card } from '@/components/ui';
export { Modal } from '@/components/ui';
export { Alert } from '@/components/ui';
export { Badge } from '@/components/ui';
export { Tag } from '@/components/ui';
export { Tooltip } from '@/components/ui';
export { Container } from '@/components/ui';

// ============= Form Components =============
export { 
  Form,
  FormItem,
  Input,
  TextArea,
  Select,
  AnimatedSwitch,
  RadioGroup,
  CheckboxGroup,
  UploadArea,
  AnimatedSlider,
  FormActions,
  validateMessages 
} from '@/components/ui/forms';

// ============= Layout Components =============
// These will be created as enhanced versions
// export { default as Header } from '@/components/layout/HeaderEnhanced';
// export { default as NotificationItem } from '@/components/layout/NotificationItemEnhanced';

// ============= Game Components =============
// These will be created as enhanced versions
// export { default as ChemWordle } from '@/components/games/ChemWordleEnhanced';
// export { default as BalanceChallenge } from '@/components/games/BalanceChallengeEnhanced';
// export { default as MemoryGame } from '@/components/games/MemoryGameEnhanced';
// export { default as PeriodicSpeedGame } from '@/components/games/PeriodicSpeedGameEnhanced';
// export { default as QuizGame } from '@/components/games/QuizGameEnhanced';

// ============= Utility Functions =============
export { cn } from '@/lib/utils';

// ============= Theme Configuration =============
export { ENHANCED_THEME } from '@/components/migration-map';

// ============= Type Exports =============
export type { ButtonProps } from '@/components/ui';
export type { CardProps } from '@/components/ui';
export type { ModalProps } from '@/components/ui';
export type { AlertProps } from '@/components/ui';

// ============= Migration Utilities =============
export { getNewImportPath, COMPONENT_MIGRATION_MAP } from '@/components/migration-map';
