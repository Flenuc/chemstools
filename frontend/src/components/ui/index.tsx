import React, { ReactNode, forwardRef } from 'react';
import { 
  Button as AntButton, 
  Input as AntInput,
  Card as AntCard,
  Modal as AntModal,
  Spin as AntSpin,
  message as antMessage,
  notification as antNotification,
  Space as AntSpace,
  Typography as AntTypography,
  Divider as AntDivider,
  Badge as AntBadge,
  Tag as AntTag,
  Tooltip as AntTooltip,
  Alert as AntAlert,
} from 'antd';
import type { 
  ButtonProps as AntButtonProps,
  InputProps as AntInputProps,
  CardProps as AntCardProps,
  ModalProps as AntModalProps,
  SpinProps as AntSpinProps,
  SpaceProps as AntSpaceProps,
  DividerProps as AntDividerProps,
  BadgeProps as AntBadgeProps,
  TagProps as AntTagProps,
  TooltipProps as AntTooltipProps,
  AlertProps as AntAlertProps,
} from 'antd';
import { cn } from '@/lib/utils';

// Enhanced Button Component
export interface ButtonProps extends Omit<AntButtonProps, 'className'> {
  className?: string;
  variant?: 'primary' | 'secondary' | 'ghost' | 'link' | 'danger';
  fullWidth?: boolean;
  isLoading?: boolean; // Custom loading prop
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', fullWidth, children, isLoading, ...props }, ref) => {
    const variantMap = {
      primary: 'primary',
      secondary: 'default',
      ghost: 'ghost',
      link: 'link',
      danger: 'primary',
    } as const;

    return (
      <AntButton
        ref={ref}
        type={variantMap[variant]}
        danger={variant === 'danger'}
        loading={isLoading} // Map isLoading to the correct Ant Design prop
        className={cn(
          'transition-all duration-200',
          fullWidth && 'w-full',
          className
        )}
        {...props}
      >
        {children}
      </AntButton>
    );
  }
);
Button.displayName = 'Button';

// Enhanced Input Component
export interface InputProps extends Omit<AntInputProps, 'className'> {
  className?: string;
  fullWidth?: boolean;
}

export const Input = forwardRef<any, InputProps>(
  ({ className, fullWidth, ...props }, ref) => {
    return (
      <AntInput
        ref={ref}
        className={cn(
          'transition-all duration-200',
          fullWidth && 'w-full',
          className
        )}
        {...props}
      />
    );
  }
);
Input.displayName = 'Input';

// Enhanced Card Component
export interface CardProps extends Omit<AntCardProps, 'className'> {
  className?: string;
  variant?: 'default' | 'bordered' | 'shadow';
}

export const Card: React.FC<CardProps> = ({ 
  className, 
  variant = 'default',
  children,
  ...props 
}) => {
  const variantClasses = {
    default: '',
    bordered: 'border border-gray-200',
    shadow: 'shadow-lg hover:shadow-xl transition-shadow duration-300',
  };

  return (
    <AntCard
      className={cn(
        'transition-all duration-200',
        variantClasses[variant],
        className
      )}
      {...props}
    >
      {children}
    </AntCard>
  );
};

// Enhanced Modal Component
export interface ModalProps extends Omit<AntModalProps, 'className'> {
  className?: string;
  containerClassName?: string;
}

export const Modal: React.FC<ModalProps> = ({ 
  className,
  containerClassName,
  children,
  ...props 
}) => {
  return (
    <AntModal
      className={cn('transition-all duration-200', className)}
      wrapClassName={containerClassName}
      {...props}
    >
      {children}
    </AntModal>
  );
};

// Enhanced Spinner Component
export interface SpinnerProps extends Omit<AntSpinProps, 'className'> {
  className?: string;
  fullScreen?: boolean;
}

export const Spinner: React.FC<SpinnerProps> = ({ 
  className,
  fullScreen,
  ...props 
}) => {
  if (fullScreen) {
    return (
      <div className="fixed inset-0 flex items-center justify-center bg-white bg-opacity-75 z-50">
        <AntSpin size="large" {...props} />
      </div>
    );
  }

  return (
    <AntSpin
      className={cn('transition-all duration-200', className)}
      {...props}
    />
  );
};

