'use client';

import { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function HealthMetrics({ wearableData, ehrData, onSync }) {
  const [timeRange, setTimeRange] = useState('7days');
  const [selectedMetric, setSelectedMetric] = useState('heartRate');

  const metrics = [
    { id: 'heartRate', label: 'Heart Rate', icon: '❤️', unit: 'bpm', color: '#e53e3e' },
    { id: 'steps', label: 'Steps', icon: '👟', unit: 'steps', color: '#3182ce' },
    { id: 'sleep', label: 'Sleep', icon: '😴', unit: 'hours', color: '#805ad5' },
    { id: 'activity', label: 'Activity', icon: '🏃', unit: 'minutes', color: '#38a169' },
    { id: 'weight', label: 'Weight', icon: '⚖️', unit: 'lbs', color: '#dd6b20' },
    { id: 'bloodPressure', label: 'Blood Pressure', icon: '🩸', unit: 'mmHg', color: '#c53030' }
  ];

  const timeRanges = [
    { id: '7days', label: '7 Days' },
    { id: '30days', label: '30 Days' },
    { id: '90days', label: '90 Days' },
    { id: '1year', label: '1 Year' }
  ];

  // Generate sample data - in production, this would come from API
  const generateChartData = () => {
    const days = timeRange === '7days' ? 7 : timeRange === '30days' ? 30 : timeRange === '90days' ? 90 : 365;
    const data = [];
    
    for (let i = days - 1; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      
      data.push({
        date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        heartRate: Math.floor(Math.random() * 20) + 70,
        steps: Math.floor(Math.random() * 5000) + 5000,
        sleep: Math.random() * 2 + 6.5,
        activity: Math.floor(Math.random() * 40) + 20,
        weight: Math.random() * 5 + 165,
        systolic: Math.floor(Math.random() * 20) + 110,
        diastolic: Math.floor(Math.random() * 10) + 70
      });
    }
    
    return data;
  };

  const chartData = generateChartData();
  const currentMetric = metrics.find(m => m.id === selectedMetric);

  // Calculate statistics
  const getStats = () => {
    if (chartData.length === 0) return { avg: 0, min: 0, max: 0, trend: 'stable' };
    
    const values = chartData.map(d => d[selectedMetric]);
    const avg = values.reduce((a, b) => a + b, 0) / values.length;
    const min = Math.min(...values);
    const max = Math.max(...values);
    
    // Simple trend calculation
    const firstHalf = values.slice(0, Math.floor(values.length / 2));
    const secondHalf = values.slice(Math.floor(values.length / 2));
    const firstAvg = firstHalf.reduce((a, b) => a + b, 0) / firstHalf.length;
    const secondAvg = secondHalf.reduce((a, b) => a + b, 0) / secondHalf.length;
    const trend = secondAvg > firstAvg * 1.05 ? 'up' : secondAvg < firstAvg * 0.95 ? 'down' : 'stable';
    
    return { avg: avg.toFixed(1), min: min.toFixed(1), max: max.toFixed(1), trend };
  };

  const stats = getStats();

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h2 style={{ margin: 0, color: '#2d3748', fontSize: '1.75rem' }}>
            📊 Health Metrics
          </h2>
          <p style={{ margin: '0.5rem 0 0 0', color: '#718096' }}>
            Track your health data over time
          </p>
        </div>
        <button
          onClick={onSync}
          style={{
            padding: '0.5rem 1rem',
            background: '#667eea',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}
        >
          🔄 Sync Data
        </button>
      </div>

      {/* Metric Selection */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
        gap: '0.75rem',
        marginBottom: '1.5rem'
      }}>
        {metrics.map(metric => (
          <button
            key={metric.id}
            onClick={() => setSelectedMetric(metric.id)}
            style={{
              padding: '1rem',
              background: selectedMetric === metric.id ? metric.color : 'white',
              color: selectedMetric === metric.id ? 'white' : '#4a5568',
              border: selectedMetric === metric.id ? 'none' : '2px solid #e2e8f0',
              borderRadius: '8px',
              cursor: 'pointer',
              transition: 'all 0.2s',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '0.25rem'
            }}
          >
            <span style={{ fontSize: '1.5rem' }}>{metric.icon}</span>
            <span style={{ fontSize: '0.875rem', fontWeight: '600' }}>{metric.label}</span>
          </button>
        ))}
      </div>

      {/* Time Range Selection */}
      <div style={{
        display: 'flex',
        gap: '0.5rem',
        marginBottom: '1.5rem',
        justifyContent: 'center'
      }}>
        {timeRanges.map(range => (
          <button
            key={range.id}
            onClick={() => setTimeRange(range.id)}
            style={{
              padding: '0.5rem 1rem',
              background: timeRange === range.id ? '#667eea' : 'white',
              color: timeRange === range.id ? 'white' : '#4a5568',
              border: timeRange === range.id ? 'none' : '2px solid #e2e8f0',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: '600'
            }}
          >
            {range.label}
          </button>
        ))}
      </div>

      {/* Statistics Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '1rem',
        marginBottom: '1.5rem'
      }}>
        <StatCard
          label="Average"
          value={`${stats.avg} ${currentMetric?.unit}`}
          color={currentMetric?.color}
        />
        <StatCard
          label="Minimum"
          value={`${stats.min} ${currentMetric?.unit}`}
          color="#90cdf4"
        />
        <StatCard
          label="Maximum"
          value={`${stats.max} ${currentMetric?.unit}`}
          color="#fc8181"
        />
        <StatCard
          label="Trend"
          value={stats.trend === 'up' ? '↗ Increasing' : stats.trend === 'down' ? '↘ Decreasing' : '→ Stable'}
          color={stats.trend === 'up' ? '#48bb78' : stats.trend === 'down' ? '#f56565' : '#a0aec0'}
        />
      </div>

      {/* Chart */}
      <div style={{
        border: '2px solid #e2e8f0',
        borderRadius: '12px',
        padding: '1.5rem',
        background: 'white'
      }}>
        <h3 style={{ margin: '0 0 1rem 0', color: '#2d3748' }}>
          {currentMetric?.icon} {currentMetric?.label} Trend
        </h3>
        <ResponsiveContainer width="100%" height={400}>
          {selectedMetric === 'steps' || selectedMetric === 'activity' ? (
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Bar dataKey={selectedMetric} fill={currentMetric?.color} />
            </BarChart>
          ) : selectedMetric === 'bloodPressure' ? (
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="systolic" stroke="#e53e3e" strokeWidth={2} name="Systolic" />
              <Line type="monotone" dataKey="diastolic" stroke="#3182ce" strokeWidth={2} name="Diastolic" />
            </LineChart>
          ) : (
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey={selectedMetric} stroke={currentMetric?.color} strokeWidth={2} />
            </LineChart>
          )}
        </ResponsiveContainer>
      </div>

      {/* Health Insights */}
      <div style={{
        marginTop: '1.5rem',
        padding: '1.5rem',
        background: '#f7fafc',
        borderRadius: '8px',
        border: '2px solid #e2e8f0'
      }}>
        <h4 style={{ margin: '0 0 0.75rem 0', color: '#2d3748' }}>
          💡 Insights
        </h4>
        <ul style={{ margin: 0, paddingLeft: '1.5rem', color: '#4a5568', lineHeight: '1.8' }}>
          {selectedMetric === 'heartRate' && (
            <>
              <li>Your average resting heart rate is within normal range (60-100 bpm)</li>
              <li>Consider tracking morning resting heart rate for best baseline</li>
            </>
          )}
          {selectedMetric === 'steps' && (
            <>
              <li>You're averaging {stats.avg} steps per day</li>
              <li>Aim for 10,000 steps daily for optimal health benefits</li>
            </>
          )}
          {selectedMetric === 'sleep' && (
            <>
              <li>Adults need 7-9 hours of sleep per night</li>
              <li>Consistent sleep schedule improves sleep quality</li>
            </>
          )}
          {selectedMetric === 'activity' && (
            <>
              <li>150 minutes of moderate activity per week is recommended</li>
              <li>You're on track with {(stats.avg * 7).toFixed(0)} minutes weekly</li>
            </>
          )}
        </ul>
      </div>
    </div>
  );
}

function StatCard({ label, value, color }) {
  return (
    <div style={{
      padding: '1.5rem',
      background: 'white',
      border: '2px solid #e2e8f0',
      borderRadius: '8px'
    }}>
      <div style={{ fontSize: '0.875rem', color: '#718096', marginBottom: '0.5rem' }}>
        {label}
      </div>
      <div style={{ fontSize: '1.5rem', fontWeight: '700', color: color || '#2d3748' }}>
        {value}
      </div>
    </div>
  );
}
