from flask import Flask, render_template, redirect, request, session, jsonify
from flask_cors import CORS
import uuid
import json
from db import Database
from ollama_service import OllamaService
from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG
import bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
CORS(app)

# 初始化数据库和Ollama服务
db = Database()
ollama_service = OllamaService()

@app.route('/')
def index():
    # 为每个用户生成唯一标识
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    return render_template('index.html')

@app.route('/api/generate_natal_chart', methods=['POST'])
def generate_natal_chart():
    try:
        data = request.json
        birth_year = data.get('birth_year')
        birth_month = data.get('birth_month')
        birth_day = data.get('birth_day')
        birth_hour = data.get('birth_hour')
        username = data.get('username', session['user_id'])
        
        # 验证输入
        if not all([birth_year, birth_month, birth_day, birth_hour]):
            return jsonify({'status': 'error', 'message': '请填写完整的出生信息'})
        
        # 检查用户是否已存在
        user = db.fetch_one("SELECT * FROM users WHERE username = %s", (username,))
        
        if not user:
            # 创建新用户，设置默认密码
            default_password = 'default_password'
            hashed_default_password = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt())
            db.execute_query(
                "INSERT INTO users (username, password, birth_year, birth_month, birth_day, birth_hour) VALUES (%s, %s, %s, %s, %s, %s)",
                (username, hashed_default_password.decode('utf-8'), birth_year, birth_month, birth_day, birth_hour)
            )
            user = db.fetch_one("SELECT * FROM users WHERE username = %s", (username,))
        
        user_id = user['id']
        
        # 检查是否已有命盘
        natal_chart = db.fetch_one("SELECT * FROM natal_charts WHERE user_id = %s", (user_id,))
        
        if natal_chart:
            chart_result = natal_chart['chart_result']
        else:
            # 调用Ollama生成命盘
            chart_result = ollama_service.get_natal_chart(
                birth_year, birth_month, birth_day, birth_hour
            )
            
            # 保存命盘信息
            db.execute_query(
                "INSERT INTO natal_charts (user_id, birth_data, chart_result) VALUES (%s, %s, %s)",
                (user_id, json.dumps({"year": birth_year, "month": birth_month, "day": birth_day, "hour": birth_hour}), chart_result)
            )
        
        # 保存用户信息到session
        session['db_user_id'] = user_id
        
        return jsonify({
            'status': 'success',
            'natal_chart': chart_result
        })
        
    except Exception as e:
        print(f"生成命盘异常: {e}")
        return jsonify({'status': 'error', 'message': f'生成命盘失败: {str(e)}'})

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message')
        
        if not user_message:
            return jsonify({'status': 'error', 'message': '请输入问题'})
        
        # 检查用户是否已登录
        if 'db_user_id' not in session:
            return jsonify({'status': 'error', 'message': '请先生成命盘'})
        
        user_id = session['db_user_id']
        
        # 获取用户的命盘信息
        natal_chart = db.fetch_one("SELECT chart_result FROM natal_charts WHERE user_id = %s", (user_id,))
        
        if not natal_chart:
            return jsonify({'status': 'error', 'message': '未找到命盘信息'})
        
        # 调用Ollama进行对话
        ai_response = ollama_service.chat_with_ai(user_message, natal_chart['chart_result'])
        
        # 保存对话记录
        db.execute_query(
            "INSERT INTO conversations (user_id, query, response) VALUES (%s, %s, %s)",
            (user_id, user_message, ai_response)
        )
        
        return jsonify({
            'status': 'success',
            'response': ai_response
        })
        
    except Exception as e:
        print(f"对话异常: {e}")
        return jsonify({'status': 'error', 'message': f'对话失败: {str(e)}'})

