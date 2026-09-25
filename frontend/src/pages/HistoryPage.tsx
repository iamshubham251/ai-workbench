import React from 'react';
import { History } from 'lucide-react';

export const HistoryPage: React.FC = () => {
  return (
    <div className="documents-page">
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          gap: '20px',
          marginBottom: '24px',
          flexWrap: 'wrap',
        }}
      >
        <div>
          <div className="eyebrow">ACTIVITY</div>
          <h1
            style={{
              fontSize: '1.5rem',
              fontWeight: 600,
              marginBottom: '6px',
            }}
          >
            Workflow History
          </h1>
          <p
            style={{
              color: 'var(--text-secondary)',
              fontSize: '0.9rem',
            }}
          >
            Review past workflow executions and agent activities.
          </p>
        </div>
      </div>

      <div className="placeholder-page" style={{ height: '400px' }}>
        <History
          size={48}
          style={{
            color: 'var(--border-light)',
            marginBottom: '16px',
          }}
        />
        <h2>No workflow runs yet</h2>
        <p style={{ maxWidth: '400px' }}>
          Completed approval workflows will appear here. The backend currently processes workflows synchronously and does not store execution history in the database.
        </p>
      </div>
    </div>
  );
};
