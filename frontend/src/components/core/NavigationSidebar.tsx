'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Layout, Menu, Drawer, Button, Badge, Avatar, Dropdown, Space, Typography, Tooltip } from 'antd';
import {
  MenuOutlined,
  HomeOutlined,
  ExperimentOutlined,
  BookOutlined,
  TrophyOutlined,
  ToolOutlined,
  AppstoreOutlined,
  TableOutlined,
  FormatPainterOutlined,
  FireOutlined,
  BgColorsOutlined,
  ThunderboltOutlined,
  BlockOutlined,
  ClockCircleOutlined,
  QuestionCircleOutlined,
  CalculatorOutlined,
  ApartmentOutlined,
  LogoutOutlined,
  UserOutlined,
  SettingOutlined,
  ApiOutlined,
  BugOutlined,
  CodeOutlined,
  DashboardOutlined,
} from '@ant-design/icons';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '@/store';
import { logout } from '@/store/authSlice';
import type { MenuProps } from 'antd';

const { Title, Text } = Typography;

interface NavigationItem {
  key: string;
  label: string;
  path: string;
  icon?: React.ReactNode;
  badge?: number | string;
  description?: string;
}

interface NavigationCategory {
  key: string;
  label: string;
  icon: React.ReactNode;
  children: NavigationItem[];
}

