# 导入Flask相关模块，用于创建Web应用、处理请求和响应
from flask import Flask, request, jsonify, render_template, send_from_directory
# 导入自定义的TestDatabase类，用于处理数据库操作
from test_db import TestDatabase
# 导入os模块，用于处理文件路径
import os
# 导入datetime模块，用于处理日期时间
from datetime import datetime

# 创建Flask应用实例，设置静态文件夹为当前目录
app = Flask(__name__, static_folder='.', static_url_path='')

# 获取当前文件所在目录的绝对路径
# 这行代码用于设置模板文件夹的路径，确保模板文件能被正确找到
template_dir = os.path.abspath(os.path.dirname(__file__))
# 设置Flask应用的模板文件夹
app.template_folder = template_dir

# 全局数据库连接对象，初始值为None
# 使用全局变量可以在多个请求间共享数据库连接，提高性能
db = None

# 定义获取数据库连接的函数
def get_db():
    # 声明使用全局变量db
    global db
    # 检查数据库连接是否存在或是否已连接
    if db is None or not db.connection.is_connected():
        # 如果连接不存在或已断开，创建新的数据库连接
        db = TestDatabase()
    # 返回数据库连接对象
    return db

# 定义根路由，处理GET请求
@app.route('/')
def index():
    # 直接从当前目录发送form.html文件作为响应
    return send_from_directory('.', 'form.html')

# 定义/submit路由，处理POST请求，用于提交表单数据
@app.route('/submit', methods=['POST'])
def submit_data():
    try:
        # 根据请求类型获取表单数据
        if request.is_json:
            # 如果是JSON格式请求，解析JSON数据
            data = request.get_json()
            name = data.get('name')  # 获取姓名字段
            date_str = data.get('date')  # 获取日期字段
        else:
            # 如果是表单格式请求，从表单中获取数据
            name = request.form.get('name')  # 获取姓名字段
            date_str = request.form.get('date')  # 获取日期字段
        
        # 验证数据是否为空
        if not name or not date_str:
            # 如果姓名或日期为空，返回错误响应
            return jsonify({'success': False, 'error': '姓名和日期不能为空'})
        
        # 验证日期格式是否正确
        try:
            # 尝试将日期字符串解析为datetime对象，预期格式为YYYY-MM-DD
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            # 将datetime对象格式化为MySQL的DATE格式字符串
            formatted_date = date_obj.strftime('%Y-%m-%d')
        except ValueError:
            # 如果日期格式错误，返回错误响应
            return jsonify({'success': False, 'error': '日期格式错误，请使用YYYY-MM-DD格式'})

        # 获取数据库连接
        test_db = get_db()
        # 调用数据库的insert_data方法，将数据插入到test表中
        success = test_db.insert_data(name, formatted_date)
        
        # 根据插入结果返回相应的响应
        if success:
            # 插入成功，返回成功响应
            return jsonify({'success': True, 'message': '数据保存成功'})
        else:
            # 插入失败，返回失败响应
            return jsonify({'success': False, 'error': '数据库操作失败'})
            
    except Exception as e:
        # 捕获所有异常，打印错误信息到控制台
        print(f"处理提交请求时出错: {e}")
        # 返回服务器错误响应
        return jsonify({'success': False, 'error': f'服务器内部错误: {str(e)}'})

# 定义/view-data路由，处理GET请求，用于查询和查看已提交的数据
@app.route('/view-data')
def view_data():
    try:
        # 获取数据库连接
        test_db = get_db()
        # 执行SQL查询，从test表中获取所有数据，并按创建时间倒序排列
        test_db.cursor.execute("SELECT * FROM test ORDER BY created_at DESC")
        # 获取查询结果
        data = test_db.cursor.fetchall()
        # 返回查询成功响应，包含查询到的数据
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        # 捕获所有异常，打印错误信息到控制台
        print(f"查询数据时出错: {e}")
        # 返回查询失败响应
        return jsonify({'success': False, 'error': str(e)})

# 主程序入口，当直接运行此脚本时执行
if __name__ == '__main__':
    try:
        # 初始化数据库连接
        db = TestDatabase()
        # 打印启动成功信息到控制台
        print("测试应用启动成功")
        # 打印访问提示信息到控制台
        print("访问 http://localhost:5001 查看表单页面")
        # 启动Flask应用，监听所有IP地址的5001端口，开启调试模式
        # 使用5001端口是为了避免与主应用冲突
        app.run(host='0.0.0.0', port=5001, debug=True)
    finally:
        # 无论程序如何结束，确保关闭数据库连接
        if db:
            db.close()