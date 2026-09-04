import React from 'react';
import { Server, Database, Cpu } from 'lucide-react';

export const StatusBar: React.FC = () => {
  return (
    <footer className="statusbar">
      <div className="statusbar-item">
        <Server size={14} />
        <span>Mode: Local</span>
      </div>
      <div className="statusbar-item">
        <Database size={14} />
        <span>Knowledge Base: Not configured</span>
      </div>
      <div className="statusbar-item">
        <Cpu size={14} />
        <span>Model: Not configured</span>
      </div>
    </footer>
  );
};
