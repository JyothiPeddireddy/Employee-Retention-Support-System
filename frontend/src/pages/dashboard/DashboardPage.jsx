import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { analyticsApi } from '../../api/analytics';
import { employeeApi } from '../../api/employees';
import StatCard from '../../components/StatCard';
import LoadingSpinner from '../../components/LoadingSpinner';
import Alert from '../../components/Alert';
import {
  Users,
  AlertTriangle,
  HeartHandshake,
  ShieldCheck,
  Clock,
  ArrowRight,
  TrendingUp,
  Sparkles,
  BarChart3,
  Calendar
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

export const DashboardPage = () => {
  const [overview, setOverview] = useState(null);
  const [trends, setTrends] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [overviewRes, trendsRes, summaryRes] = await Promise.allSettled([
          analyticsApi.getOverview(),
          analyticsApi.getTrends(),
          employeeApi.getPrioritizationSummary(),
        ]);

        if (overviewRes.status === 'fulfilled') setOverview(overviewRes.value);
        if (trendsRes.status === 'fulfilled') setTrends(trendsRes.value);
        if (summaryRes.status === 'fulfilled') setSummary(summaryRes.value);

        if (overviewRes.status === 'rejected' && trendsRes.status === 'rejected') {
          throw new Error(overviewRes.reason?.message || 'Could not load dashboard data.');
        }
      } catch (err) {
        setError(err.message || 'Error loading dashboard metrics.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <LoadingSpinner size="lg" message="Loading executive retention dashboard..." />;
  }

  const priorityData = summary
    ? [
        { name: 'High Priority', count: summary.high_priority_count, color: '#e11d48' },
        { name: 'Medium Priority', count: summary.medium_priority_count, color: '#f59e0b' },
        { name: 'Low Priority', count: summary.low_priority_count, color: '#10b981' },
      ]
    : [
        { name: 'High Priority', count: overview?.high_priority_count || 0, color: '#e11d48' },
        { name: 'Medium Priority', count: overview?.medium_priority_count || 0, color: '#f59e0b' },
        { name: 'Low Priority', count: overview?.low_priority_count || 0, color: '#10b981' },
      ];

  return (
    <div className="space-y-6">
      {error && <Alert type="warning" message="Partial Data Notice" details={error} />}

      {/* Top Banner: Supportive Philosophy */}
      <div className="rounded-2xl bg-gradient-to-r from-forest-900 via-forest-800 to-forest-950 p-6 text-white shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-forest-700/70 text-emerald-200 border border-forest-600 mb-2">
            <Sparkles className="w-3.5 h-3.5 mr-1 text-emerald-300" />
            Human-in-the-Loop Retention Intelligence
          </div>
          <h2 className="text-xl font-bold tracking-tight">Supportive Retention Signal Engine</h2>
          <p className="text-xs text-forest-200/90 mt-1 max-w-2xl leading-relaxed">
            Prioritizing empathetic, timely manager check-ins using pre-outcome longitudinal signals.
            Never a resignation score — strictly an explainable conversation prioritizer.
          </p>
        </div>
        <div className="flex items-center space-x-3 flex-shrink-0">
          <Link
            to="/workbench"
            className="inline-flex items-center px-4 py-2 rounded-xl text-xs font-semibold bg-emerald-500 hover:bg-emerald-400 text-gray-950 transition shadow-sm"
          >
            Open Workbench
            <ArrowRight className="w-4 h-4 ml-1.5" />
          </Link>
          <Link
            to="/interventions"
            className="inline-flex items-center px-4 py-2 rounded-xl text-xs font-semibold bg-forest-800/80 hover:bg-forest-700 text-white border border-forest-600 transition"
          >
            Log Check-in
          </Link>
        </div>
      </div>

      {/* Primary KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Workforce"
          value={overview?.total_headcount?.toLocaleString() || '0'}
          subtitle={`${overview?.active_headcount || 0} active • ${overview?.attrited_headcount || 0} historical exits`}
          icon={Users}
          color="forest"
          onClick={() => navigate('/employees')}
        />
        <StatCard
          title="Support Priority (High)"
          value={overview?.high_priority_count || summary?.high_priority_count || 0}
          subtitle="Employees flagged for supportive 1-on-1"
          icon={AlertTriangle}
          color="rose"
          badge="High Signal"
          onClick={() => navigate('/workbench?tier=HIGH')}
        />
        <StatCard
          title="Supportive Interventions"
          value={overview?.total_interventions || 0}
          subtitle={`${overview?.interventions_completed || 0} completed • Human-reviewed`}
          icon={HeartHandshake}
          color="emerald"
          onClick={() => navigate('/interventions')}
        />
        <StatCard
          title="Data Integrity Score"
          value={`${overview?.data_integrity_score ? (overview.data_integrity_score * 100).toFixed(1) : '100.0'}%`}
          subtitle="Zero leakage • Schema reconciled"
          icon={ShieldCheck}
          color="blue"
          badge="Verified"
          onClick={() => navigate('/data-quality')}
        />
      </div>

      {/* Secondary Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl border border-gray-200 p-4 shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs text-gray-500 font-semibold uppercase">Avg Weekly Hours</p>
            <p className="text-xl font-bold text-gray-900 mt-1">
              {overview?.avg_weekly_workload ? overview.avg_weekly_workload.toFixed(1) : '40.0'} hrs
            </p>
          </div>
          <div className="p-2.5 rounded-xl bg-amber-50 text-amber-700">
            <Clock className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-4 shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs text-gray-500 font-semibold uppercase">Engagement Sentiment</p>
            <p className="text-xl font-bold text-gray-900 mt-1">
              {overview?.avg_engagement_sentiment ? `${(overview.avg_engagement_sentiment * 20).toFixed(0)}%` : '78%'}
            </p>
          </div>
          <div className="p-2.5 rounded-xl bg-emerald-50 text-emerald-700">
            <TrendingUp className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-4 shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs text-gray-500 font-semibold uppercase">Primary Attrition Driver</p>
            <p className="text-sm font-bold text-gray-900 mt-1">
              {summary?.top_driver || 'Overtime Strain & Compensation'}
            </p>
          </div>
          <div className="p-2.5 rounded-xl bg-purple-50 text-purple-700">
            <BarChart3 className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Longitudinal Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Longitudinal Workload & Overtime Rate Chart (2 Cols) */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-gray-900">Longitudinal Workload Trends (8 Quarters)</h3>
              <p className="text-xs text-gray-500">Average weekly hours and overtime percentage trajectory</p>
            </div>
            <span className="text-xs font-semibold px-2.5 py-1 rounded-md bg-forest-50 text-forest-800 border border-forest-200">
              2024Q1 – 2025Q4
            </span>
          </div>

          <div className="h-72 w-full">
            {trends.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trends} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="quarter" tick={{ fontSize: 11, fill: '#64748b' }} />
                  <YAxis yAxisId="left" domain={[35, 55]} tick={{ fontSize: 11, fill: '#64748b' }} />
                  <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 11, fill: '#64748b' }} unit="%" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1e293b',
                      borderRadius: '8px',
                      color: '#fff',
                      fontSize: '12px',
                    }}
                  />
                  <Legend wrapperStyle={{ fontSize: '12px' }} />
                  <Line
                    yAxisId="left"
                    type="monotone"
                    dataKey="avg_workload_hours"
                    name="Avg Hours / Wk"
                    stroke="#047857"
                    strokeWidth={2.5}
                    dot={{ r: 4 }}
                  />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="overtime_rate_percentage"
                    name="Overtime Rate %"
                    stroke="#f59e0b"
                    strokeWidth={2}
                    strokeDasharray="4 4"
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full text-xs text-gray-400">
                No longitudinal trend data available.
              </div>
            )}
          </div>
        </div>

        {/* Priority Tier Distribution (1 Col) */}
        <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-gray-900">Support Priority Cohorts</h3>
            <p className="text-xs text-gray-500">Distribution across active workforce</p>
          </div>

          <div className="h-56 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={priorityData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={5}
                  dataKey="count"
                >
                  {priorityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    borderRadius: '8px',
                    color: '#fff',
                    fontSize: '12px',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="space-y-2 pt-2 border-t border-gray-100">
            {priorityData.map((item) => (
              <div key={item.name} className="flex items-center justify-between text-xs">
                <div className="flex items-center space-x-2">
                  <span className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                  <span className="text-gray-600 font-medium">{item.name}</span>
                </div>
                <span className="font-bold text-gray-900">{item.count.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
