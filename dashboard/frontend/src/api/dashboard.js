import axios from 'axios'

const API_BASE_URL = '/api'

class DashboardAPIClass {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })
  }

  async getStats() {
    const response = await this.client.get('/stats')
    return response.data
  }

  async getFunctions() {
    const response = await this.client.get('/functions')
    return response.data
  }

  async getTestPools() {
    const response = await this.client.get('/test-pools')
    return response.data
  }

  async getTestPoolDetails(poolName) {
    const response = await this.client.get(`/test-pools/${poolName}`)
    return response.data
  }

  async createTestPool(poolData) {
    const response = await this.client.post('/test-pools', poolData)
    return response.data
  }

  async deleteTestPool(poolName) {
    const response = await this.client.delete(`/test-pools/${poolName}`)
    return response.data
  }
}

export const DashboardAPI = new DashboardAPIClass() 