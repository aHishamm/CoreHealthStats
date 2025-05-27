import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts';
import { Paper, Typography, Box } from '@mui/material';
import { WorkoutChartData } from '../../types/health';
import { formatDisplayDate, formatDuration, getWorkoutTypeColor } from '../../utils/helpers';

interface WorkoutBarChartProps {
  data: WorkoutChartData[];
  title: string;
  dataKey: 'duration' | 'distance' | 'energy' | 'trimp_score';
  unit?: string;
  height?: number;
}

const WorkoutBarChart: React.FC<WorkoutBarChartProps> = ({
  data,
  title,
  dataKey,
  unit = '',
  height = 300
}) => {
  const formatTooltipValue = (value: any, name: string) => {
    if (dataKey === 'duration') {
      return [formatDuration(value), 'Duration'];
    }
    return [`${value?.toFixed(1) || 0} ${unit}`, name];
  };

  const formatYAxisLabel = (value: number) => {
    if (dataKey === 'duration') {
      return formatDuration(value);
    }
    return `${value} ${unit}`;
  };

  return (
    <Paper elevation={2} sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>
      <Box sx={{ width: '100%', height }}>
        <ResponsiveContainer>
          <BarChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="date" 
              tick={{ fontSize: 12 }}
              tickFormatter={formatDisplayDate}
            />
            <YAxis 
              tick={{ fontSize: 12 }}
              tickFormatter={formatYAxisLabel}
            />
            <Tooltip 
              formatter={formatTooltipValue}
              labelFormatter={formatDisplayDate}
            />
            <Bar dataKey={dataKey} radius={[4, 4, 0, 0]}>
              {data.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={getWorkoutTypeColor(entry.activity_type)} 
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </Box>
    </Paper>
  );
};

export default WorkoutBarChart;
