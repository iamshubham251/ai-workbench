import React, { useEffect, useState } from 'react';
import {
  FileStack,
  FileText,
  Layers3,
  Workflow,
} from 'lucide-react';
import {
  getDocuments,
  type DocumentRecord,
} from '../../services/documentService';
import { getWorkflowHistory, type WorkflowRunHistoryItem } from '../../services/workflowService';

interface StatCard {
  label: string;
  value: string;
  description: string;
  icon: React.ReactNode;
}

export const DashboardStats: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [history, setHistory] = useState<WorkflowRunHistoryItem[]>([]);

  useEffect(() => {
    let active = true;

    const loadData = async () => {
      try {
        const [records, historyData] = await Promise.all([
          getDocuments(),
          getWorkflowHistory().catch(() => []) // Gracefully degrade if history fails
        ]);

        if (active) {
          setDocuments(records);
          setHistory(historyData);
        }
      } catch {
        // Dashboard statistics are supplementary UI.
        // The main workspace remains usable if the API is unavailable.
      }
    };

    void loadData();

    return () => {
      active = false;
    };
  }, []);

  const pdfCount = documents.filter(
    (document) => document.extension.toLowerCase() === '.pdf',
  ).length;

  const uniqueFormats = new Set(documents.map(d => d.extension.toLowerCase())).size;

  const stats: StatCard[] = [
    {
      label: 'Documents',
      value: documents.length.toString(),
      description: 'Uploaded documents',
      icon: <FileStack size={18} />,
    },
    {
      label: 'PDF Reports',
      value: pdfCount.toString(),
      description: 'Ready for analysis',
      icon: <FileText size={18} />,
    },
    {
      label: 'Formats',
      value: uniqueFormats.toString(),
      description: 'Unique file types',
      icon: <Layers3 size={18} />,
    },
    {
      label: 'Workflows',
      value: history.length.toString(),
      description: 'Total pipeline runs',
      icon: <Workflow size={18} />,
    },
  ];

  return (
    <section className="dashboard-stats" aria-label="Workbench overview">
      {stats.map((stat) => (
        <div className="dashboard-stat-card" key={stat.label}>
          <div className="dashboard-stat-top">
            <div className="dashboard-stat-icon">
              {stat.icon}
            </div>

            <span className="dashboard-stat-label">
              {stat.label}
            </span>
          </div>

          <div className="dashboard-stat-value">
            {stat.value}
          </div>

          <div className="dashboard-stat-description">
            {stat.description}
          </div>
        </div>
      ))}
    </section>
  );
};