import React, { useState, useEffect } from 'react'
import styled from '@emotion/styled'
import { X, Loader, FileText } from 'lucide-react'
import { DashboardAPI } from '../api/dashboard'

const Overlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`

const Modal = styled.div`
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  width: 90%;
  max-width: 800px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
`

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
`

const Title = styled.h2`
  font-size: 20px;
  font-weight: 500;
  color: #202124;
  margin: 0;
`

const CloseButton = styled.button`
  background: none;
  border: none;
  color: #5f6368;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.2s;

  &:hover {
    background: #f1f3f4;
    color: #202124;
  }
`

const LoadingContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 40px;
  color: #5f6368;
`

const PoolInfo = styled.div`
  margin-bottom: 24px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
`

const InfoRow = styled.div`
  display: flex;
  gap: 16px;
  margin-bottom: 8px;
  
  &:last-child {
    margin-bottom: 0;
  }
`

const InfoLabel = styled.div`
  font-weight: 500;
  color: #5f6368;
  min-width: 100px;
`

const InfoValue = styled.div`
  color: #202124;
`

const Section = styled.div`
  margin-bottom: 24px;
`

const SectionTitle = styled.h3`
  font-size: 16px;
  font-weight: 500;
  color: #202124;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
`

const TestCasesList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`

const TestCaseCard = styled.div`
  background: #fff;
  border: 1px solid #e8eaed;
  border-radius: 8px;
  padding: 16px;
  border-left: 3px solid ${props => props.borderColor || '#1a73e8'};
`

const TestCaseHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
`

const TestCaseId = styled.div`
  font-weight: 500;
  color: #1a73e8;
  font-size: 14px;
`

const TestCaseTags = styled.div`
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
`

const Tag = styled.span`
  background: #e8f0fe;
  color: #1a73e8;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
`

const TestCaseContent = styled.div`
  font-size: 13px;
  color: #5f6368;
`

const ContentBlock = styled.div`
  background: ${props => props.bgColor || '#f1f3f4'};
  padding: 8px 12px;
  border-radius: 4px;
  margin-bottom: 8px;
  font-family: monospace;
  white-space: pre-wrap;
  word-break: break-word;
  
  &:last-child {
    margin-bottom: 0;
  }
`

const ContentLabel = styled.div`
  font-weight: 600;
  margin-bottom: 4px;
  font-family: 'Roboto', sans-serif;
`

const EmptyState = styled.div`
  text-align: center;
  padding: 20px;
  color: #5f6368;
  font-style: italic;
`

const TestPoolModal = ({ poolName, onClose }) => {
  const [pool, setPool] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const loadPoolDetails = async () => {
      try {
        setLoading(true)
        const poolData = await DashboardAPI.getTestPoolDetails(poolName)
        setPool(poolData)
      } catch (err) {
        setError(err.message || 'Failed to load pool details')
      } finally {
        setLoading(false)
      }
    }

    if (poolName) {
      loadPoolDetails()
    }
  }, [poolName])

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose()
    }
  }

  const renderTestCases = (cases, title, borderColor) => {
    if (!cases || cases.length === 0) {
      return (
        <Section>
          <SectionTitle>
            <FileText size={16} />
            {title}
          </SectionTitle>
          <EmptyState>No {title.toLowerCase()} available</EmptyState>
        </Section>
      )
    }

    return (
      <Section>
        <SectionTitle>
          <FileText size={16} />
          {title} ({cases.length})
        </SectionTitle>
        <TestCasesList>
          {cases.map((testCase, index) => (
            <TestCaseCard key={testCase.id || index} borderColor={borderColor}>
              <TestCaseHeader>
                <TestCaseId>{testCase.id}</TestCaseId>
                {testCase.tags && testCase.tags.length > 0 && (
                  <TestCaseTags>
                    {testCase.tags.map((tag, tagIndex) => (
                      <Tag key={tagIndex}>{tag}</Tag>
                    ))}
                  </TestCaseTags>
                )}
              </TestCaseHeader>
              
              {testCase.description && (
                <TestCaseContent style={{ marginBottom: '12px', fontStyle: 'italic' }}>
                  {testCase.description}
                </TestCaseContent>
              )}
              
              <TestCaseContent>
                <ContentBlock bgColor="#f1f3f4">
                  <ContentLabel>Input:</ContentLabel>
                  {testCase.input}
                </ContentBlock>
                <ContentBlock bgColor="#e8f5e8">
                  <ContentLabel>Expected Output:</ContentLabel>
                  {testCase.expected_output}
                </ContentBlock>
                {testCase.weight !== undefined && testCase.weight !== 1.0 && (
                  <div style={{ fontSize: '12px', color: '#5f6368', marginTop: '8px' }}>
                    Weight: {testCase.weight}
                  </div>
                )}
              </TestCaseContent>
            </TestCaseCard>
          ))}
        </TestCasesList>
      </Section>
    )
  }

  return (
    <Overlay onClick={handleOverlayClick}>
      <Modal>
        <Header>
          <Title>Test Pool: {poolName}</Title>
          <CloseButton onClick={onClose}>
            <X size={20} />
          </CloseButton>
        </Header>

        {loading && (
          <LoadingContainer>
            <Loader className="animate-spin" size={24} />
            Loading pool details...
          </LoadingContainer>
        )}

        {error && (
          <div style={{ 
            background: '#fce8e6', 
            color: '#d93025', 
            padding: '12px', 
            borderRadius: '8px',
            marginBottom: '20px'
          }}>
            {error}
          </div>
        )}

        {pool && !loading && (
          <>
            <PoolInfo>
              <InfoRow>
                <InfoLabel>Description:</InfoLabel>
                <InfoValue>{pool.description || 'No description'}</InfoValue>
              </InfoRow>
              <InfoRow>
                <InfoLabel>Category:</InfoLabel>
                <InfoValue>{pool.category}</InfoValue>
              </InfoRow>
              <InfoRow>
                <InfoLabel>Total Cases:</InfoLabel>
                <InfoValue>
                  {(pool.test_cases?.length || 0) + 
                   (pool.edge_cases?.length || 0) + 
                   (pool.negative_cases?.length || 0)}
                </InfoValue>
              </InfoRow>
            </PoolInfo>

            {renderTestCases(pool.test_cases, 'Test Cases', '#1a73e8')}
            {renderTestCases(pool.edge_cases, 'Edge Cases', '#fbbc04')}
            {renderTestCases(pool.negative_cases, 'Negative Cases', '#ea4335')}
          </>
        )}
      </Modal>
    </Overlay>
  )
}

export default TestPoolModal 