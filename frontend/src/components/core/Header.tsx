'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '@/store';
import { logout } from '@/store/authSlice';

export default function Header() {
  const pathname = usePathname();
  const { isAuthenticated, user } = useSelector((state: RootState) => state.auth);
  const dispatch = useDispatch();

  return (
    <header className="w-full max-w-7xl flex justify-between items-center p-4 bg-white/80 backdrop-blur-md shadow-lg rounded-xl mb-8 sticky top-6 z-40">
      <Link href="/" className="text-2xl font-bold text-slate-900">ChemsTools</Link>
      <nav className="flex items-center space-x-6">
        {pathname !== '/' && <Link href="/" className="text-base text-gray-600 hover:text-indigo-600">Dashboard</Link>}
        <Link href="/periodic-table" className="text-base text-gray-600 hover:text-indigo-600">Tabla Periódica</Link>
      </nav>
      <div>
        {isAuthenticated && user ? (
          <div className="flex items-center space-x-4">
            <span className="text-gray-800">Bienvenido, {user.username}</span>
            <button onClick={() => dispatch(logout())} className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700">Logout</button>
          </div>
        ) : null }
      </div>
    </header>
  );
}