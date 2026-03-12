import akshare as ak
import sys

def get_top10_gainers():
    """使用 AkShare 查询今日涨幅最大的股票"""
    try:
        # 获取所有 A 股实时行情
        df = ak.stock_zh_a_spot_em()
        
        if df is None or df.empty:
            return {"error": "No data available"}
        
        # 按涨跌幅排序，取前10
        df_top10 = df.nlargest(10, '涨跌幅')
        result = df_top10.astype(str).to_dict(orient="records")
        return {"success": True, "data": result, "count": len(result)}
    except Exception as e:
        return {"error": str(e)}

def main():
    print("=== Query Today Top 10 Gainers ===\n")
    
    result = get_top10_gainers()
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    print(f"[OK] Success! Retrieved {result['count']} records\n")
    print("--- Today Top 10 Gainers ---\n")
    
    for i, item in enumerate(result["data"], 1):
        code = item.get("代码", "N/A")
        name = item.get("名称", "N/A")
        price = item.get("最新价", "N/A")
        pct = item.get("涨跌幅", "N/A")
        
        print(f"{i:2}. {code} | {name:10} | Price: {price:>8} | Chg: {pct}%")

if __name__ == "__main__":
    main()
