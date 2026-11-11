import React from 'react';
import { AlertCircle, CheckCircle2, Info, AlertTriangle, X } from 'lucide-react';

export const Alert = ({ type = 'info', message, details, onClose, className = '' }) => {
  if (!message) return null;

  const config = {
    info: {
      bg: 'bg-blue-50 border-blue-200 text-blue-800',
      icon: <Info className="w-5 h-5 text-blue-600 flex-shrink-0" />,
    },
    success: {
      bg: 'bg-emerald-50 border-emerald-200 text-emerald-800',
      icon: <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />,
    },
    warning: {
      bg: 'bg-amber-50 border-amber-200 text-amber-800',
      icon: <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0" />,
    },
    error: {
      bg: 'bg-rose-50 border-rose-200 text-rose-800',
      icon: <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0" />,
    },
  }[type] || {
    bg: 'bg-gray-50 border-gray-200 text-gray-800',
    icon: <Info className="w-5 h-5 text-gray-600 flex-shrink-0" />,
  };

  return (
    <div className={`p-4 rounded-xl border flex items-start justify-between shadow-sm ${config.bg} ${className}`}>
      <div className="flex items-start space-x-3">
        {config.icon}
        <div className="text-sm">
          <p className="font-semibold leading-5">{message}</p>
          {details && <p className="mt-1 text-xs opacity-90">{details}</p>}
        </div>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 ml-3 -mr-1 -mt-1 p-1 rounded-md transition"
        >
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  );
};

export default Alert;
