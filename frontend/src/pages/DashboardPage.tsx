import React from 'react';
import { WelcomeHeader } from '../components/dashboard/WelcomeHeader';
import { DashboardStats } from '../components/dashboard/DashboardStats';
import { UploadDropzone } from '../components/dashboard/UploadDropzone';
import { QuickActions } from '../components/dashboard/QuickActions';
import { RecentWorkflows } from '../components/dashboard/RecentWorkflows';
import { ActivityPanel } from '../components/dashboard/ActivityPanel';
import { ApprovalWorkflowPanel } from '../components/dashboard/ApprovalWorkflowPanel';

export const DashboardPage: React.FC = () => {
  return (
    <div className="dashboard-layout">
      <div className="dashboard-main">
        <WelcomeHeader />
        <DashboardStats />
        <UploadDropzone />
        <ApprovalWorkflowPanel />
        <QuickActions />
        <RecentWorkflows />
      </div>

      <div>
        <ActivityPanel />
      </div>
    </div>
  );
};