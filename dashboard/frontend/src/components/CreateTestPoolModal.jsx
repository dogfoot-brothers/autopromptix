import React, { useState } from 'react'
import styled from '@emotion/styled'
import { X, Save, Plus } from 'lucide-react'

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
  max-width: 600px;
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

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 16px;
`

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`

const Label = styled.label`
  font-weight: 500;
  color: #202124;
  font-size: 14px;
`

const Input = styled.input`
  width: 100%;
  padding: 12px;
  border: 1px solid #e8eaed;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s ease;

  &:focus {
    outline: none;
    border-color: #1a73e8;
  }
`

const TextArea = styled.textarea`
  width: 100%;
  padding: 12px;
  border: 1px solid #e8eaed;
  border-radius: 6px;
  font-size: 14px;
  font-family: monospace;
  resize: vertical;
  min-height: 120px;
  transition: border-color 0.2s ease;

  &:focus {
    outline: none;
    border-color: #1a73e8;
  }
`

const ButtonGroup = styled.div`
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 20px;
`

const Button = styled.button`
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;

  &.primary {
    background: #1a73e8;
    color: #fff;

    &:hover {
      background: #1557b0;
      transform: translateY(-1px);
      box-shadow: 0 2px 8px rgba(26, 115, 232, 0.3);
    }

    &:disabled {
      background: #ccc;
      cursor: not-allowed;
      transform: none;
      box-shadow: none;
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

const ErrorMessage = styled.div`
  background: #fce8e6;
  color: #d93025;
  padding: 12px;
  border-radius: 8px;
  font-size: 14px;
`

const HelperText = styled.div`
  font-size: 12px;
  color: #5f6368;
  margin-top: 4px;
`

const CreateTestPoolModal = ({ onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    function_name: '',
    description: '',
    category: 'general',
    test_cases: ''
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      // Validate test cases JSON
      let testCases = []
      if (formData.test_cases.trim()) {
        try {
          testCases = JSON.parse(formData.test_cases)
          if (!Array.isArray(testCases)) {
            throw new Error('Test cases must be an array')
          }
        } catch (jsonError) {
          setError(`Invalid JSON in test cases: ${jsonError.message}`)
          setLoading(false)
          return
        }
      }

      const poolData = {
        ...formData,
        test_cases: testCases
      }

      const result = await onSubmit(poolData)
      if (!result.success) {
        setError(result.error || 'Failed to create test pool')
      }
    } catch (err) {
      setError(err.message || 'An unexpected error occurred')
    } finally {
      setLoading(false)
    }
  }

  const exampleTestCases = `[
  {
    "id": "test_001",
    "input": "Hello world",
    "expected_output": "Hello, world!",
    "weight": 1.0,
    "tags": ["basic", "greeting"],
    "description": "Basic greeting test"
  },
  {
    "id": "test_002",
    "input": "How are you?",
    "expected_output": "I'm doing well, thank you!",
    "weight": 1.0,
    "tags": ["conversation"],
    "description": "Conversation test"
  }
]`

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose()
    }
  }

  return (
    <Overlay onClick={handleOverlayClick}>
      <Modal>
        <Header>
          <Title>Create Test Data Pool</Title>
          <CloseButton onClick={onClose}>
            <X size={20} />
          </CloseButton>
        </Header>

        <Form onSubmit={handleSubmit}>
          <FormGroup>
            <Label htmlFor="function_name">Function Name *</Label>
            <Input
              type="text"
              id="function_name"
              name="function_name"
              value={formData.function_name}
              onChange={handleInputChange}
              required
              placeholder="e.g., greeting_function"
            />
            <HelperText>
              The name of the function this test pool is for
            </HelperText>
          </FormGroup>

          <FormGroup>
            <Label htmlFor="description">Description</Label>
            <Input
              type="text"
              id="description"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              placeholder="Describe what this test pool is for"
            />
          </FormGroup>

          <FormGroup>
            <Label htmlFor="category">Category</Label>
            <Input
              type="text"
              id="category"
              name="category"
              value={formData.category}
              onChange={handleInputChange}
              placeholder="general"
            />
          </FormGroup>

          <FormGroup>
            <Label htmlFor="test_cases">Test Cases (JSON)</Label>
            <TextArea
              id="test_cases"
              name="test_cases"
              value={formData.test_cases}
              onChange={handleInputChange}
              placeholder={exampleTestCases}
            />
            <HelperText>
              JSON array of test cases. Each test case should have: id, input, expected_output, weight (optional), tags (optional), description (optional)
            </HelperText>
          </FormGroup>

          {error && <ErrorMessage>{error}</ErrorMessage>}

          <ButtonGroup>
            <Button type="button" className="secondary" onClick={onClose}>
              Cancel
            </Button>
            <Button 
              type="submit" 
              className="primary" 
              disabled={loading || !formData.function_name.trim()}
            >
              {loading ? (
                <>Creating...</>
              ) : (
                <>
                  <Save size={16} />
                  Create Pool
                </>
              )}
            </Button>
          </ButtonGroup>
        </Form>
      </Modal>
    </Overlay>
  )
}

export default CreateTestPoolModal 