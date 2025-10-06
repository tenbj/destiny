import os
import sys

if __name__ == '__main__':
    print("启动Destiny算命小程序...")
    print("正在加载依赖项...")
    
    try:
        # 导入必要的模块以验证安装
        import flask
        import mysql.connector
        import requests
        import sqlalchemy
        
        print("依赖项验证成功！")
        print("正在启动Flask应用...")
        
        # 运行Flask应用
        os.system(f"{sys.executable} app.py")
        
    except ImportError as e:
        print(f"依赖项安装不完整: {e}")
        print("请运行以下命令安装所有依赖：")
        print(f"{sys.executable} -m pip install -r requirements.txt")
        sys.exit(1)