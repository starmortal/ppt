import { useState, useEffect, useRef } from 'react'
import { Layout, Input, Button, List, Avatar, Upload, message, Dropdown } from 'antd'
import { 
  SendOutlined, 
  PlusOutlined, 
  PaperClipOutlined,
  UserOutlined,
  SettingOutlined,
  DeleteOutlined,
  MoreOutlined
} from '@ant-design/icons'
import { sessionAPI, chatAPI, fileAPI } from '../services/api'
import './ChatPage.css'

const { Sider, Content } = Layout

interface Message {
  id: string
  role: string
  content: string
  timestamp: string
}

interface Session {
  id: string
  title: string
  lastMessage: string
  timestamp: string
}

const ChatPage = () => {
  const [sessionId, setSessionId] = useState<string>('')
  const [sessions, setSessions] = useState<Session[]>([])
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [showWelcome, setShowWelcome] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Initialize session on mount
  useEffect(() => {
    initSession()
  }, [])

  const initSession = async () => {
    try {
      const response = await sessionAPI.create('user_default')
      setSessionId(response.session_id)
      
      // Add to sessions list
      setSessions([{
        id: response.session_id,
        title: '新建对话',
        lastMessage: '',
        timestamp: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
      }])
    } catch (error) {
      message.error('创建会话失败')
      console.error(error)
    }
  }

  const handleNewChat = async () => {
    try {
      const response = await sessionAPI.create('user_default')
      setSessionId(response.session_id)
      setMessages([])
      setShowWelcome(true)
      
      // Add to sessions list
      const newSession = {
        id: response.session_id,
        title: '新建对话',
        lastMessage: '',
        timestamp: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
      }
      setSessions([newSession, ...sessions])
    } catch (error) {
      message.error('创建新会话失败')
      console.error(error)
    }
  }

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !sessionId) return

    const userMessage = inputMessage.trim()
    setInputMessage('')
    setShowWelcome(false)
    setLoading(true)

    // Add user message to UI
    const userMsg: Message = {
      id: 'temp_' + Date.now(),
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, userMsg])

    try {
      const response = await chatAPI.sendMessage(sessionId, userMessage)
      
      // Add AI response
      const aiMsg: Message = {
        id: response.message_id,
        role: 'assistant',
        content: response.content,
        timestamp: response.timestamp
      }
      setMessages(prev => [...prev, aiMsg])

      // Update session in list
      setSessions(prev => prev.map(s => 
        s.id === sessionId 
          ? { ...s, lastMessage: userMessage, timestamp: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) }
          : s
      ))
    } catch (error) {
      message.error('发送消息失败')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (file: File) => {
    if (!sessionId) {
      message.error('请先创建会话')
      return false
    }

    try {
      const hide = message.loading('正在上传文件...', 0)
      await fileAPI.upload(file, sessionId, 'source')
      hide()
      
      message.success('文件上传成功')
      
      // Add system message
      setMessages(prev => [...prev, {
        id: 'system_' + Date.now(),
        role: 'system',
        content: `已上传文件: ${file.name}`,
        timestamp: new Date().toISOString()
      }])
    } catch (error) {
      message.error('文件上传失败')
      console.error(error)
    }

    return false
  }

  const handleQuickAction = (action: string) => {
    setInputMessage(action)
  }

  const getGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return '上午好'
    if (hour < 18) return '下午好'
    return '晚上好'
  }

  return (
    <Layout className="chat-page">
      {/* Left Sidebar */}
      <Sider width={280} className="chat-sidebar">
        <div className="sidebar-header">
          <div className="user-info">
            <Avatar size={40} icon={<UserOutlined />} className="user-avatar" />
            <span className="user-name">SANDUN</span>
          </div>
          <Button 
            type="text" 
            icon={<SettingOutlined />} 
            className="settings-btn"
          />
        </div>

        <Button 
          type="default" 
          icon={<PlusOutlined />} 
          className="new-chat-btn"
          onClick={handleNewChat}
          block
        >
          新建会话
        </Button>

        <div className="sessions-section">
          <div className="section-title">聊天记录</div>
          <List
            className="sessions-list"
            dataSource={sessions}
            renderItem={(session) => (
              <List.Item
                className={`session-item ${session.id === sessionId ? 'active' : ''}`}
                onClick={() => {
                  setSessionId(session.id)
                  setShowWelcome(false)
                }}
              >
                <div className="session-content">
                  <div className="session-title">{session.title}</div>
                  {session.lastMessage && (
                    <div className="session-preview">{session.lastMessage}</div>
                  )}
                </div>
                <div className="session-meta">
                  <span className="session-time">{session.timestamp}</span>
                  <Dropdown
                    menu={{
                      items: [
                        {
                          key: 'delete',
                          label: '删除',
                          icon: <DeleteOutlined />,
                          danger: true,
                        },
                      ],
                    }}
                    trigger={['click']}
                  >
                    <Button 
                      type="text" 
                      size="small" 
                      icon={<MoreOutlined />}
                      className="session-more-btn"
                      onClick={(e) => e.stopPropagation()}
                    />
                  </Dropdown>
                </div>
              </List.Item>
            )}
          />
        </div>

        <div className="sidebar-footer">
          <div className="current-project">
            <div className="project-icon">📄</div>
            <div className="project-info">
              <div className="project-title">当前项目名称 PPT</div>
              <div className="project-meta">项目ID: 000 时长</div>
            </div>
          </div>
        </div>
      </Sider>

      {/* Main Content */}
      <Layout className="chat-main">
        <Content className="chat-content">
          {/* Top Bar */}
          <div className="top-bar">
            <div className="top-bar-left"></div>
            <div className="top-bar-right">
              <Button type="default" className="auth-btn">
                登录 / 注册
              </Button>
            </div>
          </div>

          {/* Messages or Welcome */}
          <div className="messages-container">
            {showWelcome && messages.length === 0 ? (
              <div className="welcome-screen">
                <h1 className="welcome-title">
                  {getGreeting()}，<br />
                  有什么PPT需要我做吗？
                </h1>
                <p className="welcome-subtitle">AI生成精美PPT，可编辑的PPT</p>
                
                <div className="quick-actions">
                  <Button 
                    className="quick-action-btn"
                    onClick={() => handleQuickAction('帮我做一个产品介绍PPT')}
                  >
                    Drivy: 品牌化
                  </Button>
                  <Button 
                    className="quick-action-btn"
                    onClick={() => handleQuickAction('北京5月份8天旅游攻略')}
                  >
                    北京5月份8天旅游攻略
                  </Button>
                  <Button 
                    className="quick-action-btn"
                    onClick={() => handleQuickAction('自己出版企业介绍')}
                  >
                    自己出版企业介绍
                  </Button>
                  <Button 
                    className="quick-action-btn"
                    onClick={() => handleQuickAction('汽车行业调研报告')}
                  >
                    汽车行业调研报告
                  </Button>
                </div>

                <div className="welcome-footer">
                  <span className="footer-link">生成专属</span>
                </div>
              </div>
            ) : (
              <div className="messages-list">
                {messages.map((msg) => (
                  <div key={msg.id} className={`message-item ${msg.role}`}>
                    <Avatar 
                      size={32} 
                      icon={msg.role === 'user' ? <UserOutlined /> : null}
                      className="message-avatar"
                    >
                      {msg.role === 'assistant' ? 'AI' : null}
                    </Avatar>
                    <div className="message-content">
                      <div className="message-text">{msg.content}</div>
                    </div>
                  </div>
                ))}
                {loading && (
                  <div className="message-item assistant">
                    <Avatar size={32} className="message-avatar">AI</Avatar>
                    <div className="message-content">
                      <div className="message-text typing">正在思考...</div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="input-area">
            <div className="input-container">
              <Upload
                beforeUpload={handleFileUpload}
                showUploadList={false}
              >
                <Button 
                  type="text" 
                  icon={<PaperClipOutlined />} 
                  className="attach-btn"
                />
              </Upload>

              <Input
                className="message-input"
                placeholder="描述你的主题..."
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onPressEnter={handleSendMessage}
                disabled={loading}
              />

              <Button
                type="primary"
                icon={<SendOutlined />}
                className="send-btn"
                onClick={handleSendMessage}
                loading={loading}
                disabled={!inputMessage.trim()}
              />
            </div>
          </div>
        </Content>
      </Layout>
    </Layout>
  )
}

export default ChatPage
