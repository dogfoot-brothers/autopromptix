import React from 'react'
import styled from '@emotion/styled'
import { Activity, Database, FlaskConical } from 'lucide-react'

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
`

const StatCard = styled.div`
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.12);
  transition: box-shadow 0.2s ease;

  &:hover {
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
  }
`

const StatHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
`

const StatIcon = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 20px;
  background: ${props => props.color};
`

const StatInfo = styled.div`
  flex: 1;
`

const StatTitle = styled.div`
  font-size: 14px;
  color: #5f6368;
  font-weight: 500;
`

const StatValue = styled.div`
  font-size: 32px;
  font-weight: 400;
  color: #202124;
  margin-bottom: 8px;
`

const StatsGrid = ({ stats }) => {
  const statItems = [
    {
      title: 'Functions',
      value: stats.total_functions,
      color: '#1a73e8',
      icon: Activity
    },
    {
      title: 'Test Pools',
      value: stats.total_test_pools,
      color: '#34a853',
      icon: Database
    },
    {
      title: 'Test Cases',
      value: stats.total_test_cases,
      color: '#fbbc04',
      icon: FlaskConical
    }
  ]

  return (
    <Grid>
      {statItems.map((stat, index) => {
        const IconComponent = stat.icon
        return (
          <StatCard key={index}>
            <StatHeader>
              <StatIcon color={stat.color}>
                <IconComponent size={20} />
              </StatIcon>
              <StatInfo>
                <StatTitle>{stat.title}</StatTitle>
                <StatValue>{stat.value}</StatValue>
              </StatInfo>
            </StatHeader>
          </StatCard>
        )
      })}
    </Grid>
  )
}

export default StatsGrid 