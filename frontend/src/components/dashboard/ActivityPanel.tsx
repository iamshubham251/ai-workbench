import React from 'react';
import { Cpu, FileSearch, Database, Zap } from 'lucide-react';

export const ActivityPanel: React.FC = () => {
  return (
    <div className="card" style={{ height: '100%' }}>
      <div className="section-title">Agent Activity</div>
      <div className="activity-panel">
        <div className="activity-item">
          <div className="activity-indicator active">
            <Zap size={14} />
          </div>
          <div className="activity-content">
            <div className="activity-title">Ready</div>
            <div className="activity-time">Awaiting new tasks</div>
          </div>
        </div>
        <div className="activity-item">
          <div className="activity-indicator">
            <FileSearch size={14} style={{ color: 'var(--text-muted)' }} />
          </div>
          <div className="activity-content">
            <div className="activity-title" style={{ color: 'var(--text-muted)' }}>Document processing</div>
            <div className="activity-time">Standby</div>
          </div>
        </div>
        <div className="activity-item">
          <div className="activity-indicator">
            <Database size={14} style={{ color: 'var(--text-muted)' }} />
          </div>
          <div className="activity-content">
            <div className="activity-title" style={{ color: 'var(--text-muted)' }}>Searching knowledge base</div>
            <div className="activity-time">Standby</div>
          </div>
        </div>
        <div className="activity-item">
          <div className="activity-indicator">
            <Cpu size={14} style={{ color: 'var(--text-muted)' }} />
          </div>
          <div className="activity-content">
            <div className="activity-title" style={{ color: 'var(--text-muted)' }}>Generating deliverable</div>
            <div className="activity-time">Standby</div>
          </div>
        </div>
      </div>
    </div>
  );
};
