import React, { useState, useEffect } from 'react';
import { roleApi } from '../../api/roles';
import { compensationApi } from '../../api/compensation';
import { useAuth } from '../../context/AuthContext';
import Modal from '../../components/Modal';
import Alert from '../../components/Alert';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';
import { Briefcase, Plus, Shield, Search } from 'lucide-react';

export const RolesPage = () => {
  const { role } = useAuth();
  const [roles, setRoles] = useState([]);
  const [bands, setBands] = useState([]);
  const [department, setDepartment] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  // Create Role Modal
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [createForm, setCreateForm] = useState({
    role_id: '',
    title: '',
    level: 'IC2',
    band_id: 'BAND-IC2',
    department: 'Engineering',
  });
  const [submitting, setSubmitting] = useState(false);

  const fetchRolesAndBands = async () => {
    setLoading(true);
    setError(null);
    try {
      const [rRes, bRes] = await Promise.all([
        roleApi.listRoles(department ? { department } : {}),
        compensationApi.listBands(),
      ]);
      setRoles(rRes || []);
      setBands(bRes || []);
    } catch (err) {
      setError(err.message || 'Failed to load roles and compensation bands.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRolesAndBands();
  }, [department]);

  const handleCreateSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await roleApi.createRole({
        role_id: createForm.role_id.trim(),
        title: createForm.title.trim(),
        level: createForm.level,
        band_id: createForm.band_id,
        department: createForm.department,
      });
      setSuccessMsg(`Role '${createForm.title}' created successfully.`);
      setIsCreateModalOpen(false);
      setCreateForm({
        role_id: '',
        title: '',
        level: 'IC2',
        band_id: bands[0]?.band_id || 'BAND-IC2',
        department: 'Engineering',
      });
      fetchRolesAndBands();
    } catch (err) {
      setError(err.message || 'Failed to create role.');
    } finally {
      setSubmitting(false);
    }
  };

  const canManage = ['HR_PARTNER', 'ADMIN', 'SYSTEM_ADMIN'].includes(role);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-gray-900">Job Classification Roles</h2>
          <p className="text-xs text-gray-500">
            Standard career tracks, job levels, and compensation band mapping.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={department}
            onChange={(e) => setDepartment(e.target.value)}
            className="text-xs rounded-xl border border-gray-300 py-2 px-3 bg-white focus:ring-2 focus:ring-forest-600"
          >
            <option value="">All Departments</option>
            <option value="Engineering">Engineering</option>
            <option value="Product">Product</option>
            <option value="Design">Design</option>
            <option value="Sales">Sales</option>
            <option value="Operations">Operations</option>
          </select>

          {canManage && (
            <button
              onClick={() => setIsCreateModalOpen(true)}
              className="inline-flex items-center px-3.5 py-2 rounded-xl text-xs font-semibold text-white bg-forest-700 hover:bg-forest-800 transition shadow-xs"
            >
              <Plus className="w-4 h-4 mr-1.5" />
              Create Role
            </button>
          )}
        </div>
      </div>

      {successMsg && <Alert type="success" message={successMsg} onClose={() => setSuccessMsg(null)} />}
      {error && <Alert type="error" message="Notice" details={error} onClose={() => setError(null)} />}

      <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-xs">
        {loading ? (
          <LoadingSpinner size="lg" message="Loading job classifications..." />
        ) : roles.length === 0 ? (
          <EmptyState icon={Briefcase} title="No roles found" description="Try selecting another department." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-gray-50/75 border-b border-gray-200 text-gray-500 uppercase font-semibold">
                  <th className="py-3 px-4">Role ID</th>
                  <th className="py-3 px-4">Role Title</th>
                  <th className="py-3 px-4">Level Track</th>
                  <th className="py-3 px-4">Compensation Band</th>
                  <th className="py-3 px-4">Department</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {roles.map((r) => (
                  <tr key={r.role_id} className="hover:bg-gray-50/80 transition">
                    <td className="py-3.5 px-4 font-mono font-medium text-gray-600">{r.role_id}</td>
                    <td className="py-3.5 px-4 font-bold text-gray-900">{r.title}</td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded-md bg-forest-50 text-forest-800 font-mono font-bold text-[11px] border border-forest-200">
                        {r.level}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 font-mono text-gray-600 font-medium">{r.band_id}</td>
                    <td className="py-3.5 px-4 text-gray-700">{r.department || 'General'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Create Role Modal */}
      <Modal isOpen={isCreateModalOpen} onClose={() => setIsCreateModalOpen(false)} title="Create New Role">
        <form onSubmit={handleCreateSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                Role ID (Unique)
              </label>
              <input
                type="text"
                required
                value={createForm.role_id}
                onChange={(e) => setCreateForm({ ...createForm, role_id: e.target.value })}
                placeholder="e.g. ROLE-IC3-DATA"
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600 font-mono"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                Role Title
              </label>
              <input
                type="text"
                required
                value={createForm.title}
                onChange={(e) => setCreateForm({ ...createForm, title: e.target.value })}
                placeholder="e.g. Senior Data Engineer"
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                Level Classification
              </label>
              <select
                value={createForm.level}
                onChange={(e) => setCreateForm({ ...createForm, level: e.target.value })}
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600 bg-white"
              >
                <option value="IC1">IC1 - Associate</option>
                <option value="IC2">IC2 - Mid-Level</option>
                <option value="IC3">IC3 - Senior</option>
                <option value="IC4">IC4 - Staff</option>
                <option value="M1">M1 - Manager</option>
                <option value="M2">M2 - Director</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                Compensation Band
              </label>
              <select
                value={createForm.band_id}
                onChange={(e) => setCreateForm({ ...createForm, band_id: e.target.value })}
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600 bg-white"
              >
                {bands.map((b) => (
                  <option key={b.band_id} value={b.band_id}>
                    {b.name} ({b.band_id}) - ${b.min_salary.toLocaleString()} to ${b.max_salary.toLocaleString()}
                  </option>
                ))}
              </select>
            </div>
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
              disabled={submitting}
              className="px-5 py-2 rounded-xl text-xs font-semibold text-white bg-forest-700 hover:bg-forest-800 disabled:opacity-50"
            >
              {submitting ? 'Creating...' : 'Create Role'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default RolesPage;
