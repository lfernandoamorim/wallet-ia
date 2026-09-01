import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { AppLayout } from './components/layout/AppLayout';

// Páginas de Autenticação e Públicas
import { LoginPage } from './pages/auth/LoginPage';
import { RegisterPage } from './pages/auth/RegisterPage';
import { SharedViewPage } from './pages/shared/SharedViewPage';

// Páginas Protegidas da Plataforma
import { ChatPage } from './pages/chat/ChatPage';
import { AgentsPage } from './pages/agents/AgentsPage';
import { KnowledgeBasesPage } from './pages/knowledge/KnowledgeBasesPage';
import { KnowledgeBaseDetailPage } from './pages/knowledge/KnowledgeBaseDetailPage';
import { ProvidersPage } from './pages/providers/ProvidersPage';

// Páginas de Administração
import { UsersAdminPage } from './pages/admin/UsersAdminPage';
import { RolesAdminPage } from './pages/admin/RolesAdminPage';

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Rotas Públicas */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/share/:slug" element={<SharedViewPage />} />

            {/* Rotas Protegidas dentro do Layout Base */}
            <Route element={<ProtectedRoute />}>
              <Route element={<AppLayout />}>
                <Route path="/" element={<Navigate to="/chat" replace />} />
                <Route path="/chat" element={<ChatPage />} />
                <Route path="/agents" element={<AgentsPage />} />
                <Route path="/knowledge" element={<KnowledgeBasesPage />} />
                <Route path="/knowledge/:id" element={<KnowledgeBaseDetailPage />} />
                <Route path="/providers" element={<ProvidersPage />} />

                {/* Rotas Administrativas com RBAC */}
                <Route
                  path="/admin/users"
                  element={<ProtectedRoute requiredPermission="users:read" />}
                >
                  <Route index element={<UsersAdminPage />} />
                </Route>

                <Route
                  path="/admin/roles"
                  element={<ProtectedRoute requiredPermission="roles:read" />}
                >
                  <Route index element={<RolesAdminPage />} />
                </Route>
              </Route>
            </Route>

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/chat" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}
