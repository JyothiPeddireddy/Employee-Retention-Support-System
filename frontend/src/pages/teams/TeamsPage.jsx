import React, { useState, useEffect } from 'react';
import { teamApi } from '../../api/teams';
import { roleApi } from '../../api/roles';
import { employeeApi } from '../../api/employees';
import { useAuth } from '../../context/AuthContext';
import Modal from '../../components/Modal';
import Alert from '../../components/Alert';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';
import {
  Network,
  Users,
  Plus,
  ArrowRightLeft,
  Building2,
  Calendar,
  CheckCircle2,
  ChevronRight,
  Shield
} from 'lucide-react';

export const TeamsPage = () => {
  const { role } = useAuth();
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  // Members modal
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [teamMembers, setTeamMembers] = useState([]);
  const [loadingMembers, setLoadingMembers] = useState(false);
  const [isMembersModalOpen, setIsMembersModalOpen] = useState(false);

  // Create Team modal
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [createForm, setCreateForm] = useState({
    name: '',
    department: 'Engineering',
    lead_employee_id: '',
  });
  const [submittingCreate, setSubmittingCreate] = useState(false);

  // Transfer modal
  const [isTransferModalOpen, setIsTransferModalOpen] = useState(false);
  const [transferForm, setTransferForm] = useState({
    employee_id: '',
    target_team_id: '',
    new_role_id: '',
    effective_date: new Date().toISOString().split('T')[0],
    reason: 'LATERAL_MOVE',
  });
  const [rolesList, setRolesList] = useState([]);
  const [submittingTransfer, setSubmittingTransfer] = useState(false);

  const fetchTeams = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await teamApi.listTeams();
      setTeams(res || []);
    } catch (err) {
      setError(err.message || 'Failed to load teams.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTeams();
  }, []);

  const openMembersModal = async (team) => {
    setSelectedTeam(team);
    setIsMembersModalOpen(true);
    setLoadingMembers(true);
    try {
      const members = await teamApi.getTeamMembers(team.team_id);
      setTeamMembers(members || []);
    } catch (err) {
      setError(err.message || 'Failed to fetch team members.');
    } finally {
      setLoadingMembers(false);
    }
  };

  const openTransferModal = async (defaultTeamId = '') => {
    try {
      const roles = await roleApi.listRoles();
      setRolesList(roles || []);
      setTransferForm({
        employee_id: '',
        target_team_id: defaultTeamId || (teams[0]?.team_id || ''),
        new_role_id: roles[0]?.role_id || '',
        effective_date: new Date().toISOString().split('T')[0],
        reason: 'ORGANIZATIONAL_REBALANCING',
      });
      setIsTransferModalOpen(true);
    } catch (err) {
      setError('Could not prepare transfer options.');
    }
  };

  const handleCreateSubmit = async (e) => {
    e.preventDefault();
    setSubmittingCreate(true);
    try {
      await teamApi.createTeam(createForm);
      setSuccessMsg(`Team '${createForm.name}' created successfully.`);
      setIsCreateModalOpen(false);
      setCreateForm({ name: '', department: 'Engineering', lead_employee_id: '' });
      fetchTeams();
    } catch (err) {
      setError(err.message || 'Failed to create team.');
    } finally {
      setSubmittingCreate(false);
    }
  };

  const handleTransferSubmit = async (e) => {
    e.preventDefault();
    setSubmittingTransfer(true);
    try {
      await teamApi.transferEmployee(transferForm.target_team_id, {
        employee_id: transferForm.employee_id.trim(),
        target_team_id: transferForm.target_team_id,
        new_role_id: transferForm.new_role_id || null,
        effective_date: transferForm.effective_date,
        reason: transferForm.reason,
      });
      setSuccessMsg(`Employee '${transferForm.employee_id}' successfully transferred.`);
      setIsTransferModalOpen(false);
      fetchTeams();
    } catch (err) {
      setError(err.message || 'Failed to complete employee transfer.');
    } finally {
      setSubmittingTransfer(false);
    }
  };

  const canManage = ['HR_PARTNER', 'ADMIN', 'SYSTEM_ADMIN'].includes(role);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-gray-900">Teams & Effective-Dated Membership</h2>
          <p className="text-xs text-gray-500">
            Historical tracking of team transfers without losing previous membership continuity.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          {canManage && (
            <>
              <button
                onClick={() => openTransferModal()}
                className="inline-flex items-center px-3.5 py-2 rounded-xl text-xs font-semibold text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 transition shadow-xs"
              >
                <ArrowRightLeft className="w-3.5 h-3.5 mr-1.5 text-forest-700" />
                Transfer Employee
              </button>
              <button
                onClick={() => setIsCreateModalOpen(true)}
                className="inline-flex items-center px-3.5 py-2 rounded-xl text-xs font-semibold text-white bg-forest-700 hover:bg-forest-800 transition shadow-xs"
              >
                <Plus className="w-4 h-4 mr-1.5" />
                Create Team
              </button>
            </>
          )}
        </div>
      </div>

      {successMsg && <Alert type="success" message={successMsg} onClose={() => setSuccessMsg(null)} />}
      {error && <Alert type="error" message="Notice" details={error} onClose={() => setError(null)} />}

      {/* Teams Grid */}
      {loading ? (
        <LoadingSpinner size="lg" message="Loading teams..." />
      ) : teams.length === 0 ? (
        <EmptyState
          icon={Network}
          title="No teams registered"
          description="Create your first team to initialize organizational structure."
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {teams.map((team) => (
            <div
              key={team.team_id}
              className="bg-white rounded-2xl border border-gray-200 p-5 shadow-xs transition hover:shadow-md hover:border-forest-500/50 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between">
                  <div>
                    <span className="font-mono text-[10px] text-gray-400 font-semibold">{team.team_id}</span>
                    <h3 className="text-base font-bold text-gray-900 mt-0.5">{team.name}</h3>
                  </div>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-forest-50 text-forest-800 border border-forest-200">
                    {team.department}
                  </span>
                </div>

                <div className="mt-4 pt-3 border-t border-gray-100 space-y-2 text-xs">
                  <div className="flex justify-between text-gray-600">
                    <span>Active Members:</span>
                    <strong className="text-gray-900">{team.member_count}</strong>
                  </div>
                  <div className="flex justify-between text-gray-600">
                    <span>Lead Employee:</span>
                    <strong className="font-mono text-gray-800">{team.lead_employee_id || 'Unassigned'}</strong>
                  </div>
                </div>
              </div>

              <div className="mt-5 pt-3 border-t border-gray-100 flex items-center justify-between">
                <button
                  onClick={() => openMembersModal(team)}
                  className="text-xs font-semibold text-forest-700 hover:text-forest-800 flex items-center"
                >
                  View Members
                  <ChevronRight className="w-3.5 h-3.5 ml-1" />
                </button>
                {canManage && (
                  <button
                    onClick={() => openTransferModal(team.team_id)}
                    className="text-xs font-medium text-gray-500 hover:text-gray-800"
                  >
                    Transfer In
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Team Members Modal */}
      <Modal
        isOpen={isMembersModalOpen}
        onClose={() => setIsMembersModalOpen(false)}
        title={`Members of Team: ${selectedTeam?.name}`}
      >
        {loadingMembers ? (
          <LoadingSpinner size="md" message="Loading membership..." />
        ) : teamMembers.length === 0 ? (
          <p className="text-xs text-gray-400 py-6 text-center">No active members found in this team.</p>
        ) : (
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {teamMembers.map((m) => (
              <div
                key={m.employee_id}
                className="p-3 bg-gray-50 rounded-xl border border-gray-200 flex items-center justify-between text-xs"
              >
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-gray-900">{m.full_name}</span>
                    <span className="font-mono text-[10px] text-gray-500 bg-gray-200 px-1.5 py-0.5 rounded">
                      {m.employee_id}
                    </span>
                  </div>
                  <p className="text-gray-500 text-[11px] mt-0.5">
                    {m.role_title} • Started: {m.start_date}
                  </p>
                </div>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                  Active Member
                </span>
              </div>
            ))}
          </div>
        )}
      </Modal>

      {/* Create Team Modal */}
      <Modal isOpen={isCreateModalOpen} onClose={() => setIsCreateModalOpen(false)} title="Create New Team">
        <form onSubmit={handleCreateSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
              Team Name
            </label>
            <input
              type="text"
              required
              value={createForm.name}
              onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
              placeholder="e.g. Distributed Data Platform"
              className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
              Department
            </label>
            <select
              value={createForm.department}
              onChange={(e) => setCreateForm({ ...createForm, department: e.target.value })}
              className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600 bg-white"
            >
              <option value="Engineering">Engineering</option>
              <option value="Product">Product</option>
              <option value="Design">Design</option>
              <option value="Sales">Sales</option>
              <option value="Operations">Operations</option>
              <option value="Human Resources">Human Resources</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
              Team Lead Employee ID <span className="text-gray-400 normal-case">(Optional)</span>
            </label>
            <input
              type="text"
              value={createForm.lead_employee_id}
              onChange={(e) => setCreateForm({ ...createForm, lead_employee_id: e.target.value })}
              placeholder="e.g. EMP-000002"
              className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
            />
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
              {submittingCreate ? 'Creating...' : 'Create Team'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Transfer Employee Modal */}
      <Modal
        isOpen={isTransferModalOpen}
        onClose={() => setIsTransferModalOpen(false)}
        title="Transfer Employee (Effective-Dated)"
      >
        <form onSubmit={handleTransferSubmit} className="space-y-4">
          <div className="p-3 bg-forest-50 border border-forest-100 rounded-xl text-xs text-forest-800">
            Transfers automatically close out the previous team membership record on the effective date
            and initialize the new membership timeline without deleting historical records.
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
              Employee ID
            </label>
            <input
              type="text"
              required
              value={transferForm.employee_id}
              onChange={(e) => setTransferForm({ ...transferForm, employee_id: e.target.value })}
              placeholder="e.g. EMP-000005"
              className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
              Target Team
            </label>
            <select
              value={transferForm.target_team_id}
              onChange={(e) => setTransferForm({ ...transferForm, target_team_id: e.target.value })}
              className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600 bg-white"
            >
              {teams.map((t) => (
                <option key={t.team_id} value={t.team_id}>
                  {t.name} ({t.department})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
              New Role <span className="text-gray-400 normal-case">(Optional if role unchanged)</span>
            </label>
            <select
              value={transferForm.new_role_id}
              onChange={(e) => setTransferForm({ ...transferForm, new_role_id: e.target.value })}
              className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600 bg-white"
            >
              <option value="">Keep Existing Role</option>
              {rolesList.map((r) => (
                <option key={r.role_id} value={r.role_id}>
                  {r.title} ({r.level})
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                Effective Date
              </label>
              <input
                type="date"
                required
                value={transferForm.effective_date}
                onChange={(e) => setTransferForm({ ...transferForm, effective_date: e.target.value })}
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                Transfer Reason
              </label>
              <select
                value={transferForm.reason}
                onChange={(e) => setTransferForm({ ...transferForm, reason: e.target.value })}
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600 bg-white"
              >
                <option value="LATERAL_MOVE">Lateral Move</option>
                <option value="ORGANIZATIONAL_REBALANCING">Org Rebalancing</option>
                <option value="PROMOTION_TRANSFER">Promotion Transfer</option>
                <option value="PROJECT_REALIGNMENT">Project Realignment</option>
              </select>
            </div>
          </div>

          <div className="flex justify-end space-x-3 pt-3 border-t border-gray-100">
            <button
              type="button"
              onClick={() => setIsTransferModalOpen(false)}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-gray-700 hover:bg-gray-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submittingTransfer}
              className="px-5 py-2 rounded-xl text-xs font-semibold text-white bg-forest-700 hover:bg-forest-800 disabled:opacity-50"
            >
              {submittingTransfer ? 'Executing Transfer...' : 'Complete Transfer'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default TeamsPage;
