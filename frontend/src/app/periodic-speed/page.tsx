'use client';

import React from 'react';
import PeriodicSpeedGame from '@/components/features/PeriodicSpeedGame';
import Header from '@/components/core/Header';

export default function PeriodicSpeedPage() {
  return (
    <div className="min-h-screen">
        <Header />
      <PeriodicSpeedGame />
    </div>
  );
}