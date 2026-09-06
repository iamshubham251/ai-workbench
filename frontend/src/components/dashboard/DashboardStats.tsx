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

interface StatCard {
  label: string;
  value: string;
  description: string;
  icon: React.ReactNode;
}

export const DashboardStats: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);

  useEffect(() => {
    let active = true;

    const loadDocuments = async () => {
      try {
        const records = await getDocuments();

        if (active) {
          setDocuments(records);
        }
      } catch {
        // Dashboard statistics are supplementary UI.
        // The main workspace remains usable if the API is unavailable.
      }
    };

    void loadDocuments();

    return () => {
      active = false;
    };
  }, []);

  const pdfCount = documents.filter(
    (document) => document.extension.toLowerCase() === '.pdf',
  ).length;

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
      value: '4',
      description: 'PDF, DOCX, XLSX, PPTX',
      icon: <Layers3 size={18} />,
    },
    {
      label: 'Workflow',
      value: 'Ready',
      description: 'Inspection approval',
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