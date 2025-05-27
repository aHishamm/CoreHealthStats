import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Avatar,
  Chip
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Remove
} from '@mui/icons-material';

interface StatsCardProps {
  title: string;
  value: string | number;
  unit?: string;
  change?: number;
  changeType?: 'increase' | 'decrease' | 'neutral';
  icon?: React.ReactNode;
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error';
}

const StatsCard: React.FC<StatsCardProps> = ({
  title,
  value,
  unit = '',
  change,
  changeType = 'neutral',
  icon,
  color = 'primary'
}) => {
  const getTrendIcon = () => {
    switch (changeType) {
      case 'increase':
        return <TrendingUp fontSize="small" />;
      case 'decrease':
        return <TrendingDown fontSize="small" />;
      default:
        return <Remove fontSize="small" />;
    }
  };

  const getTrendColor = () => {
    switch (changeType) {
      case 'increase':
        return 'success';
      case 'decrease':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Card elevation={2} sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Typography variant="h6" component="div" color="text.secondary">
            {title}
          </Typography>
          {icon && (
            <Avatar sx={{ bgcolor: `${color}.light`, width: 40, height: 40 }}>
              {icon}
            </Avatar>
          )}
        </Box>
        
        <Box display="flex" alignItems="baseline" mb={1}>
          <Typography variant="h4" component="div" fontWeight="bold">
            {typeof value === 'number' ? value.toLocaleString() : value}
          </Typography>
          {unit && (
            <Typography variant="body1" color="text.secondary" ml={1}>
              {unit}
            </Typography>
          )}
        </Box>
        
        {change !== undefined && (
          <Chip
            icon={getTrendIcon()}
            label={`${Math.abs(change).toFixed(1)}%`}
            color={getTrendColor()}
            variant="outlined"
            size="small"
          />
        )}
      </CardContent>
    </Card>
  );
};

export default StatsCard;
