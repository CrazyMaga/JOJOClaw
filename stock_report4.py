import tushare as ts
import os

token = 'e71c793f44bc9d99bdd321ec7dc1ddbba53faf1a63278fabeae21b44'
pro = ts.pro_api(token)

# 1. 获取上证指数昨日行情
print('=== 上证指数昨日行情 (20260310) ===')
df = pro.index_daily(ts_code='000001.SH', start_date='20260309', end_date='20260310')
for _, row in df.iterrows():
    if row['trade_date'] == '20260310':
        print(f"开盘: {row['open']}, 收盘: {row['close']}, 最高: {row['high']}, 最低: {row['low']}, 涨跌幅: {row['pct_chg']}%")

# 2. 黄金价格
print('\n=== 黄金价格 (Au99.99) ===')
df_gold = pro.sge_daily(trade_date='20260310')
gold_row = df_gold[df_gold['ts_code'] == 'Au99.99']
print(f"开盘: {gold_row['open'].values[0]}, 收盘: {gold_row['close'].values[0]}, 最高: {gold_row['high'].values[0]}, 最低: {gold_row['low'].values[0]}")

# 3. 获取所有A股涨跌幅数据
print('\n=== 涨幅前30股票 ===')
df_daily = pro.daily(trade_date='20260310')
df_daily = df_daily.sort_values('pct_chg', ascending=False).head(30)
print(df_daily[['ts_code','close','open','high','low','pct_chg','pre_close']].to_string())

# 4. 筛选条件：排除创业板、科创板、北交所、ST
print('\n=== 短线精选10只 (排除创业板/科创板/北交所/ST) ===')
stock_df = pro.stock_basic(list_status='L', fields='ts_code,symbol,name')
stock_df = stock_df[~stock_df['ts_code'].str.startswith(('300','301','688','8','4'))]
stock_df = stock_df[~stock_df['name'].str.contains('ST|退', na=False)]
valid_codes = stock_df['ts_code'].tolist()

df_daily_valid = df_daily[df_daily['ts_code'].isin(valid_codes)].head(10)
print(df_daily_valid[['ts_code','pre_close','open','high','close','pct_chg']].to_string())
