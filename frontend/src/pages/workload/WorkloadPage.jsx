import React, { useState, useEffect } from 'react';
import { workloadApi } from '../../api/workload';
import { useAuth } from '../../context/AuthContext';
import Modal from '../../components/Modal';
import Alert from '../../components/Alert';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';
import { Clock, Plus, Filter, AlertTriangle, CheckCircle2 } from 'lucide-react';

export const WorkloadPage = () => {
  const { role } = useAuth();
  const [snapshots, setSnapshots] = useState([]);
  const [employeeIdFilter, setEmployeeIdFilter] = useState('');
  const [quarterFilter, setQuarterFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  // Record Snapshot Modal
  const [isRecordModalOpen, setIsRecordModalOpen] = useState(false);
  const [form, setForm] = useState({
    employee_id: '',
    period_quarter: '2025Q4',
    period_date: new Date().toISOString().split('T')[0],
    avg_weekly_hours: 42.0,
    overtime_hours: 2.0,
    consecutive_overtime_weeks: 1,
    active_project_count: 3,
    is_benign_surge: false,
  });
  const [submitting, setSubmitting] = useState(false);

  const fetchSnapshots = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = { limit: 50 };
      if (employeeIdFilter.trim()) params.employee_id = employeeIdFilter.trim();
      if (quarterFilter) params.period_quarter = quarterFilter;

      const res = await workloadApi.listSnapshots(params);
      setSnapshots(res || []);
    } catch (err) {
      setError(err.message || 'Failed to load workload snapshots.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSnapshots();
  }, [quarterFilter]);

  const handleFilterSubmit = (e) => {
    e.preventDefault();
    fetchSnapshots();
  };

  const handleRecordSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await workloadApi.recordSnapshot({
        employee_id: form.employee_id.trim(),
        period_quarter: form.period_quarter,
        period_date: form.period_date,
        avg_weekly_hours: parseFloat(form.avg_weekly_hours),
        overtime_hours: parseFloat(form.overtime_hours),
        consecutive_overtime_weeks: parseInt(form.consecutive_overtime_weeks, 10),
        active_project_count: parseInt(form.active_project_count, 10),
        is_benign_surge: form.is_benign_surge,
      });
      setSuccessMsg(`Workload snapshot recorded for '${form.employee_id}'.`);
      setIsRecordModalOpen(false);
      setForm({
        employee_id: '',
        period_quarter: '2025Q4',
        period_date: new Date().toISOString().split('T')[0],
        avg_weekly_hours: 42.0,
        overtime_hours: 2.0,
        consecutive_overtime_weeks: 1,
        active_project_count: 3,
        is_benign_surge: false,
      });
      fetchSnapshots();
    } catch (err) {
      setError(err.message || 'Failed to record workload snapshot.');
    } finally {
      setSubmitting(false);
    }
  };

  const canRecord = ['IT_OPS_PARTNER', 'HR_PARTNER', 'ADMIN', 'SYSTEM_ADMIN'].includes(role);

  return (
    <div className="space-y-6">
      <div className="p-4 bg-amber-50 border border-amber-200 rounded-2xl flex items-start space-x-3 text-xs text-amber-900">
        <Clock className="w-5 h-5 text-amber-700 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-bold">Workload & Benign Surge Rule:</span> High workload alone does
          NOT trigger high retention priority. Temporary workload surges (e.g. project releases)
          without accompanying sentiment drop are classified as benign surges. Only sustained overtime
          exceeding tolerance thresholds triggers support factor attribution.
        </div>
      </div>

      {successMsg && <Alert type="success" message={successMsg} onClose={() => setSuccessMsg(null)} />}
      {error && <Alert type="error" message="Notice" details={error} onClose={() => setError(null)} />}

      <div className="bg-white rounded-2xl border border-gray-200 p-4 shadow-xs flex flex-wrap items-center justify-between gap-4">
        <form onSubmit={handleFilterSubmit} className="flex flex-wrap items-center gap-3">
          <input
            type="text"
            value={employeeIdFilter}
            onChange={(e) => setEmployeeIdFilter(e.target.value)}
            placeholder="Filter by EMP-000001..."
            className="text-xs rounded-xl border border-gray-300 py-2 px-3 focus:ring-2 focus:ring-forest-600"
          />
          <select
            value={quarterFilter}
            onChange={(e) => setQuarterFilter(e.target.value)}
            className="text-xs rounded-xl border border-gray-300 py-2 px-3 bg-white focus:ring-2 focus:ring-forest-600"
          >
            <option value="">All Quarters</option>
            <option value="2025Q4">2025Q4</option>
            <option value="2025Q3">2025Q3</option>
            <option value="2025Q2">2025Q2</option>
            <option value="2025Q1">2025Q1</option>
            <option value="2024Q4">2024Q4</option>
            <option value="2024Q3">2024Q3</option>
          </select>
          <button
            type="submit"
            className="px-3.5 py-2 rounded-xl text-xs font-semibold text-gray-700 bg-gray-100 hover:bg-gray-200 transition"
          >
            Filter
          </button>
        </form>

        {canRecord && (
          <button
            onClick={() => setIsRecordModalOpen(true)}
            className="inline-flex items-center px-3.5 py-2 rounded-xl text-xs font-semibold text-white bg-forest-700 hover:bg-forest-800 transition shadow-xs"
          >
            <Plus className="w-4 h-4 mr-1.5" />
            Record Workload Snapshot
          </button>
        )}
      </div>

      <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-xs">
        {loading ? (
          <LoadingSpinner size="lg" message="Loading workload snapshots..." />
        ) : snapshots.length === 0 ? (
          <EmptyState
            icon={Clock}
            title="No workload records found"
            description="Adjust your search criteria or log a new quarterly workload snapshot."
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-gray-50/75 border-b border-gray-200 text-gray-500 uppercase font-semibold">
                  <th className="py-3 px-4">Snapshot ID</th>
                  <th className="py-3 px-4">Employee ID</th>
                  <th className="py-3 px-4">Quarter</th>
                  <th className="py-3 px-4">Avg Weekly Hours</th>
                  <th className="py-3 px-4">Overtime Hours</th>
                  <th className="py-3 px-4">Consecutive Wks</th>
                  <th className="py-3 px-4">Active Projects</th>
                  <th className="py-3 px-4">Surge Classification</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {snapshots.map((w) => (
                  <tr key={w.workload_id} className="hover:bg-gray-50/80 transition">
                    <td className="py-3.5 px-4 font-mono font-medium text-gray-600">{w.workload_id}</td>
                    <td className="py-3.5 px-4 font-mono font-bold text-gray-900">{w.employee_id}</td>
                    <td className="py-3.5 px-4 font-semibold text-gray-800">{w.period_quarter}</td>
                    <td className="py-3.5 px-4 font-bold text-gray-900">{w.avg_weekly_hours.toFixed(1)} hrs</td>
                    <td className="py-3.5 px-4 text-rose-600 font-semibold">{w.overtime_hours.toFixed(1)} hrs</td>
                    <td className="py-3.5 px-4">{w.consecutive_overtime_weeks} weeks</td>
                    <td className="py-3.5 px-4">{w.active_project_count} projects</td>
                    <td className="py-3.5 px-4">
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
        )}
      </div>

      {/* Record Workload Modal */}
      <Modal isOpen={isRecordModalOpen} onClose={() => setIsRecordModalOpen(false)} title="Record Workload Snapshot">
        <form onSubmit={handleRecordSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                Employee ID
              </label>
              <input
                type="text"
                required
                value={form.employee_id}
                onChange={(e) => setForm({ ...form, employee_id: e.target.value })}
                placeholder="e.g. EMP-000001"
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                Quarter
              </label>
              <select
                value={form.period_quarter}
                onChange={(e) => setForm({ ...form, period_quarter: e.target.value })}
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600 bg-white"
              >
                <option value="2025Q4">2025Q4</option>
                <option value="2025Q3">2025Q3</option>
                <option value="2025Q2">2025Q2</option>
                <option value="2025Q1">2025Q1</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                Avg Weekly Hours
              </label>
              <input
                type="number"
                step="0.5"
                min="20"
                max="90"
                value={form.avg_weekly_hours}
                onChange={(e) => setForm({ ...form, avg_weekly_hours: e.target.value })}
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                Weekly Overtime Hours
              </label>
              <input
                type="number"
                step="0.5"
                min="0"
                max="40"
                value={form.overtime_hours}
                onChange={(e) => setForm({ ...form, overtime_hours: e.target.value })}
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                Consecutive Overtime Weeks
              </label>
              <input
                type="number"
                min="0"
                max="52"
                value={form.consecutive_overtime_weeks}
                onChange={(e) => setForm({ ...form, consecutive_overtime_weeks: e.target.value })}
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                Active Projects Count
              </label>
              <input
                type="number"
                min="1"
                max="15"
                value={form.active_project_count}
                onChange={(e) => setForm({ ...form, active_project_count: e.target.value })}
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
              />
            </div>
          </div>

          <div className="flex items-center space-x-2 pt-1">
            <input
              type="checkbox"
              id="is_benign"
              checked={form.is_benign_surge}
              onChange={(e) => setForm({ ...form, is_benign_surge: e.target.checked })}
              className="h-4 w-4 rounded-sm border-gray-300 text-forest-700 focus:ring-forest-600"
            />
            <label htmlFor="is_benign" className="text-xs font-medium text-gray-700">
              Flag as Benign Surge (Planned, productive sprint crunch; non-harmful to retention)
            </label>
          </div>

          <div className="flex justify-end space-x-3 pt-3 border-t border-gray-100">
            <button
              type="button"
              onClick={() => setIsRecordModalOpen(false)}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-gray-700 hover:bg-gray-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-5 py-2 rounded-xl text-xs font-semibold text-white bg-forest-700 hover:bg-forest-800 disabled:opacity-50"
            >
              {submitting ? 'Recording...' : 'Save Snapshot'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default WorkloadPage;
