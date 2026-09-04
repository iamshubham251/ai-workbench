import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, FileText, Activity, Database, BookOpen, Clock, ChevronLeft, ChevronRight } from 'lucide-react';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ collapsed, onToggle }) => {
  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <nav className="sidebar-nav">
        <div>
          <div className="sidebar-section-title">Workbench</div>
          <NavLink to="/" end className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
            <LayoutDashboard size={18} />
            <span>Dashboard</span>
          </NavLink>
          <NavLink to="/documents" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
            <FileText size={18} />
            <span>Documents</span>
          </NavLink>
          <NavLink to="/workflows" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
            <Activity size={18} />
            <span>Workflows</span>
          </NavLink>
        </div>

        <div>
          <div className="sidebar-section-title">Knowledge</div>
          <NavLink to="/knowledge" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
            <Database size={18} />
            <span>Knowledge Base</span>
          </NavLink>
          <NavLink to="/sops" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
            <BookOpen size={18} />
            <span>SOP Library</span>
          </NavLink>
        </div>

        <div>
          <div className="sidebar-section-title">Activity</div>
          <NavLink to="/history" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
            <Clock size={18} />
            <span>History</span>
          </NavLink>
        </div>
      </nav>
      
      <div className="sidebar-footer">
        <button className="icon-btn" onClick={onToggle} aria-label="Toggle Sidebar" style={{ width: '100%' }}>
          {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </button>
      </div>
    </aside>
  );
};
