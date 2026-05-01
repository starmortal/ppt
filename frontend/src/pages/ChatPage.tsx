import { useState, useEffect, useRef } from 'react'
import { Layout, Input, Button, List, Avatar, Upload, message } from 'antd'
import { 
  SendOutlined, 
  PlusOutlined, 
  PaperClipOutlined,
  UserOutlined,
  HistoryOutlined,
  DeleteOutlined
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
      const userId = 'user_' + Math.random().toString(36).substr(2, 9)
      const session = await sessionAPI.create(userId)
      setSessionId(session.session_id)
      
      // Add to sessions list
      const newSession: Session = {
        id: session.session_id,
        title: '新建会话',
        lastMessage: '',
        timestamp: new Date().toISOString()
      }
      setSessions([newSession])
    } catch (error) {
      message.error('创建会话失败')
      console.error(error)
    }
  }

  const handleNewSession = async () => {
    try {
      const userId = 'user_' + Math.random().toString(36).substr(2, 9)
      const session = await sessionAPI.create(userId)
      setSessionId(session.session_id)
      setMessages([])
      
      const newSession: Session = {
        id: session.session_id,
        title: '新建会话',
        lastMessage: '',
        timestamp: new Date().toISOString()
      }
      setSessions([newSession, ...sessions])
      message.success('新会话已创建')
    } catch (error) {
      message.error('创建会话失败')
    }
  }

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !sessionId) return

    const userMessage: Message = {
      id: 'user_' + Date.now(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setLoading(true)

    try {
      const response = await chatAPI.sendMessage(sessionId, inputMessage)
      
      const aiMessage: Message = {
        id: response.message_id,
        role: response.role,
        content: response.content,
        timestamp: response.timestamp
      }

      setMessages(prev => [...prev, aiMessage])
      
      // Update session title if first message
      if (messages.length === 0) {
        setSessions(prev => prev.map(s => 
          s.id === sessionId 
            ? { ...s, title: inputMessage.substring(0, 20) + '...', lastMessage: response.content }
            : s
        ))
      }
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
      const uploadResult = await fileAPI.upload(file, sessionId, 'source')
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

  const quickExamples = [
    'Dify产品介绍',
    '北京自由行攻略',
    '白雪公主企业介绍',
    '汽车行业周报'
  ]

  const handleQuickExample = (example: string) => {
    setInputMessage(example)
  }

  // Empty state (no messages)
  const renderEmptyState = () => (
    <div className="empty-state">
      <div className="welcome-title">
        <h1>下午好,</h1>
        <h1>有什么PPT需要我做?</h1>
      </div>
      <p className="welcome-subtitle">AI生成制版、可编辑的PPT</p>
      
      <div className="quick-examples">
        {quickExamples.map((example, index) => (
          <Button
            key={index}
            className="example-btn"
            onClick={() => handleQuickExample(example)}
          >
            {example}
          </Button>
        ))}
      </div>
    </div>
  )

  return (
    <Layout className="chat-layout">
      {/* Left Sidebar */}
      <Sider width={240} className="chat-sider">
        <div className="sider-header">
          <div className="user-info">
            <Avatar icon={<UserOutlined />} />
            <span className="username">SANDUN</span>
          </div>
        </div>

        <Button 
          type="text" 
          icon={<PlusOutlined />} 
          className="new-chat-btn"
          onClick={handleNewSession}
          block
        >
          新建会话
          <span className="shortcut">New</span>
        </Button>

        <div className="sessions-section">
          <div className="section-title">
            <HistoryOutlined />
            <span>聊天记录</span>
          </div>
          
          {sessions.length === 0 ? (
            <div className="no-sessions">暂无记录</div>
          ) : (
            <List
              className="sessions-list"
              dataSource={sessions}
              renderItem={(session) => (
                <List.Item
                  className={`session-item ${session.id === sessionId ? 'active' : ''}`}
                  onClick={() => setSessionId(session.id)}
                >
                  <div className="session-content">
                    <div className="session-title">{session.title}</div>
                    {session.lastMessage && (
                      <div className="session-preview">{session.lastMessage.substring(0, 30)}...</div>
                    )}
                  </div>
                  <Button
                    type="text"
                    size="small"
                    icon={<DeleteOutlined />}
                    className="delete-btn"
                    onClick={(e) => {
                      e.stopPropagation()
                      setSessions(sessions.filter(s => s.id !== session.id))
                    }}
                  />
                </List.Item>
              )}
            />
          )}
        </div>

        <div className="sider-footer">
          <Button type="text" icon={<UserOutlined />} size="small">
            设置
          </Button>
        </div>
      </Sider>

      {/* Main Content */}
      <Content className="chat-content">
        {/* Top Bar */}
        <div className="top-bar">
          <div className="top-bar-left"></div>
          <div className="top-bar-right">
            <Button type="primary" ghost>
              登录 / 注册
            </Button>
          </div>
        </div>

        {/* Messages Area */}
        <div className="messages-container">
          {messages.length === 0 ? (
            renderEmptyState()
          ) : (
            <div className="messages-list">
              {messages.map((msg) => (
                <div 
                  key={msg.id} 
                  className={`message-item ${msg.role === 'user' ? 'user-message' : 'ai-message'}`}
                >
                  {msg.role !== 'user' && (
                    <Avatar className="message-avatar" size={32}>
                      AI
                    </Avatar>
                  )}
                  <div className="message-content">
                    <div className="message-text">{msg.content}</div>
                  </div>
                  {msg.role === 'user' && (
                    <Avatar className="message-avatar" size={32} icon={<UserOutlined />} />
                  )}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="input-container">
          <div className="input-wrapper">
            <Upload
              fileList={fileList}
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
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onPressEnter={(e) => {
                if (!e.shiftKey) {
                  e.preventDefault()
                  handleSendMessage()
                }
              }}
              placeholder="描述你的工作..."
              className="message-input"
              disabled={loading || !sessionId}
              suffix={
                <Button
                  type="text"
                  icon={<SendOutlined />}
                  onClick={handleSendMessage}
                  loading={loading}
                  disabled={!inputMessage.trim() || !sessionId}
                  className="send-btn"
                />
              }
            />
          </div>
          
          <div className="input-footer">
            <span className="footer-text">生成案例</span>
          </div>
        </div>
      </Content>
    </Layout>
  )
}

export default ChatPage
