import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppShell } from './components/layout/AppShell';
import { DashboardPage } from './pages/DashboardPage';
import { DocumentsPage } from './pages/DocumentsPage';
import { KnowledgeBasePage } from './pages/KnowledgeBasePage';
import { SOPLibraryPage } from './pages/SOPLibraryPage';
import { HistoryPage } from './pages/HistoryPage';
import { ApprovalWorkflowPanel } from './components/dashboard/ApprovalWorkflowPanel';
import { ArchitecturePage } from './pages/ArchitecturePage';
import LoginPage from './pages/LoginPage';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import './App.css';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      
      <Route path="/" element={
        <ProtectedRoute>
          <AppShell />
        </ProtectedRoute>
      }>
        <Route index element={<DashboardPage />} />
        <Route path="documents" element={<DocumentsPage />} />

        <Route
          path="workflows"
          element={
            <div>
              <ApprovalWorkflowPanel />
            </div>
          }
        />

        <Route path="knowledge" element={<KnowledgeBasePage />} />
        
        <Route path="architecture" element={<ArchitecturePage />} />

        <Route path="sops" element={<SOPLibraryPage />} />
        <Route path="history" element={<HistoryPage />} />
      </Route>
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
