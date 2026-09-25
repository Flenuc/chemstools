'use client';
import { App } from 'antd';
import type { MessageInstance } from 'antd/es/message/interface';

/**
 * Hook personalizado para usar el sistema de mensajes de Ant Design
 * con el contexto correcto para evitar warnings de tema dinámico.
 */
export const useMessage = (): MessageInstance => {
  const { message } = App.useApp();
  return message;
};

// Exportar también una versión imperativa para usar fuera de componentes
// Esta versión no tendrá tema dinámico pero funcionará sin warnings
let messageApi: MessageInstance | null = null;

export const setMessageApi = (api: MessageInstance) => {
  messageApi = api;
};

export const showMessage = {
  success: (content: string) => {
    if (messageApi) {
      messageApi.success(content);
    } else {
      console.log('[Message]', content);
    }
  },
  error: (content: string) => {
    if (messageApi) {
      messageApi.error(content);
    } else {
      console.error('[Message]', content);
    }
  },
  info: (content: string) => {
    if (messageApi) {
      messageApi.info(content);
    } else {
      console.info('[Message]', content);
    }
  },
  warning: (content: string) => {
    if (messageApi) {
      messageApi.warning(content);
    } else {
      console.warn('[Message]', content);
    }
  },
  loading: (content: string) => {
    if (messageApi) {
      return messageApi.loading(content);
    } else {
      console.log('[Message Loading]', content);
      return () => {};
    }
  },
};
