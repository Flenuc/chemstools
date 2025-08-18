'use client';
import React from 'react';
import { Form as AntForm, Input as AntInput, Select as AntSelect, DatePicker, Switch, Checkbox, Radio, Upload, Slider } from 'antd';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { Button } from '../index';
import { CloudUploadOutlined, InfoCircleOutlined } from '@ant-design/icons';
import type { FormInstance, FormItemProps, InputProps, SelectProps, TextAreaProps } from 'antd';

const { TextArea: AntTextArea } = AntInput;
const { Option } = AntSelect;

// ============= Form Provider =============
export const Form = AntForm;

// ============= Form Item con animaciones =============
interface AnimatedFormItemProps extends FormItemProps {
  animation?: 'fadeIn' | 'slideIn' | 'zoomIn';
  delay?: number;
}

export const FormItem: React.FC<AnimatedFormItemProps> = ({ 
  animation = 'fadeIn', 
  delay = 0,
  className,
  children,
  ...props 
}) => {
  const animations = {
    fadeIn: { initial: { opacity: 0 }, animate: { opacity: 1 } },
    slideIn: { initial: { x: -20, opacity: 0 }, animate: { x: 0, opacity: 1 } },
    zoomIn: { initial: { scale: 0.9, opacity: 0 }, animate: { scale: 1, opacity: 1 } }
  };

  return (
    <motion.div
      {...animations[animation]}
      transition={{ duration: 0.3, delay }}
    >
      <AntForm.Item 
        className={cn("mb-6", className)}
        {...props}
      >
        {children}
      </AntForm.Item>
    </motion.div>
  );
};

// ============= Input mejorado =============
interface EnhancedInputProps extends InputProps {
  icon?: React.ReactNode;
  showCount?: boolean;
  allowClear?: boolean;
}

export const Input: React.FC<EnhancedInputProps> = ({ 
  className, 
  icon, 
  showCount = false,
  allowClear = true,
  ...props 
}) => {
  return (
    <div className="relative">
      {icon && (
        <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 z-10">
          {icon}
        </div>
      )}
      <AntInput
        className={cn(
          "rounded-lg transition-all duration-200",
          "hover:border-primary-400 focus:border-primary-500",
          "placeholder:text-gray-400",
          icon && "pl-10",
          className
        )}
        showCount={showCount}
        allowClear={allowClear}
        {...props}
      />
    </div>
  );
};

// ============= TextArea mejorado =============
interface EnhancedTextAreaProps extends TextAreaProps {
  animate?: boolean;
}

export const TextArea: React.FC<EnhancedTextAreaProps> = ({ 
  className, 
  animate = true,
  ...props 
}) => {
  return (
    <motion.div
      whileFocus={{ scale: 1.01 }}
      transition={{ duration: 0.2 }}
    >
      <AntTextArea
        className={cn(
          "rounded-lg transition-all duration-200",
          "hover:border-primary-400 focus:border-primary-500",
          "placeholder:text-gray-400",
          className
        )}
        {...props}
      />
    </motion.div>
  );
};

// ============= Select mejorado =============
interface EnhancedSelectProps extends SelectProps {
  options?: { label: string; value: any; icon?: React.ReactNode }[];
  animate?: boolean;
}

export const Select: React.FC<EnhancedSelectProps> = ({ 
  className,
  options = [],
  animate = true,
  children,
  ...props 
}) => {
  const selectContent = (
    <AntSelect
      className={cn(
        "w-full rounded-lg",
        className
      )}
      {...props}
    >
      {options.map(option => (
        <Option key={option.value} value={option.value}>
          <div className="flex items-center gap-2">
            {option.icon}
            <span>{option.label}</span>
          </div>
        </Option>
      ))}
      {children}
    </AntSelect>
  );

  if (!animate) return selectContent;

  return (
    <motion.div
      whileFocus={{ scale: 1.01 }}
      transition={{ duration: 0.2 }}
    >
      {selectContent}
    </motion.div>
  );
};

// ============= Switch animado =============
interface AnimatedSwitchProps {
  label?: string;
  checked?: boolean;
  onChange?: (checked: boolean) => void;
  className?: string;
}

export const AnimatedSwitch: React.FC<AnimatedSwitchProps> = ({ 
  label, 
  checked, 
  onChange,
  className 
}) => {
  return (
    <motion.div 
      className={cn("flex items-center gap-3", className)}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <Switch 
        checked={checked}
        onChange={onChange}
        className="bg-gray-300"
      />
      {label && <span className="text-sm font-medium">{label}</span>}
    </motion.div>
  );
};

// ============= Radio Group mejorado =============
interface RadioOption {
  label: string;
  value: any;
  description?: string;
  icon?: React.ReactNode;
}

interface EnhancedRadioGroupProps {
  options: RadioOption[];
  value?: any;
  onChange?: (value: any) => void;
  className?: string;
  layout?: 'horizontal' | 'vertical' | 'grid';
}

export const RadioGroup: React.FC<EnhancedRadioGroupProps> = ({ 
  options, 
  value, 
  onChange,
  className,
  layout = 'vertical'
}) => {
  const layoutClasses = {
    horizontal: 'flex flex-row gap-4',
    vertical: 'flex flex-col gap-3',
    grid: 'grid grid-cols-2 gap-4'
  };

  return (
    <Radio.Group 
      value={value} 
      onChange={(e) => onChange?.(e.target.value)}
      className={cn(layoutClasses[layout], className)}
    >
      {options.map((option, index) => (
        <motion.label
          key={option.value}
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: index * 0.05 }}
          className={cn(
            "flex items-start gap-3 p-3 rounded-lg border border-gray-200",
            "hover:border-primary-300 hover:bg-primary-50/50 cursor-pointer",
            "transition-all duration-200",
            value === option.value && "border-primary-500 bg-primary-50"
          )}
        >
          <Radio value={option.value} />
          <div className="flex-1">
            <div className="flex items-center gap-2">
              {option.icon}
              <span className="font-medium">{option.label}</span>
            </div>
            {option.description && (
              <p className="text-sm text-gray-500 mt-1">{option.description}</p>
            )}
          </div>
        </motion.label>
      ))}
    </Radio.Group>
  );
};

