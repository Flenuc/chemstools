'use client';
import { useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { removeNotification } from '@/store/notificationsSlice';

interface NotificationProps {
  id: number;
  message: string;
  type: 'success' | 'error' | 'info';
}

export default function NotificationItem({ id, message, type }: NotificationProps) {
  const dispatch = useDispatch();

  // Este hook ahora se llama de forma segura dentro de su propio componente.
  useEffect(() => {
    const timer = setTimeout(() => {
      dispatch(removeNotification(id));
    }, 5000);

    return () => clearTimeout(timer);
  }, [id, dispatch]);

  const typeClasses = {
    success: 'bg-green-500',
    error: 'bg-red-500',
    info: 'bg-blue-500',
  };

  return (
    <div
      className={`flex items-center justify-between p-4 rounded-lg text-white shadow-lg ${typeClasses[type]}`}
    >
      <p>{message}</p>
      <button onClick={() => dispatch(removeNotification(id))} className="ml-4 font-bold">
        &times;
      </button>
    </div>
  );
}