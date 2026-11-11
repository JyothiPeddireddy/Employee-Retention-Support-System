import React from 'react';

export const StatCard = ({ title, value, subtitle, icon: Icon, color = 'emerald', badge, onClick }) => {
  const colorStyles = {
    emerald: 'bg-emerald-50 text-emerald-700 border-emerald-100',
    forest: 'bg-forest-50 text-forest-700 border-forest-100',
    amber: 'bg-amber-50 text-amber-700 border-amber-100',
    rose: 'bg-rose-50 text-rose-700 border-rose-100',
    blue: 'bg-blue-50 text-blue-700 border-blue-100',
    purple: 'bg-purple-50 text-purple-700 border-purple-100',
  }[color] || 'bg-gray-50 text-gray-700 border-gray-100';

  return (
    <div
      onClick={onClick}
      className={`bg-white rounded-xl border border-gray-200 p-5 shadow-sm transition hover:shadow-md ${
        onClick ? 'cursor-pointer hover:border-forest-500' : ''
      }`}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-gray-500">{title}</span>
        {Icon && (
          <div className={`p-2 rounded-lg border ${colorStyles}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>

      <div className="mt-3 flex items-baseline justify-between">
        <span className="text-2xl font-bold tracking-tight text-gray-900">{value}</span>
        {badge && (
          <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-gray-100 text-gray-700 border border-gray-200">
            {badge}
          </span>
        )}
      </div>

      {subtitle && <p className="mt-1 text-xs text-gray-500 font-medium">{subtitle}</p>}
    </div>
  );
};

export default StatCard;
