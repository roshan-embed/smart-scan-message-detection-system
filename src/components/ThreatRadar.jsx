import React from 'react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip } from 'recharts';

const ThreatRadar = ({ factors }) => {
  if (!factors) return null;

  const data = [
    { subject: 'Urgency', A: factors.urgency || 0, fullMark: 100 },
    { subject: 'Financial', A: factors.financial || 0, fullMark: 100 },
    { subject: 'Credential', A: factors.credential || 0, fullMark: 100 },
    { subject: 'Impersonation', A: factors.impersonation || 0, fullMark: 100 },
    { subject: 'URL Risk', A: factors.url_risk || 0, fullMark: 100 },
  ];

  return (
    <div className="w-full h-[300px] bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 flex items-center justify-center p-4">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="70%" data={data}>
          <PolarGrid stroke="#e5e7eb" className="dark:stroke-gray-600" />
          <PolarAngleAxis dataKey="subject" tick={{ fill: '#6b7280', fontSize: 12 }} />
          <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
          <Tooltip 
            contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px', color: '#fff' }}
            itemStyle={{ color: '#60a5fa' }}
          />
          <Radar
            name="Risk Level"
            dataKey="A"
            stroke="#ef4444"
            fill="#ef4444"
            fillOpacity={0.4}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ThreatRadar;
