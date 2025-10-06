import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.connect()
        self.initialize_database()
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=DB_CONFIG['host'],
                port=DB_CONFIG['port'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database']
            )
            self.cursor = self.connection.cursor(dictionary=True)
            print("数据库连接成功")
        except Error as e:
            print(f"数据库连接失败: {e}")
            # 尝试创建database
            try:
                temp_conn = mysql.connector.connect(
                    host=DB_CONFIG['host'],
                    port=DB_CONFIG['port'],
                    user=DB_CONFIG['user'],
                    password=DB_CONFIG['password']
                )
                temp_cursor = temp_conn.cursor()
                temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
                temp_conn.close()
                print(f"创建数据库 {DB_CONFIG['database']} 成功")
                # 重新连接
                self.connect()
            except Error as e:
                print(f"创建数据库失败: {e}")
    
    def initialize_database(self):
        if not self.connection or not self.connection.is_connected():
            self.connect()
        
        # 创建用户表
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            birth_year INT DEFAULT NULL,
            birth_month INT DEFAULT NULL,
            birth_day INT DEFAULT NULL,
            birth_hour INT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """
        
        # 确保password字段存在（修复已有表结构问题）
        add_password_column = """
        ALTER TABLE users 
        ADD COLUMN password VARCHAR(255) NOT NULL DEFAULT 'default_password'
        """
        
        # 创建对话表
        create_conversations_table = """
        CREATE TABLE IF NOT EXISTS conversations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            query TEXT NOT NULL,
            response TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
        
        # 创建命盘表
        create_natal_charts_table = """
        CREATE TABLE IF NOT EXISTS natal_charts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            birth_data TEXT NOT NULL,
            chart_result TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE KEY unique_user (user_id)
        )
        """
        
        try:
            self.cursor.execute(create_users_table)
            self.cursor.execute(create_conversations_table)
            self.cursor.execute(create_natal_charts_table)
            self.connection.commit()
            print("数据库表创建成功")
        except Error as e:
            print(f"创建数据库表失败: {e}")
            self.connection.rollback()
        
        # 单独处理password字段添加，即使失败也不影响其他功能
        try:
            self.cursor.execute(add_password_column)
            self.connection.commit()
            print("成功添加password字段")
        except Error as e:
            # 如果字段已存在，忽略这个错误
            if "Duplicate column name" in str(e):
                print("password字段已存在")
            else:
                print(f"添加password字段失败: {e}")
            # 不回滚整个事务，只回滚这个操作
            self.connection.rollback()
    
    def execute_query(self, query, params=None):
        if not self.connection or not self.connection.is_connected():
            self.connect()
        
        try:
            self.cursor.execute(query, params or ())
            self.connection.commit()
            return True
        except Error as e:
            print(f"执行查询失败: {e}")
            self.connection.rollback()
            return False
    
    def fetch_query(self, query, params=None):
        if not self.connection or not self.connection.is_connected():
            self.connect()
        
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        except Error as e:
            print(f"获取数据失败: {e}")
            return []
    
    def fetch_one(self, query, params=None):
        if not self.connection or not self.connection.is_connected():
            self.connect()
        
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchone()
        except Error as e:
            print(f"获取单条数据失败: {e}")
            return None
    
    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("数据库连接已关闭")