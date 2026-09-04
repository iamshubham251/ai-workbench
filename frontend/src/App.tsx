import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AppShell } from './components/layout/AppShell';
import { DashboardPage } from './pages/DashboardPage';
import { PlaceholderPage } from './pages/PlaceholderPage';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppShell />}>
          <Route index element={<DashboardPage />} />
          <Route path="documents" element={<PlaceholderPage title="Documents" description="Upload, manage, and process your documents securely." />} />
          <Route path="workflows" element={<PlaceholderPage title="Workflows" description="Design and monitor AI agent workflows." />} />
          <Route path="knowledge" element={<PlaceholderPage title="Your local knowledge base will appear here." description="Connect documents and SOPs to enable grounded AI workflows." />} />
          <Route path="sops" element={<PlaceholderPage title="SOP Library" description="Manage your Standard Operating Procedures." />} />
          <Route path="history" element={<PlaceholderPage title="History" description="Review past workflow executions and agent activities." />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
