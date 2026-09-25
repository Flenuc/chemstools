'use client';
// antd v5 necesita este parche para sus APIs estáticas (message, Modal.confirm, notification) en React 19.
import '@ant-design/v5-patch-for-react-19';
import { Provider } from 'react-redux';
import { store } from '@/store';

export default function StoreProvider({ children }: { children: React.ReactNode }) {
  return <Provider store={store}>{children}</Provider>;
}
