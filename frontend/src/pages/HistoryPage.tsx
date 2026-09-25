import React, { useEffect, useState } from 'react';
import { History, Loader2, AlertCircle, CheckCircle2, ShieldAlert, Activity, FileText } from 'lucide-react';
import { getWorkflowHistory, type WorkflowRunHistoryItem } from '../services/workflowService';

export const HistoryPage: React.FC = () => {
  const [history, setHistory] = useState<WorkflowRunHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getWorkflowHistory();
      setHistory(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load history');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadHistory();
  }, []);

  const getStatusBadge = (status: string, decision: string | null) => {
    if (status === 'RUNNING') {
      return (
        <span className="badge" style={{ backgroundColor: 'var(--bg-card-hover)', color: 'var(--text-secondary)' }}>
          <Loader2 size={12} className="spin" style={{ marginRight: '4px' }} />
          RUNNING
        </span>
      );
    }
    if (status === 'FAILED') {
      return (
        <span className="badge badge-danger">
          <AlertCircle size={12} style={{ marginRight: '4px' }} />
          FAILED
        </span>
      );
    }
    
    if (status === 'COMPLETED' && decision) {
      if (decision === 'approve') {
        return (
          <span className="badge badge-success">
            <CheckCircle2 size={12} style={{ marginRight: '4px' }} />
            APPROVE
          </span>
        );
      }
      if (decision === 'reject') {
        return (
          <span className="badge badge-danger">
            <ShieldAlert size={12} style={{ marginRight: '4px' }} />
            REJECT
          </span>
        );
      }
      if (decision === 'review') {
        return (
          <span className="badge badge-warning">
            <AlertCircle size={12} style={{ marginRight: '4px' }} />
            REVIEW
          </span>
        );
      }
    }
    
    return <span className="badge">{status}</span>;
  };

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

      {loading ? (
        <div className="placeholder-page" style={{ height: '400px' }}>
          <Loader2 size={48} className="spin" style={{ color: 'var(--border-light)', marginBottom: '16px' }} />
          <p>Loading workflow history...</p>
        </div>
      ) : error ? (
        <div className="placeholder-page" style={{ height: '400px' }}>
          <AlertCircle size={48} style={{ color: 'var(--red-400)', marginBottom: '16px' }} />
          <p style={{ color: 'var(--red-400)', marginBottom: '16px' }}>{error}</p>
          <button className="primary-action" onClick={loadHistory}>Retry</button>
        </div>
      ) : history.length === 0 ? (
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
            Completed approval workflows will appear here.
          </p>
        </div>
      ) : (
        <div className="card documents-table-container">
          <table className="documents-table">
            <thead>
              <tr>
                <th>Workflow ID</th>
                <th>Document</th>
                <th>Status / Decision</th>
                <th>Started</th>
                <th>Output</th>
              </tr>
            </thead>
            <tbody>
              {history.map((run) => (
                <tr key={run.id}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Activity size={16} style={{ color: 'var(--text-muted)' }} />
                      <span style={{ fontFamily: 'monospace', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                        {run.id.substring(0, 8)}...
                      </span>
                    </div>
                  </td>
                  <td>
                    <div style={{ fontWeight: 500 }}>{run.document_name}</div>
                  </td>
                  <td>
                    {getStatusBadge(run.status, run.decision)}
                  </td>
                  <td style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                    {new Date(run.created_at).toLocaleString()}
                  </td>
                  <td>
                    {run.has_output ? (
                      <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                        <FileText size={14} /> Available
                      </span>
                    ) : (
                      <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>None</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
