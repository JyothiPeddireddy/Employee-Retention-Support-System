import React, { useState, useEffect } from 'react';
import { dataQualityApi } from '../../api/dataQuality';
import { useAuth } from '../../context/AuthContext';
import Modal from '../../components/Modal';
import Alert from '../../components/Alert';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';
import {
  ShieldCheck,
  Play,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Database,
  Layers,
  ChevronRight,
  ShieldAlert
} from 'lucide-react';

export const DataQualityPage = () => {
  const { role } = useAuth();
  const [runs, setRuns] = useState([]);
  const [groundTruthAnomalies, setGroundTruthAnomalies] = useState([]);
  const [selectedRun, setSelectedRun] = useState(null);
  const [runIssues, setRunIssues] = useState([]);
  const [isIssuesModalOpen, setIsIssuesModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [loadingIssues, setLoadingIssues] = useState(false);
  const [validating, setValidating] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [runsRes, anomRes] = await Promise.all([
        dataQualityApi.listValidationRuns({ limit: 20 }),
        dataQualityApi.getGroundTruthAnomalies(),
      ]);
      setRuns(runsRes || []);
      setGroundTruthAnomalies(anomRes || []);
    } catch (err) {
      setError(err.message || 'Failed to load validation suite data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleTriggerValidation = async () => {
    setValidating(true);
    setError(null);
    try {
      const result = await dataQualityApi.triggerValidation({
        seed: 20261022,
        scale: 500,
      });
      setSuccessMsg(
        `Validation Run '${result.run_id}' completed with status: ${result.status}. (${result.passed_checks}/${result.total_checks} checks passed)`
      );
      fetchData();
    } catch (err) {
      setError(err.message || 'Validation execution failed.');
    } finally {
      setValidating(false);
    }
  };

  const openIssuesModal = async (run) => {
    setSelectedRun(run);
    setIsIssuesModalOpen(true);
    setLoadingIssues(true);
    try {
      const issues = await dataQualityApi.getRunIssues(run.run_id);
      setRunIssues(issues || []);
    } catch (err) {
      setError('Failed to fetch run issues.');
    } finally {
      setLoadingIssues(false);
    }
  };

  const getSeverityBadge = (sev) => {
    switch (sev) {
      case 'CRITICAL':
        return 'bg-rose-100 text-rose-800 border-rose-300';
      case 'HIGH':
        return 'bg-amber-100 text-amber-800 border-amber-300';
      case 'MEDIUM':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'LOW':
      default:
        return 'bg-gray-100 text-gray-700 border-gray-300';
    }
  };

  const canValidate = ['HR_PARTNER', 'ADMIN', 'SYSTEM_ADMIN'].includes(role);

  return (
    <div className="space-y-6">
      {/* Banner */}
      <div className="bg-white rounded-2xl border border-gray-200 p-5 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h2 className="text-base font-bold text-gray-900">Data Quality & Schema Integrity Suite</h2>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
              Zero Leakage Architecture
            </span>
          </div>
          <p className="text-xs text-gray-500 mt-1 max-w-2xl leading-relaxed">
            Verifies temporal constraint ordering, survey neutrality compliance, foreign key integrity,
            and validates that ground-truth labels remain strictly isolated from model features.
          </p>
        </div>

        {canValidate && (
          <button
            onClick={handleTriggerValidation}
            disabled={validating}
            className="inline-flex items-center px-4 py-2.5 rounded-xl text-xs font-semibold text-white bg-forest-700 hover:bg-forest-800 disabled:opacity-50 transition shadow-xs flex-shrink-0"
          >
            {validating ? (
              <span className="inline-flex items-center">
                <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                Validating Schema...
              </span>
            ) : (
              <span className="inline-flex items-center">
                <Play className="w-3.5 h-3.5 mr-1.5 fill-current" />
                Run Validation Suite
              </span>
            )}
          </button>
        )}
      </div>

      {successMsg && <Alert type="success" message={successMsg} onClose={() => setSuccessMsg(null)} />}
      {error && <Alert type="error" message="Notice" details={error} onClose={() => setError(null)} />}

      {/* Validation Runs Table */}
      <div className="space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-gray-700">Historical Validation Runs</h3>

        <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-xs">
          {loading ? (
            <LoadingSpinner size="lg" message="Loading validation runs..." />
          ) : runs.length === 0 ? (
            <EmptyState
              icon={ShieldCheck}
              title="No validation runs recorded"
              description="Click 'Run Validation Suite' to trigger automated constraints reconciliation."
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-gray-50/75 border-b border-gray-200 text-gray-500 uppercase font-semibold">
                    <th className="py-3 px-4">Run ID</th>
                    <th className="py-3 px-4">Timestamp</th>
                    <th className="py-3 px-4">Version & Seed</th>
                    <th className="py-3 px-4">Total Checks</th>
                    <th className="py-3 px-4">Passed Checks</th>
                    <th className="py-3 px-4">Failed Checks</th>
                    <th className="py-3 px-4">Overall Status</th>
                    <th className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {runs.map((r) => (
                    <tr key={r.run_id} className="hover:bg-gray-50/80 transition">
                      <td className="py-3.5 px-4 font-mono font-medium text-gray-600">{r.run_id}</td>
                      <td className="py-3.5 px-4 text-gray-500 font-mono">
                        {new Date(r.run_timestamp).toLocaleString()}
                      </td>
                      <td className="py-3.5 px-4 text-gray-700">
                        {r.dataset_version} <span className="text-gray-400 font-mono">(seed: {r.seed_used})</span>
                      </td>
                      <td className="py-3.5 px-4 font-bold text-gray-900">{r.total_checks}</td>
                      <td className="py-3.5 px-4 text-emerald-700 font-bold">{r.passed_checks}</td>
                      <td className="py-3.5 px-4 text-rose-700 font-bold">{r.failed_checks}</td>
                      <td className="py-3.5 px-4">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold ${
                            r.status === 'PASSED'
                              ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                              : 'bg-rose-50 text-rose-700 border border-rose-200'
                          }`}
                        >
                          {r.status}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <button
                          onClick={() => openIssuesModal(r)}
                          className="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold text-forest-700 bg-forest-50 hover:bg-forest-100 transition"
                        >
                          View Issues
                          <ChevronRight className="w-3.5 h-3.5 ml-1" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Ground Truth Isolated Anomalies Table */}
      <div className="space-y-3 pt-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-gray-700">
              Isolated Ground-Truth Anomalies (Test Suite Only)
            </h3>
            <p className="text-xs text-gray-400">
              These records represent intentional anomalies maintained in an isolated ground-truth table
              to verify audit suite detection with strictly zero leakage into prediction features.
            </p>
          </div>
          <span className="text-xs font-bold px-2.5 py-1 rounded-md bg-purple-50 text-purple-700 border border-purple-200">
            {groundTruthAnomalies.length} Isolated Anomalies
          </span>
        </div>

        <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-xs">
          {groundTruthAnomalies.length === 0 ? (
            <div className="p-8 text-center text-xs text-gray-400">No anomalies recorded.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-gray-50/75 border-b border-gray-200 text-gray-500 uppercase font-semibold">
                    <th className="py-3 px-4">Anomaly ID</th>
                    <th className="py-3 px-4">Entity & Record ID</th>
                    <th className="py-3 px-4">Issue Type</th>
                    <th className="py-3 px-4">Severity</th>
                    <th className="py-3 px-4">Expected vs Actual</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {groundTruthAnomalies.map((a) => (
                    <tr key={a.anomaly_id} className="hover:bg-gray-50/80 transition">
                      <td className="py-3.5 px-4 font-mono font-medium text-gray-600">{a.anomaly_id}</td>
                      <td className="py-3.5 px-4">
                        <span className="font-semibold text-gray-900">{a.entity_type}</span>
                        <p className="text-[10px] font-mono text-gray-400">{a.record_id}</p>
                      </td>
                      <td className="py-3.5 px-4 font-semibold text-gray-800">{a.issue_type}</td>
                      <td className="py-3.5 px-4">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold border ${getSeverityBadge(
                            a.severity
                          )}`}
                        >
                          {a.severity}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-gray-600 max-w-md">
                        <p>Expected: <span className="font-mono text-emerald-700">{a.expected_behavior}</span></p>
                        <p>Actual: <span className="font-mono text-rose-700">{a.actual_behavior}</span></p>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Issues Modal */}
      <Modal
        isOpen={isIssuesModalOpen}
        onClose={() => setIsIssuesModalOpen(false)}
        title={`Validation Issues: ${selectedRun?.run_id || ''}`}
        maxWidth="max-w-3xl"
      >
        {loadingIssues ? (
          <LoadingSpinner size="md" message="Loading validation issues..." />
        ) : runIssues.length === 0 ? (
          <div className="py-8 text-center text-xs text-emerald-700 flex flex-col items-center">
            <CheckCircle2 className="w-8 h-8 text-emerald-600 mb-2" />
            <p className="font-bold">Zero Integrity Issues Identified</p>
            <p className="text-gray-500 mt-1">All consistency, neutrality, and schema constraints passed cleanly.</p>
          </div>
        ) : (
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {runIssues.map((issue) => (
              <div
                key={issue.issue_id}
                className="p-3.5 bg-gray-50 rounded-xl border border-gray-200 text-xs space-y-1"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono text-gray-500 font-semibold">{issue.issue_id}</span>
                    <span className="font-bold text-gray-900">Table: {issue.table_name}</span>
                    <span className="font-mono text-gray-400">({issue.record_id})</span>
                  </div>
                  <span
                    className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold border ${getSeverityBadge(
                      issue.severity
                    )}`}
                  >
                    {issue.severity}
                  </span>
                </div>
                <p className="text-gray-700 font-medium">{issue.issue_type}: {issue.description}</p>
                <p className="text-[10px] text-gray-400 font-mono">
                  Identified: {new Date(issue.created_at).toLocaleString()}
                </p>
              </div>
            ))}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default DataQualityPage;
