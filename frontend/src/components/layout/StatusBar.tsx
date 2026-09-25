import React, { useEffect, useState } from 'react';
import { Server, Database, Cpu } from 'lucide-react';
import { API_BASE } from '../../services/apiClient';

interface HealthStatus {
  status: string;
  gemini_api_configured: boolean;
  model_name: string;
  embedding_model_ready: boolean;
}

export const StatusBar: React.FC = () => {
  const [health, setHealth] = useState<HealthStatus | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/health`)
      .then(res => res.json())
      .then(data => setHealth(data))
      .catch(() => setHealth(null));
  }, []);

  return (
    <footer className="statusbar">
      <div className="statusbar-item">
        <Server size={14} />
        <span>Mode: Local</span>
      </div>
      <div className="statusbar-item">
        <Database size={14} />
        <span>
          Knowledge Base: {health?.embedding_model_ready ? 'Available' : 'Unavailable'}
        </span>
      </div>
      <div className="statusbar-item">
        <Cpu size={14} />
        <span>
          Model: {health?.gemini_api_configured ? 'Configured' : 'Not configured'}
        </span>
      </div>
    </footer>
  );
};
