"""
QVeris 股票查询脚本 - 查询 A 股涨停板信息
"""

import os
import subprocess
import sys
import json
import re

# QVeris API Key
API_KEY = "sk-t4J_cA3WIBtXqf3DXUWMZAW80WIOydDTH35tB1WmJzA"


def search_qveris(query: str, limit: int = 5):
    """搜索 QVeris 工具"""
    os.environ["QVERIS_API_KEY"] = API_KEY
    
    try:
        result = subprocess.run(
            ["python", "C:/Users/yezhihong/.openclaw/workspace/skills/qveris/scripts/qveris_tool.py", 
             "search", query, "--limit", str(limit), "--json"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"搜索失败：{result.stderr}")
            return None
    except Exception as e:
        print(f"发生错误：{e}")
        return None


def execute_tool(tool_id: str, search_id: str, params: dict):
    """执行 QVeris 工具"""
    os.environ["QVERIS_API_KEY"] = API_KEY
    
    try:
        result = subprocess.run(
            ["python", "C:/Users/yezhihong/.openclaw/workspace/skills/qveris/scripts/qveris_tool.py", 
             "execute", tool_id, "--search-id", search_id, "--params", json.dumps(params), "--json"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"执行失败：{result.stderr}")
            return None
    except Exception as e:
        print(f"发生错误：{e}")
        return None


def query_a_share_limit_up():
    """查询今日 A 股涨停板"""
    print("="*50)
    print("📈 正在查询今日 A 股涨停板信息...")
    print("="*50)
    
    # 搜索股票相关的工具
    search_query = "A 股涨停板查询 real-time stock price limit up"
    print(f"\n🔍 搜索中：{search_query}")
    
    search_result = search_qveris(search_query, limit=5)
    
    if not search_result:
        print("❌ 未找到合适的工具，尝试使用 AkShare 直接查询...")
        return query_with_akshare()
    
    tools = search_result.get("results", [])
    
    if not tools:
        print("❌ 没有可用的股票数据工具")
        return None
    
    # 显示找到的工具
    print(f"\n📋 找到 {len(tools)} 个相关工具：")
    for i, tool in enumerate(tools[:3], 1):
        print(f"\n{i}. {tool.get('name', 'Unknown')}")
        print(f"   - 成功率：{tool.get('success_rate', 'N/A')}")
        print(f"   - 平均执行时间：{tool.get('avg_execution_time', 'N/A')}")
    
    # 尝试执行找到的第一个工具
    if tools:
        tool_id = tools[0].get("id")
        search_id = tools[0].get("search_id")
        
        print(f"\n⚡ 正在执行工具：{tool_id}")
        
        params = {
            "market": "A 股",
            "stock_type": "主板",
            "limit_up_only": True,
            "today_date": get_today_date()
        }
        
        result = execute_tool(tool_id, search_id, params)
        
        if result and "result" in result:
            return format_result(result["result"])
        else:
            print("❌ 工具执行失败")
            return None
    
    return None


def get_today_date():
    """获取今天的日期"""
    from datetime import datetime
    today = datetime.now()
    return today.strftime("%Y-%m-%d")


def format_result(data):
    """格式化涨停板数据"""
    print("\n" + "="*50)
    print("🎯 今日 A 股涨停板 TOP10")
    print("="*50)
    
    if isinstance(data, list) and len(data) > 0:
        print(f"\n{'排名':<6} {'股票代码':<12} {'股票名称':<10} {'涨停价':<10} {'涨跌幅'}")
        print("-" * 58)
        
        for i, stock in enumerate(data[:10], 1):
            code = stock.get("code", "N/A")
            name = stock.get("name", "N/A")
            price = f"¥{stock.get('price', 'N/A'):,.2f}"
            pct = f"+{stock.get('change_pct', 'N/A')}%"
            
            print(f"{i:<6} {code:<12} {name:<10} {price:<10} {pct}")
    else:
        print("\n未获取到涨停板数据")
    
    return data


def query_with_akshare():
    """使用 AkShare 查询涨停板（备用方案）"""
    try:
        import akshare as aks
        
        print("\n⏳ 正在使用 AkShare 查询 A 股涨停板...")
        
        # 查询涨停和跌停的股票
        df = aks.stock_zt_stock_em(limit=10)
        
        if not df.empty:
            print("\n" + "="*50)
            print("🎯 今日 A 股涨停榜 TOP10")
            print("="*50)
            
            cols = ['stock_code', 'name', 'price', 'pct_chg']
            df_display = df[cols].rename(columns={
                'stock_code': '股票代码',
                'name': '股票名称',
                'price': '涨停价',
                'pct_chg': '涨跌幅'
            })
            
            print(f"\n{'排名':<6} {'股票代码':<12} {'股票名称':<10} {'涨停价':<10} {'涨跌幅'}")
            print("-" * 58)
            
            for i, row in df_display.head(10).iterrows():
                print(f"{i+1:<6} {row['股票代码']:<12} {row['股票名称']:<10} "
                      f"¥{float(row['涨停价']):>9.2f} {float(row['涨跌幅']):+.2f}%")
            
            return df.to_dict('records')
        
        print("未获取到涨停数据")
        return []
    except Exception as e:
        print(f"AkShare 查询失败：{e}")
        return None


if __name__ == "__main__":
    # 运行查询
    result = query_a_share_limit_up()
    
    if result:
        print("\n✅ 查询完成！")
    else:
        print("\n⚠️ 未找到可用的股票数据源，建议安装 Tushare 或配置其他数据接口。")
