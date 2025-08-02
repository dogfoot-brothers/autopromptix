import React, { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  CircularProgress,
  Alert,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material'
import {
  Functions as FunctionsIcon,
  Storage as StorageIcon,
  Info as InfoIcon,
} from '@mui/icons-material'
import { getFunctions, FunctionInfo } from '../services/api'

const Functions: React.FC = () => {
  const [functions, setFunctions] = useState<FunctionInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchFunctions = async () => {
      try {
        setLoading(true)
        const data = await getFunctions()
        setFunctions(data.functions)
        setError(null)
      } catch (err) {
        setError('Failed to load functions')
        console.error('Error fetching functions:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchFunctions()
  }, [])

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
      <Box display="flex" alignItems="center" gap={2} mb={3}>
        <FunctionsIcon sx={{ fontSize: 32, color: 'primary.main' }} />
        <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
          Registered Functions
        </Typography>
      </Box>
      
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        View and manage your AI functions registered with AutoPromptix
      </Typography>

      {functions.length === 0 ? (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <FunctionsIcon sx={{ fontSize: 80, color: 'text.disabled', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No Functions Registered
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Register functions using the @autopromptix.test decorator to see them here
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {functions.map((func) => (
            <Grid item xs={12} md={6} lg={4} key={func.id}>
              <Card
                sx={{
                  height: '100%',
                  transition: 'transform 0.2s, box-shadow 0.2s',
                  '&:hover': {
                    transform: 'translateY(-2px)',
                    boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
                  },
                }}
              >
                <CardContent sx={{ p: 3 }}>
                  <Box display="flex" alignItems="flex-start" justifyContent="space-between" mb={2}>
                    <Box flex={1}>
                      <Typography variant="h6" sx={{ fontWeight: 600, mb: 0.5 }}>
                        {func.name}
                      </Typography>
                      <Typography variant="body2" color="primary.main" sx={{ fontWeight: 500 }}>
                        {func.module}
                      </Typography>
                    </Box>
                    <Tooltip title="Function Information">
                      <IconButton size="small">
                        <InfoIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>

                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ mb: 3, minHeight: 40, lineHeight: 1.4 }}
                  >
                    {func.metadata.description || 'No description available'}
                  </Typography>

                  <Box display="flex" gap={1} mb={2} flexWrap="wrap">
                    <Chip
                      icon={<StorageIcon />}
                      label={func.has_test_pool ? 'Has Test Pool' : 'No Test Pool'}
                      size="small"
                      color={func.has_test_pool ? 'success' : 'default'}
                      variant={func.has_test_pool ? 'filled' : 'outlined'}
                    />
                  </Box>

                  {func.has_test_pool && func.test_pool_info && (
                    <Box
                      sx={{
                        mt: 2,
                        p: 2,
                        backgroundColor: 'success.50',
                        borderRadius: 1,
                        border: '1px solid',
                        borderColor: 'success.200',
                      }}
                    >
                      <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                        Test Pool: {func.test_pool_info.total_cases} cases
                      </Typography>
                      {func.test_pool_info.description && (
                        <Typography variant="body2" color="text.secondary">
                          {func.test_pool_info.description}
                        </Typography>
                      )}
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  )
}

export default Functions