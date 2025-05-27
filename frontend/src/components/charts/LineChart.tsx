import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import { Paper, Typography, Box } from '@mui/material';
import { ChartDataPoint } from '../../types/health';
import { formatDisplayDate, formatNumber } from '../../utils/helpers';

interface LineChartComponentProps {
  data: ChartDataPoint[];
  title: string;
  dataKey: string;
  unit?: string;
  color?: string;
  height?: number;
}

const LineChartComponent: React.FC<LineChartComponentProps> = ({
  data,
  title,
  dataKey,
  unit = '',
  color = '#8884d8',
  height = 300
}) => {
  const formatTooltipValue = (value: any, name: string) => {
    return [`${formatNumber(value, 1)} ${unit}`, name];
  };

  const formatXAxisLabel = (tickItem: string) => {
    return formatDisplayDate(tickItem);
  };

  return (
    <Paper elevation={2} sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>
      <Box sx={{ width: '100%', height }}>
        <ResponsiveContainer>
          <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="date" 
              tick={{ fontSize: 12 }}
              tickFormatter={formatXAxisLabel}
            />
            <YAxis 
              tick={{ fontSize: 12 }}
              tickFormatter={(value) => `${formatNumber(value)} ${unit}`}
            />
            <Tooltip 
              formatter={formatTooltipValue}
              labelFormatter={formatXAxisLabel}
            />
            <Line 
              type="monotone" 
              dataKey={dataKey} 
              stroke={color} 
              strokeWidth={2}
              dot={{ fill: color, strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </Box>
    </Paper>
  );
};

export default LineChartComponent;
