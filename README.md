# Destiny - 命理测算小程序

一个基于中国传统五行八卦紫微斗数理论，结合现代AI技术的命理测算小程序。用户可以通过输入出生信息获取命盘分析，并与AI命理师进行对话。

## 功能特点

- 🔮 **命盘生成**：基于用户出生年月日时，生成详细的五行八卦紫微命盘分析
- 💬 **AI对话**：与AI命理师进行关于命理的问答对话
- 💾 **数据保存**：保存用户信息和所有对话记录
- 📱 **响应式设计**：兼容PC端和移动端

## 技术栈

- **后端**：Python + Flask
- **前端**：HTML + Tailwind CSS + JavaScript
- **数据库**：MySQL
- **AI服务**：Ollama (Qwen3模型)

## 快速开始

### 前提条件

- 已安装Python 3.7+环境
- 已配置MySQL数据库连接
- 可访问Ollama API服务

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置文件

项目使用`config.py`文件存储配置信息：
- 数据库连接信息
- Ollama API地址
- Flask服务配置

### 启动应用

```bash
python run_app.py
```

或者直接运行Flask应用：

```bash
python app.py
```

应用启动后，可通过浏览器访问 `http://localhost:5000` 来使用程序。

## 使用说明

1. **输入出生信息**：在首页填写您的出生年份、月份、日期和时辰
2. **生成命盘**：点击"生成命盘"按钮，系统将为您生成详细的命盘分析
3. **查看命盘**：命盘生成后，您可以查看五行分析、八卦定位、紫微斗数等详细信息
4. **与命理师对话**：点击"与命理师对话"按钮，您可以根据命盘信息向AI提问
5. **历史记录**：系统会保存您的所有对话记录

## 项目结构

```
destiny/
├── app.py              # Flask应用主文件
├── config.py           # 配置文件
├── db.py               # 数据库操作模块
├── ollama_service.py   # Ollama服务交互模块
├── requirements.txt    # 项目依赖
├── run_app.py          # 应用启动脚本
├── README.md           # 项目说明文档
└── templates/
    └── index.html      # 前端HTML模板
```

## 注意事项

- 请确保MySQL数据库服务可用，并已正确配置连接信息
- 请确保可访问Ollama API服务
- 本程序仅供娱乐参考，请勿完全依赖

## License

MIT