import React from 'react';
import { AuthProvider } from './contexts/AuthContext';
import { ChatProvider } from './contexts/ChatContext';
import { AuthGuard } from './components/auth/AuthGuard';
import { Layout } from './components/layout/Layout';
import { AuthPage } from './pages/AuthPage';

function App() {
  return (
    <AuthProvider>
      <ChatProvider>
        <AuthGuard fallback={<AuthPage />}>
          <Layout />
        </AuthGuard>
      </ChatProvider>
    </AuthProvider>
  );
}

export default App;