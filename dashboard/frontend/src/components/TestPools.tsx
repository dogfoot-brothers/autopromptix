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
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material'
import {
  Storage as StorageIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  ExpandMore as ExpandMoreIcon,
  Assignment as AssignmentIcon,
} from '@mui/icons-material'
import { getTestPools, getPoolDetails, createPool, deletePool, TestPool, PoolDetails, TestCase } from '../services/api'

const TestPools: React.FC = () => {
  const [pools, setPools] = useState<TestPool[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [selectedPool, setSelectedPool] = useState<PoolDetails | null>(null)
  const [detailsLoading, setDetailsLoading] = useState(false)

  // Form state for creating new pool
  const [newPool, setNewPool] = useState({
    name: '',
    description: '',
    category: 'general',
    test_cases: [] as Omit<TestCase, 'id'>[],
  })

  useEffect(() => {
    fetchPools()
  }, [])

  const fetchPools = async () => {
    try {
      setLoading(true)
      const data = await getTestPools()
      setPools(data.pools)
      setError(null)
    } catch (err) {
      setError('Failed to load test pools')
      console.error('Error fetching pools:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreatePool = async () => {
    try {
      await createPool(newPool)
      setCreateDialogOpen(false)
      setNewPool({
        name: '',
        description: '',
        category: 'general',
        test_cases: [],
      })
      fetchPools()
    } catch (err) {
      console.error('Error creating pool:', err)
    }
  }

  const handleDeletePool = async (poolName: string) => {
    if (window.confirm(`Are you sure you want to delete pool "${poolName}"?`)) {
      try {
        await deletePool(poolName)
        fetchPools()
      } catch (err) {
        console.error('Error deleting pool:', err)
      }
    }
  }

  const handleViewDetails = async (poolName: string) => {
    try {
      setDetailsLoading(true)
      const details = await getPoolDetails(poolName)
      setSelectedPool(details)
    } catch (err) {
      console.error('Error fetching pool details:', err)
    } finally {
      setDetailsLoading(false)
    }
  }

  const addTestCase = () => {
    setNewPool({
      ...newPool,
      test_cases: [
        ...newPool.test_cases,
        { input: '', expected_output: '', description: '' },
      ],
    })
  }

  const updateTestCase = (index: number, field: keyof Omit<TestCase, 'id'>, value: string) => {
    const updatedCases = [...newPool.test_cases]
    updatedCases[index] = { ...updatedCases[index], [field]: value }
    setNewPool({ ...newPool, test_cases: updatedCases })
  }

  const removeTestCase = (index: number) => {
    setNewPool({
      ...newPool,
      test_cases: newPool.test_cases.filter((_, i) => i !== index),
    })
  }

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
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
        <Box display="flex" alignItems="center" gap={2}>
          <StorageIcon sx={{ fontSize: 32, color: 'primary.main' }} />
          <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
            Test Data Pools
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setCreateDialogOpen(true)}
          sx={{ borderRadius: 2 }}
        >
          Create Pool
        </Button>
      </Box>
      
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Manage test data pools for validating your AI functions
      </Typography>

      {pools.length === 0 ? (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <StorageIcon sx={{ fontSize: 80, color: 'text.disabled', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No Test Pools Found
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Create test data pools to validate your AI functions
            </Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setCreateDialogOpen(true)}
            >
              Create Your First Pool
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {pools.map((pool) => (
            <Grid item xs={12} md={6} lg={4} key={pool.name}>
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
                        {pool.name}
                      </Typography>
                      <Chip
                        label={pool.category}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    </Box>
                    <IconButton
                      size="small"
                      onClick={() => handleDeletePool(pool.name)}
                      color="error"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>

                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ mb: 3, minHeight: 40, lineHeight: 1.4 }}
                  >
                    {pool.description || 'No description available'}
                  </Typography>

                  <Box
                    sx={{
                      p: 2,
                      backgroundColor: 'primary.50',
                      borderRadius: 1,
                      border: '1px solid',
                      borderColor: 'primary.200',
                      mb: 2,
                    }}
                  >
                    <Box display="flex" alignItems="center" gap={1}>
                      <AssignmentIcon sx={{ fontSize: 18, color: 'primary.main' }} />
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {pool.stats.total_cases || 0} test cases
                      </Typography>
                    </Box>
                  </Box>

                  <Button
                    variant="outlined"
                    fullWidth
                    onClick={() => handleViewDetails(pool.name)}
                    disabled={detailsLoading}
                  >
                    View Details
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Create Pool Dialog */}
      <Dialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Create New Test Pool</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TextField
              autoFocus
              margin="dense"
              label="Pool Name"
              fullWidth
              variant="outlined"
              value={newPool.name}
              onChange={(e) => setNewPool({ ...newPool, name: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              margin="dense"
              label="Description"
              fullWidth
              multiline
              rows={2}
              variant="outlined"
              value={newPool.description}
              onChange={(e) => setNewPool({ ...newPool, description: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              margin="dense"
              label="Category"
              fullWidth
              variant="outlined"
              value={newPool.category}
              onChange={(e) => setNewPool({ ...newPool, category: e.target.value })}
              sx={{ mb: 3 }}
            />

            <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
              <Typography variant="h6">Test Cases</Typography>
              <Button startIcon={<AddIcon />} onClick={addTestCase}>
                Add Test Case
              </Button>
            </Box>

            {newPool.test_cases.map((testCase, index) => (
              <Accordion key={index} sx={{ mb: 1 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box display="flex" alignItems="center" justifyContent="space-between" width="100%">
                    <Typography>Test Case {index + 1}</Typography>
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation()
                        removeTestCase(index)
                      }}
                      color="error"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <TextField
                      label="Input"
                      multiline
                      rows={2}
                      value={testCase.input}
                      onChange={(e) => updateTestCase(index, 'input', e.target.value)}
                    />
                    <TextField
                      label="Expected Output"
                      multiline
                      rows={2}
                      value={testCase.expected_output}
                      onChange={(e) => updateTestCase(index, 'expected_output', e.target.value)}
                    />
                    <TextField
                      label="Description"
                      value={testCase.description}
                      onChange={(e) => updateTestCase(index, 'description', e.target.value)}
                    />
                  </Box>
                </AccordionDetails>
              </Accordion>
            ))}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleCreatePool} variant="contained">
            Create Pool
          </Button>
        </DialogActions>
      </Dialog>

      {/* Pool Details Dialog */}
      <Dialog
        open={!!selectedPool}
        onClose={() => setSelectedPool(null)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          {selectedPool?.name} - Test Cases
        </DialogTitle>
        <DialogContent>
          {selectedPool && (
            <Box sx={{ pt: 1 }}>
              <Typography variant="body1" color="text.secondary" paragraph>
                {selectedPool.description}
              </Typography>
              
              {selectedPool.test_cases.map((testCase) => (
                <Accordion key={testCase.id} sx={{ mb: 1 }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography>{testCase.description || `Test Case ${testCase.id}`}</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                      <Box>
                        <Typography variant="subtitle2" gutterBottom>Input:</Typography>
                        <Typography variant="body2" sx={{ bgcolor: 'grey.100', p: 1, borderRadius: 1 }}>
                          {testCase.input}
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="subtitle2" gutterBottom>Expected Output:</Typography>
                        <Typography variant="body2" sx={{ bgcolor: 'grey.100', p: 1, borderRadius: 1 }}>
                          {testCase.expected_output}
                        </Typography>
                      </Box>
                    </Box>
                  </AccordionDetails>
                </Accordion>
              ))}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedPool(null)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default TestPools