// ============= Checkbox Group mejorado =============
export const CheckboxGroup: React.FC<{
  options: RadioOption[];
  value?: any[];
  onChange?: (values: any[]) => void;
  className?: string;
}> = ({ options, value = [], onChange, className }) => {
  return (
    <Checkbox.Group 
      value={value} 
      onChange={onChange}
      className={cn("flex flex-col gap-3", className)}
    >
      {options.map((option, index) => (
        <motion.label
          key={option.value}
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: index * 0.05 }}
          className={cn(
            "flex items-start gap-3 p-3 rounded-lg border border-gray-200",
            "hover:border-primary-300 hover:bg-primary-50/50 cursor-pointer",
            "transition-all duration-200",
            value?.includes(option.value) && "border-primary-500 bg-primary-50"
          )}
        >
          <Checkbox value={option.value} />
          <div className="flex-1">
            <div className="flex items-center gap-2">
              {option.icon}
              <span className="font-medium">{option.label}</span>
            </div>
            {option.description && (
              <p className="text-sm text-gray-500 mt-1">{option.description}</p>
            )}
          </div>
        </motion.label>
      ))}
    </Checkbox.Group>
  );
};

// ============= Upload mejorado =============
interface EnhancedUploadProps {
  accept?: string;
  multiple?: boolean;
  maxCount?: number;
  onUpload?: (files: File[]) => void;
  className?: string;
}

export const UploadArea: React.FC<EnhancedUploadProps> = ({ 
  accept,
  multiple = false,
  maxCount = 1,
  onUpload,
  className
}) => {
  return (
    <motion.div
      whileHover={{ scale: 1.01 }}
      whileTap={{ scale: 0.99 }}
      className={className}
    >
      <Upload.Dragger
        accept={accept}
        multiple={multiple}
        maxCount={maxCount}
        beforeUpload={(file) => {
          onUpload?.([file]);
          return false;
        }}
        className={cn(
          "!bg-gray-50 !border-2 !border-dashed !border-gray-300",
          "hover:!border-primary-400 hover:!bg-primary-50/30",
          "transition-all duration-200"
        )}
      >
        <div className="p-6">
          <CloudUploadOutlined className="text-4xl text-primary-500 mb-2" />
          <p className="text-base font-medium">
            Arrastra archivos aquí o haz clic para seleccionar
          </p>
          <p className="text-sm text-gray-500 mt-1">
            {multiple ? `Máximo ${maxCount} archivos` : 'Un archivo'}
          </p>
        </div>
      </Upload.Dragger>
    </motion.div>
  );
};

// ============= Slider mejorado =============
interface EnhancedSliderProps {
  min?: number;
  max?: number;
  step?: number;
  value?: number;
  onChange?: (value: number) => void;
  marks?: Record<number, string>;
  showValue?: boolean;
  className?: string;
}

export const AnimatedSlider: React.FC<EnhancedSliderProps> = ({
  min = 0,
  max = 100,
  step = 1,
  value,
  onChange,
  marks,
  showValue = true,
  className
}) => {
  return (
    <div className={cn("relative", className)}>
      {showValue && value !== undefined && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="absolute -top-8 left-0 right-0 text-center"
        >
          <span className="px-2 py-1 bg-primary-500 text-white text-sm rounded-full">
            {value}
          </span>
        </motion.div>
      )}
      <Slider
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={onChange}
        marks={marks}
        className="mt-2"
      />
    </div>
  );
};

// ============= Form Actions (botones del formulario) =============
interface FormActionsProps {
  onSubmit?: () => void;
  onCancel?: () => void;
  submitText?: string;
  cancelText?: string;
  loading?: boolean;
  className?: string;
  align?: 'left' | 'center' | 'right';
}

export const FormActions: React.FC<FormActionsProps> = ({
  onSubmit,
  onCancel,
  submitText = 'Guardar',
  cancelText = 'Cancelar',
  loading = false,
  className,
  align = 'right'
}) => {
  const alignClasses = {
    left: 'justify-start',
    center: 'justify-center',
    right: 'justify-end'
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className={cn(
        "flex gap-3 mt-8",
        alignClasses[align],
        className
      )}
    >
      {onCancel && (
        <Button
          variant="outline"
          onClick={onCancel}
          disabled={loading}
        >
          {cancelText}
        </Button>
      )}
      {onSubmit && (
        <Button
          variant="primary"
          onClick={onSubmit}
          loading={loading}
        >
          {submitText}
        </Button>
      )}
    </motion.div>
  );
};

// ============= Validación Helper =============
export const validateMessages = {
  required: '${label} es requerido',
  types: {
    email: '${label} no es un email válido',
    number: '${label} no es un número válido',
  },
  number: {
    range: '${label} debe estar entre ${min} y ${max}',
  },
  string: {
    min: '${label} debe tener al menos ${min} caracteres',
    max: '${label} debe tener máximo ${max} caracteres',
  }
};

// Export todo como namespace
export default {
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
};
