'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Layout, Menu, Button, Badge, Tooltip, Input, Space } from 'antd';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  HomeOutlined,
  ExperimentOutlined,
  BookOutlined,
  TrophyOutlined,
  TableOutlined,
  FireOutlined,
  ThunderboltOutlined,
  BlockOutlined,
  QuestionCircleOutlined,
  CalculatorOutlined,
  ApartmentOutlined,
  AppstoreOutlined,
  SearchOutlined,
  BellOutlined,
} from '@ant-design/icons';
import type { MenuProps } from 'antd';

const { Sider } = Layout;
const { Search } = Input;

interface DesktopSidebarProps {
  collapsed?: boolean;
  onCollapse?: (collapsed: boolean) => void;
}

const DesktopSidebar: React.FC<DesktopSidebarProps> = ({ 
  collapsed: controlledCollapsed, 
  onCollapse 
}) => {
  const [localCollapsed, setLocalCollapsed] = useState(false);
  const pathname = usePathname();
  
  // Use controlled or local state
  const collapsed = controlledCollapsed !== undefined ? controlledCollapsed : localCollapsed;
  const handleCollapse = (value: boolean) => {
    if (onCollapse) {
      onCollapse(value);
    } else {
      setLocalCollapsed(value);
    }
  };

  // Menu items with icons and badges
  const menuItems: MenuProps['items'] = [
    {
      key: 'home',
      icon: <HomeOutlined />,
      label: <Link href="/">Dashboard</Link>,
    },
    {
      type: 'divider',
    },
    {
      key: 'tools',
      icon: <ExperimentOutlined />,
      label: 'Herramientas',
      children: [
        {
          key: 'periodic-table',
          icon: <TableOutlined />,
          label: <Link href="/periodic-table">Tabla Periódica</Link>,
        },
        {
          key: 'calculator',
          icon: <CalculatorOutlined />,
          label: <Link href="/molar-calculator">Calculadora de Masa Molar</Link>,
        },
        {
          key: 'simulator',
          icon: <FireOutlined />,
          label: <Link href="/simulator">Simulador</Link>,
        },
        {
          key: 'lewis',
          icon: <ApartmentOutlined />,
          label: (
            
              <Link href="lewis">Estructuras Lewis</Link>
            
          ),
        },
        {
          key: 'glossary',
          icon: <BookOutlined />,
          label: <Link href="/glossary">Glosario</Link>,
        },
      ],
    },
    {
      key: 'games',
      icon: <TrophyOutlined />,
      label: 'Juegos',
      children: [
        {
          key: 'quiz',
          icon: <QuestionCircleOutlined />,
          label: <Link href="/games">Quiz</Link>,
        },
        {
          key: 'chemwordle',
          icon: <BlockOutlined />,
          label: (
            <Badge count="Hot" size="small" color="red">
              <Link href="/chemwordle">ChemWordle</Link>
            </Badge>
          ),
        },
        {
          key: 'memory',
          icon: <AppstoreOutlined />,
          label: <Link href="/memory">Memory</Link>,
        },
        {
          key: 'balance',
          icon: <CalculatorOutlined />,
          label: <Link href="/balance-challenge">Balance</Link>,
        },
        {
          key: 'speed',
          icon: <ThunderboltOutlined />,
          label: <Link href="/periodic-speed">Speed</Link>,
        },
      ],
    },
  ];

  // Get active menu keys
  const getSelectedKeys = () => {
    if (pathname === '/') return ['home'];
    if (pathname === '/periodic-table') return ['periodic-table'];
    if (pathname === '/simulator') return ['simulator'];
    if (pathname === '/glossary') return ['glossary'];
    if (pathname === '/games') return ['quiz'];
    if (pathname === '/chemwordle') return ['chemwordle'];
    if (pathname === '/memory') return ['memory'];
    if (pathname === '/balance-challenge') return ['balance'];
    if (pathname === '/periodic-speed') return ['speed'];
    return [];
  };

  const getOpenKeys = () => {
    const path = pathname;
    if (['/periodic-table', '/simulator', '/glossary'].includes(path) || path === '/') {
      return ['tools'];
    }
    if (['/games', '/chemwordle', '/memory', '/balance-challenge', '/periodic-speed'].includes(path)) {
      return ['games'];
    }
    return [];
  };

  return (
    <Sider
      collapsible
      collapsed={collapsed}
      onCollapse={handleCollapse}
      breakpoint="lg"
      collapsedWidth="80"
      width={260}
      className="hidden lg:block"
      theme="light"
      style={{
        overflow: 'auto',
        height: '100vh',
        position: 'sticky',
        left: 0,
        top: 0,
        bottom: 0,
        borderRight: '1px solid #e8e8e8',
      }}
    >
      {/* Logo Area */}
      <div className="h-16 flex items-center justify-center border-b border-gray-200 bg-white">
        {!collapsed ? (
          <Link href="/" className="flex items-center space-x-2">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <ExperimentOutlined className="text-white text-xl" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              ChemsTools
            </span>
          </Link>
        ) : (
          <Link href="/">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <ExperimentOutlined className="text-white text-xl" />
            </div>
          </Link>
        )}
      </div>

      {/* Search Box (when not collapsed) */}
      {!collapsed && (
        <div className="p-4">
          <Search
            placeholder="Buscar..."
            size="middle"
            prefix={<SearchOutlined />}
            allowClear
          />
        </div>
      )}

      {/* Navigation Menu */}
      <Menu
        mode="inline"
        selectedKeys={getSelectedKeys()}
        defaultOpenKeys={collapsed ? [] : getOpenKeys()}
        items={menuItems}
        className="border-none"
        style={{ borderRight: 0 }}
      />

      {/* Quick Actions (when not collapsed) */}
      {!collapsed && (
        <div className="absolute bottom-20 left-0 right-0 px-4">
          <Space direction="vertical" className="w-full">
            <Tooltip title="Notificaciones" placement="right">
              <Button
                type="text"
                icon={<BellOutlined />}
                className="w-full justify-start"
              >
                <Badge count={3} size="small">
                  <span className="ml-2">Notificaciones</span>
                </Badge>
              </Button>
            </Tooltip>
          </Space>
        </div>
      )}

      {/* Collapse Button */}
      <div className="absolute bottom-4 left-0 right-0 flex justify-center">
        <Button
          type="text"
          onClick={() => handleCollapse(!collapsed)}
          icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          className="text-gray-500"
        />
      </div>
    </Sider>
  );
};

export default DesktopSidebar;
