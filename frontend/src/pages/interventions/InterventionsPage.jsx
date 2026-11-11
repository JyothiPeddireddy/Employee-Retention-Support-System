import React, { useState, useEffect } from 'react';
import { interventionApi } from '../../api/interventions';
import { useAuth } from '../../context/AuthContext';
import Modal from '../../components/Modal';
import Alert from '../../components/Alert';
import LoadingSpinner from '../../components/LoadingSpinner';
import Pagination from '../../components/Pagination';
import EmptyState from '../../components/EmptyState';
import {
  MessageSquareHeart,
  Plus,
  Filter,
  CheckCircle2,
  Clock,
  XCircle,
  FileText,
  ChevronRight,
  User,
  History
} from 'lucide-react';

export const InterventionsPage = () => {
  const { user, role } = useAuth();
  const [interventions, setInterventions] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(15);
  const [totalPages, setTotalPages] = useState(1);
  const [statusFilter, setStatusFilter] = useState('');
  const [employeeIdFilter, setEmployeeIdFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  // Detail Modal
  const [selectedIntervention, setSelectedIntervention] = useState(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [loadingDetail, setLoadingDetail] = useState(false);

  // Status Update Modal
  const [isStatusModalOpen, setIsStatusModalOpen] = useState(false);
  const [statusForm, setStatusForm] = useState({ status: 'COMPLETED', notes: '' });
  const [submittingStatus, setSubmittingStatus] = useState(false);

  // Outcome Update Modal
  const [isOutcomeModalOpen, setIsOutcomeModalOpen] = useState(false);
  const [outcomeForm, setOutcomeForm] = useState({
    simulated_outcome: 'RETENTION_REINFORCED',
    notes: '',
  });
  const [submittingOutcome, setSubmittingOutcome] = useState(false);

  // Log Event Modal
  const [isEventModalOpen, setIsEventModalOpen] = useState(false);
  const [eventForm, setEventForm] = useState({
    event_type: 'NOTES_UPDATED',
    notes: '',
  });
  const [submittingEvent, setSubmittingEvent] = useState(false);

  // Log New Intervention Modal
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [createForm, setCreateForm] = useState({
    employee_id: '',
    intervention_type: '1_ON_1_CAREER_CHECKIN',
    discussion_summary: '',
    agreed_actions: '',
    follow_up_date: '',
    status: 'SCHEDULED',
  });
  const [submittingCreate, setSubmittingCreate] = useState(false);

  const fetchInterventions = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        page,
        page_size: pageSize,
      };
      if (statusFilter) params.status = statusFilter;
      if (employeeIdFilter.trim()) params.employee_id = employeeIdFilter.trim();

      const res = await interventionApi.listInterventions(params);
      setInterventions(res.items || []);
      setTotal(res.total || 0);
      setTotalPages(res.total_pages || 1);
    } catch (err) {
      setError(err.message || 'Failed to retrieve interventions list.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInterventions();
  }, [page, statusFilter]);

  const openDetailModal = async (intId) => {
    setIsDetailModalOpen(true);
    setLoadingDetail(true);
    try {
      const detail = await interventionApi.getInterventionDetail(intId);
      setSelectedIntervention(detail);
    } catch (err) {
      setError(err.message || 'Failed to fetch intervention details.');
    } finally {
      setLoadingDetail(false);
    }
  };

  const handleStatusSubmit = async (e) => {
    e.preventDefault();
    setSubmittingStatus(true);
    try {
      await interventionApi.updateStatus(selectedIntervention.intervention_id, statusForm);
      setSuccessMsg(`Status updated to '${statusForm.status}'.`);
      setIsStatusModalOpen(false);
      openDetailModal(selectedIntervention.intervention_id);
      fetchInterventions();
    } catch (err) {
      setError(err.message || 'Failed to update status.');
    } finally {
      setSubmittingStatus(false);
    }
  };

  const handleOutcomeSubmit = async (e) => {
    e.preventDefault();
    setSubmittingOutcome(true);
    try {
      await interventionApi.updateOutcome(selectedIntervention.intervention_id, outcomeForm);
      setSuccessMsg(`Outcome updated to '${outcomeForm.simulated_outcome}'.`);
      setIsOutcomeModalOpen(false);
      openDetailModal(selectedIntervention.intervention_id);
      fetchInterventions();
    } catch (err) {
      setError(err.message || 'Failed to update outcome.');
    } finally {
      setSubmittingOutcome(false);
    }
  };

  const handleEventSubmit = async (e) => {
    e.preventDefault();
    setSubmittingEvent(true);
    try {
      const actorId = user?.employee_id || user?.user_id || 'USR-000001';
      await interventionApi.recordEvent(selectedIntervention.intervention_id, {
        event_type: eventForm.event_type,
        actor_id: actorId,
        notes: eventForm.notes,
      });
      setSuccessMsg('Lifecycle event recorded.');
      setIsEventModalOpen(false);
      setEventForm({ event_type: 'NOTES_UPDATED', notes: '' });
      openDetailModal(selectedIntervention.intervention_id);
    } catch (err) {
      setError(err.message || 'Failed to append event.');
    } finally {
      setSubmittingEvent(false);
    }
  };

  const handleCreateSubmit = async (e) => {
    e.preventDefault();
    setSubmittingCreate(true);
    try {
      const today = new Date().toISOString().split('T')[0];
      await interventionApi.createIntervention({
        employee_id: createForm.employee_id.trim(),
        conducted_by_id: user?.employee_id || 'EMP-000001',
        intervention_date: today,
        intervention_type: createForm.intervention_type,
        discussion_summary: createForm.discussion_summary,
        agreed_actions: createForm.agreed_actions || null,
        follow_up_date: createForm.follow_up_date || null,
        status: createForm.status,
      });
      setSuccessMsg(`Supportive intervention created for '${createForm.employee_id}'.`);
      setIsCreateModalOpen(false);
      setCreateForm({
        employee_id: '',
        intervention_type: '1_ON_1_CAREER_CHECKIN',
        discussion_summary: '',
        agreed_actions: '',
        follow_up_date: '',
        status: 'SCHEDULED',
      });
      fetchInterventions();
    } catch (err) {
      setError(err.message || 'Failed to log intervention.');
    } finally {
      setSubmittingCreate(false);
    }
  };

  const getStatusBadge = (s) => {
    switch (s) {
      case 'COMPLETED':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'CANCELLED':
        return 'bg-gray-100 text-gray-600 border-gray-200';
      case 'SCHEDULED':
      default:
        return 'bg-blue-50 text-blue-700 border-blue-200';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-gray-900">Supportive Interventions & Event Audit Trail</h2>
          <p className="text-xs text-gray-500">
            Documented human-in-the-loop touchpoints, agreed support actions, and simulated outcomes.
          </p>
        </div>
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="inline-flex items-center px-3.5 py-2 rounded-xl text-xs font-semibold text-white bg-forest-700 hover:bg-forest-800 transition shadow-xs"
        >
          <Plus className="w-4 h-4 mr-1.5" />
          Log Supportive 1-on-1
        </button>
      </div>

      {successMsg && <Alert type="success" message={successMsg} onClose={() => setSuccessMsg(null)} />}
      {error && <Alert type="error" message="Notice" details={error} onClose={() => setError(null)} />}

      {/* Filter Controls */}
      <div className="bg-white rounded-2xl border border-gray-200 p-4 shadow-xs flex flex-wrap items-center justify-between gap-4">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            setPage(1);
            fetchInterventions();
          }}
          className="flex flex-wrap items-center gap-3"
        >
          <input
            type="text"
            value={employeeIdFilter}
            onChange={(e) => setEmployeeIdFilter(e.target.value)}
            placeholder="Filter by EMP-000001..."
            className="text-xs rounded-xl border border-gray-300 py-2 px-3 focus:ring-2 focus:ring-forest-600"
          />
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
            className="text-xs rounded-xl border border-gray-300 py-2 px-3 bg-white focus:ring-2 focus:ring-forest-600"
          >
            <option value="">All Statuses</option>
            <option value="SCHEDULED">Scheduled</option>
            <option value="COMPLETED">Completed</option>
            <option value="CANCELLED">Cancelled</option>
          </select>
          <button
            type="submit"
            className="px-3.5 py-2 rounded-xl text-xs font-semibold text-gray-700 bg-gray-100 hover:bg-gray-200 transition"
          >
            Filter
          </button>
        </form>

        <span className="text-xs text-gray-500 font-medium">{total} total intervention records</span>
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-xs">
        {loading ? (
          <LoadingSpinner size="lg" message="Loading interventions..." />
        ) : interventions.length === 0 ? (
          <EmptyState
            icon={MessageSquareHeart}
            title="No interventions found"
            description="Adjust your search criteria or log a new supportive check-in."
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-gray-50/75 border-b border-gray-200 text-gray-500 uppercase font-semibold">
                  <th className="py-3 px-4">Intervention ID</th>
                  <th className="py-3 px-4">Employee</th>
                  <th className="py-3 px-4">Conducted By</th>
                  <th className="py-3 px-4">Check-in Type</th>
                  <th className="py-3 px-4">Date</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Simulated Outcome</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {interventions.map((item) => (
                  <tr key={item.intervention_id} className="hover:bg-gray-50/80 transition">
                    <td className="py-3.5 px-4 font-mono font-medium text-gray-600">{item.intervention_id}</td>
                    <td className="py-3.5 px-4">
                      <span className="font-bold text-gray-900">{item.employee_name || item.employee_id}</span>
                      <p className="text-[10px] font-mono text-gray-400">{item.employee_id}</p>
                    </td>
                    <td className="py-3.5 px-4 text-gray-700">{item.conducted_by_name || item.conducted_by_id}</td>
                    <td className="py-3.5 px-4">
                      <span className="font-medium text-gray-800">
                        {item.intervention_type.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-gray-500 font-mono">{item.intervention_date}</td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold border ${getStatusBadge(
                          item.status
                        )}`}
                      >
                        {item.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      {item.simulated_outcome ? (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-forest-50 text-forest-800 border border-forest-200">
                          {item.simulated_outcome}
                        </span>
                      ) : (
                        <span className="text-gray-400">Pending Review</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => openDetailModal(item.intervention_id)}
                        className="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold text-forest-700 bg-forest-50 hover:bg-forest-100 transition"
                      >
                        Details & Audit
                        <ChevronRight className="w-3.5 h-3.5 ml-1" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <Pagination
          currentPage={page}
          totalPages={totalPages}
          totalItems={total}
          pageSize={pageSize}
          onPageChange={(p) => setPage(p)}
        />
      </div>

      {/* Intervention Detail & Audit Trail Modal */}
      <Modal
        isOpen={isDetailModalOpen}
        onClose={() => setIsDetailModalOpen(false)}
        title={`Intervention Audit Trail: ${selectedIntervention?.intervention_id || ''}`}
        maxWidth="max-w-3xl"
      >
        {loadingDetail || !selectedIntervention ? (
          <LoadingSpinner size="md" message="Loading intervention details..." />
        ) : (
          <div className="space-y-6">
            {/* Header Summary */}
            <div className="p-4 bg-gray-50 rounded-xl border border-gray-200 grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div>
                <span className="text-[10px] uppercase text-gray-400">Employee</span>
                <p className="font-bold text-gray-900">{selectedIntervention.employee_name}</p>
                <p className="text-[10px] font-mono text-gray-500">{selectedIntervention.employee_id}</p>
              </div>
              <div>
                <span className="text-[10px] uppercase text-gray-400">Conducted By</span>
                <p className="font-semibold text-gray-900">{selectedIntervention.conducted_by_name}</p>
                <p className="text-[10px] font-mono text-gray-500">{selectedIntervention.conducted_by_id}</p>
              </div>
              <div>
                <span className="text-[10px] uppercase text-gray-400">Status</span>
                <p>
                  <span
                    className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold border ${getStatusBadge(
                      selectedIntervention.status
                    )}`}
                  >
                    {selectedIntervention.status}
                  </span>
                </p>
              </div>
              <div>
                <span className="text-[10px] uppercase text-gray-400">Simulated Outcome</span>
                <p className="font-semibold text-forest-800">
                  {selectedIntervention.simulated_outcome || 'In Progress'}
                </p>
              </div>
            </div>

            {/* Discussion & Actions */}
            <div className="space-y-3 text-xs">
              <div>
                <span className="font-semibold text-gray-700 uppercase tracking-wider text-[10px]">
                  Discussion Summary:
                </span>
                <p className="mt-1 p-3 bg-white rounded-xl border border-gray-200 text-gray-800 leading-relaxed">
                  {selectedIntervention.discussion_summary}
                </p>
              </div>

              <div>
                <span className="font-semibold text-gray-700 uppercase tracking-wider text-[10px]">
                  Agreed Supportive Actions:
                </span>
                <p className="mt-1 p-3 bg-forest-50/50 rounded-xl border border-forest-100 text-forest-900 leading-relaxed">
                  {selectedIntervention.agreed_actions || 'No explicit actions recorded.'}
                </p>
              </div>
            </div>

            {/* Lifecycle Action Buttons */}
            <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-gray-100">
              <button
                onClick={() => setIsStatusModalOpen(true)}
                className="px-3 py-1.5 rounded-xl text-xs font-semibold text-gray-700 bg-gray-100 hover:bg-gray-200 transition"
              >
                Update Lifecycle Status
              </button>
              <button
                onClick={() => setIsOutcomeModalOpen(true)}
                className="px-3 py-1.5 rounded-xl text-xs font-semibold text-forest-700 bg-forest-50 hover:bg-forest-100 border border-forest-200 transition"
              >
                Record Retention Outcome
              </button>
              <button
                onClick={() => setIsEventModalOpen(true)}
                className="px-3 py-1.5 rounded-xl text-xs font-semibold text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 transition"
              >
                Log Progress Event
              </button>
            </div>

            {/* Event Timeline */}
            <div>
              <div className="flex items-center space-x-2 mb-3">
                <History className="w-4 h-4 text-forest-700" />
                <h4 className="text-xs font-bold text-gray-900 uppercase tracking-wider">
                  Immutable Lifecycle Event History
                </h4>
              </div>

              {selectedIntervention.events?.length === 0 ? (
                <p className="text-xs text-gray-400">No additional lifecycle events recorded yet.</p>
              ) : (
                <div className="relative pl-6 border-l-2 border-forest-200 space-y-4">
                  {selectedIntervention.events?.map((ev) => (
                    <div key={ev.event_id} className="relative text-xs">
                      <div className="absolute -left-[31px] top-1 w-3.5 h-3.5 rounded-full bg-forest-600 border-2 border-white" />
                      <div className="bg-gray-50 p-3 rounded-xl border border-gray-200">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-gray-900">{ev.event_type}</span>
                          <span className="text-[10px] text-gray-400 font-mono">
                            {new Date(ev.event_timestamp).toLocaleString()}
                          </span>
                        </div>
                        <p className="text-gray-600 mt-1">{ev.notes || 'Status updated.'}</p>
                        <p className="text-[10px] text-gray-400 mt-1">Logged by: {ev.actor_name || ev.actor_id}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </Modal>

      {/* Update Status Modal */}
      <Modal
        isOpen={isStatusModalOpen}
        onClose={() => setIsStatusModalOpen(false)}
        title="Update Intervention Status"
        maxWidth="max-w-md"
      >
        <form onSubmit={handleStatusSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
              New Status
            </label>
            <select
              value={statusForm.status}
              onChange={(e) => setStatusForm({ ...statusForm, status: e.target.value })}
              className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600 bg-white"
            >
              <option value="SCHEDULED">SCHEDULED</option>
              <option value="COMPLETED">COMPLETED</option>
              <option value="CANCELLED">CANCELLED</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
              Status Notes
            </label>
            <textarea
              rows={2}
              value={statusForm.notes}
              onChange={(e) => setStatusForm({ ...statusForm, notes: e.target.value })}
              placeholder="e.g. Conducted 45-minute sprint bandwidth discussion."
              className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
            />
          </div>

          <div className="flex justify-end space-x-3 pt-2">
            <button
              type="button"
              onClick={() => setIsStatusModalOpen(false)}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-gray-700 hover:bg-gray-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submittingStatus}
              className="px-5 py-2 rounded-xl text-xs font-semibold text-white bg-forest-700 hover:bg-forest-800 disabled:opacity-50"
            >
              {submittingStatus ? 'Saving...' : 'Update Status'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Update Outcome Modal */}
      <Modal
        isOpen={isOutcomeModalOpen}
        onClose={() => setIsOutcomeModalOpen(false)}
        title="Record Simulated Retention Outcome"
        maxWidth="max-w-md"
      >
        <form onSubmit={handleOutcomeSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
              Simulated Outcome
            </label>
            <select
              value={outcomeForm.simulated_outcome}
              onChange={(e) => setOutcomeForm({ ...outcomeForm, simulated_outcome: e.target.value })}
              className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600 bg-white"
            >
              <option value="RETENTION_REINFORCED">RETENTION_REINFORCED (Check-in stabilized trajectory)</option>
              <option value="STILL_AT_RISK">STILL_AT_RISK (Requires follow-up check-in)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
              Outcome Observations
            </label>
            <textarea
              rows={2}
              value={outcomeForm.notes}
              onChange={(e) => setOutcomeForm({ ...outcomeForm, notes: e.target.value })}
              placeholder="e.g. Agreed to sprint offloading roadmap and milestone sync."
              className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
            />
          </div>

          <div className="flex justify-end space-x-3 pt-2">
            <button
              type="button"
              onClick={() => setIsOutcomeModalOpen(false)}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-gray-700 hover:bg-gray-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submittingOutcome}
              className="px-5 py-2 rounded-xl text-xs font-semibold text-white bg-forest-700 hover:bg-forest-800 disabled:opacity-50"
            >
              {submittingOutcome ? 'Saving...' : 'Save Outcome'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Log Progress Event Modal */}
      <Modal
        isOpen={isEventModalOpen}
        onClose={() => setIsEventModalOpen(false)}
        title="Log Lifecycle Progress Event"
        maxWidth="max-w-md"
      >
        <form onSubmit={handleEventSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
              Event Type
            </label>
            <select
              value={eventForm.event_type}
              onChange={(e) => setEventForm({ ...eventForm, event_type: e.target.value })}
              className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600 bg-white"
            >
              <option value="NOTES_UPDATED">NOTES_UPDATED</option>
              <option value="ACTION_COMPLETED">ACTION_COMPLETED</option>
              <option value="FOLLOW_UP_SCHEDULED">FOLLOW_UP_SCHEDULED</option>
              <option value="CANCELLED">CANCELLED</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
              Event Details
            </label>
            <textarea
              required
              rows={3}
              value={eventForm.notes}
              onChange={(e) => setEventForm({ ...eventForm, notes: e.target.value })}
              placeholder="e.g. Completed initial sprint redistributions; next milestone set for next week."
              className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
            />
          </div>

          <div className="flex justify-end space-x-3 pt-2">
            <button
              type="button"
              onClick={() => setIsEventModalOpen(false)}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-gray-700 hover:bg-gray-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submittingEvent}
              className="px-5 py-2 rounded-xl text-xs font-semibold text-white bg-forest-700 hover:bg-forest-800 disabled:opacity-50"
            >
              {submittingEvent ? 'Recording...' : 'Record Event'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Log New Intervention Modal */}
      <Modal isOpen={isCreateModalOpen} onClose={() => setIsCreateModalOpen(false)} title="Log Supportive Check-in">
        <form onSubmit={handleCreateSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                Employee ID
              </label>
              <input
                type="text"
                required
                value={createForm.employee_id}
                onChange={(e) => setCreateForm({ ...createForm, employee_id: e.target.value })}
                placeholder="e.g. EMP-000001"
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600 font-mono"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                Check-in Type
              </label>
              <select
                value={createForm.intervention_type}
                onChange={(e) => setCreateForm({ ...createForm, intervention_type: e.target.value })}
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600 bg-white"
              >
                <option value="1_ON_1_CAREER_CHECKIN">1-on-1 Career & Growth Check-in</option>
                <option value="WORKLOAD_REBALANCING">Workload Rebalancing & Offloading</option>
                <option value="COMP_REVIEW">Compensation & Role Band Alignment</option>
                <option value="MENTORSHIP_ALIGNMENT">Mentorship Alignment</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
              Discussion Summary (min 10 characters)
            </label>
            <textarea
              required
              rows={3}
              value={createForm.discussion_summary}
              onChange={(e) => setCreateForm({ ...createForm, discussion_summary: e.target.value })}
              placeholder="e.g. Supportive 1-on-1 discussing capacity, workload pacing, and progression roadmap."
              className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
              Agreed Actions
            </label>
            <textarea
              rows={2}
              value={createForm.agreed_actions}
              onChange={(e) => setCreateForm({ ...createForm, agreed_actions: e.target.value })}
              placeholder="e.g. Rebalance sprint commitments; scheduled quarterly milestone check-in."
              className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                Follow-up Date
              </label>
              <input
                type="date"
                value={createForm.follow_up_date}
                onChange={(e) => setCreateForm({ ...createForm, follow_up_date: e.target.value })}
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                Initial Status
              </label>
              <select
                value={createForm.status}
                onChange={(e) => setCreateForm({ ...createForm, status: e.target.value })}
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600 bg-white"
              >
                <option value="SCHEDULED">SCHEDULED</option>
                <option value="COMPLETED">COMPLETED</option>
              </select>
            </div>
          </div>

          <div className="flex justify-end space-x-3 pt-3 border-t border-gray-100">
            <button
              type="button"
              onClick={() => setIsCreateModalOpen(false)}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-gray-700 hover:bg-gray-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submittingCreate}
              className="px-5 py-2 rounded-xl text-xs font-semibold text-white bg-forest-700 hover:bg-forest-800 disabled:opacity-50"
            >
              {submittingCreate ? 'Saving...' : 'Create Check-in'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default InterventionsPage;
