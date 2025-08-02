import { Routes, Route } from 'react-router-dom'
import { Box } from '@mui/material'
import Layout from './components/Layout'
import Dashboard from './components/Dashboard'
import Functions from './components/Functions'
import TestPools from './components/TestPools'

function App() {
  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/functions" element={<Functions />} />
          <Route path="/test-pools" element={<TestPools />} />
        </Routes>
      </Layout>
    </Box>
  )
}

export default App