@app.route('/api/chat_stream', methods=['POST'])
def chat_stream():
    try:
        data = request.json
        user_message = data.get('message')
        
        if not user_message:
            return jsonify({'status': 'error', 'message': '请输入问题'}), 400
        
        # 检查用户是否已登录
        if 'db_user_id' not in session:
            return jsonify({'status': 'error', 'message': '请先生成命盘'}), 401
        
        user_id = session['db_user_id']
        
        # 获取用户的命盘信息
        natal_chart = db.fetch_one("SELECT chart_result FROM natal_charts WHERE user_id = %s", (user_id,))
        
        if not natal_chart:
            return jsonify({'status': 'error', 'message': '未找到命盘信息'}), 400
        
        # 保存用户问题
        db.execute_query(
            "INSERT INTO conversations (user_id, query, response) VALUES (%s, %s, '')",
            (user_id, user_message)
        )
        
        # 获取刚插入的对话ID
        conversation_id = db.cursor.lastrowid
        
        # 定义流式响应的生成器函数
        def generate():
            full_response = ''
            # 调用Ollama的流式响应方法
            for chunk in ollama_service.chat_with_ai_stream(user_message, natal_chart['chart_result']):
                full_response += chunk
                # 以text/plain格式返回每一个chunk
                yield chunk
            
            # 流式传输结束后，更新数据库中的完整响应
            db.execute_query(
                "UPDATE conversations SET response = %s WHERE id = %s",
                (full_response, conversation_id)
            )
        
        # 设置响应头，返回流式响应
        return app.response_class(generate(), mimetype='text/plain')
        
    except Exception as e:
        print(f"流式对话异常: {e}")
        return jsonify({'status': 'error', 'message': f'对话失败: {str(e)}'}), 500

@app.route('/api/get_history', methods=['GET'])
def get_history():
    try:
        if 'db_user_id' not in session:
            return jsonify({'status': 'error', 'message': '请先生成命盘'})
        
        user_id = session['db_user_id']
        
        # 获取对话历史
        history = db.fetch_query(
            "SELECT query, response, created_at FROM conversations WHERE user_id = %s ORDER BY created_at ASC",
            (user_id,)
        )
        
        return jsonify({
            'status': 'success',
            'history': history
        })
        
    except Exception as e:
        print(f"获取历史记录异常: {e}")
        return jsonify({'status': 'error', 'message': f'获取历史记录失败: {str(e)}'})

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # 验证输入
        if not username or not password or not confirm_password:
            return render_template('register.html', error='请填写所有字段')
        
        if password != confirm_password:
            return render_template('register.html', error='两次输入的密码不一致')
        
        # 检查用户名是否已存在
        existing_user = db.fetch_one("SELECT * FROM users WHERE username = %s", (username,))
        if existing_user:
            return render_template('register.html', error='用户名已存在')
        
        # 加密密码
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # 创建用户
        success = db.execute_query(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hashed_password.decode('utf-8'))
        )
        
        if success:
            # 设置注册成功提示
            return render_template('login.html', success='注册成功，请登录！')
        else:
            return render_template('register.html', error='注册失败，请稍后再试')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 验证输入
        if not username or not password:
            return render_template('login.html', error='请填写所有字段')
        
        # 检查用户是否存在
        user = db.fetch_one("SELECT * FROM users WHERE username = %s", (username,))
        if not user:
            return render_template('login.html', error='用户名或密码错误')
        
        # 验证密码
        if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            # 登录成功，设置session
            session['logged_in'] = True
            session['username'] = username
            session['user_id'] = user['id']
            session['db_user_id'] = user['id']
            return redirect('/dashboard')
        else:
            return render_template('login.html', error='用户名或密码错误')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    # 清除session
    session.clear()
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    # 检查是否已登录
    if not session.get('logged_in'):
        return redirect('/login')
    
    user_id = session['user_id']
    
    # 获取用户信息
    user = db.fetch_one("SELECT * FROM users WHERE id = %s", (user_id,))
    
    # 获取命盘信息
    natal_chart = db.fetch_one("SELECT * FROM natal_charts WHERE user_id = %s", (user_id,))
    
    # 获取对话历史
    conversations = db.fetch_query(
        "SELECT query, response, created_at FROM conversations WHERE user_id = %s ORDER BY created_at DESC LIMIT 5",
        (user_id,)
    )
    
    return render_template('dashboard.html', user=user, natal_chart=natal_chart, conversations=conversations)

@app.route('/calculator')
def calculator():
    # 检查是否已登录
    if not session.get('logged_in'):
        return redirect('/login')
    
    return render_template('calculator.html')

