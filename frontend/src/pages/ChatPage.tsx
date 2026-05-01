import { useState, useEffect, useRef } from 'react'
import { Layout, Input, Button, List, Avatar, Upload, message } from 'antd'
import { 
  SendOutlined, 
  PlusOutlined, 
  PaperClipOutlined,
  UserOutlined
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

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    initSession()
  }, [])

  const initSession = async () => {
    try {
      const response = await sessionAPI.create('user_default')
      setSessionId(response.session_id)
      
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

    const userMsg: Message = {
      id: 'temp_' + Date.now(),
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, userMsg])

    try {
      const response = await chatAPI.sendMessage(sessionId, userMessage)
      
      const aiMsg: Message = {
        id: response.message_id,
        role: 'assistant',
        content: response.content,
        timestamp: response.timestamp
      }
      setMessages(prev => [...prev, aiMsg])

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
    <Layout style={{ height: '100vh' }}>
      {/* 左侧灰色侧边栏 */}
      <Sider width={280} style={{ background: '#f5f5f5' }}>
        <div style={{ padding: '20px 16px', borderBottom: '1px solid #e8e8e8' }}>
          <div style={{ fontSize: '18px', fontWeight: 600, color: '#262626', marginBottom: '16px' }}>
            PPT Agent
          </div>
          <Button 
            type="default" 
            icon={<PlusOutlined />} 
            onClick={handleNewChat}
            block
            style={{ height: '40px', borderRadius: '8px' }}
          >
            新建会话
          </Button>
        </div>

        <div style={{ padding: '16px', overflowY: 'auto', height: 'calc(100vh - 120px)' }}>
          <div style={{ fontSize: '12px', color: '#8c8c8c', marginBottom: '8px' }}>聊天记录</div>
          <List
            dataSource={sessions}
            renderItem={(session) => (
              <div
                key={session.id}
                onClick={() => {
                  setSessionId(session.id)
                  setShowWelcome(false)
                }}
                style={{
                  padding: '12px',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  marginBottom: '4px',
                  background: session.id === sessionId ? '#ffffff' : 'transparent',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  if (session.id !== sessionId) {
                    e.currentTarget.style.background = '#e6e6e6'
                  }
                }}
                onMouseLeave={(e) => {
                  if (session.id !== sessionId) {
                    e.currentTarget.style.background = 'transparent'
                  }
                }}
              >
                <div style={{ fontSize: '14px', fontWeight: 500, color: '#262626', marginBottom: '4px' }}>
                  {session.title}
                </div>
                {session.lastMessage && (
                  <div style={{ fontSize: '12px', color: '#8c8c8c', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {session.lastMessage}
                  </div>
                )}
              </div>
            )}
          />
        </div>
      </Sider>

      {/* 右侧白色主区域 */}
      <Layout style={{ background: '#ffffff' }}>
        <Content style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
          {/* 顶部登录按钮 */}
          <div style={{ 
            height: '60px', 
            padding: '0 32px', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'flex-end',
            borderBottom: '1px solid #f0f0f0'
          }}>
            <Button 
              style={{ 
                height: '36px', 
                padding: '0 20px', 
                borderRadius: '18px',
                background: '#262626',
                color: '#ffffff',
                border: 'none'
              }}
            >
              登录 / 注册
            </Button>
          </div>

          {/* 消息区域 */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '24px 32px' }}>
            {showWelcome && messages.length === 0 ? (
              <div style={{ 
                display: 'flex', 
                flexDirection: 'column', 
                alignItems: 'center', 
                justifyContent: 'center',
                height: '100%',
                maxWidth: '800px',
                margin: '0 auto'
              }}>
                <h1 style={{ fontSize: '48px', fontWeight: 600, color: '#262626', textAlign: 'center', marginBottom: '16px' }}>
                  {getGreeting()}，<br />
                  有什么PPT需要我做吗？
                </h1>
                <p style={{ fontSize: '16px', color: '#8c8c8c', textAlign: 'center', marginBottom: '48px' }}>
                  AI生成精美PPT，可编辑的PPT
                </p>
                
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', width: '100%', maxWidth: '600px' }}>
                  <Button 
                    onClick={() => handleQuickAction('帮我做一个产品介绍PPT')}
                    style={{ height: '48px', borderRadius: '8px', border: '1px solid #e8e8e8', background: '#fafafa' }}
                  >
                    产品介绍PPT
                  </Button>
                  <Button 
                    onClick={() => handleQuickAction('北京5月份8天旅游攻略')}
                    style={{ height: '48px', borderRadius: '8px', border: '1px solid #e8e8e8', background: '#fafafa' }}
                  >
                    旅游攻略PPT
                  </Button>
                  <Button 
                    onClick={() => handleQuickAction('公司年度总结报告')}
                    style={{ height: '48px', borderRadius: '8px', border: '1px solid #e8e8e8', background: '#fafafa' }}
                  >
                    年度总结报告
                  </Button>
                  <Button 
                    onClick={() => handleQuickAction('市场调研分析报告')}
                    style={{ height: '48px', borderRadius: '8px', border: '1px solid #e8e8e8', background: '#fafafa' }}
                  >
                    市场调研报告
                  </Button>
                </div>
              </div>
            ) : (
              <div style={{ maxWidth: '900px', margin: '0 auto', width: '100%' }}>
                {messages.map((msg) => (
                  <div 
                    key={msg.id} 
                    style={{ 
                      display: 'flex', 
                      gap: '12px', 
                      marginBottom: '24px',
                      flexDirection: msg.role === 'user' ? 'row-reverse' : 'row'
                    }}
                  >
                    <Avatar 
                      size={32} 
                      style={{ 
                        flexShrink: 0,
                        background: msg.role === 'user' ? '#1890ff' : '#52c41a',
                        marginTop: '4px'
                      }}
                      icon={msg.role === 'user' ? <UserOutlined /> : null}
                    >
                      {msg.role === 'assistant' ? 'AI' : null}
                    </Avatar>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{
                        fontSize: '15px',
                        lineHeight: '1.6',
                        color: '#262626',
                        wordWrap: 'break-word',
                        whiteSpace: 'pre-wrap',
                        ...(msg.role === 'user' ? {
                          background: '#e6f7ff',
                          padding: '12px 16px',
                          borderRadius: '12px',
                          display: 'inline-block',
                          maxWidth: '100%'
                        } : {
                          padding: '4px 0'
                        })
                      }}>
                        {msg.content}
                      </div>
                    </div>
                  </div>
                ))}
                {loading && (
                  <div style={{ display: 'flex', gap: '12px', marginBottom: '24px' }}>
                    <Avatar size={32} style={{ background: '#52c41a', marginTop: '4px' }}>AI</Avatar>
                    <div style={{ padding: '4px 0', color: '#8c8c8c', fontStyle: 'italic' }}>
                      正在思考...
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* 输入框 */}
          <div style={{ padding: '20px 32px 24px', borderTop: '1px solid #f0f0f0' }}>
            <div style={{ 
              maxWidth: '900px', 
              margin: '0 auto',
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '8px 12px',
              background: '#ffffff',
              borderRadius: '24px',
              border: '1px solid #d9d9d9'
            }}>
              <Upload beforeUpload={handleFileUpload} showUploadList={false}>
                <Button type="text" icon={<PaperClipOutlined />} style={{ color: '#8c8c8c' }} />
              </Upload>

              <Input
                placeholder="描述你的主题..."
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onPressEnter={handleSendMessage}
                disabled={loading}
                bordered={false}
                style={{ flex: 1, fontSize: '15px' }}
              />

              <Button
                type="primary"
                icon={<SendOutlined />}
                onClick={handleSendMessage}
                loading={loading}
                disabled={!inputMessage.trim()}
                style={{ 
                  height: '36px',
                  width: '36px',
                  borderRadius: '18px',
                  padding: 0,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              />
            </div>
          </div>
        </Content>
      </Layout>
    </Layout>
  )
}

export default ChatPage
