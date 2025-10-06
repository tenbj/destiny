import json
from db import Database

# 数据验证工具类
class DataValidator:
    def __init__(self):
        self.db = Database()
        self.validated_results = []
    
    # 验证natal_charts表中的所有命盘数据
    def validate_natal_charts(self):
        try:
            print("\n===== 开始验证命盘数据 =====")
            
            # 查询所有命盘数据
            natal_charts = self.db.fetch_query("SELECT * FROM natal_charts")
            
            if not natal_charts:
                print("数据库中没有命盘数据")
                return False
            
            print(f"找到 {len(natal_charts)} 条命盘数据")
            
            # 验证每条命盘数据
            for idx, chart in enumerate(natal_charts, 1):
                print(f"\n--- 验证命盘 #{idx} (ID: {chart.get('id')}) ---")
                result = self._validate_single_chart(chart)
                self.validated_results.append({
                    'chart_id': chart.get('id'),
                    'valid': result,
                    'user_id': chart.get('user_id')
                })
            
            # 输出验证统计
            self._print_validation_summary()
            return True
        
        except Exception as e:
            print(f"验证过程中发生错误: {e}")
            return False
        finally:
            self.db.close()
    
    # 验证单条命盘数据
    def _validate_single_chart(self, chart):
        is_valid = True
        
        # 验证必要字段存在
        required_fields = ['id', 'user_id', 'created_at', 'birth_data', 'chart_result']
        for field in required_fields:
            if field not in chart or chart[field] is None:
                print(f"  ❌ 缺失必要字段: {field}")
                is_valid = False
        
        # 验证birth_data格式
        if chart.get('birth_data'):
            try:
                birth_data_json = json.loads(chart['birth_data'])
                required_birth_fields = ['year', 'month', 'day', 'hour']
                for field in required_birth_fields:
                    if field not in birth_data_json:
                        print(f"  ❌ birth_data中缺失字段: {field}")
                        is_valid = False
                print(f"  ✅ birth_data格式正确: {birth_data_json}")
            except json.JSONDecodeError:
                print(f"  ❌ birth_data格式错误: {chart['birth_data']}")
                is_valid = False
        
        # 验证chart_result内容
        if chart.get('chart_result'):
            chart_len = len(chart['chart_result'])
            print(f"  ✅ chart_result存在，长度: {chart_len} 字符")
            
            # 检查内容质量（包含关键信息）
            keywords = ['五行', '生肖', '八字', '紫微', '运势']
            found_keywords = [kw for kw in keywords if kw in chart['chart_result']]
            if len(found_keywords) >= 2:
                print(f"  ✅ chart_result包含足够的命盘信息")
            else:
                print(f"  ⚠️ chart_result可能信息不足，只包含关键词: {', '.join(found_keywords)}")
        
        # 验证关联用户存在
        if chart.get('user_id'):
            user = self.db.fetch_one("SELECT * FROM users WHERE id = %s", (chart['user_id'],))
            if user:
                print(f"  ✅ 用户关联正确: ID={chart['user_id']}, 用户名={user.get('username')}")
            else:
                print(f"  ❌ 未找到关联用户: ID={chart['user_id']}")
                is_valid = False
        
        return is_valid
    
    # 打印验证摘要
    def _print_validation_summary(self):
        total = len(self.validated_results)
        valid = sum(1 for r in self.validated_results if r['valid'])
        invalid = total - valid
        
        print("\n===== 数据验证摘要 =====")
        print(f"总记录数: {total}")
        print(f"有效记录: {valid} ({valid/total*100:.1f}%)")
        print(f"无效记录: {invalid} ({invalid/total*100:.1f}%)")
        
        if invalid > 0:
            print("\n无效记录ID:")
            for r in self.validated_results:
                if not r['valid']:
                    print(f"  - 命盘ID: {r['chart_id']}, 用户ID: {r['user_id']}")
    
    # 修复无效数据（如果可能）
    def fix_invalid_data(self):
        try:
            print("\n===== 尝试修复无效数据 =====")
            
            # 这里可以实现具体的修复逻辑
            # 例如重新生成chart_result、修复birth_data等
            
            print("修复功能待实现")
        except Exception as e:
            print(f"修复过程中发生错误: {e}")

# 验证数据传输流程
def validate_data_flow():
    validator = DataValidator()
    
    # 1. 验证数据库中的命盘数据
    db_validation = validator.validate_natal_charts()
    
    # 2. 检查前端数据处理逻辑
    print("\n===== 前端数据处理逻辑检查 ====")
    print("1. 前端从data-chart-result属性提取命盘数据")
    print("2. extractFiveElements()函数负责提取五行属性")
    print("3. extractZodiacFromContent()函数负责提取生肖信息")
    print("4. 建议添加更多的错误处理和日志记录")
    
    # 3. 提供改进建议
    print("\n===== 数据传输改进建议 ====")
    print("1. 在服务器端添加更严格的数据验证")
    print("2. 为chart_result添加版本控制")
    print("3. 实现数据完整性检查机制")
    print("4. 添加数据传输日志记录")
    print("5. 优化前端错误处理，避免降级显示")
    
    return db_validation

if __name__ == '__main__':
    print("开始数据传输验证...")
    validate_data_flow()
    print("\n数据传输验证完成")