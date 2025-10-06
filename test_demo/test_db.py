import mysql.connector
from mysql.connector import Error
import time
import sys
import os

# 添加上级目录到路径，以便导入config模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_CONFIG

class TestDatabase:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.connect()
        self.create_test_table()
    
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
            print("测试数据库连接成功")
        except Error as e:
            print(f"测试数据库连接失败: {e}")
    
    def create_test_table(self):
        if not self.connection or not self.connection.is_connected():
            self.connect()
        
        create_test_table_sql = """
        CREATE TABLE IF NOT EXISTS test (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        try:
            self.cursor.execute(create_test_table_sql)
            self.connection.commit()
            print("测试表创建成功")
        except Error as e:
            print(f"创建测试表失败: {e}")
    
    def insert_data(self, name, date):
        if not self.connection or not self.connection.is_connected():
            self.connect()
        
        insert_sql = "INSERT INTO test (name, date) VALUES (%s, %s)"
        try:
            self.cursor.execute(insert_sql, (name, date))
            self.connection.commit()
            print(f"数据插入成功，ID: {self.cursor.lastrowid}")
            return True
        except Error as e:
            print(f"数据插入失败: {e}")
            return False
    
    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("测试数据库连接已关闭")