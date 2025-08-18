'use client';

import React, { useState } from 'react';
import { Layout } from 'antd';
import NavigationSidebar from './NavigationSidebar';
import DesktopSidebar from './DesktopSidebar';
import { usePathname } from 'next/navigation';

const { Content } = Layout;

interface AppLayoutProps {
  children: React.ReactNode;
}

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const pathname = usePathname();
  
  // Check if we should show navigation (not on login/register pages)
  const showNavigation = !['/login', '/register', '/register-debug', '/test-register'].includes(pathname);

  if (!showNavigation) {
    // For auth pages, just render children without navigation
    return <>{children}</>;
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* Desktop Sidebar - Hidden on mobile/tablet */}
      <DesktopSidebar 
        collapsed={sidebarCollapsed} 
        onCollapse={setSidebarCollapsed}
      />
      
      <Layout>
        {/* Mobile/Tablet Navigation Header */}
        <div className="lg:hidden">
          <NavigationSidebar />
        </div>
        
        {/* Main Content Area */}
        <Content
          style={{
            padding: '24px',
            minHeight: 280,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          }}
          className="overflow-auto"
        >
          <div 
            style={{
              background: 'rgba(255, 255, 255, 0.95)',
              borderRadius: '12px',
              padding: '24px',
              minHeight: '100%',
              backdropFilter: 'blur(10px)',
            }}
          >
            {children}
          </div>
        </Content>
      </Layout>
    </Layout>
  );
};

export default AppLayout;
