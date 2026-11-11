import React, { useState, useEffect } from 'react';
import { engagementApi } from '../../api/engagement';
import { useAuth } from '../../context/AuthContext';
import Modal from '../../components/Modal';
import Alert from '../../components/Alert';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';
import { HeartHandshake, Plus, HelpCircle, Filter, CheckCircle2 } from 'lucide-react';

export const EngagementSurveysPage = () => {
  const { role, user } = useAuth();
  const [surveys, setSurveys] = useState([]);
  const [employeeIdFilter, setEmployeeIdFilter] = useState('');
  const [quarterFilter, setQuarterFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  // Record Survey Modal
  const [isRecordModalOpen, setIsRecordModalOpen] = useState(false);
  const [form, setForm] = useState({
    employee_id: '',
    survey_quarter: '2025Q4',
    survey_date: new Date().toISOString().split('T')[0],
    is_missing: false,
    satisfaction_score: 4.0,
    work_life_balance_score: 3.5,
    career_growth_score: 4.0,
    manager_support_score: 4.5,
  });
  const [submitting, setSubmitting] = useState(false);

  const fetchSurveys = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = { limit: 50 };
      if (employeeIdFilter.trim()) params.employee_id = employeeIdFilter.trim();
      if (quarterFilter) params.survey_quarter = quarterFilter;

      const res = await engagementApi.listSurveys(params);
      setSurveys(res || []);
    } catch (err) {
      setError(err.message || 'Failed to load engagement pulse surveys.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSurveys();
  }, [quarterFilter]);

  const handleFilterSubmit = (e) => {
    e.preventDefault();
    fetchSurveys();
  };

  const handleRecordSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const payload = {
        employee_id: form.employee_id.trim(),
        survey_quarter: form.survey_quarter,
        survey_date: form.survey_date,
        is_missing: form.is_missing,
        satisfaction_score: form.is_missing ? null : parseFloat(form.satisfaction_score),
        work_life_balance_score: form.is_missing ? null : parseFloat(form.work_life_balance_score),
        career_growth_score: form.is_missing ? null : parseFloat(form.career_growth_score),
        manager_support_score: form.is_missing ? null : parseFloat(form.manager_support_score),
      };

      await engagementApi.recordSurvey(payload);
      setSuccessMsg(`Survey recorded successfully for '${form.employee_id}'.`);
      setIsRecordModalOpen(false);
      setForm({
        employee_id: '',
        survey_quarter: '2025Q4',
        survey_date: new Date().toISOString().split('T')[0],
        is_missing: false,
        satisfaction_score: 4.0,
        work_life_balance_score: 3.5,
        career_growth_score: 4.0,
        manager_support_score: 4.5,
      });
      fetchSurveys();
    } catch (err) {
      setError(err.message || 'Failed to record survey.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Policy banner on Survey Neutrality */}
      <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-2xl flex items-start space-x-3 text-xs text-emerald-900">
        <HeartHandshake className="w-5 h-5 text-emerald-700 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-bold">Strict Survey Neutrality Mandate:</span> Missing or uncompleted
          engagement pulse surveys are flagged as incomplete data records. In accordance with system
          rules, non-responses are never imputed as negative scores or used to penalize retention priority.
        </div>
      </div>

      {successMsg && <Alert type="success" message={successMsg} onClose={() => setSuccessMsg(null)} />}
      {error && <Alert type="error" message="Notice" details={error} onClose={() => setError(null)} />}

      {/* Control Bar */}
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
            Apply Filter
          </button>
        </form>

        <button
          onClick={() => setIsRecordModalOpen(true)}
          className="inline-flex items-center px-3.5 py-2 rounded-xl text-xs font-semibold text-white bg-forest-700 hover:bg-forest-800 transition shadow-xs"
        >
          <Plus className="w-4 h-4 mr-1.5" />
          Record Pulse Survey
        </button>
      </div>

      {/* Surveys Table */}
      <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-xs">
        {loading ? (
          <LoadingSpinner size="lg" message="Loading engagement surveys..." />
        ) : surveys.length === 0 ? (
          <EmptyState
            icon={HeartHandshake}
            title="No survey records found"
            description="Adjust your search criteria or record a new quarterly survey."
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-gray-50/75 border-b border-gray-200 text-gray-500 uppercase font-semibold">
                  <th className="py-3 px-4">Survey ID</th>
                  <th className="py-3 px-4">Employee ID</th>
                  <th className="py-3 px-4">Quarter</th>
                  <th className="py-3 px-4">Satisfaction</th>
                  <th className="py-3 px-4">Work-Life Balance</th>
                  <th className="py-3 px-4">Career Growth</th>
                  <th className="py-3 px-4">Manager Support</th>
                  <th className="py-3 px-4">Composite</th>
                  <th className="py-3 px-4">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {surveys.map((s) => (
                  <tr key={s.survey_id} className="hover:bg-gray-50/80 transition">
                    <td className="py-3.5 px-4 font-mono font-medium text-gray-600">{s.survey_id}</td>
                    <td className="py-3.5 px-4 font-mono font-bold text-gray-900">{s.employee_id}</td>
                    <td className="py-3.5 px-4 font-semibold text-gray-800">{s.survey_quarter}</td>
                    <td className="py-3.5 px-4">
                      {s.is_missing ? '—' : `${s.satisfaction_score?.toFixed(1)} / 5.0`}
                    </td>
                    <td className="py-3.5 px-4">
                      {s.is_missing ? '—' : `${s.work_life_balance_score?.toFixed(1)} / 5.0`}
                    </td>
                    <td className="py-3.5 px-4">
                      {s.is_missing ? '—' : `${s.career_growth_score?.toFixed(1)} / 5.0`}
                    </td>
                    <td className="py-3.5 px-4">
                      {s.is_missing ? '—' : `${s.manager_support_score?.toFixed(1)} / 5.0`}
                    </td>
                    <td className="py-3.5 px-4 font-bold text-forest-800">
                      {s.is_missing ? '—' : `${s.composite_engagement?.toFixed(2)} / 5.0`}
                    </td>
                    <td className="py-3.5 px-4">
                      {s.is_missing ? (
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-gray-100 text-gray-600">
                          Missing (Neutral)
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                          Completed
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Record Pulse Survey Modal */}
      <Modal isOpen={isRecordModalOpen} onClose={() => setIsRecordModalOpen(false)} title="Record Pulse Survey">
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
                Survey Quarter
              </label>
              <select
                value={form.survey_quarter}
                onChange={(e) => setForm({ ...form, survey_quarter: e.target.value })}
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600 bg-white"
              >
                <option value="2025Q4">2025Q4</option>
                <option value="2025Q3">2025Q3</option>
                <option value="2025Q2">2025Q2</option>
                <option value="2025Q1">2025Q1</option>
              </select>
            </div>
          </div>

          <div className="flex items-center space-x-2 pt-1">
            <input
              type="checkbox"
              id="is_missing"
              checked={form.is_missing}
              onChange={(e) => setForm({ ...form, is_missing: e.target.checked })}
              className="h-4 w-4 rounded-sm border-gray-300 text-forest-700 focus:ring-forest-600"
            />
            <label htmlFor="is_missing" className="text-xs font-medium text-gray-700">
              Record as Non-Response (Flagged as missing, strictly neutral score)
            </label>
          </div>

          {!form.is_missing && (
            <div className="grid grid-cols-2 gap-4 pt-2">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                  Satisfaction (1 - 5)
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="1"
                  max="5"
                  value={form.satisfaction_score}
                  onChange={(e) => setForm({ ...form, satisfaction_score: e.target.value })}
                  className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                  Work-Life Balance (1 - 5)
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="1"
                  max="5"
                  value={form.work_life_balance_score}
                  onChange={(e) => setForm({ ...form, work_life_balance_score: e.target.value })}
                  className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                  Career Growth (1 - 5)
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="1"
                  max="5"
                  value={form.career_growth_score}
                  onChange={(e) => setForm({ ...form, career_growth_score: e.target.value })}
                  className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                  Manager Support (1 - 5)
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="1"
                  max="5"
                  value={form.manager_support_score}
                  onChange={(e) => setForm({ ...form, manager_support_score: e.target.value })}
                  className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
                />
              </div>
            </div>
          )}

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
              {submitting ? 'Recording...' : 'Save Survey'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default EngagementSurveysPage;
