import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { employeeApi } from '../../api/employees';
import { interventionApi } from '../../api/interventions';
import { assessmentApi } from '../../api/assessments';
import { useAuth } from '../../context/AuthContext';
import FactorChip from '../../components/FactorChip';
import StatCard from '../../components/StatCard';
import Modal from '../../components/Modal';
import Alert from '../../components/Alert';
import LoadingSpinner from '../../components/LoadingSpinner';
import Pagination from '../../components/Pagination';
import EmptyState from '../../components/EmptyState';
import {
  UserCheck,
  ShieldAlert,
  Sparkles,
  Filter,
  RefreshCw,
  MessageSquareHeart,
  Calendar,
  Info,
  CheckCircle2,
  ExternalLink,
  ChevronRight,
  TrendingUp,
  Clock,
  Layers
} from 'lucide-react';

export const RetentionWorkbenchPage = () => {
  const { user, role } = useAuth();
  const [employees, setEmployees] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [totalPages, setTotalPages] = useState(1);
  const [department, setDepartment] = useState('');
  const [minTier, setMinTier] = useState('HIGH');
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Modal states
  const [checkinModalOpen, setCheckinModalOpen] = useState(false);
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [checkinForm, setCheckinForm] = useState({
    intervention_type: '1_ON_1_CAREER_CHECKIN',
    discussion_summary: '',
    agreed_actions: '',
    follow_up_date: '',
  });
  const [submittingCheckin, setSubmittingCheckin] = useState(false);
  const [actionSuccess, setActionSuccess] = useState(null);

  // Run Rules Modal
  const [runRulesModalOpen, setRunRulesModalOpen] = useState(false);
  const [runningRules, setRunningRules] = useState(false);

  const fetchPrioritizedList = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        page,
        page_size: pageSize,
      };
      if (department) params.department = department;
      if (minTier) params.min_tier = minTier;

      const [res, sumRes] = await Promise.all([
        employeeApi.getPrioritizedList(params),
        employeeApi.getPrioritizationSummary(),
      ]);

      setEmployees(res.items || []);
      setTotal(res.total || 0);
      setTotalPages(res.total_pages || 1);
      setSummary(sumRes);
    } catch (err) {
      setError(err.message || 'Error fetching prioritized retention list.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPrioritizedList();
  }, [page, department, minTier]);

  const openCheckinModal = (candidate) => {
    setSelectedCandidate(candidate);
    // Pre-populate recommended topics into discussion summary placeholder
    const recommendedSummary = candidate.recommended_topics?.length
      ? `Discussed: ${candidate.recommended_topics.join('; ')}.`
      : 'Discussed workload pacing and career milestone roadmap.';

    setCheckinForm({
      intervention_type: '1_ON_1_CAREER_CHECKIN',
      discussion_summary: recommendedSummary,
      agreed_actions: 'Agreed on sprint rebalancing and schedule follow-up check-in.',
      follow_up_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    });
    setCheckinModalOpen(true);
  };

  const handleCheckinSubmit = async (e) => {
    e.preventDefault();
    setSubmittingCheckin(true);
    setActionSuccess(null);

    try {
      const today = new Date().toISOString().split('T')[0];
      const payload = {
        employee_id: selectedCandidate.employee_id,
        conducted_by_id: user?.employee_id || 'EMP-000001',
        intervention_date: today,
        intervention_type: checkinForm.intervention_type,
        discussion_summary: checkinForm.discussion_summary,
        agreed_actions: checkinForm.agreed_actions || null,
        follow_up_date: checkinForm.follow_up_date || null,
        status: 'SCHEDULED',
      };

      await interventionApi.createIntervention(payload);
      setActionSuccess(`Supportive check-in scheduled for ${selectedCandidate.full_name}.`);
      setCheckinModalOpen(false);
      fetchPrioritizedList();
    } catch (err) {
      setError(err.message || 'Failed to record check-in.');
    } finally {
      setSubmittingCheckin(false);
    }
  };

  const handleRunRules = async () => {
    setRunningRules(true);
    try {
      await assessmentApi.generateAssessments({
        observation_cutoff: '2025-12-31',
      });
      setActionSuccess('Assessment rules evaluated successfully across all longitudinal cohorts.');
      setRunRulesModalOpen(false);
      fetchPrioritizedList();
    } catch (err) {
      setError(err.message || 'Failed to run assessment rules.');
    } finally {
      setRunningRules(false);
    }
  };

  const getTierBadge = (tier) => {
    switch (tier) {
      case 'HIGH':
        return 'bg-rose-100 text-rose-800 border-rose-300';
      case 'MEDIUM':
        return 'bg-amber-100 text-amber-800 border-amber-300';
      case 'LOW':
      default:
        return 'bg-emerald-100 text-emerald-800 border-emerald-300';
    }
  };

  return (
    <div className="space-y-6">
      {/* Ethical AI & Human-in-the-Loop Mission Banner */}
      <div className="rounded-2xl bg-white border border-forest-200 p-5 shadow-xs">
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-3.5">
            <div className="p-2.5 rounded-xl bg-forest-50 text-forest-700 border border-forest-200 flex-shrink-0">
              <Sparkles className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-gray-900">Explainable Supportive Retention Policy</h3>
              <p className="mt-1 text-xs text-gray-600 leading-relaxed max-w-3xl">
                This workbench prioritizes supportive 1-on-1 check-ins. Predictions are strictly
                decision-support signals, never a resignation probability or punitive metric.
                Temporary workload surges without sentiment decline are categorized as benign surges, and
                missing surveys are treated as neutral incompleteness without score penalties.
              </p>
            </div>
          </div>
          <button
            onClick={() => setRunRulesModalOpen(true)}
            className="hidden sm:inline-flex items-center px-3.5 py-2 rounded-xl text-xs font-semibold text-white bg-forest-700 hover:bg-forest-800 transition shadow-xs flex-shrink-0"
          >
            <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
            Evaluate Rules Engine
          </button>
        </div>
      </div>

      {actionSuccess && (
        <Alert
          type="success"
          message={actionSuccess}
          onClose={() => setActionSuccess(null)}
        />
      )}
      {error && <Alert type="error" message="Notice" details={error} onClose={() => setError(null)} />}

      {/* Summary KPI Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <span className="text-[11px] font-semibold uppercase text-gray-500">Evaluated Cohort</span>
          <p className="text-xl font-bold text-gray-900 mt-1">{summary?.total_evaluated || 0}</p>
        </div>
        <div className="bg-white rounded-xl border border-rose-200 p-4 bg-rose-50/20">
          <span className="text-[11px] font-semibold uppercase text-rose-600">High Priority Tier</span>
          <p className="text-xl font-bold text-rose-700 mt-1">{summary?.high_priority_count || 0}</p>
        </div>
        <div className="bg-white rounded-xl border border-amber-200 p-4 bg-amber-50/20">
          <span className="text-[11px] font-semibold uppercase text-amber-600">Medium Priority Tier</span>
          <p className="text-xl font-bold text-amber-700 mt-1">{summary?.medium_priority_count || 0}</p>
        </div>
        <div className="bg-white rounded-xl border border-emerald-200 p-4 bg-emerald-50/20">
          <span className="text-[11px] font-semibold uppercase text-emerald-600">Active Interventions</span>
          <p className="text-xl font-bold text-emerald-700 mt-1">{summary?.interventions_logged || 0}</p>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="bg-white rounded-2xl border border-gray-200 p-4 shadow-xs flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center space-x-2 text-xs font-semibold text-gray-700">
            <Filter className="w-4 h-4 text-forest-700" />
            <span>Filters:</span>
          </div>

          <select
            value={department}
            onChange={(e) => {
              setDepartment(e.target.value);
              setPage(1);
            }}
            className="text-xs rounded-xl border border-gray-300 py-1.5 px-3 bg-white focus:outline-hidden focus:ring-2 focus:ring-forest-600"
          >
            <option value="">All Departments</option>
            <option value="Engineering">Engineering</option>
            <option value="Product">Product</option>
            <option value="Design">Design</option>
            <option value="Sales">Sales</option>
            <option value="Operations">Operations</option>
            <option value="Human Resources">Human Resources</option>
          </select>

          <select
            value={minTier}
            onChange={(e) => {
              setMinTier(e.target.value);
              setPage(1);
            }}
            className="text-xs rounded-xl border border-gray-300 py-1.5 px-3 bg-white focus:outline-hidden focus:ring-2 focus:ring-forest-600"
          >
            <option value="">All Tiers (High, Med, Low)</option>
            <option value="HIGH">High Priority Only</option>
            <option value="MEDIUM">Medium & High Priority</option>
            <option value="LOW">Low, Medium & High</option>
          </select>
        </div>

        <div className="text-xs text-gray-500 font-medium">
          Showing {employees.length} prioritized candidates
        </div>
      </div>

      {/* Candidates List */}
      {loading ? (
        <LoadingSpinner size="lg" message="Evaluating explainability signals..." />
      ) : employees.length === 0 ? (
        <EmptyState
          icon={UserCheck}
          title="No prioritized retention signals found"
          description="Adjust your department or minimum priority filter to explore other cohorts."
        />
      ) : (
        <div className="space-y-4">
          {employees.map((emp) => (
            <div
              key={emp.employee_id}
              className="bg-white rounded-2xl border border-gray-200 p-5 shadow-xs transition hover:shadow-md hover:border-gray-300"
            >
              <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
                {/* Employee Header */}
                <div className="flex-1">
                  <div className="flex flex-wrap items-center gap-2 mb-1.5">
                    <span className="font-mono text-xs font-semibold text-gray-500 bg-gray-100 px-2 py-0.5 rounded-md">
                      {emp.employee_id}
                    </span>
                    <Link
                      to={`/employees/${emp.employee_id}`}
                      className="text-base font-bold text-gray-900 hover:text-forest-700 flex items-center transition"
                    >
                      {emp.full_name}
                      <ChevronRight className="w-4 h-4 ml-1 opacity-40" />
                    </Link>
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-bold border ${getTierBadge(
                        emp.priority_tier
                      )}`}
                    >
                      {emp.priority_tier} PRIORITY
                    </span>
                    {emp.has_active_intervention && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                        <CheckCircle2 className="w-3 h-3 mr-1" />
                        Check-in Scheduled
                      </span>
                    )}
                  </div>

                  {/* Metadata Row */}
                  <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-gray-500 mb-3 font-medium">
                    <span>
                      Role: <strong className="text-gray-700">{emp.role_title}</strong> ({emp.role_level})
                    </span>
                    <span>•</span>
                    <span>
                      Dept: <strong className="text-gray-700">{emp.department}</strong> ({emp.team_name})
                    </span>
                    <span>•</span>
                    <span>
                      Tenure: <strong className="text-gray-700">{emp.tenure_months} mos</strong>
                    </span>
                    <span>•</span>
                    <span>
                      In Role: <strong className="text-gray-700">{emp.months_in_role} mos</strong>
                    </span>
                  </div>

                  {/* Explainability Signal Chips */}
                  <div className="mb-3">
                    <p className="text-[11px] font-semibold uppercase tracking-wider text-gray-500 mb-1">
                      Signal Factor Attribution:
                    </p>
                    <div className="flex flex-wrap items-center gap-1">
                      {emp.factors && emp.factors.length > 0 ? (
                        emp.factors.map((f, idx) => <FactorChip key={idx} factor={f} />)
                      ) : (
                        <span className="text-xs text-gray-400">Baseline monitoring parameters.</span>
                      )}
                    </div>
                  </div>

                  {/* Recommended Discussion Topics */}
                  {emp.recommended_topics && emp.recommended_topics.length > 0 && (
                    <div className="p-3 rounded-xl bg-forest-50/50 border border-forest-100 text-xs">
                      <span className="font-semibold text-forest-900 block mb-1">
                        Suggested Supportive 1-on-1 Discussion Topics:
                      </span>
                      <ul className="list-disc list-inside space-y-0.5 text-forest-800">
                        {emp.recommended_topics.map((topic, i) => (
                          <li key={i}>{topic}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                {/* Score & Actions Panel */}
                <div className="flex flex-row lg:flex-col items-center lg:items-end justify-between border-t lg:border-t-0 pt-3 lg:pt-0 gap-3 flex-shrink-0">
                  <div className="text-left lg:text-right">
                    <span className="text-[11px] font-semibold uppercase text-gray-400">Support Priority Score</span>
                    <p className="text-2xl font-black text-gray-900">
                      {emp.composite_priority_score.toFixed(1)}
                      <span className="text-xs text-gray-400 font-normal"> / 100</span>
                    </p>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Link
                      to={`/employees/${emp.employee_id}/timeline`}
                      className="px-3 py-1.5 rounded-xl text-xs font-semibold text-gray-700 bg-gray-100 hover:bg-gray-200 transition"
                    >
                      360 Timeline
                    </Link>
                    <button
                      onClick={() => openCheckinModal(emp)}
                      className="inline-flex items-center px-3.5 py-1.5 rounded-xl text-xs font-semibold text-white bg-forest-700 hover:bg-forest-800 transition shadow-xs"
                    >
                      <MessageSquareHeart className="w-3.5 h-3.5 mr-1.5" />
                      Log Check-in
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}

          {/* Pagination */}
          <Pagination
            currentPage={page}
            totalPages={totalPages}
            totalItems={total}
            pageSize={pageSize}
            onPageChange={(p) => setPage(p)}
          />
        </div>
      )}

      {/* Schedule Supportive Check-in Modal */}
      <Modal
        isOpen={checkinModalOpen}
        onClose={() => setCheckinModalOpen(false)}
        title={`Log Supportive Check-in: ${selectedCandidate?.full_name}`}
      >
        <form onSubmit={handleCheckinSubmit} className="space-y-4">
          <div className="p-3 bg-forest-50 border border-forest-100 rounded-xl text-xs text-forest-800">
            <strong>Supportive Goal:</strong> Have a non-evaluative conversation to understand
            bandwidth, career progression alignment, and managerial support requirements.
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
              Intervention Format
            </label>
            <select
              value={checkinForm.intervention_type}
              onChange={(e) => setCheckinForm({ ...checkinForm, intervention_type: e.target.value })}
              className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:outline-hidden focus:ring-2 focus:ring-forest-600 bg-white"
            >
              <option value="1_ON_1_CAREER_CHECKIN">1-on-1 Career & Growth Check-in</option>
              <option value="WORKLOAD_REBALANCING">Workload Rebalancing & Sprint Adjustment</option>
              <option value="COMP_REVIEW">Compensation & Role Band Alignment Review</option>
              <option value="MENTORSHIP_ALIGNMENT">Mentorship & Project Alignment</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
              Discussion Summary
            </label>
            <textarea
              required
              rows={3}
              value={checkinForm.discussion_summary}
              onChange={(e) => setCheckinForm({ ...checkinForm, discussion_summary: e.target.value })}
              className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:outline-hidden focus:ring-2 focus:ring-forest-600"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
              Agreed Supportive Actions
            </label>
            <textarea
              rows={2}
              value={checkinForm.agreed_actions}
              onChange={(e) => setCheckinForm({ ...checkinForm, agreed_actions: e.target.value })}
              placeholder="e.g. Offload secondary sprint tasks; schedule milestone discussion."
              className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:outline-hidden focus:ring-2 focus:ring-forest-600"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
              Follow-up Review Date
            </label>
            <input
              type="date"
              value={checkinForm.follow_up_date}
              onChange={(e) => setCheckinForm({ ...checkinForm, follow_up_date: e.target.value })}
              className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:outline-hidden focus:ring-2 focus:ring-forest-600"
            />
          </div>

          <div className="flex justify-end space-x-3 pt-3 border-t border-gray-100">
            <button
              type="button"
              onClick={() => setCheckinModalOpen(false)}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-gray-700 hover:bg-gray-100 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submittingCheckin}
              className="px-5 py-2 rounded-xl text-xs font-semibold text-white bg-forest-700 hover:bg-forest-800 disabled:opacity-50 transition shadow-xs"
            >
              {submittingCheckin ? 'Saving...' : 'Record Check-in'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Run Rules Confirmation Modal */}
      <Modal
        isOpen={runRulesModalOpen}
        onClose={() => setRunRulesModalOpen(false)}
        title="Execute Supportive Rules Engine"
        maxWidth="max-w-md"
      >
        <div className="space-y-4">
          <p className="text-xs text-gray-600 leading-relaxed">
            This operation evaluates all workforce snapshots up to observation cutoff (2025-12-31).
            It assigns explainability chips and composite priority tiers based on documented
            heuristics.
          </p>
          <div className="p-3 bg-gray-50 rounded-xl text-xs text-gray-500 font-mono">
            Cutoff Horizon: 2025-12-31<br />
            Pre-outcome features only: Strict Temporal Separation
          </div>
          <div className="flex justify-end space-x-3 pt-2">
            <button
              onClick={() => setRunRulesModalOpen(false)}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-gray-700 hover:bg-gray-100"
            >
              Cancel
            </button>
            <button
              onClick={handleRunRules}
              disabled={runningRules}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-white bg-forest-700 hover:bg-forest-800 disabled:opacity-50"
            >
              {runningRules ? 'Evaluating...' : 'Run Evaluation'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default RetentionWorkbenchPage;
