import React, { useState } from 'react'
import styled from '@emotion/styled'
import { Plus, RefreshCw, Info, Sparkles } from 'lucide-react'
import CreateTestPoolModal from './CreateTestPoolModal'

const Container = styled.div`
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

const ActionButtons = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`

const Button = styled.button`
  padding: 12px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
  
  &.primary {
    background: #1a73e8;
    color: #fff;

    &:hover {
      background: #1557b0;
      transform: translateY(-1px);
      box-shadow: 0 2px 8px rgba(26, 115, 232, 0.3);
    }
  }

  &.secondary {
    background: #f1f3f4;
    color: #5f6368;

    &:hover {
      background: #e8eaed;
      transform: translateY(-1px);
    }
  }
`

const SystemInfoSection = styled.div`
  margin-top: 24px;
`

const SystemInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`

const StatBadge = styled.div`
  background: #f1f3f4;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 12px;
  color: #5f6368;
  font-weight: 500;
  text-align: center;
`

const Sidebar = ({ onRefresh, onCreateTestPool }) => {
  const [showCreateModal, setShowCreateModal] = useState(false)

  const handleCreateTestPool = () => {
    setShowCreateModal(true)
  }

  const handleCloseCreateModal = () => {
    setShowCreateModal(false)
  }

  const handleCreatePoolSubmit = async (poolData) => {
    const result = await onCreateTestPool(poolData)
    if (result.success) {
      setShowCreateModal(false)
      alert('Test data pool created successfully!')
    } else {
      alert(`Failed to create pool: ${result.error}`)
    }
    return result
  }

  return (
    <Container>
      <SectionTitle>
        <Sparkles size={20} />
        Quick Actions
      </SectionTitle>
      
      <ActionButtons>
        <Button className="primary" onClick={handleCreateTestPool}>
          <Plus size={16} />
          Create Test Pool
        </Button>
        <Button className="secondary" onClick={onRefresh}>
          <RefreshCw size={16} />
          Refresh Data
        </Button>
      </ActionButtons>
      
      <SystemInfoSection>
        <SectionTitle>
          <Info size={20} />
          System Info
        </SectionTitle>
        <SystemInfo>
          <StatBadge>Server: Running</StatBadge>
          <StatBadge>Port: 8001</StatBadge>
          <StatBadge>Version: 1.0</StatBadge>
        </SystemInfo>
      </SystemInfoSection>

      {showCreateModal && (
        <CreateTestPoolModal
          onClose={handleCloseCreateModal}
          onSubmit={handleCreatePoolSubmit}
        />
      )}
    </Container>
  )
}

export default Sidebar 