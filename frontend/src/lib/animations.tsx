import React, { ReactNode } from 'react';
import { motion, AnimatePresence, Variants } from 'framer-motion';
import type { MotionProps } from 'framer-motion';

// Animation Variants
export const animations = {
  // Fade animations
  fadeIn: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
  },
  
  fadeInUp: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 },
  },
  
  fadeInDown: {
    initial: { opacity: 0, y: -20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: 20 },
  },
  
  fadeInLeft: {
    initial: { opacity: 0, x: -20 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: 20 },
  },
  
  fadeInRight: {
    initial: { opacity: 0, x: 20 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -20 },
  },
  
  // Scale animations
  scaleIn: {
    initial: { scale: 0.8, opacity: 0 },
    animate: { scale: 1, opacity: 1 },
    exit: { scale: 0.8, opacity: 0 },
  },
  
  scaleInBounce: {
    initial: { scale: 0, opacity: 0 },
    animate: { 
      scale: 1, 
      opacity: 1,
      transition: {
        type: 'spring',
        stiffness: 260,
        damping: 20,
      },
    },
    exit: { scale: 0, opacity: 0 },
  },
  
  // Slide animations
  slideInFromLeft: {
    initial: { x: '-100%', opacity: 0 },
    animate: { x: 0, opacity: 1 },
    exit: { x: '-100%', opacity: 0 },
  },
  
  slideInFromRight: {
    initial: { x: '100%', opacity: 0 },
    animate: { x: 0, opacity: 1 },
    exit: { x: '100%', opacity: 0 },
  },
  
  slideInFromTop: {
    initial: { y: '-100%', opacity: 0 },
    animate: { y: 0, opacity: 1 },
    exit: { y: '-100%', opacity: 0 },
  },
  
  slideInFromBottom: {
    initial: { y: '100%', opacity: 0 },
    animate: { y: 0, opacity: 1 },
    exit: { y: '100%', opacity: 0 },
  },
  
  // Rotate animations
  rotateIn: {
    initial: { rotate: -180, opacity: 0 },
    animate: { rotate: 0, opacity: 1 },
    exit: { rotate: 180, opacity: 0 },
  },
  
  // Flip animations
  flipIn: {
    initial: { rotateX: -90, opacity: 0 },
    animate: { rotateX: 0, opacity: 1 },
    exit: { rotateX: 90, opacity: 0 },
  },
  
  // Complex animations
  morphIn: {
    initial: { 
      scale: 0,
      rotate: -180,
      opacity: 0,
    },
    animate: { 
      scale: 1,
      rotate: 0,
      opacity: 1,
      transition: {
        duration: 0.5,
        ease: 'easeInOut',
      },
    },
    exit: { 
      scale: 0,
      rotate: 180,
      opacity: 0,
    },
  },
};

// Stagger animations for lists
export const staggerVariants: Variants = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.1,
    },
  },
  exit: {
    transition: {
      staggerChildren: 0.05,
      staggerDirection: -1,
    },
  },
};

export const staggerItemVariants: Variants = {
  initial: {
    opacity: 0,
    y: 20,
  },
  animate: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.3,
    },
  },
  exit: {
    opacity: 0,
    y: -20,
    transition: {
      duration: 0.2,
    },
  },
};

// Animation Components
interface AnimatedComponentProps extends MotionProps {
  children: ReactNode;
  animation?: keyof typeof animations;
  delay?: number;
  duration?: number;
  className?: string;
}

export const AnimatedDiv: React.FC<AnimatedComponentProps> = ({
  children,
  animation = 'fadeIn',
  delay = 0,
  duration = 0.3,
  className,
  ...props
}) => {
  const selectedAnimation = animations[animation];
  
  return (
    <motion.div
      initial={selectedAnimation.initial}
      animate={selectedAnimation.animate}
      exit={selectedAnimation.exit}
      transition={{ delay, duration }}
      className={className}
      {...props}
    >
      {children}
    </motion.div>
  );
};

// Page Transition Component
interface PageTransitionProps {
  children: ReactNode;
  animation?: keyof typeof animations;
}

