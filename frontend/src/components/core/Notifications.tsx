'use client';
import { useSelector } from 'react-redux';
import { RootState } from '@/store';
import NotificationItem from './NotificationItem';

export default function Notifications() {
  const notifications = useSelector((state: RootState) => state.notifications.items);

  return (
    <div className="fixed bottom-4 right-4 space-y-2 z-50">
      {notifications.map(notification => (
        <NotificationItem
          key={notification.id}
          id={notification.id}
          message={notification.message}
          type={notification.type}
        />
      ))}
    </div>
  );
}