import React from 'react';

export const WelcomeHeader: React.FC = () => {
  const hour = new Date().getHours();

  const greeting =
    hour < 12
      ? 'Good morning'
      : hour < 17
        ? 'Good afternoon'
        : 'Good evening';

  return (
    <div className="welcome-header">
      <h1>{greeting}</h1>
      <p>
        Your local AI workspace for documents, knowledge and automated
        workflows.
      </p>
    </div>
  );
};
