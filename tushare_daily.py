import tushare as ts
import datetime

# 核心配置
TUSHARE_TOKEN = "03eed883a368f22668fd2e781d1002fe2445dc3bde2c48db43a8f6b9"
DEFAULT_STOCK_CODE = "000001.SZ"  # 平安银行
DEFAULT_DAYS = 30

# 初始化
ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api()

def get_stock_daily(ts_code=DEFAULT_STOCK_CODE, days=DEFAULT_DAYS):
    start_date = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime("%Y%m%d")
    end_date = datetime.datetime.now().strftime("%Y%m%d")
    
    try:
        df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        
        if df.empty:
            return f"未查询到 {ts_code} 在 {start_date} 至 {end_date} 的日线数据"
        
        df = df.sort_values(by="trade_date", ascending=False)
        result_df = df.astype(str)  # 转换所有列为字符串
        return result_df.to_json(orient="records", force_ascii=False)
    except Exception as e:
        return f"获取日线数据失败：{str(e)}"

if __name__ == "__main__":
    print("=== 股票日线行情查询结果 ===")
    result = get_stock_daily()
    print(result)
