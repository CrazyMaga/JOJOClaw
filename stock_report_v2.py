# -*- coding: utf-8 -*-
import tushare as ts
import os
from datetime import datetime, timedelta

token = os.getenv('TUSHARE_TOKEN')
pro = ts.pro_api(token)

today = datetime.now().strftime('%Y-%m-%d')
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
day_before = (datetime.now() - timedelta(days=2)).strftime('%Y%m%d')

print('='*60)
print('  Daily Stock Report', today)
print('='*60)

# 1. Shanghai Index
print()
print('[1] Shanghai Index')
sh = pro.index_daily(ts_code='000001.SH', start_date=yesterday, end_date=yesterday)
if not sh.empty:
    r = sh.iloc[0]
    print(f'  Close: {r["close"]:.2f}')
    print(f'  Open: {r["open"]:.2f}')
    print(f'  High: {r["high"]:.2f}')
    print(f'  Low: {r["low"]:.2f}')
    print(f'  Change: {r["pct_chg"]:+.2f}%')
    print(f'  Amount: {r["amount"]/100000000:.2f}B CNY')

# 2. Gold Price
print()
print('[2] Gold Price')
gold = pro.sge_daily(trade_date=yesterday, symbol='Au99.99')
if not gold.empty:
    g = gold.iloc[0]
    print(f'  Au99.99 Close: {g["close"]:.2f} CNY/g')
else:
    print('  No data')

# 3. Top 10 (exclude limit-up)
print()
print('[3] Top 10 (Exclude Limit-Up Stocks)')
stocks = pro.stock_basic(list_status='L', fields='ts_code,symbol,name')
main_board = stocks[stocks['symbol'].str.match(r'^(600|601|603|605|000|001|002)', na=False)]

daily = pro.daily(trade_date=yesterday)
if not daily.empty:
    # Filter out limit-up (>9.9%)
    daily = daily[daily['pct_chg'] < 9.9]
    # Main board only
    daily = daily[daily['ts_code'].isin(main_board['ts_code'])]
    # Top 10
    top10 = daily.nlargest(10, 'pct_chg')
    
    print(f'  {"Code":<12} {"Name":<10} {"Close":<8} {"Change"}')
    print('  ' + '-'*45)
    for _, row in top10.iterrows():
        name = main_board[main_board['ts_code']==row['ts_code']]['name'].values
        name = name[0] if len(name) > 0 else row['ts_code']
        print(f'  {row["ts_code"]:<12} {name:<10} {row["close"]:<8.2f} {row["pct_chg"]:+.2f}%')

print()
print('='*60)
print('Done!')
print('='*60)
