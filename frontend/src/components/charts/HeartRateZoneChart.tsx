import React from 'react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend
} from 'recharts';
import { Paper, Typography, Box } from '@mui/material';
import { HeartRateZoneData } from '../../types/health';

interface HeartRateZoneChartProps {
  data: HeartRateZoneData[];
  title: string;
  height?: number;
}

const HeartRateZoneChart: React.FC<HeartRateZoneChartProps> = ({
  data,
  title,
  height = 300
}) => {
  const formatTooltipValue = (value: number, name: string) => {
    return [`${value.toFixed(1)}%`, name];
  };

  const renderCustomizedLabel = (entry: any) => {
    return `${entry.percentage.toFixed(1)}%`;
  };

  return (
    <Paper elevation={2} sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>
      <Box sx={{ width: '100%', height }}>
        <ResponsiveContainer>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={renderCustomizedLabel}
              outerRadius={80}
              fill="#8884d8"
              dataKey="percentage"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip formatter={formatTooltipValue} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </Box>
    </Paper>
  );
};

export default HeartRateZoneChart;
