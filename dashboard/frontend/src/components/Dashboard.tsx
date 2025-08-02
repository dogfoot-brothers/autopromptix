import React, { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  CircularProgress,
  Alert,
} from '@mui/material'
import {
  Functions as FunctionsIcon,
  Storage as StorageIcon,
  Assignment as TestCasesIcon,
  CheckCircle as StatusIcon,
  CheckCircle,
} from '@mui/icons-material'
import { getStats, SystemStats } from '../services/api'

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<SystemStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true)
        const data = await getStats()
        setStats(data)
        setError(null)
      } catch (err) {
        setError('Failed to load statistics')
        console.error('Error fetching stats:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  const statCards = [
    {
      title: 'Functions',
      value: stats?.total_functions || 0,
      icon: <FunctionsIcon sx={{ fontSize: 40, color: 'primary.main' }} />,
      color: '#1976d2',
    },
    {
      title: 'Test Pools',
      value: stats?.total_test_pools || 0,
      icon: <StorageIcon sx={{ fontSize: 40, color: 'success.main' }} />,
      color: '#2e7d32',
    },
    {
      title: 'Test Cases',
      value: stats?.total_test_cases || 0,
      icon: <TestCasesIcon sx={{ fontSize: 40, color: 'warning.main' }} />,
      color: '#ed6c02',
    },
    {
      title: 'System Status',
      value: stats?.system_status || 'Unknown',
      icon: <StatusIcon sx={{ fontSize: 40, color: 'success.main' }} />,
      color: '#2e7d32',
      isStatus: true,
    },
  ]

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={60} />
      </Box>
    )
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    )
  }

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
        Dashboard
      </Typography>
      
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Welcome to AutoPromptix - AI Function Testing and Improvement Framework
      </Typography>

      <Grid container spacing={3}>
        {statCards.map((card) => (
          <Grid item xs={12} sm={6} md={3} key={card.title}>
            <Card
              sx={{
                height: '100%',
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
                },
              }}
            >
              <CardContent sx={{ p: 3 }}>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="text.secondary" gutterBottom variant="h6">
                      {card.title}
                    </Typography>
                    <Typography variant="h4" component="div" sx={{ fontWeight: 700, color: card.color }}>
                      {card.isStatus ? (
                        <Box display="flex" alignItems="center" gap={1}>
                          <CheckCircle sx={{ color: 'success.main' }} />
                          <Typography variant="h6" sx={{ textTransform: 'capitalize' }}>
                            {card.value}
                          </Typography>
                        </Box>
                      ) : (
                        card.value
                      )}
                    </Typography>
                  </Box>
                  <Box sx={{ opacity: 0.8 }}>
                    {card.icon}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Box mt={4}>
        <Card>
          <CardContent sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
              🚀 Getting Started
            </Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
              AutoPromptix helps you test and improve AI functions through automated testing and prompt optimization.
            </Typography>
            <Box component="ul" sx={{ mt: 2, pl: 2 }}>
              <Typography component="li" variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                <strong>Functions:</strong> View and manage your registered AI functions
              </Typography>
              <Typography component="li" variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                <strong>Test Pools:</strong> Create and manage test data pools for your functions
              </Typography>
              <Typography component="li" variant="body2" color="text.secondary">
                <strong>Testing:</strong> Run automated tests to validate function performance
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Box>
  )
}

export default Dashboard