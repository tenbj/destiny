# 测试数据提交系统

这是一个简单的测试项目，用于演示如何通过HTML表单收集用户输入（姓名和日期），并将数据提交到MySQL数据库。

## 项目结构

```
test/
├── test_db.py        # 数据库连接和操作模块
├── test_app.py       # Flask后端应用
├── form.html         # 用户输入表单页面
└── README.md         # 项目说明文档
```

## 功能说明

1. **表单页面**：提供一个美观的HTML表单，允许用户输入姓名和日期
2. **数据验证**：在前端和后端都进行基本的数据验证
3. **数据库操作**：自动创建test表并将数据保存到MySQL数据库
4. **数据预览**：提交成功后显示最新提交的数据信息

## 技术栈

- **前端**：HTML, Tailwind CSS, JavaScript
- **后端**：Python, Flask
- **数据库**：MySQL

## 使用方法

1. 确保已安装必要的Python依赖：
   ```bash
   pip install flask mysql-connector-python
   ```

2. 运行后端应用：
   ```bash
   cd e:/trae_project/destiny/test
   python test_app.py
   ```

3. 在浏览器中访问：
   ```
   http://localhost:5001
   ```

4. 填写表单并提交数据

## 注意事项

- 该项目使用与主应用相同的数据库配置
- 后端应用运行在5001端口，避免与主应用的5000端口冲突
- 提交的数据将保存在MySQL数据库的test表中
- 如果数据库连接失败，应用会尝试创建必要的表结构

## 测试数据查看

提交数据后，可以通过页面上的数据预览区域查看最新提交的数据

## 开发说明

- 如需修改数据库连接信息，请修改主项目目录下的config.py文件
- 如需扩展功能，可以修改相应的文件：
  - 前端UI修改：form.html
  - 后端逻辑修改：test_app.py
  - 数据库操作修改：test_db.py