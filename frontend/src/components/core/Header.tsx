'use client';
import Link from 'next/link';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '@/store';
import { logout } from '@/store/authSlice';

export default function Header() {
  const { isAuthenticated, user } = useSelector((state: RootState) => state.auth);
  const dispatch = useDispatch();

  return (
    <header className="w-full max-w-4xl flex justify-between items-center p-4 bg-white shadow-md rounded-lg mb-8">
      <h1 className="text-2xl font-bold text-black-800">ChemsTools</h1>
      <div>
        <Link href="/periodic-table" className="text-blue-600 hover:underline">Tabla Periódica</Link>
        {isAuthenticated && user ? (
          <div className="flex items-center space-x-4">
            <span>Bienvenido, {user.username}</span>
            <button onClick={() => dispatch(logout())} className="px-3 py-1 bg-red-500 text-white rounded">Logout</button>
          </div>
        ) : (
          <p>Por favor, inicie sesión o regístrese.</p>
        )}
      </div>
    </header>
  );
}