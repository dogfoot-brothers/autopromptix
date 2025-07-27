import React from 'react'
import styled from '@emotion/styled'
import { Play, Database, Loader } from 'lucide-react'

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`

const FunctionItem = styled.div`
  border: 1px solid #e8eaed;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.2s ease;
  position: relative;
  cursor: pointer;

  &:hover {
    border-color: #1a73e8;
    box-shadow: 0 4px 12px rgba(26, 115, 232, 0.15);
    transform: translateY(-2px);
  }
`

const FunctionName = styled.div`
  font-weight: 500;
  color: #202124;
  margin-bottom: 8px;
  font-size: 16px;
`

const FunctionMeta = styled.div`
  font-size: 12px;
  color: #5f6368;
  margin-bottom: 12px;
`

const FunctionStats = styled.div`
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  flex-wrap: wrap;
`

const StatBadge = styled.div`
  background: #f1f3f4;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 12px;
  color: #5f6368;
  font-weight: 500;
`

const TestPoolBadge = styled.div`
  background: #e8f0fe;
  color: #1a73e8;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
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
  text-decoration: none;
  
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

const FunctionsTab = ({ functions, loading }) => {
  if (loading) {
    return (
      <LoadingContainer>
        <Loader className="animate-spin" size={24} />
        Loading functions...
      </LoadingContainer>
    )
  }

  if (functions.length === 0) {
    return (
      <EmptyState>
        <EmptyIcon>📝</EmptyIcon>
        <EmptyTitle>No Functions Found</EmptyTitle>
        <EmptyDescription>
          Add @autopromptix decorators to your functions to see them here.
        </EmptyDescription>
      </EmptyState>
    )
  }

  const handleRunTest = (funcId) => {
    // TODO: Implement test running functionality
    console.log('Running test for function:', funcId)
    alert(`Test running for ${funcId} - Feature coming soon!`)
  }

  const handleViewTestPool = (funcName) => {
    // TODO: Implement test pool viewing functionality
    console.log('Viewing test pool for function:', funcName)
    alert(`Viewing test pool for ${funcName} - Feature coming soon!`)
  }

  return (
    <Container>
      {functions.map((func) => (
        <FunctionItem key={func.id}>
          <FunctionName>{func.name}()</FunctionName>
          <FunctionMeta>{func.module}</FunctionMeta>
          <FunctionStats>
            <StatBadge>Role: {func.metadata.role}</StatBadge>
            <StatBadge>Temp: {func.metadata.temperature}</StatBadge>
            <StatBadge>Max: {func.metadata.max_tokens}</StatBadge>
            {func.has_test_pool && (
              <TestPoolBadge>
                📦 Test Pool: {func.test_pool_info.total_cases} cases
              </TestPoolBadge>
            )}
          </FunctionStats>
          <ActionButtons>
            <Button className="primary" onClick={() => handleRunTest(func.id)}>
              <Play size={16} />
              Test
            </Button>
            {func.has_test_pool && (
              <Button className="warning" onClick={() => handleViewTestPool(func.name)}>
                <Database size={16} />
                View Pool
              </Button>
            )}
          </ActionButtons>
        </FunctionItem>
      ))}
    </Container>
  )
}

export default FunctionsTab 