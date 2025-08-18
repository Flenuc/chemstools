'use client';

import React from 'react';
import { Provider } from 'react-redux';
import { store } from '../../store';
import BalanceChallengeGame from '../../components/features/BalanceChallenge/BalanceChallengeGame';


export default function BalanceChallengePage() {
  return (
    <Provider store={store}>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <BalanceChallengeGame />
      </div>
    </Provider>
  );
}