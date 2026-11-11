import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { employeeApi } from '../../api/employees';
import { interventionApi } from '../../api/interventions';
import { useAuth } from '../../context/AuthContext';
import LoadingSpinner from '../../components/LoadingSpinner';
import Alert from '../../components/Alert';
import Modal from '../../components/Modal';
import {
  User,
  ArrowLeft,
  Calendar,
  Briefcase,
  DollarSign,
  TrendingUp,
  Clock,
  HeartHandshake,
  MessageSquareHeart,
  Shield,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  Edit
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  BarChart,
  Bar,
} from 'recharts';

export const EmployeeProfilePage = () => {
  const { id } = useParams();
  const { role, user } = useAuth();
  const [employee, setEmployee] = useState(null);
  const [timeline, setTimeline] = useState(null);
  const [activeTab, setActiveTab] = useState('timeline');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Edit Modal
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editForm, setEditForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    current_salary: '',
  });
  const [submittingEdit, setSubmittingEdit] = useState(false);
  const [successMsg, setSuccessMsg] = useState(null);

  const fetchProfileData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [empRes, timeRes] = await Promise.all([
        employeeApi.getEmployee(id),
        employeeApi.getEmployeeTimeline(id),
      ]);
      setEmployee(empRes);
      setTimeline(timeRes);
      setEditForm({
        first_name: empRes.first_name || '',
        last_name: empRes.last_name || '',
        email: empRes.email || '',
        current_salary: empRes.current_salary || '',
      });
    } catch (err) {
      setError(err.message || `Failed to retrieve profile for employee '${id}'.`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfileData();
  }, [id]);

  const handleEditSubmit = async (e) => {
    e.preventDefault();
    setSubmittingEdit(true);
    try {
      await employeeApi.updateEmployee(id, {
        first_name: editForm.first_name,
        last_name: editForm.last_name,
        email: editForm.email,
        current_salary: parseFloat(editForm.current_salary),
      });
      setSuccessMsg('Employee profile updated successfully.');
      setIsEditModalOpen(false);
      fetchProfileData();
    } catch (err) {
      setError(err.message || 'Failed to update profile.');
    } finally {
      setSubmittingEdit(false);
    }
  };

  if (loading) {
    return <LoadingSpinner size="lg" message="Loading employee 360 profile..." />;
  }

  if (error || !employee) {
    return (
      <div className="space-y-4">
        <Alert type="error" message="Profile Load Error" details={error} />
        <Link
          to="/employees"
          className="inline-flex items-center text-xs font-semibold text-forest-700 hover:text-forest-800"
        >
          <ArrowLeft className="w-4 h-4 mr-1" />
          Back to Employee Directory
        </Link>
      </div>
    );
  }

  const canEdit = ['HR_PARTNER', 'ADMIN', 'SYSTEM_ADMIN'].includes(role);

  // Format workload data for chart
  const workloadChartData = (timeline?.workload_history || []).map((w) => ({
    quarter: w.period_quarter,
    avgHours: w.avg_weekly_hours,
    overtimeHours: w.overtime_hours,
    activeProjects: w.active_project_count,
    isBenign: w.is_benign_surge,
  }));

  // Format survey sentiment for chart
  const surveyChartData = (timeline?.survey_history || [])
    .filter((s) => !s.is_missing && s.composite_engagement !== null)
    .map((s) => ({
      quarter: s.survey_quarter,
      sentiment: s.composite_engagement ? s.composite_engagement * 20 : 0, // scale to 100%
      satisfaction: s.satisfaction_score ? s.satisfaction_score * 20 : 0,
      balance: s.work_life_balance_score ? s.work_life_balance_score * 20 : 0,
      growth: s.career_growth_score ? s.career_growth_score * 20 : 0,
    }));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Link
          to="/employees"
          className="inline-flex items-center text-xs font-semibold text-gray-500 hover:text-gray-900 transition"
        >
          <ArrowLeft className="w-4 h-4 mr-1.5" />
          Back to Directory
        </Link>
        {canEdit && (
          <button
            onClick={() => setIsEditModalOpen(true)}
            className="inline-flex items-center px-3.5 py-1.5 rounded-xl text-xs font-semibold text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 transition shadow-xs"
          >
            <Edit className="w-3.5 h-3.5 mr-1.5 text-forest-700" />
            Edit Profile
          </button>
        )}
      </div>

      {successMsg && <Alert type="success" message={successMsg} onClose={() => setSuccessMsg(null)} />}

      {/* Header Profile Card */}
      <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="flex items-start space-x-4">
            <div className="w-16 h-16 rounded-2xl bg-forest-800 text-white flex items-center justify-center font-bold text-2xl shadow-md">
              {employee.full_name?.slice(0, 2).toUpperCase()}
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-xl font-bold text-gray-900">{employee.full_name}</h1>
                <span className="font-mono text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded-md">
                  {employee.employee_id}
                </span>
                <span
                  className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                    employee.status === 'ACTIVE'
                      ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                      : 'bg-rose-50 text-rose-700 border border-rose-200'
                  }`}
                >
                  {employee.status}
                </span>
              </div>
              <p className="text-xs text-gray-500 mt-0.5">{employee.email}</p>

              <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-gray-600 font-medium">
                <span>
                  Department: <strong className="text-gray-900">{employee.department}</strong>
                </span>
                <span>•</span>
                <span>
                  Team: <strong className="text-gray-900">{employee.team_name}</strong>
                </span>
                <span>•</span>
                <span>
                  Role: <strong className="text-gray-900">{employee.role_title}</strong> ({employee.role_level})
                </span>
                {employee.manager_name && (
                  <>
                    <span>•</span>
                    <span>
                      Manager: <strong className="text-gray-900">{employee.manager_name}</strong>
                    </span>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Quick Metrics */}
          <div className="flex items-center gap-4 border-t md:border-t-0 pt-4 md:pt-0">
            <div className="p-3 bg-gray-50 rounded-xl text-center min-w-[90px]">
              <span className="text-[10px] font-semibold uppercase text-gray-400">Total Tenure</span>
              <p className="text-lg font-bold text-gray-900">{employee.tenure_months || 0} mos</p>
            </div>
            <div className="p-3 bg-gray-50 rounded-xl text-center min-w-[90px]">
              <span className="text-[10px] font-semibold uppercase text-gray-400">Time in Role</span>
              <p className="text-lg font-bold text-gray-900">{employee.months_in_role || 0} mos</p>
            </div>
            <div className="p-3 bg-emerald-50/50 border border-emerald-100 rounded-xl text-center min-w-[90px]">
              <span className="text-[10px] font-semibold uppercase text-emerald-600">Base Salary</span>
              <p className="text-lg font-bold text-emerald-800">${employee.current_salary?.toLocaleString()}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="border-b border-gray-200 bg-white rounded-t-2xl px-4">
        <nav className="flex space-x-6 overflow-x-auto" aria-label="Tabs">
          {[
            { id: 'timeline', label: 'Longitudinal Timeline', icon: Clock },
            { id: 'workload', label: 'Workload & Overtime', icon: Briefcase },
            { id: 'surveys', label: 'Engagement Sentiment', icon: HeartHandshake },
            { id: 'promotions', label: 'Career & Promotions', icon: TrendingUp },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-3.5 px-1 border-b-2 font-semibold text-xs flex items-center space-x-2 transition ${
                  isActive
                    ? 'border-forest-600 text-forest-700'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Contents */}
      <div className="bg-white rounded-b-2xl border-x border-b border-gray-200 p-6 shadow-xs">
        {/* Tab 1: Longitudinal Timeline */}
        {activeTab === 'timeline' && (
          <div className="space-y-6">
            <div>
              <h3 className="text-sm font-bold text-gray-900">24-Month Longitudinal Career Progression</h3>
              <p className="text-xs text-gray-500">
                Quarterly snapshot history capturing role progression and tenure accumulation
              </p>
            </div>

            <div className="relative pl-6 border-l-2 border-forest-200 space-y-6 my-4">
              {(timeline?.tenure_history || []).map((snap, idx) => (
                <div key={snap.snapshot_id} className="relative">
                  <div className="absolute -left-[31px] top-1 w-3.5 h-3.5 rounded-full bg-forest-600 border-2 border-white shadow-xs" />
                  <div className="bg-gray-50 p-4 rounded-xl border border-gray-200">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-xs text-forest-900">{snap.snapshot_quarter}</span>
                      <span className="text-[11px] text-gray-500 font-mono">{snap.snapshot_date}</span>
                    </div>
                    <div className="mt-2 grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                      <div>
                        <span className="text-gray-400 text-[10px] uppercase">Snapshot ID</span>
                        <p className="font-mono text-gray-700">{snap.snapshot_id}</p>
                      </div>
                      <div>
                        <span className="text-gray-400 text-[10px] uppercase">Total Tenure</span>
                        <p className="font-semibold text-gray-900">{snap.tenure_months} months</p>
                      </div>
                      <div>
                        <span className="text-gray-400 text-[10px] uppercase">Months in Role</span>
                        <p className="font-semibold text-gray-900">{snap.months_in_current_role} months</p>
                      </div>
                      <div>
                        <span className="text-gray-400 text-[10px] uppercase">Role Code</span>
                        <p className="font-mono text-gray-700">{snap.role_id}</p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {timeline?.attrition_outcome && (
              <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-xs">
                <span className="font-bold text-rose-800">Ground-Truth Historical Exit Record:</span>
                <p className="text-rose-700 mt-1">
                  Attrition Date: {timeline.attrition_outcome.attrition_date || 'N/A'} • Voluntary:{' '}
                  {timeline.attrition_outcome.voluntary ? 'Yes' : 'No'} • Primary Reason:{' '}
                  {timeline.attrition_outcome.primary_reason || 'Not specified'}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Tab 2: Workload & Overtime */}
        {activeTab === 'workload' && (
          <div className="space-y-6">
            <div>
              <h3 className="text-sm font-bold text-gray-900">Workload Capacity & Strain Trajectory</h3>
              <p className="text-xs text-gray-500">
                Quarterly tracking of weekly hours, overtime thresholds, and benign surge classification
              </p>
            </div>

            {/* Chart */}
            <div className="h-64 w-full bg-gray-50/50 p-4 rounded-xl border border-gray-100">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={workloadChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="quarter" tick={{ fontSize: 11 }} />
                  <YAxis domain={[30, 65]} tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Legend wrapperStyle={{ fontSize: '11px' }} />
                  <Line
                    type="monotone"
                    dataKey="avgHours"
                    name="Avg Weekly Hours"
                    stroke="#047857"
                    strokeWidth={2.5}
                  />
                  <Line
                    type="monotone"
                    dataKey="overtimeHours"
                    name="Weekly Overtime Hours"
                    stroke="#e11d48"
                    strokeWidth={2}
                    strokeDasharray="3 3"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Snapshots Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-gray-50 border-b text-gray-500 uppercase font-semibold">
                    <th className="py-2.5 px-3">Quarter</th>
                    <th className="py-2.5 px-3">Avg Hours/Wk</th>
                    <th className="py-2.5 px-3">Overtime Hours</th>
                    <th className="py-2.5 px-3">Consecutive Weeks</th>
                    <th className="py-2.5 px-3">Active Projects</th>
                    <th className="py-2.5 px-3">Surge Classification</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {(timeline?.workload_history || []).map((w) => (
                    <tr key={w.workload_id}>
                      <td className="py-2.5 px-3 font-semibold text-gray-800">{w.period_quarter}</td>
                      <td className="py-2.5 px-3 font-bold text-gray-900">{w.avg_weekly_hours.toFixed(1)} hrs</td>
                      <td className="py-2.5 px-3 text-rose-600 font-semibold">{w.overtime_hours.toFixed(1)} hrs</td>
                      <td className="py-2.5 px-3">{w.consecutive_overtime_weeks} wks</td>
                      <td className="py-2.5 px-3">{w.active_project_count}</td>
                      <td className="py-2.5 px-3">
                        {w.is_benign_surge ? (
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                            Benign Surge (Non-Harmful)
                          </span>
                        ) : w.overtime_hours > 5 ? (
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-50 text-amber-700 border border-amber-200">
                            Sustained Strain
                          </span>
                        ) : (
                          <span className="text-gray-400">Normal Band</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Tab 3: Engagement Surveys */}
        {activeTab === 'surveys' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-gray-900">Engagement Sentiment & Survey Neutrality</h3>
                <p className="text-xs text-gray-500">
                  Quarterly sentiment scores. Missing responses are marked neutral without score penalty.
                </p>
              </div>
            </div>

            {/* Survey Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {(timeline?.survey_history || []).map((s) => (
                <div
                  key={s.survey_id}
                  className={`p-4 rounded-xl border ${
                    s.is_missing
                      ? 'bg-gray-50/70 border-dashed border-gray-300'
                      : 'bg-white border-gray-200 shadow-xs'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-xs text-gray-900">{s.survey_quarter}</span>
                    {s.is_missing ? (
                      <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-gray-200 text-gray-600">
                        Missing (Neutral)
                      </span>
                    ) : (
                      <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                        Completed
                      </span>
                    )}
                  </div>

                  {s.is_missing ? (
                    <div className="py-4 text-center">
                      <HelpCircle className="w-5 h-5 mx-auto text-gray-400 mb-1" />
                      <p className="text-[11px] text-gray-500 font-medium">Non-Response Treated Neutrally</p>
                      <p className="text-[10px] text-gray-400">Zero penalty applied to priority</p>
                    </div>
                  ) : (
                    <div className="space-y-1.5 text-xs">
                      <div className="flex justify-between">
                        <span className="text-gray-500">Satisfaction:</span>
                        <span className="font-semibold text-gray-900">{s.satisfaction_score} / 5.0</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Work-Life Balance:</span>
                        <span className="font-semibold text-gray-900">{s.work_life_balance_score} / 5.0</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Career Growth:</span>
                        <span className="font-semibold text-gray-900">{s.career_growth_score} / 5.0</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Manager Support:</span>
                        <span className="font-semibold text-gray-900">{s.manager_support_score} / 5.0</span>
                      </div>
                      <div className="pt-2 border-t flex justify-between font-bold text-emerald-800">
                        <span>Composite:</span>
                        <span>{s.composite_engagement?.toFixed(2)} / 5.0</span>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab 4: Promotions & Career Moves */}
        {activeTab === 'promotions' && (
          <div className="space-y-6">
            <div>
              <h3 className="text-sm font-bold text-gray-900">Career Movement & Compensation History</h3>
              <p className="text-xs text-gray-500">
                Official promotion records and lateral role transitions
              </p>
            </div>

            {(timeline?.promotions || []).length === 0 ? (
              <div className="p-6 text-center text-xs text-gray-400 bg-gray-50 rounded-xl">
                No promotions recorded during the observation horizon.
              </div>
            ) : (
              <div className="space-y-3">
                {timeline.promotions.map((p) => (
                  <div
                    key={p.promotion_id}
                    className="p-4 rounded-xl border border-gray-200 bg-gray-50 flex items-center justify-between"
                  >
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="font-mono text-xs text-gray-500 font-semibold">{p.promotion_id}</span>
                        <span className="text-xs font-bold text-gray-900">
                          {p.from_role_id} → {p.to_role_id}
                        </span>
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-forest-100 text-forest-800">
                          {p.movement_type}
                        </span>
                      </div>
                      <p className="text-[11px] text-gray-500 mt-1">Effective Date: {p.effective_date}</p>
                    </div>
                    <div className="text-right">
                      <span className="text-[10px] uppercase text-gray-400">Compensation Adjustment</span>
                      <p className="text-xs font-bold text-gray-900">
                        ${p.from_salary.toLocaleString()} → ${p.to_salary.toLocaleString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Edit Profile Modal */}
      <Modal isOpen={isEditModalOpen} onClose={() => setIsEditModalOpen(false)} title="Edit Employee Profile">
        <form onSubmit={handleEditSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                First Name
              </label>
              <input
                type="text"
                required
                value={editForm.first_name}
                onChange={(e) => setEditForm({ ...editForm, first_name: e.target.value })}
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                Last Name
              </label>
              <input
                type="text"
                required
                value={editForm.last_name}
                onChange={(e) => setEditForm({ ...editForm, last_name: e.target.value })}
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
              Corporate Email
            </label>
            <input
              type="email"
              required
              value={editForm.email}
              onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
              className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
              Current Base Salary ($)
            </label>
            <input
              type="number"
              required
              step={1000}
              value={editForm.current_salary}
              onChange={(e) => setEditForm({ ...editForm, current_salary: e.target.value })}
              className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
            />
          </div>

          <div className="flex justify-end space-x-3 pt-3 border-t border-gray-100">
            <button
              type="button"
              onClick={() => setIsEditModalOpen(false)}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-gray-700 hover:bg-gray-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submittingEdit}
              className="px-5 py-2 rounded-xl text-xs font-semibold text-white bg-forest-700 hover:bg-forest-800 disabled:opacity-50"
            >
              {submittingEdit ? 'Saving...' : 'Update Profile'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default EmployeeProfilePage;
