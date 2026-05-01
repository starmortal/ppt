# PPT Master Web

PPT Master 的 Web 服务版本，提供基于浏览器的 AI 驱动 PPT 生成服务。

## 📚 文档

- **[部署教程](./部署教程.md)** - 完整的服务器部署指南（从 GitHub 克隆到部署）

## 🚀 快速开始

### 从 GitHub 部署

```bash
# 1. 克隆项目
git clone https://github.com/starmortal/ppt.git
cd ppt/web

# 2. 配置环境变量
cd backend
cp .env.example .env
vim .env  # 配置 API 密钥和密码

# 3. 启动服务
cd ..
docker-compose up -d
```

详细步骤请查看 [部署教程.md](./部署教程.md)

## 🔄 更新部署

```bash
# 拉取最新代码
cd /opt/ppt
git pull origin main

# 重启服务
cd web
docker-compose down
docker-compose up -d --build
```

## 🏗️ 技术栈

### 后端
- **框架**: FastAPI
- **数据库**: PostgreSQL 15
- **缓存**: Redis 7
- **存储**: MinIO
- **任务队列**: Celery
- **AI**: OpenAI / Anthropic Claude

### 前端
- **框架**: React 18 + TypeScript
- **UI 库**: Ant Design 5
- **构建工具**: Vite 5
- **状态管理**: Zustand

### 部署
- **容器化**: Docker + Docker Compose
- **反向代理**: Nginx

## 📦 服务架构

```
┌─────────────┐
│   Nginx     │  反向代理
└──────┬──────┘
       │
   ┌───┴────┐
   │        │
┌──▼──┐  ┌─▼────┐
│React│  │FastAPI│  Web 服务
└─────┘  └───┬───┘
             │
    ┌────────┼────────┐
    │        │        │
┌───▼──┐ ┌──▼───┐ ┌─▼────┐
│Postgres│Redis│ │MinIO │  数据层
└────────┘└──────┘└──────┘
             │
         ┌───▼───┐
         │Celery │  异步任务
         └───────┘
```

## 🔧 环境变量配置

关键配置项（在 `backend/.env` 中）：

```bash
# 应用密钥（必须修改）
SECRET_KEY=your-secret-key

# 数据库
DATABASE_URL=postgresql://pptmaster:password@postgres:5432/pptmaster

# LLM API（可选，配置后启用 AI 功能）
OPENAI_API_KEY=sk-your-key
# 或
ANTHROPIC_API_KEY=sk-ant-your-key
```

## 📝 API 文档

启动服务后访问：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🐛 故障排除

### 服务无法启动
```bash
# 查看日志
docker-compose logs -f

# 检查服务状态
docker-compose ps
```

### 数据库连接失败
```bash
# 重启数据库
docker-compose restart postgres

# 查看数据库日志
docker-compose logs postgres
```

更多问题请查看 [部署教程.md](./部署教程.md) 的"常见问题"章节。

## 📞 支持

- **GitHub**: https://github.com/starmortal/ppt
- **Issues**: https://github.com/starmortal/ppt/issues

## 📄 许可证

本项目采用 MIT 许可证。

---

**版本**: 1.0.0  
**最后更新**: 2026-04-30
