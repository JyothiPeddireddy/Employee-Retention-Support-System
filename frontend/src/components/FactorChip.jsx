import React, { useState } from 'react';
import { Clock, TrendingUp, HeartHandshake, DollarSign, HelpCircle, Info } from 'lucide-react';

export const FactorChip = ({ factor }) => {
  const [showTooltip, setShowTooltip] = useState(false);

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'WORKLOAD':
        return <Clock className="w-3.5 h-3.5 mr-1" />;
      case 'CAREER_GROWTH':
        return <TrendingUp className="w-3.5 h-3.5 mr-1" />;
      case 'ENGAGEMENT':
        return <HeartHandshake className="w-3.5 h-3.5 mr-1" />;
      case 'COMPENSATION':
        return <DollarSign className="w-3.5 h-3.5 mr-1" />;
      default:
        return <Info className="w-3.5 h-3.5 mr-1" />;
    }
  };

  const getImpactBadge = (level) => {
    switch (level) {
      case 'HIGH':
        return 'bg-amber-100 text-amber-800 border-amber-300';
      case 'MEDIUM':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'LOW':
      default:
        return 'bg-emerald-100 text-emerald-800 border-emerald-300';
    }
  };

  return (
    <div className="relative inline-block m-1">
      <div
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border cursor-pointer transition shadow-xs hover:shadow-sm ${getImpactBadge(
          factor.impact_level
        )}`}
      >
        {getCategoryIcon(factor.category)}
        <span className="font-semibold mr-1">{factor.signal_name}:</span>
        <span className="opacity-90">{factor.raw_value}</span>
        <HelpCircle className="w-3 h-3 ml-1.5 opacity-60 hover:opacity-100" />
      </div>

      {showTooltip && (
        <div className="absolute z-50 bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-72 p-3 bg-gray-900 text-white rounded-lg shadow-xl text-xs pointer-events-none animate-fade-in">
          <div className="font-semibold text-emerald-400 mb-1 flex items-center">
            <span>Supportive Recommendation</span>
          </div>
          <p className="text-gray-200 leading-relaxed">{factor.supportive_guidance}</p>
          <div className="mt-2 pt-1 border-t border-gray-700 flex justify-between text-[10px] text-gray-400">
            <span>Category: {factor.category}</span>
            <span>Signal Weight: {factor.impact_level}</span>
          </div>
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-900" />
        </div>
      )}
    </div>
  );
};

export default FactorChip;
