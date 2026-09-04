import React from 'react';
import { ArrowRight, CheckCircle2 } from 'lucide-react';

const mockWorkflows = [
  {
    id: 1,
    title: 'Inspection Report Analysis',
    status: 'Completed',
    input: 'inspection_report.pdf',
    output: 'approval_note.docx'
  },
  {
    id: 2,
    title: 'SOP Compliance Check',
    status: 'Completed',
    input: 'maintenance_report.pdf',
    output: 'compliance_report.docx'
  },
  {
    id: 3,
    title: 'Document Extraction',
    status: 'Completed',
    input: 'site_report.pdf',
    output: 'extracted_data.xlsx'
  }
];

export const RecentWorkflows: React.FC = () => {
  return (
    <div>
      <div className="section-title">Recent Workflows</div>
      <div className="workflows-list">
        {mockWorkflows.map(workflow => (
          <div key={workflow.id} className="workflow-item">
            <div className="workflow-info">
              <h4>{workflow.title}</h4>
              <div className="workflow-meta">
                <span className="badge badge-success">
                  <CheckCircle2 size={12} style={{ marginRight: '4px' }} />
                  {workflow.status}
                </span>
              </div>
            </div>
            <div className="workflow-meta">
              <span>{workflow.input}</span>
              <ArrowRight size={14} style={{ color: 'var(--text-muted)' }} />
              <span>{workflow.output}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
