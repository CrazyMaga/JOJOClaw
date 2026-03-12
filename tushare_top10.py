import tushare as ts
import datetime
import sys

TUSHARE_TOKEN = "03eed883a368f22668fd2e781d1002fe2445dc3bde2c48db43a8f6b9"
ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api()

def get_top10_limit_up():
    """查询今日涨停板 TOP10"""
    today = datetime.datetime.now().strftime("%Y%m%d")
    
    try:
        # 使用涨停价表查询
        df = pro.limit_list(trade_date=today, limit_type='U')
        
        if df.empty:
            return {"error": f"No limit up data for {today}"}
        
        # 按涨停时间排序，取前10
        df = df.sort_values('first_time').head(10)
        result = df.astype(str).to_dict(orient="records")
        return {"success": True, "data": result, "count": len(result)}
    except Exception as e:
        return {"error": str(e)}

def main():
    print(f"=== 查询今日涨停板 TOP10 ===\n")
    
    result = get_top10_limit_up()
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    print(f"[OK] Success! Retrieved {result['count']} records\n")
    print("--- 今日涨停板 TOP10 ---\n")
    
    for i, item in enumerate(result["data"], 1):
        code = item.get("ts_code", "N/A")
        name = item.get("name", "N/A")
        price = float(item.get("close", 0)) if item.get("close") else 0
        pct = float(item.get("pct_chg", 0)) if item.get("pct_chg") else 0
        first_time = item.get("first_time", "N/A")
        
        print(f"{i:2}. {code} | {name:8} | Close: {price:>6.2f} | Chg: +{pct:>5.2f}% | First: {first_time}")

if __name__ == "__main__":
    main()
