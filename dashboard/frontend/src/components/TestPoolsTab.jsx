import React, { useState } from 'react'
import styled from '@emotion/styled'
import { Eye, Trash2, Loader } from 'lucide-react'
import TestPoolModal from './TestPoolModal'

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`

const TestPoolCard = styled.div`
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  transition: all 0.2s ease;
  border: 1px solid #e8eaed;

  &:hover {
    border-color: #1a73e8;
    box-shadow: 0 2px 8px rgba(26, 115, 232, 0.1);
    transform: translateY(-1px);
  }
`

const TestPoolHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
`

const TestPoolTitle = styled.div`
  font-weight: 500;
  color: #202124;
  font-size: 16px;
`

const TestPoolStats = styled.div`
  display: flex;
  gap: 8px;
  font-size: 12px;
  color: #5f6368;
`

const TestPoolStat = styled.div`
  background: #fff;
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid #e8eaed;
`

const TestPoolDescription = styled.div`
  margin-bottom: 12px;
  color: #5f6368;
  font-size: 14px;
`

const ActionButtons = styled.div`
  display: flex;
  gap: 8px;
`

const Button = styled.button`
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 6px;
  
  &.primary {
    background: #1a73e8;
    color: #fff;

    &:hover {
      background: #1557b0;
      transform: translateY(-1px);
      box-shadow: 0 2px 8px rgba(26, 115, 232, 0.3);
    }
  }

  &.warning {
    background: #fbbc04;
    color: #fff;

    &:hover {
      background: #f9ab00;
      transform: translateY(-1px);
      box-shadow: 0 2px 8px rgba(251, 188, 4, 0.3);
    }
  }
`

const EmptyState = styled.div`
  text-align: center;
  padding: 40px 20px;
  color: #5f6368;
`

const EmptyIcon = styled.div`
  font-size: 48px;
  color: #dadce0;
  margin-bottom: 16px;
`

const EmptyTitle = styled.div`
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 8px;
  color: #202124;
`

const EmptyDescription = styled.div`
  font-size: 14px;
  line-height: 1.5;
`

const LoadingContainer = styled.div`
  text-align: center;
  padding: 40px;
  color: #5f6368;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
`

const TestPoolsTab = ({ testPools, loading, onDeletePool }) => {
  const [selectedPool, setSelectedPool] = useState(null)
  const [showModal, setShowModal] = useState(false)

  if (loading) {
    return (
      <LoadingContainer>
        <Loader className="animate-spin" size={24} />
        Loading test data pools...
      </LoadingContainer>
    )
  }

  if (testPools.length === 0) {
    return (
      <EmptyState>
        <EmptyIcon>📦</EmptyIcon>
        <EmptyTitle>No Test Data Pools</EmptyTitle>
        <EmptyDescription>
          Create your first test data pool to get started with comprehensive testing.
        </EmptyDescription>
      </EmptyState>
    )
  }

  const handleViewPool = (poolName) => {
    setSelectedPool(poolName)
    setShowModal(true)
  }

  const handleDeletePool = async (poolName) => {
    if (!confirm(`Are you sure you want to delete the test pool "${poolName}"?`)) {
      return
    }

    const result = await onDeletePool(poolName)
    if (result.success) {
      alert('Test data pool deleted successfully!')
    } else {
      alert(`Failed to delete pool: ${result.error}`)
    }
  }

  const handleCloseModal = () => {
    setShowModal(false)
    setSelectedPool(null)
  }

  return (
    <Container>
      {testPools.map((pool) => (
        <TestPoolCard key={pool.name}>
          <TestPoolHeader>
            <TestPoolTitle>{pool.name}</TestPoolTitle>
            <TestPoolStats>
              <TestPoolStat>{pool.stats.total_cases} total</TestPoolStat>
              <TestPoolStat>{pool.stats.test_cases} test</TestPoolStat>
              <TestPoolStat>{pool.stats.edge_cases} edge</TestPoolStat>
              <TestPoolStat>{pool.stats.negative_cases} negative</TestPoolStat>
            </TestPoolStats>
          </TestPoolHeader>
          <TestPoolDescription>
            {pool.description}
          </TestPoolDescription>
          <ActionButtons>
            <Button className="primary" onClick={() => handleViewPool(pool.name)}>
              <Eye size={16} />
              View Details
            </Button>
            <Button className="warning" onClick={() => handleDeletePool(pool.name)}>
              <Trash2 size={16} />
              Delete
            </Button>
          </ActionButtons>
        </TestPoolCard>
      ))}

      {showModal && (
        <TestPoolModal
          poolName={selectedPool}
          onClose={handleCloseModal}
        />
      )}
    </Container>
  )
}

export default TestPoolsTab 