// Container Component
export interface ContainerProps {
  children: ReactNode;
  className?: string;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full';
  padding?: boolean;
}

export const Container: React.FC<ContainerProps> = ({
  children,
  className,
  maxWidth = 'xl',
  padding = true,
}) => {
  const maxWidthClasses = {
    sm: 'max-w-screen-sm',
    md: 'max-w-screen-md',
    lg: 'max-w-screen-lg',
    xl: 'max-w-screen-xl',
    '2xl': 'max-w-screen-2xl',
    full: 'max-w-full',
  };

  return (
    <div
      className={cn(
        'mx-auto',
        maxWidthClasses[maxWidth],
        padding && 'px-4 sm:px-6 lg:px-8',
        className
      )}
    >
      {children}
    </div>
  );
};

// Flex Component
export interface FlexProps {
  children: ReactNode;
  className?: string;
  direction?: 'row' | 'col' | 'row-reverse' | 'col-reverse';
  align?: 'start' | 'center' | 'end' | 'stretch' | 'baseline';
  justify?: 'start' | 'center' | 'end' | 'between' | 'around' | 'evenly';
  wrap?: boolean;
  gap?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
}

export const Flex: React.FC<FlexProps> = ({
  children,
  className,
  direction = 'row',
  align = 'start',
  justify = 'start',
  wrap = false,
  gap,
}) => {
  const directionClasses = {
    row: 'flex-row',
    col: 'flex-col',
    'row-reverse': 'flex-row-reverse',
    'col-reverse': 'flex-col-reverse',
  };

  const alignClasses = {
    start: 'items-start',
    center: 'items-center',
    end: 'items-end',
    stretch: 'items-stretch',
    baseline: 'items-baseline',
  };

  const justifyClasses = {
    start: 'justify-start',
    center: 'justify-center',
    end: 'justify-end',
    between: 'justify-between',
    around: 'justify-around',
    evenly: 'justify-evenly',
  };

  const gapClasses = {
    xs: 'gap-1',
    sm: 'gap-2',
    md: 'gap-4',
    lg: 'gap-6',
    xl: 'gap-8',
  };

  return (
    <div
      className={cn(
        'flex',
        directionClasses[direction],
        alignClasses[align],
        justifyClasses[justify],
        wrap && 'flex-wrap',
        gap && gapClasses[gap],
        className
      )}
    >
      {children}
    </div>
  );
};

// Grid Component
export interface GridProps {
  children: ReactNode;
  className?: string;
  cols?: 1 | 2 | 3 | 4 | 5 | 6 | 12;
  gap?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  responsive?: boolean;
}

export const Grid: React.FC<GridProps> = ({
  children,
  className,
  cols = 12,
  gap = 'md',
  responsive = true,
}) => {
  const gapClasses = {
    xs: 'gap-1',
    sm: 'gap-2',
    md: 'gap-4',
    lg: 'gap-6',
    xl: 'gap-8',
  };

  const colClasses = responsive
    ? {
        1: 'grid-cols-1',
        2: 'grid-cols-1 md:grid-cols-2',
        3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
        4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4',
        5: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-5',
        6: 'grid-cols-1 md:grid-cols-3 lg:grid-cols-6',
        12: 'grid-cols-1 md:grid-cols-4 lg:grid-cols-12',
      }
    : {
        1: 'grid-cols-1',
        2: 'grid-cols-2',
        3: 'grid-cols-3',
        4: 'grid-cols-4',
        5: 'grid-cols-5',
        6: 'grid-cols-6',
        12: 'grid-cols-12',
      };

  return (
    <div
      className={cn(
        'grid',
        colClasses[cols],
        gapClasses[gap],
        className
      )}
    >
      {children}
    </div>
  );
};

// Export remaining Ant Design components with consistent naming
export const Space = AntSpace;
export const Typography = AntTypography;
export const Divider = AntDivider;
export const Badge = AntBadge;
export const Tag = AntTag;
export const Tooltip = AntTooltip;
export const Alert = AntAlert;

// Export message and notification APIs
export const message = antMessage;
export const notification = antNotification;

// Type exports
export type {
  SpaceProps,
  DividerProps,
  BadgeProps,
  TagProps,
  TooltipProps,
  AlertProps,
};
