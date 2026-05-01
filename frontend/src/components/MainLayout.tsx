import { Layout } from 'antd'
import { Outlet } from 'react-router-dom'

const { Header, Content } = Layout

const MainLayout = () => {
  return (
    <Layout style={{ height: '100vh' }}>
      <Header style={{ 
        display: 'flex', 
        alignItems: 'center',
        padding: '0 24px',
        background: '#001529'
      }}>
        <div style={{ 
          color: 'white', 
          fontSize: '20px', 
          fontWeight: 'bold' 
        }}>
          PPT Master Web
        </div>
      </Header>
      <Content style={{ overflow: 'hidden' }}>
        <Outlet />
      </Content>
    </Layout>
  )
}

export default MainLayout
