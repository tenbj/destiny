import json
from db import Database

# 检查数据库中的命盘数据
def check_natal_charts():
    db = Database()
    
    try:
        # 查询所有命盘数据
        print("查询数据库中的命盘数据...")
        natal_charts = db.fetch_query("SELECT * FROM natal_charts")
        
        if not natal_charts:
            print("数据库中没有命盘数据")
            return
        
        print(f"找到 {len(natal_charts)} 条命盘数据")
        
        # 查看第一条命盘数据的详细信息
        first_chart = natal_charts[0]
        print("\n第一条命盘数据详情：")
        print(f"ID: {first_chart.get('id')}")
        print(f"用户ID: {first_chart.get('user_id')}")
        print(f"创建时间: {first_chart.get('created_at')}")
        
        # 解析birth_data
        birth_data = first_chart.get('birth_data')
        if birth_data:
            try:
                birth_data_json = json.loads(birth_data)
                print(f"出生数据: {birth_data_json}")
            except json.JSONDecodeError:
                print(f"出生数据格式错误: {birth_data}")
        else:
            print("没有出生数据")
        
        # 查看chart_result
        chart_result = first_chart.get('chart_result')
        if chart_result:
            print(f"命盘分析结果长度: {len(chart_result)} 字符")
            print("命盘分析结果前200字符: ")
            print(chart_result[:200] + '...')
        else:
            print("没有命盘分析结果")
            
        # 检查用户信息
        user_id = first_chart.get('user_id')
        if user_id:
            user = db.fetch_one("SELECT * FROM users WHERE id = %s", (user_id,))
            if user:
                print(f"\n用户信息: {user.get('username')}")
                print(f"用户出生信息: {user.get('birth_year')}年{user.get('birth_month')}月{user.get('birth_day')}日{user.get('birth_hour')}时")
            else:
                print(f"未找到用户ID为 {user_id} 的用户信息")
        
    except Exception as e:
        print(f"查询数据库时发生错误: {e}")
    finally:
        db.close()

if __name__ == '__main__':
    print("开始检查数据库中的命盘数据...")
    check_natal_charts()
    print("检查完成")