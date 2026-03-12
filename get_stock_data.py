import os
import tushare as ts

# Initialize Tushare with token
ts.set_token('e71c793f44bc9d99bdd321ec7dc1ddbba53faf1a63278fabeae21b44')
pro = ts.pro_api()

# Get Shanghai Composite Index (上证指数) data
# Yesterday = March 10, 2026
print("=== 上证指数 (3月10日) ===")
try:
    index_df = pro.index_daily(ts_code='000001.SH', start_date='20260309', end_date='20260310')
    print(index_df.to_string())
except Exception as e:
    print(f"Error: {e}")

# Get Gold price (上海黄金)
print("\n=== 黄金价格 (3月10日) ===")
try:
    gold_df = pro.sge_daily(trade_date='20260310')
    print(gold_df.to_string())
except Exception as e:
    print(f"Error: {e}")

# Get stock list (exclude 创业板, 科创板, 北交所, ST)
print("\n=== 短线精选股票池 ===")
try:
    stock_df = pro.stock_basic(list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    # Filter: exclude 30* (创业板), 68* (科创板), 8* (北交所), 4* (北交所)
    stock_df = stock_df[~stock_df['symbol'].str.startswith(('30', '68', '8', '4'))]
    # Exclude ST
    stock_df = stock_df[~stock_df['name'].str.contains('ST|退', na=False, regex=True)]
    print(f"Total stocks after filter: {len(stock_df)}")
    print(stock_df.head(30).to_string())
except Exception as e:
    print(f"Error: {e}")
