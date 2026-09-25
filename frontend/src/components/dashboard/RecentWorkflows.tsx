import React from 'react';
import { Download, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';

const demoScenarios = [
  {
    id: 'approve',
    title: '🟢 Pipeline Alpha (Approve)',
    description: 'Clean pass. Pressure and temp are within SOP thresholds.',
    inspection: '/demo-fixtures/demo_inspection_approve.pdf',
    sop: '/demo-fixtures/demo_sop_approve.pdf'
  },
  {
    id: 'review',
    title: '🟡 Generator Beta (Review)',
    description: 'Missing voltage data. SOP requires manual review.',
    inspection: '/demo-fixtures/demo_inspection_review.pdf',
    sop: '/demo-fixtures/demo_sop_review.pdf'
  },
  {
    id: 'reject',
    title: '🔴 Boiler Gamma (Reject)',
    description: 'Hairline fracture detected. SOP dictates immediate failure.',
    inspection: '/demo-fixtures/demo_inspection_reject.pdf',
    sop: '/demo-fixtures/demo_sop_reject.pdf'
  }
];

export const RecentWorkflows: React.FC = () => {
  return (
    <div>
      <div className="section-title">Demo Scenarios</div>
      <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '16px' }}>
        Download these synthetic fixtures and upload them to test the workflow logic.
      </p>
      <div className="workflows-list">
        {demoScenarios.map(scenario => (
          <div key={scenario.id} className="workflow-item" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '8px' }}>
            <div className="workflow-info">
              <h4 style={{ margin: 0 }}>{scenario.title}</h4>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', margin: 0 }}>{scenario.description}</p>
            <div className="workflow-meta" style={{ marginTop: '8px', display: 'flex', gap: '12px' }}>
              <a href={scenario.inspection} download className="badge badge-outline" style={{ display: 'flex', alignItems: 'center', gap: '4px', textDecoration: 'none', color: 'inherit' }}>
                <Download size={12} /> Inspection Report
              </a>
              <a href={scenario.sop} download className="badge badge-outline" style={{ display: 'flex', alignItems: 'center', gap: '4px', textDecoration: 'none', color: 'inherit' }}>
                <Download size={12} /> SOP Requirements
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
