import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ConfigProvider, theme } from 'antd'
import MainLayout from './components/MainLayout'
import ChatPage from './pages/ChatPage'
import './App.css'

function App() {
  return (
    <ConfigProvider
      theme={{
        algorithm: theme.darkAlgorithm,
        token: {
          colorPrimary: '#1890ff',
        },
      }}
    >
      <Router>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<ChatPage />} />
          </Route>
        </Routes>
      </Router>
    </ConfigProvider>
  )
}

export default App
