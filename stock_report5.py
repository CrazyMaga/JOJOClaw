import tushare as ts

token = 'e71c793f44bc9d99bdd321ec7dc1ddbba53faf1a63278fabeae21b44'
pro = ts.pro_api(token)

# 1. 上证指数昨日行情
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

# 3. 获取主板股票 (上海60开头，深圳00/002开头)
print('\n=== 涨幅前50股票 ===')
df_daily = pro.daily(trade_date='20260310')
# 主板筛选条件：600/601/603/000/002开头
main_board = df_daily[df_daily['ts_code'].str.match(r'^(600|601|603|000|002)\d{3}')]
main_board = main_board.sort_values('pct_chg', ascending=False).head(50)
print(main_board[['ts_code','close','open','high','low','pct_chg','pre_close']].to_string())

# 排除ST
print('\n=== 短线精选10只 (排除ST) ===')
stock_df = pro.stock_basic(list_status='L', fields='ts_code,name')
stock_df = stock_df[~stock_df['name'].str.contains('ST|退', na=False)]
valid_codes = stock_df['ts_code'].tolist()
main_valid = main_board[main_board['ts_code'].isin(valid_codes)].head(10)
print(main_valid[['ts_code','pre_close','open','high','close','pct_chg']].to_string())

# 获取股票名称
print('\n=== 最终精选10只 ===')
for _, row in main_valid.iterrows():
    code = row['ts_code']
    name_row = stock_df[stock_df['ts_code'] == code]
    name = name_row['name'].values[0] if len(name_row) > 0 else 'N/A'
    print(f"{code} {name}: 前天收盘={row['pre_close']:.2f}, 昨日开盘={row['open']:.2f}, 最高={row['high']:.2f}, 收盘={row['close']:.2f}, 涨幅={row['pct_chg']:.2f}%")