const NavigationSidebar: React.FC = () => {
  const [drawerVisible, setDrawerVisible] = useState(false);
  const pathname = usePathname();
  const { isAuthenticated, user } = useSelector((state: RootState) => state.auth);
  const dispatch = useDispatch();

  // Navigation structure with categories
  const navigationCategories: NavigationCategory[] = [
    {
      key: 'tools',
      label: 'Herramientas Químicas',
      icon: <ExperimentOutlined />,
      children: [
        {
          key: 'periodic-table',
          label: 'Tabla Periódica',
          path: '/periodic-table',
          icon: <TableOutlined />,
          description: 'Tabla periódica interactiva'
        },
        {
          key: 'simulator',
          label: 'Simulador de Reacciones',
          path: '/simulator',
          icon: <FireOutlined />,
          description: 'Simula y balancea reacciones químicas'
        },
        {
          key: 'lewis-structures',
          label: 'Estructuras de Lewis',
          path: '/',
          icon: <ApartmentOutlined />,
          description: 'Generador de estructuras de Lewis',
          badge: 'New'
        },
        {
          key: 'glossary',
          label: 'Glosario',
          path: '/glossary',
          icon: <BookOutlined />,
          description: 'Términos y conceptos químicos'
        },
      ]
    },
    {
      key: 'games',
      label: 'Juegos Educativos',
      icon: <TrophyOutlined />,
      children: [
        {
          key: 'quiz',
          label: 'Quiz Químico',
          path: '/games',
          icon: <QuestionCircleOutlined />,
          description: 'Pon a prueba tus conocimientos'
        },
        {
          key: 'chemwordle',
          label: 'ChemWordle',
          path: '/chemwordle',
          icon: <BlockOutlined />,
          description: 'Wordle versión química',
          badge: 'Hot'
        },
        {
          key: 'memory',
          label: 'Memory Game',
          path: '/memory',
          icon: <AppstoreOutlined />,
          description: 'Juego de memoria con elementos'
        },
        {
          key: 'balance-challenge',
          label: 'Balance Challenge',
          path: '/balance-challenge',
          icon: <CalculatorOutlined />,
          description: 'Balancea ecuaciones químicas'
        },
        {
          key: 'periodic-speed',
          label: 'Periodic Speed',
          path: '/periodic-speed',
          icon: <ThunderboltOutlined />,
          description: 'Velocidad con tabla periódica'
        },
      ]
    },
    {
      key: 'demos',
      label: 'Demos y Pruebas',
      icon: <CodeOutlined />,
      children: [
        {
          key: 'demo-hybrid',
          label: 'Demo Híbrido',
          path: '/demo-hybrid',
          icon: <ApiOutlined />,
        },
        {
          key: 'ui-demo',
          label: 'Demo UI',
          path: '/ui-demo',
          icon: <FormatPainterOutlined />,
        },
        {
          key: 'test-css',
          label: 'Test CSS',
          path: '/test-css',
          icon: <BgColorsOutlined />,
        },
        {
          key: 'diagnostics',
          label: 'Diagnósticos',
          path: '/diagnostics',
          icon: <BugOutlined />,
        },
      ]
    },
  ];

  // Convert navigation structure to Ant Design Menu items
  const menuItems: MenuProps['items'] = [
    {
      key: 'home',
      icon: <HomeOutlined />,
      label: (
        <Link href="/">
          Dashboard
        </Link>
      ),
    },
    ...navigationCategories.map(category => ({
      key: category.key,
      icon: category.icon,
      label: category.label,
      children: category.children.map(item => ({
        key: item.key,
        icon: item.icon,
        label: item.badge ? (
          <Badge count={item.badge} offset={[10, 0]}>
            <Link href={item.path}>
              {item.label}
            </Link>
          </Badge>
        ) : (
          <Link href={item.path}>
            {item.label}
          </Link>
        ),
      })),
    })),
  ];

  // User menu items
  const userMenuItems: MenuProps['items'] = isAuthenticated && user ? [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Mi Perfil',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: 'Configuración',
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Cerrar Sesión',
      danger: true,
      onClick: () => dispatch(logout()),
    },
  ] : [
    {
      key: 'login',
      icon: <UserOutlined />,
      label: (
        <Link href="/login">
          Iniciar Sesión
        </Link>
      ),
    },
    {
      key: 'register',
      icon: <UserOutlined />,
      label: (
        <Link href="/register">
          Registrarse
        </Link>
      ),
    },
  ];

  // Find current active keys for menu
  const getActiveKeys = () => {
    const activeCategory = navigationCategories.find(cat =>
      cat.children.some(child => child.path === pathname)
    );
    const activeItem = activeCategory?.children.find(child => child.path === pathname);
    
    if (pathname === '/') return ['home'];
    if (activeItem) return [activeItem.key];
    return [];
  };

  const getOpenKeys = () => {
    const activeCategory = navigationCategories.find(cat =>
      cat.children.some(child => child.path === pathname)
    );
    return activeCategory ? [activeCategory.key] : [];
  };

  return (
    <>
      {/* Modern Header */}
      <header className="bg-white shadow-lg px-4 sm:px-6 lg:px-8 sticky top-0 z-50 border-b border-gray-200 h-16">
        <div className="flex justify-between items-center h-16">
          {/* Left side - Logo and Menu Button */}
          <div className="flex items-center space-x-4">
            <Button
              type="text"
              icon={<MenuOutlined />}
              onClick={() => setDrawerVisible(true)}
              className="lg:hidden"
              size="large"
            />
            
            <Link href="/" className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <ExperimentOutlined className="text-white text-xl" />
              </div>
              <Title level={4} className="!mb-0 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                ChemsTools
              </Title>
            </Link>

            {/* Desktop Navigation - Quick Access */}
            <nav className="hidden lg:flex items-center space-x-1 ml-8">
              <Tooltip title="Tabla Periódica">
                <Link href="/periodic-table">
                  <Button type="text" icon={<TableOutlined />} />
                </Link>
              </Tooltip>
              <Tooltip title="Simulador">
                <Link href="/simulator">
                  <Button type="text" icon={<FireOutlined />} />
                </Link>
              </Tooltip>
              <Tooltip title="Glosario">
                <Link href="/glossary">
                  <Button type="text" icon={<BookOutlined />} />
                </Link>
              </Tooltip>
              <Tooltip title="Juegos">
                <Link href="/games">
                  <Button type="text" icon={<TrophyOutlined />} />
                </Link>
              </Tooltip>
            </nav>
          </div>

          {/* Center - Search (optional for future) */}
          <div className="hidden xl:flex flex-1 max-w-xl mx-8">
            {/* Future search bar can go here */}
          </div>

          {/* Right side - User Menu */}
          <div className="flex items-center space-x-4">
            {isAuthenticated && user ? (
              <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
                <Space className="cursor-pointer">
                  <Avatar icon={<UserOutlined />} className="bg-gradient-to-r from-blue-500 to-purple-600" />
                  <Text className="hidden sm:inline">{user.username}</Text>
                </Space>
              </Dropdown>
            ) : (
              <Space>
                <Link href="/login">
                  <Button type="primary">Iniciar Sesión</Button>
                </Link>
              </Space>
            )}
          </div>
        </div>
      </header>

      {/* Mobile/Tablet Drawer */}
      <Drawer
        title={
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <ExperimentOutlined className="text-white" />
            </div>
            <span>ChemsTools</span>
          </div>
        }
        placement="left"
        onClose={() => setDrawerVisible(false)}
        open={drawerVisible}
        width={280}
        className="lg:hidden"
      >
        <Menu
          mode="inline"
          selectedKeys={getActiveKeys()}
          defaultOpenKeys={getOpenKeys()}
          items={menuItems}
          onClick={() => setDrawerVisible(false)}
          className="border-none"
        />
        
        {/* User info in drawer */}
        {isAuthenticated && user && (
          <div className="absolute bottom-0 left-0 right-0 p-4 border-t">
            <div className="flex items-center space-x-3 mb-3">
              <Avatar icon={<UserOutlined />} className="bg-gradient-to-r from-blue-500 to-purple-600" />
              <div>
                <div className="font-semibold">{user.username}</div>
                <div className="text-xs text-gray-500">{user.email}</div>
              </div>
            </div>
            <Button 
              danger 
              block 
              onClick={() => {
                dispatch(logout());
                setDrawerVisible(false);
              }}
              icon={<LogoutOutlined />}
            >
              Cerrar Sesión
            </Button>
          </div>
        )}
      </Drawer>
    </>
  );
};

export default NavigationSidebar;
