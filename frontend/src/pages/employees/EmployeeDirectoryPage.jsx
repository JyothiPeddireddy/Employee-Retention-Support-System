import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { employeeApi } from '../../api/employees';
import { teamApi } from '../../api/teams';
import { roleApi } from '../../api/roles';
import { useAuth } from '../../context/AuthContext';
import Modal from '../../components/Modal';
import Alert from '../../components/Alert';
import LoadingSpinner from '../../components/LoadingSpinner';
import Pagination from '../../components/Pagination';
import EmptyState from '../../components/EmptyState';
import {
  Users,
  Search,
  Filter,
  Plus,
  ExternalLink,
  ChevronRight,
  UserCheck,
  Building2,
  Calendar,
  Briefcase
} from 'lucide-react';

export const EmployeeDirectoryPage = () => {
  const { role } = useAuth();
  const navigate = useNavigate();
  const [employees, setEmployees] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(15);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState('');
  const [department, setDepartment] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Add Employee Modal
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [addForm, setAddForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    role_id: '',
    team_id: '',
    hire_date: new Date().toISOString().split('T')[0],
    current_salary: 85000,
  });
  const [teamsList, setTeamsList] = useState([]);
  const [rolesList, setRolesList] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState(null);

  const fetchEmployees = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        page,
        page_size: pageSize,
      };
      if (search.trim()) params.search = search.trim();
      if (department) params.department = department;
      if (statusFilter) params.status = statusFilter;

      const res = await employeeApi.listEmployees(params);
      setEmployees(res.items || []);
      setTotal(res.total || 0);
      setTotalPages(res.total_pages || 1);
    } catch (err) {
      setError(err.message || 'Failed to load employee directory.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEmployees();
  }, [page, department, statusFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchEmployees();
  };

  const openAddModal = async () => {
    try {
      const [tRes, rRes] = await Promise.all([teamApi.listTeams(), roleApi.listRoles()]);
      setTeamsList(tRes || []);
      setRolesList(rRes || []);
      if (tRes?.length) setAddForm((prev) => ({ ...prev, team_id: tRes[0].team_id }));
      if (rRes?.length) setAddForm((prev) => ({ ...prev, role_id: rRes[0].role_id }));
      setIsAddModalOpen(true);
    } catch (err) {
      setError('Could not load teams and roles for new employee.');
    }
  };

  const handleAddSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await employeeApi.createEmployee({
        first_name: addForm.first_name,
        last_name: addForm.last_name,
        email: addForm.email,
        role_id: addForm.role_id,
        team_id: addForm.team_id,
        hire_date: addForm.hire_date,
        current_salary: parseFloat(addForm.current_salary),
        status: 'ACTIVE',
      });
      setSuccessMsg(`Employee ${addForm.first_name} ${addForm.last_name} created successfully.`);
      setIsAddModalOpen(false);
      setAddForm({
        first_name: '',
        last_name: '',
        email: '',
        role_id: '',
        team_id: '',
        hire_date: new Date().toISOString().split('T')[0],
        current_salary: 85000,
      });
      fetchEmployees();
    } catch (err) {
      setError(err.message || 'Failed to create employee.');
    } finally {
      setSubmitting(false);
    }
  };

  const canAdd = ['HR_PARTNER', 'ADMIN', 'SYSTEM_ADMIN'].includes(role);

  return (
    <div className="space-y-6">
      {successMsg && <Alert type="success" message={successMsg} onClose={() => setSuccessMsg(null)} />}
      {error && <Alert type="error" message="Notice" details={error} onClose={() => setError(null)} />}

      {/* Control Bar */}
      <div className="bg-white rounded-2xl border border-gray-200 p-4 shadow-xs flex flex-wrap items-center justify-between gap-4">
        {/* Search */}
        <form onSubmit={handleSearchSubmit} className="flex items-center space-x-2 flex-1 min-w-[240px]">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by name, email, or EMP-000001..."
              className="w-full pl-10 pr-3.5 py-2 text-xs rounded-xl border border-gray-300 focus:outline-hidden focus:ring-2 focus:ring-forest-600"
            />
          </div>
          <button
            type="submit"
            className="px-3.5 py-2 rounded-xl text-xs font-semibold text-white bg-forest-700 hover:bg-forest-800 transition"
          >
            Search
          </button>
        </form>

        {/* Filters & Actions */}
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={department}
            onChange={(e) => {
              setDepartment(e.target.value);
              setPage(1);
            }}
            className="text-xs rounded-xl border border-gray-300 py-2 px-3 bg-white focus:outline-hidden focus:ring-2 focus:ring-forest-600"
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
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
            className="text-xs rounded-xl border border-gray-300 py-2 px-3 bg-white focus:outline-hidden focus:ring-2 focus:ring-forest-600"
          >
            <option value="">All Statuses</option>
            <option value="ACTIVE">Active Headcount</option>
            <option value="ATTRITED">Attrited (Exits)</option>
          </select>

          {canAdd && (
            <button
              onClick={openAddModal}
              className="inline-flex items-center px-3.5 py-2 rounded-xl text-xs font-semibold text-white bg-forest-700 hover:bg-forest-800 transition shadow-xs"
            >
              <Plus className="w-4 h-4 mr-1.5" />
              Add Employee
            </button>
          )}
        </div>
      </div>

      {/* Directory Table */}
      <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-xs">
        {loading ? (
          <LoadingSpinner size="lg" message="Loading employee directory..." />
        ) : employees.length === 0 ? (
          <EmptyState
            icon={Users}
            title="No employees match your search"
            description="Try adjusting your search criteria or resetting filters."
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-gray-50/75 border-b border-gray-200 text-gray-500 uppercase tracking-wider font-semibold">
                  <th className="py-3 px-4">Employee ID</th>
                  <th className="py-3 px-4">Name & Email</th>
                  <th className="py-3 px-4">Department & Team</th>
                  <th className="py-3 px-4">Role Title & Level</th>
                  <th className="py-3 px-4">Hire Date</th>
                  <th className="py-3 px-4">Annual Base</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {employees.map((emp) => (
                  <tr key={emp.employee_id} className="hover:bg-gray-50/80 transition">
                    <td className="py-3.5 px-4 font-mono font-medium text-gray-600">
                      {emp.employee_id}
                    </td>
                    <td className="py-3.5 px-4">
                      <Link
                        to={`/employees/${emp.employee_id}`}
                        className="font-bold text-gray-900 hover:text-forest-700 transition"
                      >
                        {emp.full_name}
                      </Link>
                      <p className="text-[11px] text-gray-400">{emp.email}</p>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="font-semibold text-gray-800">{emp.department}</span>
                      <p className="text-[11px] text-gray-500">{emp.team_name}</p>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="text-gray-800 font-medium">{emp.role_title}</span>
                      <span className="ml-1.5 px-1.5 py-0.5 rounded-sm bg-gray-100 text-[10px] text-gray-600 font-mono">
                        {emp.role_level}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-gray-600 font-medium">{emp.hire_date}</td>
                    <td className="py-3.5 px-4 font-semibold text-gray-800">
                      ${emp.current_salary?.toLocaleString()}
                    </td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                          emp.status === 'ACTIVE'
                            ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                            : 'bg-rose-50 text-rose-700 border border-rose-200'
                        }`}
                      >
                        {emp.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right space-x-2">
                      <Link
                        to={`/employees/${emp.employee_id}`}
                        className="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold text-forest-700 bg-forest-50 hover:bg-forest-100 transition"
                      >
                        Profile
                      </Link>
                      <Link
                        to={`/employees/${emp.employee_id}/timeline`}
                        className="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold text-gray-600 bg-gray-100 hover:bg-gray-200 transition"
                      >
                        360
                      </Link>
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

      {/* Add Employee Modal */}
      <Modal isOpen={isAddModalOpen} onClose={() => setIsAddModalOpen(false)} title="Add New Employee">
        <form onSubmit={handleAddSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                First Name
              </label>
              <input
                type="text"
                required
                value={addForm.first_name}
                onChange={(e) => setAddForm({ ...addForm, first_name: e.target.value })}
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
                value={addForm.last_name}
                onChange={(e) => setAddForm({ ...addForm, last_name: e.target.value })}
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
              Email Address
            </label>
            <input
              type="email"
              required
              value={addForm.email}
              onChange={(e) => setAddForm({ ...addForm, email: e.target.value })}
              className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                Initial Team
              </label>
              <select
                value={addForm.team_id}
                onChange={(e) => setAddForm({ ...addForm, team_id: e.target.value })}
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600 bg-white"
              >
                {teamsList.map((t) => (
                  <option key={t.team_id} value={t.team_id}>
                    {t.name} ({t.department})
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                Initial Role
              </label>
              <select
                value={addForm.role_id}
                onChange={(e) => setAddForm({ ...addForm, role_id: e.target.value })}
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600 bg-white"
              >
                {rolesList.map((r) => (
                  <option key={r.role_id} value={r.role_id}>
                    {r.title} ({r.level})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                Hire Date
              </label>
              <input
                type="date"
                required
                value={addForm.hire_date}
                onChange={(e) => setAddForm({ ...addForm, hire_date: e.target.value })}
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                Starting Base Salary ($)
              </label>
              <input
                type="number"
                required
                min={30000}
                step={1000}
                value={addForm.current_salary}
                onChange={(e) => setAddForm({ ...addForm, current_salary: e.target.value })}
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
              />
            </div>
          </div>

          <div className="flex justify-end space-x-3 pt-3 border-t border-gray-100">
            <button
              type="button"
              onClick={() => setIsAddModalOpen(false)}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-gray-700 hover:bg-gray-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-5 py-2 rounded-xl text-xs font-semibold text-white bg-forest-700 hover:bg-forest-800 disabled:opacity-50"
            >
              {submitting ? 'Creating...' : 'Create Employee'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default EmployeeDirectoryPage;