export const PageTransition: React.FC<PageTransitionProps> = ({ 
  children, 
  animation = 'fadeIn' 
}) => {
  const [pathname, setPathname] = React.useState('');
  
  React.useEffect(() => {
    // Solo acceder a window en el cliente
    if (typeof window !== 'undefined') {
      setPathname(window.location.pathname);
    }
  }, []);
  
  return (
    <AnimatePresence mode="wait">
      <AnimatedDiv
        key={pathname}
        animation={animation}
        duration={0.4}
        className="min-h-screen"
      >
        {children}
      </AnimatedDiv>
    </AnimatePresence>
  );
};

// Stagger List Component
interface StaggerListProps {
  children: ReactNode;
  className?: string;
}

export const StaggerList: React.FC<StaggerListProps> = ({
  children,
  className,
}) => {
  return (
    <motion.div
      variants={staggerVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      className={className}
    >
      {children}
    </motion.div>
  );
};

interface StaggerItemProps {
  children: ReactNode;
  className?: string;
}

export const StaggerItem: React.FC<StaggerItemProps> = ({
  children,
  className,
}) => {
  return (
    <motion.div
      variants={staggerItemVariants}
      className={className}
    >
      {children}
    </motion.div>
  );
};

// Loading State Components
export const PulseLoader: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <motion.div
      className={className}
      animate={{
        scale: [1, 1.2, 1],
        opacity: [1, 0.5, 1],
      }}
      transition={{
        duration: 1.5,
        repeat: Infinity,
        ease: 'easeInOut',
      }}
    />
  );
};

export const SpinLoader: React.FC<{ className?: string; size?: number }> = ({ 
  className,
  size = 40,
}) => {
  return (
    <motion.div
      className={className}
      style={{
        width: size,
        height: size,
        border: `3px solid rgba(24, 144, 255, 0.2)`,
        borderTop: `3px solid #1890ff`,
        borderRadius: '50%',
      }}
      animate={{ rotate: 360 }}
      transition={{
        duration: 1,
        repeat: Infinity,
        ease: 'linear',
      }}
    />
  );
};

export const DotsLoader: React.FC<{ className?: string }> = ({ className }) => {
  const dotVariants = {
    animate: {
      y: [0, -10, 0],
      transition: {
        duration: 0.6,
        repeat: Infinity,
        ease: 'easeInOut',
      },
    },
  };

  return (
    <div className={`flex space-x-2 ${className}`}>
      {[0, 0.1, 0.2].map((delay, index) => (
        <motion.div
          key={index}
          className="w-2 h-2 bg-blue-500 rounded-full"
          variants={dotVariants}
          animate="animate"
          transition={{ delay }}
        />
      ))}
    </div>
  );
};

// Skeleton Loader
interface SkeletonProps {
  className?: string;
  width?: string | number;
  height?: string | number;
  rounded?: boolean;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  className,
  width = '100%',
  height = 20,
  rounded = false,
}) => {
  return (
    <motion.div
      className={`bg-gray-200 ${rounded ? 'rounded-full' : 'rounded'} ${className}`}
      style={{ width, height }}
      animate={{
        backgroundImage: [
          'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)',
          'linear-gradient(90deg, #e0e0e0 25%, #f0f0f0 50%, #e0e0e0 75%)',
          'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)',
        ],
      }}
      transition={{
        duration: 1.5,
        repeat: Infinity,
        ease: 'linear',
      }}
    />
  );
};

// Hover animations
export const hoverScale = {
  whileHover: { scale: 1.05 },
  whileTap: { scale: 0.95 },
};

export const hoverRotate = {
  whileHover: { rotate: 5 },
  whileTap: { rotate: -5 },
};

export const hoverGlow = {
  whileHover: {
    boxShadow: '0 0 20px rgba(24, 144, 255, 0.5)',
  },
};

// Utility function to create custom animations
export const createAnimation = (
  initial: any,
  animate: any,
  exit?: any,
  transition?: any
) => ({
  initial,
  animate,
  exit: exit || initial,
  transition: transition || { duration: 0.3 },
});

// Export stagger variants
export const staggerContainer = staggerVariants;
export const staggerItem = staggerItemVariants;

// Export motion components for direct use
export { motion, AnimatePresence } from 'framer-motion';
