import React, { useState, useEffect } from 'react';
import { analyticsApi } from '../../api/analytics';
import LoadingSpinner from '../../components/LoadingSpinner';
import Alert from '../../components/Alert';
import StatCard from '../../components/StatCard';
import {
  BarChart3,
  TrendingUp,
  Clock,
  HeartHandshake,
  Users,
  Shield,
  Layers,
  Building2
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';

export const AnalyticsPage = () => {
  const [teamSummaries, setTeamSummaries] = useState([]);
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      setLoading(true);
      setError(null);
      try {
        const [teamsRes, trendsRes] = await Promise.all([
          analyticsApi.getTeamSummaries(),
          analyticsApi.getTrends(),
        ]);
        setTeamSummaries(teamsRes || []);
        setTrends(trendsRes || []);
      } catch (err) {
        setError(err.message || 'Failed to load analytics data.');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  if (loading) {
    return <LoadingSpinner size="lg" message="Computing organizational retention analytics..." />;
  }

  // Bar chart data for departments
  const departmentChartData = teamSummaries.map((dept) => ({
    department: dept.department,
    highSignals: dept.high_priority_signals,
    mediumSignals: dept.medium_priority_signals,
    interventions: dept.interventions_conducted,
    avgHours: dept.avg_hours,
  }));

  return (
    <div className="space-y-6">
      {error && <Alert type="error" message="Analytics Error" details={error} />}

      {/* Header Info */}
      <div className="bg-white rounded-2xl border border-gray-200 p-5 shadow-xs">
        <h2 className="text-base font-bold text-gray-900">Organizational Retention Analytics</h2>
        <p className="text-xs text-gray-500 mt-0.5">
          Macro-level longitudinal workforce health, capacity strain trajectories, and department support distributions.
        </p>
      </div>

      {/* Primary Visualizations Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1: Priority Signals by Department */}
        <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-gray-900">Support Priority Signals by Department</h3>
              <p className="text-xs text-gray-500">Distribution of High and Medium signals across business units</p>
            </div>
            <span className="p-2 rounded-lg bg-forest-50 text-forest-700">
              <Building2 className="w-4 h-4" />
            </span>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={departmentChartData} margin={{ top: 10, right: 10, left: -10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="department" tick={{ fontSize: 10 }} interval={0} angle={-15} textAnchor="end" />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', borderRadius: '8px', color: '#fff', fontSize: '11px' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '15px' }} />
                <Bar dataKey="highSignals" name="High Priority Signals" fill="#e11d48" radius={[4, 4, 0, 0]} />
                <Bar dataKey="mediumSignals" name="Medium Priority Signals" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                <Bar dataKey="interventions" name="Interventions Logged" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Longitudinal Workload Trajectory */}
        <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-gray-900">8-Quarter Capacity Strain Trends</h3>
              <p className="text-xs text-gray-500">Longitudinal weekly hours and overtime percentage</p>
            </div>
            <span className="p-2 rounded-lg bg-forest-50 text-forest-700">
              <Clock className="w-4 h-4" />
            </span>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trends} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="quarter" tick={{ fontSize: 11 }} />
                <YAxis yAxisId="left" domain={[35, 55]} tick={{ fontSize: 11 }} />
                <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 11 }} unit="%" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', borderRadius: '8px', color: '#fff', fontSize: '11px' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px' }} />
                <Line
                  yAxisId="left"
                  type="monotone"
                  dataKey="avg_workload_hours"
                  name="Avg Hours / Wk"
                  stroke="#047857"
                  strokeWidth={2.5}
                  dot={{ r: 3 }}
                />
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="overtime_rate_percentage"
                  name="Overtime Rate %"
                  stroke="#e11d48"
                  strokeWidth={2}
                  strokeDasharray="4 4"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Department Breakdown Table */}
      <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-xs">
        <div className="p-4 border-b border-gray-200 bg-gray-50/50">
          <h3 className="text-xs font-bold text-gray-900 uppercase tracking-wider">
            Departmental Breakdown Summary
          </h3>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-gray-50/75 border-b border-gray-200 text-gray-500 uppercase font-semibold">
                <th className="py-3 px-4">Department</th>
                <th className="py-3 px-4">Total Headcount</th>
                <th className="py-3 px-4">Active Staff</th>
                <th className="py-3 px-4">Historical Exits</th>
                <th className="py-3 px-4">High Signals</th>
                <th className="py-3 px-4">Medium Signals</th>
                <th className="py-3 px-4">Avg Weekly Hours</th>
                <th className="py-3 px-4">Interventions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {teamSummaries.map((dept) => (
                <tr key={dept.department} className="hover:bg-gray-50/80 transition">
                  <td className="py-3.5 px-4 font-bold text-gray-900">{dept.department}</td>
                  <td className="py-3.5 px-4 font-medium text-gray-700">{dept.total_employees}</td>
                  <td className="py-3.5 px-4 text-emerald-700 font-semibold">{dept.active_employees}</td>
                  <td className="py-3.5 px-4 text-rose-700 font-semibold">{dept.attrited_employees}</td>
                  <td className="py-3.5 px-4">
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-200">
                      {dept.high_priority_signals}
                    </span>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200">
                      {dept.medium_priority_signals}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 font-mono font-medium text-gray-800">{dept.avg_hours.toFixed(1)} hrs</td>
                  <td className="py-3.5 px-4 font-semibold text-forest-800">{dept.interventions_conducted}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
