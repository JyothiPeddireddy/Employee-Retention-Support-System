import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';

export const AppLayout = () => {
  const location = useLocation();

  // Dynamic Header title/subtitle based on current route
  const getHeaderInfo = (pathname) => {
    if (pathname.startsWith('/dashboard')) {
      return {
        title: 'Executive Retention Dashboard',
        subtitle: 'Longitudinal Workforce Analytics & Signals Overview',
      };
    }
    if (pathname.startsWith('/workbench')) {
      return {
        title: 'Supportive Retention Workbench',
        subtitle: 'Explainable Signals & Human-in-the-Loop 1-on-1 Prioritization',
      };
    }
    if (pathname.startsWith('/employees/') && pathname.includes('/timeline')) {
      return {
        title: 'Employee 360 Longitudinal Timeline',
        subtitle: '24-Month Temporal History (Surveys, Workload, Promotions)',
      };
    }
    if (pathname.startsWith('/employees/')) {
      return {
        title: 'Employee Profile & Signal Card',
        subtitle: 'Comprehensive Workforce & Career Trajectory Details',
      };
    }
    if (pathname.startsWith('/employees')) {
      return {
        title: 'Employee Workforce Directory',
        subtitle: 'Active & Attrited Headcount Management with RBAC',
      };
    }
    if (pathname.startsWith('/teams')) {
      return {
        title: 'Teams & Organizational Structure',
        subtitle: 'Effective-Dated Team Membership & Seamless Transfer History',
      };
    }
    if (pathname.startsWith('/roles')) {
      return {
        title: 'Job Roles & Career Bands',
        subtitle: 'Classification Levels & Compensation Band Alignment',
      };
    }
    if (pathname.startsWith('/engagement')) {
      return {
        title: 'Engagement Pulse Surveys',
        subtitle: 'Quarterly Sentiment Tracking with Strict Survey Neutrality',
      };
    }
    if (pathname.startsWith('/workload')) {
      return {
        title: 'Workload & Capacity Strain',
        subtitle: 'Quarterly Hours, Overtime Flags & Benign Surge Tracking',
      };
    }
    if (pathname.startsWith('/compensation')) {
      return {
        title: 'Compensation Bands & Promotions',
        subtitle: 'Pay Equity Bands & Lateral/Vertical Promotion Records',
      };
    }
    if (pathname.startsWith('/interventions')) {
      return {
        title: 'Supportive Retention Interventions',
        subtitle: 'Logged 1-on-1 Check-ins, Agreed Actions & Event Audit Trail',
      };
    }
    if (pathname.startsWith('/analytics')) {
      return {
        title: 'Retention Analytics & Visual Trends',
        subtitle: 'Quarterly Heatmaps, Overtime Trajectories & Sentiment Trends',
      };
    }
    if (pathname.startsWith('/data-quality')) {
      return {
        title: 'Data Quality & Validation Suite',
        subtitle: 'Zero Data Leakage Verification & Isolated Ground-Truth Audits',
      };
    }
    if (pathname.startsWith('/admin')) {
      return {
        title: 'System Administration & RBAC',
        subtitle: 'User Provisioning, Role Assignments & Immutable Audit Logs',
      };
    }
    if (pathname.startsWith('/profile')) {
      return {
        title: 'User Profile & Security',
        subtitle: 'Manage Authentication Credentials & Session Security',
      };
    }
    return {
      title: 'Supportive Retention Signal Engine',
      subtitle: 'Explainable AI for Proactive Employee Retention',
    };
  };

  const headerInfo = getHeaderInfo(location.pathname);

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Header title={headerInfo.title} subtitle={headerInfo.subtitle} />
        <main className="flex-1 p-6 md:p-8 max-w-7xl w-full mx-auto animate-fade-in">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AppLayout;
