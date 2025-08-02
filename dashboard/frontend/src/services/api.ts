import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

export interface SystemStats {
  total_functions: number
  total_test_pools: number
  total_test_cases: number
  system_status: string
}

export interface FunctionInfo {
  id: string
  name: string
  module: string
  metadata: {
    description?: string
    [key: string]: any
  }
  stats: any
  has_test_pool: boolean
  test_pool_info?: {
    total_cases: number
    description: string
  }
}

export interface TestPool {
  name: string
  description: string
  category: string
  stats: {
    total_cases: number
    [key: string]: any
  }
}

export interface TestCase {
  id: string
  input: string
  expected_output: string
  description: string
}

export interface PoolDetails extends TestPool {
  test_cases: TestCase[]
}

// API functions
export const getStats = async (): Promise<SystemStats> => {
  const response = await api.get('/stats')
  return response.data
}

export const getFunctions = async (): Promise<{ functions: FunctionInfo[]; total: number }> => {
  const response = await api.get('/functions')
  return response.data
}

export const getTestPools = async (): Promise<{ pools: TestPool[]; total: number }> => {
  const response = await api.get('/test-pools')
  return response.data
}

export const getPoolDetails = async (poolName: string): Promise<PoolDetails> => {
  const response = await api.get(`/test-pools/${poolName}`)
  return response.data
}

export const createPool = async (poolData: {
  name: string
  description: string
  category: string
  test_cases: Omit<TestCase, 'id'>[]
}): Promise<{ message: string; pool_name: string }> => {
  const response = await api.post('/test-pools', poolData)
  return response.data
}

export const deletePool = async (poolName: string): Promise<{ message: string; pool_name: string }> => {
  const response = await api.delete(`/test-pools/${poolName}`)
  return response.data
}

export default api