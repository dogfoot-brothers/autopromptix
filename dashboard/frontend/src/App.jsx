import React, { useState, useEffect } from 'react'
import styled from '@emotion/styled'
import { Sparkles } from 'lucide-react'
import StatsGrid from './components/StatsGrid'
import FunctionsTab from './components/FunctionsTab'
import TestPoolsTab from './components/TestPoolsTab'
import Sidebar from './components/Sidebar'
import { DashboardAPI } from './api/dashboard'

const AppBar = styled.div`
  background: #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 0 24px;
  height: 64px;
  display: flex;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 1000;
`

const AppTitle = styled.div`
  font-size: 22px;
  font-weight: 500;
  color: #1a73e8;
  display: flex;
  align-items: center;
  gap: 12px;
`

const MainContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
`

const ContentGrid = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`

const MainContent = styled.div`
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.12);
`

const SectionTitle = styled.div`
  font-size: 20px;
  font-weight: 500;
  color: #202124;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
`

const Tabs = styled.div`
  display: flex;
  border-bottom: 1px solid #e8eaed;
  margin-bottom: 20px;
`

const Tab = styled.div`
  padding: 12px 24px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  color: #5f6368;
  font-weight: 500;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;

  &.active {
    color: #1a73e8;
    border-bottom-color: #1a73e8;
  }

  &:hover {
    color: #1a73e8;
  }
`

const TabContent = styled.div`
  display: ${props => props.active ? 'block' : 'none'};
`

function App() {
  const [activeTab, setActiveTab] = useState('functions')
  const [stats, setStats] = useState({ total_functions: 0, total_test_pools: 0, total_test_cases: 0 })
  const [functions, setFunctions] = useState([])
  const [testPools, setTestPools] = useState([])
  const [loading, setLoading] = useState(true)

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      const [statsData, functionsData, poolsData] = await Promise.all([
        DashboardAPI.getStats(),
        DashboardAPI.getFunctions(),
        DashboardAPI.getTestPools()
      ])
      
      setStats(statsData)
      setFunctions(functionsData.functions)
      setTestPools(poolsData.pools)
    } catch (error) {
      console.error('Error loading dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadDashboardData()
    
    // Refresh every 30 seconds
    const interval = setInterval(loadDashboardData, 30000)
    return () => clearInterval(interval)
  }, [])

  const handleRefresh = () => {
    loadDashboardData()
  }

  const handleCreateTestPool = async (poolData) => {
    try {
      await DashboardAPI.createTestPool(poolData)
      loadDashboardData() // Refresh data after creation
      return { success: true }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  const handleDeleteTestPool = async (poolName) => {
    try {
      await DashboardAPI.deleteTestPool(poolName)
      loadDashboardData() // Refresh data after deletion
      return { success: true }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  return (
    <div>
      <AppBar>
        <AppTitle>
          <Sparkles size={24} />
          AutoPromptix Test Data Pool Dashboard
        </AppTitle>
      </AppBar>
      
      <MainContainer>
        <StatsGrid stats={stats} />
        
        <ContentGrid>
          <MainContent>
            <SectionTitle>
              <Sparkles size={20} />
              AutoPromptix Dashboard
            </SectionTitle>
            
            <Tabs>
              <Tab 
                className={activeTab === 'functions' ? 'active' : ''} 
                onClick={() => setActiveTab('functions')}
              >
                Functions
              </Tab>
              <Tab 
                className={activeTab === 'test-pools' ? 'active' : ''} 
                onClick={() => setActiveTab('test-pools')}
              >
                Test Data Pools
              </Tab>
            </Tabs>
            
            <TabContent active={activeTab === 'functions'}>
              <FunctionsTab functions={functions} loading={loading} />
            </TabContent>
            
            <TabContent active={activeTab === 'test-pools'}>
              <TestPoolsTab 
                testPools={testPools} 
                loading={loading}
                onDeletePool={handleDeleteTestPool}
              />
            </TabContent>
          </MainContent>
          
          <Sidebar 
            onRefresh={handleRefresh}
            onCreateTestPool={handleCreateTestPool}
          />
        </ContentGrid>
      </MainContainer>
    </div>
  )
}

export default App 