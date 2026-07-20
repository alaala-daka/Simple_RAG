# Simple RAG

基于 **检索增强生成（RAG）** 的智能知识问答系统。上传文档到知识库后，可通过自然语言提问，系统自动检索相关内容并结合大模型生成回答。

## 架构

```
用户上传文档 → 文本分割 → 向量嵌入 → ChromaDB 存储
                                          ↓
用户提问     → 向量检索 → 相关片段召回 → LLM 生成回答
```

## 功能

- **知识库管理**：上传文本文档，自动向量化存储，支持 MD5 去重
- **智能问答**：基于知识库内容的 RAG 对话，优先根据参考资料回答
- **对话历史**：自动持久化，支持多会话切换和历史清除
- **Web 交互**：基于 Streamlit 的简洁前端界面

## 技术栈

| 组件 | 技术 |
|------|------|
| 前端 | Streamlit |
| LLM | DeepSeek（通过 langchain-deepseek） |
| 向量嵌入 | DashScope text-embedding-v4 |
| 向量存储 | ChromaDB（langchain-chroma） |
| 框架 | LangChain |
| 包管理 | uv |

## 项目结构

```
Simple_RAG/
├── chat.py                  # Streamlit 前端交互页面
├── rag.py                   # RAG 核心链（检索 → 增强 → 生成）
├── knowledgebaseservice.py  # 知识库服务（文档上传、向量化）
├── vector_storage.py        # ChromaDB 向量检索封装
├── config.py                # 配置管理（模型、路径、API Key）
├── filechathistory.py       # 对话历史持久化
├── web_file_uploader.py     # 独立的知识库上传页面
├── pyproject.toml           # 项目依赖
├── .env                     # 环境变量（需自行创建）
├── chroma_db/               # ChromaDB 向量数据库文件
├── persist_dir/             # ChromaDB 持久化目录
└── 长期记忆储存/             # 对话历史存档
```

## 快速开始

### 环境要求

- Python >= 3.13
- [uv](https://docs.astral.sh/uv/) 包管理器

### 安装

```bash
# 克隆仓库
git clone <your-repo-url>
cd Simple_RAG

# 安装依赖
uv sync
```

### 配置

在项目根目录创建 `.env` 文件：

```env
CHROMA_PATH="./chroma_db"
MD5_TXT="./md5_txt_storage.txt"
PERSIST_DIRECTORY="./persist_dir"
DASHSCOPE_API_KEY="你的阿里云DashScope API Key"
DEEPSEEK_API_KEY="你的DeepSeek API Key"
```

### 运行

```bash
# 启动聊天界面
uv run streamlit run chat.py

# 或仅启动知识库上传页面
uv run streamlit run web_file_uploader.py
```

打开浏览器访问 `http://localhost:8501`。

## 使用说明

1. **上传文档**：在左侧边栏选择 `.txt` 文件上传到知识库
2. **开始提问**：在主区域输入问题，系统会检索知识库并生成回答
3. **切换会话**：修改侧边栏中的会话 ID 可创建独立对话
4. **清除历史**：点击"清除对话历史"按钮重置当前会话
