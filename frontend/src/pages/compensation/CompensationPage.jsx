import React, { useState, useEffect } from 'react';
import { compensationApi } from '../../api/compensation';
import { roleApi } from '../../api/roles';
import { useAuth } from '../../context/AuthContext';
import Modal from '../../components/Modal';
import Alert from '../../components/Alert';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';
import { DollarSign, Plus, TrendingUp, Shield, Award } from 'lucide-react';

export const CompensationPage = () => {
  const { role } = useAuth();
  const [bands, setBands] = useState([]);
  const [promotions, setPromotions] = useState([]);
  const [rolesList, setRolesList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  // Create Band Modal
  const [isBandModalOpen, setIsBandModalOpen] = useState(false);
  const [bandForm, setBandForm] = useState({
    band_id: '',
    name: '',
    min_salary: 70000,
    mid_salary: 85000,
    max_salary: 100000,
    currency: 'USD',
  });
  const [submittingBand, setSubmittingBand] = useState(false);

  // Record Promotion Modal
  const [isPromotionModalOpen, setIsPromotionModalOpen] = useState(false);
  const [promotionForm, setPromotionForm] = useState({
    employee_id: '',
    from_role_id: '',
    to_role_id: '',
    from_salary: 80000,
    to_salary: 95000,
    movement_type: 'MERIT_PROMOTION',
    effective_date: new Date().toISOString().split('T')[0],
  });
  const [submittingPromotion, setSubmittingPromotion] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [bandsRes, promsRes, rolesRes] = await Promise.all([
        compensationApi.listBands(),
        compensationApi.listPromotions(),
        roleApi.listRoles(),
      ]);
      setBands(bandsRes || []);
      setPromotions(promsRes || []);
      setRolesList(rolesRes || []);
      if (rolesRes?.length >= 2) {
        setPromotionForm((prev) => ({
          ...prev,
          from_role_id: rolesRes[0].role_id,
          to_role_id: rolesRes[1].role_id,
        }));
      }
    } catch (err) {
      setError(err.message || 'Failed to load compensation data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleBandSubmit = async (e) => {
    e.preventDefault();
    setSubmittingBand(true);
    try {
      await compensationApi.createBand({
        band_id: bandForm.band_id.trim(),
        name: bandForm.name.trim(),
        min_salary: parseFloat(bandForm.min_salary),
        mid_salary: parseFloat(bandForm.mid_salary),
        max_salary: parseFloat(bandForm.max_salary),
        currency: bandForm.currency,
      });
      setSuccessMsg(`Compensation Band '${bandForm.band_id}' created successfully.`);
      setIsBandModalOpen(false);
      setBandForm({
        band_id: '',
        name: '',
        min_salary: 70000,
        mid_salary: 85000,
        max_salary: 100000,
        currency: 'USD',
      });
      fetchData();
    } catch (err) {
      setError(err.message || 'Failed to create compensation band.');
    } finally {
      setSubmittingBand(false);
    }
  };

  const handlePromotionSubmit = async (e) => {
    e.preventDefault();
    setSubmittingPromotion(true);
    try {
      await compensationApi.recordPromotion({
        employee_id: promotionForm.employee_id.trim(),
        from_role_id: promotionForm.from_role_id,
        to_role_id: promotionForm.to_role_id,
        from_salary: parseFloat(promotionForm.from_salary),
        to_salary: parseFloat(promotionForm.to_salary),
        movement_type: promotionForm.movement_type,
        effective_date: promotionForm.effective_date,
      });
      setSuccessMsg(`Promotion recorded for '${promotionForm.employee_id}'.`);
      setIsPromotionModalOpen(false);
      fetchData();
    } catch (err) {
      setError(err.message || 'Failed to record promotion.');
    } finally {
      setSubmittingPromotion(false);
    }
  };

  const canManage = ['HR_PARTNER', 'ADMIN', 'SYSTEM_ADMIN'].includes(role);

  return (
    <div className="space-y-8">
      {successMsg && <Alert type="success" message={successMsg} onClose={() => setSuccessMsg(null)} />}
      {error && <Alert type="error" message="Notice" details={error} onClose={() => setError(null)} />}

      {/* Section 1: Standard Compensation Bands */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-base font-bold text-gray-900">Standard Compensation Bands</h2>
            <p className="text-xs text-gray-500">
              Approved pay ranges ensuring internal equity and market competitiveness.
            </p>
          </div>
          {canManage && (
            <button
              onClick={() => setIsBandModalOpen(true)}
              className="inline-flex items-center px-3.5 py-2 rounded-xl text-xs font-semibold text-white bg-forest-700 hover:bg-forest-800 transition shadow-xs"
            >
              <Plus className="w-4 h-4 mr-1.5" />
              Add Compensation Band
            </button>
          )}
        </div>

        {loading ? (
          <LoadingSpinner size="md" message="Loading compensation bands..." />
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {bands.map((band) => (
              <div
                key={band.band_id}
                className="bg-white rounded-2xl border border-gray-200 p-5 shadow-xs transition hover:shadow-md"
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-forest-700 bg-forest-50 px-2 py-0.5 rounded-md border border-forest-100">
                    {band.band_id}
                  </span>
                  <span className="text-xs font-semibold text-gray-500">{band.currency}</span>
                </div>
                <h3 className="text-sm font-bold text-gray-900 mt-2">{band.name}</h3>

                <div className="mt-4 pt-3 border-t border-gray-100 space-y-1.5 text-xs">
                  <div className="flex justify-between text-gray-500">
                    <span>Minimum:</span>
                    <strong className="text-gray-900">${band.min_salary.toLocaleString()}</strong>
                  </div>
                  <div className="flex justify-between text-forest-700 font-semibold">
                    <span>Midpoint (Target):</span>
                    <strong>${band.mid_salary.toLocaleString()}</strong>
                  </div>
                  <div className="flex justify-between text-gray-500">
                    <span>Maximum:</span>
                    <strong className="text-gray-900">${band.max_salary.toLocaleString()}</strong>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Section 2: Promotions & Career Progression */}
      <div className="space-y-4 pt-6 border-t border-gray-200">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-base font-bold text-gray-900">Career Promotions & Vertical Movement</h2>
            <p className="text-xs text-gray-500">
              Verified career advancement records preventing career stagnation attribution.
            </p>
          </div>
          {canManage && (
            <button
              onClick={() => setIsPromotionModalOpen(true)}
              className="inline-flex items-center px-3.5 py-2 rounded-xl text-xs font-semibold text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 transition shadow-xs"
            >
              <Award className="w-4 h-4 mr-1.5 text-forest-700" />
              Record Promotion
            </button>
          )}
        </div>

        <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-xs">
          {promotions.length === 0 ? (
            <div className="p-8 text-center text-xs text-gray-400">
              No promotions recorded in the observation period.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-gray-50/75 border-b border-gray-200 text-gray-500 uppercase font-semibold">
                    <th className="py-3 px-4">Promotion ID</th>
                    <th className="py-3 px-4">Employee ID</th>
                    <th className="py-3 px-4">Role Transition</th>
                    <th className="py-3 px-4">Movement Type</th>
                    <th className="py-3 px-4">Salary Change</th>
                    <th className="py-3 px-4">Effective Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {promotions.map((p) => (
                    <tr key={p.promotion_id} className="hover:bg-gray-50/80 transition">
                      <td className="py-3.5 px-4 font-mono font-medium text-gray-600">{p.promotion_id}</td>
                      <td className="py-3.5 px-4 font-mono font-bold text-gray-900">{p.employee_id}</td>
                      <td className="py-3.5 px-4 font-semibold text-gray-800">
                        {p.from_role_id} → {p.to_role_id}
                      </td>
                      <td className="py-3.5 px-4">
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                          {p.movement_type}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-gray-900 font-semibold">
                        ${p.from_salary.toLocaleString()} → ${p.to_salary.toLocaleString()}
                      </td>
                      <td className="py-3.5 px-4 text-gray-500 font-mono">{p.effective_date}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Add Band Modal */}
      <Modal isOpen={isBandModalOpen} onClose={() => setIsBandModalOpen(false)} title="Add Compensation Band">
        <form onSubmit={handleBandSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                Band Code
              </label>
              <input
                type="text"
                required
                value={bandForm.band_id}
                onChange={(e) => setBandForm({ ...bandForm, band_id: e.target.value })}
                placeholder="e.g. BAND-IC5"
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600 font-mono"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                Band Name
              </label>
              <input
                type="text"
                required
                value={bandForm.name}
                onChange={(e) => setBandForm({ ...bandForm, name: e.target.value })}
                placeholder="e.g. Principal / Lead"
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                Minimum ($)
              </label>
              <input
                type="number"
                required
                step={1000}
                value={bandForm.min_salary}
                onChange={(e) => setBandForm({ ...bandForm, min_salary: e.target.value })}
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                Midpoint ($)
              </label>
              <input
                type="number"
                required
                step={1000}
                value={bandForm.mid_salary}
                onChange={(e) => setBandForm({ ...bandForm, mid_salary: e.target.value })}
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                Maximum ($)
              </label>
              <input
                type="number"
                required
                step={1000}
                value={bandForm.max_salary}
                onChange={(e) => setBandForm({ ...bandForm, max_salary: e.target.value })}
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
              />
            </div>
          </div>

          <div className="flex justify-end space-x-3 pt-3 border-t border-gray-100">
            <button
              type="button"
              onClick={() => setIsBandModalOpen(false)}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-gray-700 hover:bg-gray-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submittingBand}
              className="px-5 py-2 rounded-xl text-xs font-semibold text-white bg-forest-700 hover:bg-forest-800 disabled:opacity-50"
            >
              {submittingBand ? 'Saving...' : 'Create Band'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Record Promotion Modal */}
      <Modal isOpen={isPromotionModalOpen} onClose={() => setIsPromotionModalOpen(false)} title="Record Promotion">
        <form onSubmit={handlePromotionSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
              Employee ID
            </label>
            <input
              type="text"
              required
              value={promotionForm.employee_id}
              onChange={(e) => setPromotionForm({ ...promotionForm, employee_id: e.target.value })}
              placeholder="e.g. EMP-000001"
              className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600 font-mono"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                From Role
              </label>
              <select
                value={promotionForm.from_role_id}
                onChange={(e) => setPromotionForm({ ...promotionForm, from_role_id: e.target.value })}
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600 bg-white"
              >
                {rolesList.map((r) => (
                  <option key={r.role_id} value={r.role_id}>
                    {r.title} ({r.role_id})
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                To Role (Promoted)
              </label>
              <select
                value={promotionForm.to_role_id}
                onChange={(e) => setPromotionForm({ ...promotionForm, to_role_id: e.target.value })}
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600 bg-white"
              >
                {rolesList.map((r) => (
                  <option key={r.role_id} value={r.role_id}>
                    {r.title} ({r.role_id})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                Previous Salary ($)
              </label>
              <input
                type="number"
                required
                step={1000}
                value={promotionForm.from_salary}
                onChange={(e) => setPromotionForm({ ...promotionForm, from_salary: e.target.value })}
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                New Base Salary ($)
              </label>
              <input
                type="number"
                required
                step={1000}
                value={promotionForm.to_salary}
                onChange={(e) => setPromotionForm({ ...promotionForm, to_salary: e.target.value })}
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                Movement Type
              </label>
              <select
                value={promotionForm.movement_type}
                onChange={(e) => setPromotionForm({ ...promotionForm, movement_type: e.target.value })}
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600 bg-white"
              >
                <option value="MERIT_PROMOTION">Merit Promotion</option>
                <option value="LATERAL_MOVE">Lateral Move</option>
                <option value="BAND_ADJUSTMENT">Market Band Adjustment</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700">
                Effective Date
              </label>
              <input
                type="date"
                required
                value={promotionForm.effective_date}
                onChange={(e) => setPromotionForm({ ...promotionForm, effective_date: e.target.value })}
                className="mt-1 block w-full px-3.5 py-2 text-sm rounded-xl border border-gray-300 focus:ring-2 focus:ring-forest-600"
              />
            </div>
          </div>

          <div className="flex justify-end space-x-3 pt-3 border-t border-gray-100">
            <button
              type="button"
              onClick={() => setIsPromotionModalOpen(false)}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-gray-700 hover:bg-gray-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submittingPromotion}
              className="px-5 py-2 rounded-xl text-xs font-semibold text-white bg-forest-700 hover:bg-forest-800 disabled:opacity-50"
            >
              {submittingPromotion ? 'Recording...' : 'Record Promotion'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default CompensationPage;
