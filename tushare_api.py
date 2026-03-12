import tushare as ts
import datetime
import sys
import json

TUSHARE_TOKEN = "03eed883a368f22668fd2e781d1002fe2445dc3bde2c48db43a8f6b9"
DEFAULT_STOCK_CODE = "000001.SZ"

ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api()

def get_stock_daily(ts_code=DEFAULT_STOCK_CODE, days=30):
    start_date = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime("%Y%m%d")
    end_date = datetime.datetime.now().strftime("%Y%m%d")
    
    try:
        df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        
        if df.empty:
            return {"error": f"No data found for {ts_code}"}
        
        df = df.sort_values("trade_date", ascending=False)
        result = df.astype(str).to_dict(orient="records")
        return {"success": True, "data": result, "count": len(result)}
    except Exception as e:
        return {"error": str(e)}

def main():
    ts_code = sys.argv[1] if len(sys.argv) >= 2 else DEFAULT_STOCK_CODE
    days = int(sys.argv[2]) if len(sys.argv) >= 3 else 30
    
    print(f"=== Query Stock: {ts_code} ({days} days) ===")
    
    result = get_stock_daily(ts_code, days)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    print(f"\n[OK] Success! Retrieved {result['count']} records")
    print("\n--- Latest 5 Days ---")
    
    for i, item in enumerate(result["data"][:5], 1):
        date = item.get("trade_date", "N/A")
        close = float(item.get("close", 0)) if item.get("close") else 0
        pct = float(item.get("pct_chg", 0)) if item.get("pct_chg") else 0
        sign = "+" if pct >= 0 else ""
        
        print(f"{i}. {date} | Close: {close:>6.2f} USD | Chg: {sign}{pct:>5.2f}%")

if __name__ == "__main__":
    main()
