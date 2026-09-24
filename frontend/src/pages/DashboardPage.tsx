import React from 'react';
import { WelcomeHeader } from '../components/dashboard/WelcomeHeader';
import { DashboardStats } from '../components/dashboard/DashboardStats';
import { UploadDropzone } from '../components/dashboard/UploadDropzone';
import { QuickActions } from '../components/dashboard/QuickActions';
import { RecentWorkflows } from '../components/dashboard/RecentWorkflows';
import { ActivityPanel } from '../components/dashboard/ActivityPanel';
import { ApprovalWorkflowPanel } from '../components/dashboard/ApprovalWorkflowPanel';
import './DashboardPage.css';

export const DashboardPage: React.FC = () => {
  return (
    <>
      <div className="dashboard-hero-bg" />
      <div className="dashboard-layout">
        <div className="dashboard-main">
          <WelcomeHeader />
          <div className="dashboard-card-hover">
            <DashboardStats />
          </div>
          <div className="dashboard-card-hover">
            <UploadDropzone />
          </div>
          <ApprovalWorkflowPanel />
          <QuickActions />
          <div className="dashboard-card-hover">
            <RecentWorkflows />
          </div>
        </div>

        <div>
          <div className="dashboard-card-hover">
            <ActivityPanel />
          </div>
        </div>
      </div>
    </>
  );
};