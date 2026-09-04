import React from 'react';
import { Layers } from 'lucide-react';

interface PlaceholderPageProps {
  title: string;
  description: string;
}

export const PlaceholderPage: React.FC<PlaceholderPageProps> = ({ title, description }) => {
  return (
    <div className="placeholder-page">
      <Layers size={48} style={{ color: 'var(--border-light)', marginBottom: '24px' }} />
      <h2>{title}</h2>
      <p>{description}</p>
    </div>
  );
};
