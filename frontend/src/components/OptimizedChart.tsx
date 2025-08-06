import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

interface ChartData {
  name: string;
  value?: number;
  pallets?: number;
  vehicles?: number;
  color?: string;
}

interface OptimizedChartProps {
  data: ChartData[];
  type: 'bar' | 'pie';
  height?: number;
}

export const OptimizedChart = React.memo<OptimizedChartProps>(({ data, type, height = 300 }) => {
  if (type === 'pie') {
    return (
      <ResponsiveContainer width="100%" height={height}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color || '#8884d8'} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis />
        <Tooltip />
        <Bar dataKey="pallets" fill="#8884d8" />
        <Bar dataKey="vehicles" fill="#82ca9d" />
      </BarChart>
    </ResponsiveContainer>
  );
});

OptimizedChart.displayName = 'OptimizedChart';
