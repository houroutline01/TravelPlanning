# 旅行规划助手 (Travel Planning Assistant)

一个基于 Streamlit 的智能旅行规划应用，支持 AI 行程生成、结构化记账和语音输入功能。

## 功能特性

- 用户注册和登录
- AI 智能生成旅行行程
- 结构化记账功能（项目和金额）
- 语音输入支持（百度智能云语音识别）
- 历史行程和记账记录管理
- 数据持久化存储

## 技术栈

- **前端框架**: Streamlit
- **后端**: Python
- **数据库**: SQLite (SQLAlchemy ORM)
- **AI 服务**: OpenAI API
- **语音识别**: 百度智能云语音识别 API
- **容器化**: Docker

## 快速开始

### 方式1：使用 Docker 镜像（推荐）

#### 1. 导入 Docker 镜像

如果你已经下载了 `travel-planning-image.tar` 文件，使用以下命令导入：

```bash
docker load -i travel-planning-image.tar
```

#### 2. 运行容器

```bash
docker run -d -p 8501:8501 --name travel-planning travel-planning:latest
```

访问 `http://localhost:8501` 即可使用应用。

#### 3. 配置环境变量

在首次运行前，需要配置以下环境变量：

- **OpenAI API 配置**:
  - `API_KEY`: OpenAI API 密钥
  - `API_BASE_URL`: OpenAI API 基础 URL（可选）

- **百度语音识别配置**（可选，用于语音输入）:
  - `BAIDU_APP_ID`: 百度应用 ID
  - `BAIDU_API_KEY`: 百度 API Key
  - `BAIDU_SECRET_KEY`: 百度 Secret Key

**配置方式1：通过环境变量文件**

创建 `.env` 文件（参考 `.env.example`）：

```bash
API_KEY=your_openai_api_key_here
API_BASE_URL=your_api_base_url_here
BAIDU_APP_ID=your_baidu_app_id_here
BAIDU_API_KEY=your_baidu_api_key_here
BAIDU_SECRET_KEY=your_baidu_secret_key_here
```

**配置方式2：通过 Docker 命令**

```bash
docker run -d -p 8501:8501 \
  -e API_KEY=your_openai_api_key_here \
  -e API_BASE_URL=your_api_base_url_here \
  -e BAIDU_APP_ID=your_baidu_app_id_here \
  -e BAIDU_API_KEY=your_baidu_api_key_here \
  -e BAIDU_SECRET_KEY=your_baidu_secret_key_here \
  --name travel-planning travel-planning:latest
```

**配置方式3：通过应用界面**

在应用侧边栏的设置中直接输入 API Key 和配置信息。

#### 4. 停止和删除容器

```bash
# 停止容器
docker stop travel-planning

# 删除容器
docker rm travel-planning
```

### 方式2：从源码构建

#### 1. 克隆项目

```bash
git clone https://github.com/houroutline01/TravelPlanning.git
cd TravelPlanning
```

#### 2. 安装依赖

```bash
pip install -r requirements.txt
```

#### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API 密钥。

#### 4. 运行应用

```bash
streamlit run app.py
```

访问 `http://localhost:8501` 即可使用应用。

### 方式3：使用 Docker 构建

#### 1. 构建 Docker 镜像

```bash
docker build -t travel-planning:latest .
```

#### 2. 运行容器

```bash
docker run -d -p 8501:8501 --name travel-planning travel-planning:latest
```

#### 3. 导出 Docker 镜像（可选）

如果需要导出镜像为 tar 文件：

```bash
docker save -o travel-planning-image.tar travel-planning:latest
```

## 使用说明

### 用户注册和登录

1. 在侧边栏选择"注册"标签
2. 输入用户名和密码进行注册
3. 注册后使用相同的用户名和密码登录

### 生成旅行行程

1. 登录后进入"行程生成"标签
2. 选择输入方式：
   - **文本输入**: 直接输入旅行需求
   - **语音录制**: 点击录制按钮，说出你的旅行需求
3. 点击"生成行程"按钮
4. 等待 AI 生成旅行计划

### 记账功能

1. 进入"记账"标签
2. 输入项目名称和金额
3. 点击"添加记录"
4. 查看历史记账记录
5. 可以删除不需要的记录

### 语音识别使用提示

为了获得更好的语音识别效果，请注意：

- 在安静环境下录音
- 靠近麦克风，说话清晰
- 录音时长建议 3-10 秒
- 避免使用填充词（如"嗯"、"啊"）

示例语音内容：
- "我想去日本旅游5天预算一万"
- "帮我规划一个去上海的3天行程"
- "我想去北京玩一周，预算5000"

## API 密钥获取

### OpenAI API

1. 访问 [OpenAI Platform](https://platform.openai.com/)
2. 注册并登录账号
3. 进入 API Keys 页面创建新的 API Key
4. 复制 API Key 到应用配置中

### 百度智能云语音识别

1. 访问 [百度智能云控制台](https://cloud.baidu.com/)
2. 注册并登录账号
3. 开通"语音技术"服务
4. 创建应用获取 App ID、API Key 和 Secret Key
5. 将这些信息填入应用配置中

## 项目结构

```
TravelPlanning/
├── app.py                 # 主应用文件
├── database.py            # 数据库操作
├── requirements.txt       # Python 依赖
├── Dockerfile            # Docker 配置
├── .env.example          # 环境变量模板
├── .gitignore            # Git 忽略配置
└── README.md             # 项目说明文档
```

## 常见问题

### Q: Docker 镜像文件很大怎么办？

A: Docker 镜像文件通常较大（几百 MB 到几 GB），这是正常的。如果需要减小文件大小，可以考虑：
- 使用更小的基础镜像（如 `python:3.9-alpine`）
- 清理不必要的文件和依赖

### Q: 语音识别不准确怎么办？

A: 请参考"语音识别使用提示"部分，确保：
- 环境安静，无噪音干扰
- 麦克风距离适中（10-20厘米）
- 说话清晰，语速适中
- 避免使用填充词

### Q: 如何备份数据？

A: 数据存储在 SQLite 数据库文件中（`travel_planning.db`），可以：
- 定期复制该数据库文件进行备份
- 使用 Docker volume 挂载持久化数据

### Q: 应用无法连接到 API 怎么办？

A: 请检查：
- API Key 是否正确
- 网络连接是否正常
- API 服务是否可用
- 防火墙是否阻止了连接

## 开发和贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过 GitHub Issues 联系。
