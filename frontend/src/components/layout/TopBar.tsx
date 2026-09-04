import React from 'react';
import { Settings, User, Hexagon } from 'lucide-react';

export const TopBar: React.FC = () => {
  return (
    <header className="topbar">
      <div className="topbar-left">
        <div className="topbar-logo">
          <Hexagon className="topbar-logo-icon" size={24} />
          <span>AI Workbench</span>
        </div>
        <span className="badge-local">LOCAL</span>
      </div>
      <div className="topbar-right">
        <div className="status-indicator">
          <div className="status-dot"></div>
          <span>System Online</span>
        </div>
        <button className="icon-btn" aria-label="Settings">
          <Settings size={18} />
        </button>
        <div className="profile-avatar">
          <User size={18} />
        </div>
      </div>
    </header>
  );
};
