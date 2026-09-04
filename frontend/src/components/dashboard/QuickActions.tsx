import React from 'react';
import { FileSearch, GitCompare, FileOutput } from 'lucide-react';

export const QuickActions: React.FC = () => {
  return (
    <div>
      <div className="section-title">Quick Actions</div>
      <div className="quick-actions-grid">
        <div className="card action-card">
          <div className="action-icon">
            <FileSearch size={20} />
          </div>
          <div className="action-title">Analyze Document</div>
        </div>
        <div className="card action-card">
          <div className="action-icon">
            <GitCompare size={20} />
          </div>
          <div className="action-title">Compare with SOP</div>
        </div>
        <div className="card action-card">
          <div className="action-icon">
            <FileOutput size={20} />
          </div>
          <div className="action-title">Generate Report</div>
        </div>
      </div>
    </div>
  );
};