@app.route('/chart')
def chart():
    db = Database()
    try:
        # 检查用户是否登录
        if 'logged_in' not in session:
            app.logger.info('未登录用户尝试访问chart页面，重定向到登录页')
            return redirect('/login')
        
        if 'db_user_id' not in session:
            # 尝试使用旧的user_id
            if 'user_id' in session:
                # 查询是否有对应的用户
                user = db.fetch_one("SELECT id FROM users WHERE username = %s", (session['user_id'],))
                if user:
                    session['db_user_id'] = user['id']
                    app.logger.info(f'成功将会话用户ID {session["user_id"]} 映射到数据库用户ID {user["id"]}')
                else:
                    app.logger.warning(f'未找到用户名 {session["user_id"]} 对应的用户记录')
                    return redirect('/login')
            else:
                app.logger.warning('会话中缺少用户ID信息，重定向到登录页')
                return redirect('/login')
        
        user_id = session['db_user_id']
        app.logger.info(f'用户ID {user_id} 访问chart页面，查询命盘数据')
        
        # 获取命盘信息
        natal_chart = db.fetch_one("SELECT * FROM natal_charts WHERE user_id = %s", (user_id,))
        
        if not natal_chart:
            app.logger.warning(f'用户ID {user_id} 没有命盘数据，重定向到计算器页面')
            return redirect('/calculator')
        
        app.logger.info(f'为用户ID {user_id} 找到命盘数据，ID: {natal_chart["id"]}')
        
        # 将命盘对象转换为字典
        natal_chart_dict = dict(natal_chart)
        
        # 解析birth_data字段，获取八字信息
        birth_data_valid = False
        try:
            birth_data = json.loads(natal_chart_dict.get('birth_data', '{}'))
            
            # 验证birth_data的完整性
            required_birth_fields = ['year', 'month', 'day', 'hour']
            missing_fields = [field for field in required_birth_fields if field not in birth_data or not birth_data[field]]
            
            if missing_fields:
                app.logger.warning(f'birth_data缺少字段: {missing_fields}，数据: {birth_data}')
            else:
                birth_data_valid = True
                app.logger.info(f'成功解析birth_data且数据完整: {birth_data}')
            
            natal_chart_dict['birth_year'] = birth_data.get('year')
            natal_chart_dict['birth_month'] = birth_data.get('month')
            natal_chart_dict['birth_day'] = birth_data.get('day')
            natal_chart_dict['birth_hour'] = birth_data.get('hour')
        except json.JSONDecodeError as e:
            app.logger.error(f'解析birth_data失败: {e}，数据: {natal_chart_dict.get("birth_data")}')
        
        # 从users表获取补充信息
        user_info = db.fetch_one("SELECT birth_year, birth_month, birth_day, birth_hour, username FROM users WHERE id = %s", (user_id,))
        
        # 合并用户信息到命盘对象中（如果birth_data中没有的话）
        if user_info:
            app.logger.info(f'成功获取用户补充信息: {user_info.get("username")}')
            for key, value in user_info.items():
                if key == 'username':
                    natal_chart_dict['username'] = value
                elif (key in natal_chart_dict and (natal_chart_dict[key] is None or natal_chart_dict[key] == '')) or key not in natal_chart_dict:
                    natal_chart_dict[key] = value
        else:
            app.logger.warning(f'未找到用户ID {user_id} 的补充信息')
        
        # 确保chart_result字段被传递给前端模板
        chart_result = natal_chart.get('chart_result', '')
        chart_result_valid = False
        
        if not chart_result:
            app.logger.error(f'命盘ID {natal_chart["id"]} 的chart_result为空')
        elif len(chart_result) < 100:
            app.logger.warning(f'命盘ID {natal_chart["id"]} 的chart_result可能不完整，长度: {len(chart_result)}')
        else:
            # 检查内容质量（包含关键信息）
            keywords = ['五行', '生肖', '八字', '紫微', '运势']
            found_keywords = [kw for kw in keywords if kw in chart_result]
            if len(found_keywords) >= 2:
                chart_result_valid = True
                app.logger.info(f'命盘分析结果质量良好，包含关键词: {found_keywords}')
            else:
                app.logger.warning(f'命盘分析结果可能信息不足，只包含关键词: {found_keywords}')
        
        natal_chart_dict['chart_result'] = chart_result
        
        # 添加数据有效性标志
        natal_chart_dict['data_valid'] = birth_data_valid and chart_result_valid
        natal_chart_dict['validation_info'] = {
            'birth_data_valid': birth_data_valid,
            'chart_result_valid': chart_result_valid,
            'chart_result_length': len(chart_result)
        }
        
        app.logger.info(f'成功构建命盘数据，准备渲染chart页面')
        return render_template('chart.html', natal_chart=natal_chart_dict)
    except Exception as e:
        app.logger.error(f"访问/chart路由时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return f"发生错误: {str(e)}", 500

@app.route('/chat')
def chat_page():
    # 检查是否已登录
    if not session.get('logged_in'):
        return redirect('/login')
    
    user_id = session['user_id']
    
    # 获取命盘信息
    natal_chart = db.fetch_one("SELECT chart_result FROM natal_charts WHERE user_id = %s", (user_id,))
    
    if not natal_chart:
        return redirect('/calculator')
    
    return render_template('chat.html')


if __name__ == '__main__':
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)