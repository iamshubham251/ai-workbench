import React from 'react';
import {
  FileSearch,
  GitCompare,
  FileOutput,
  ArrowUpRight,
} from 'lucide-react';
import { Link } from 'react-router-dom';

interface QuickAction {
  title: string;
  description: string;
  icon: React.ReactNode;
  to: string;
}

const actions: QuickAction[] = [
  {
    title: 'Analyze Document',
    description: 'Run the inspection approval workflow',
    icon: <FileSearch size={20} />,
    to: '/workflows',
  },
  {
    title: 'Compare with SOP',
    description: 'Search and explore organizational knowledge',
    icon: <GitCompare size={20} />,
    to: '/knowledge',
  },
  {
    title: 'Generate Report',
    description: 'Create an approval note from an inspection',
    icon: <FileOutput size={20} />,
    to: '/workflows',
  },
];

export const QuickActions: React.FC = () => {
  return (
    <section aria-labelledby="quick-actions-title">
      <div className="section-title" id="quick-actions-title">
        Quick Actions
      </div>

      <div className="quick-actions-grid">
        {actions.map((action) => (
          <Link
            key={action.title}
            to={action.to}
            className="card action-card"
            aria-label={`${action.title}: ${action.description}`}
          >
            <div className="action-card-top">
              <div className="action-icon">
                {action.icon}
              </div>

              <ArrowUpRight
                size={16}
                className="action-arrow"
                aria-hidden="true"
              />
            </div>

            <div>
              <div className="action-title">{action.title}</div>

              <div className="action-description">
                {action.description}
              </div>
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
};