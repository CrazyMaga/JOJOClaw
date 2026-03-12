# -*- coding: utf-8 -*-
import tushare as ts
import os
from datetime import datetime, timedelta

token = os.getenv('TUSHARE_TOKEN')
pro = ts.pro_api(token)

today = datetime.now().strftime('%Y-%m-%d')
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')

print('='*60)
print('  股票初筛报告', today)
print('='*60)

# Get main board stocks (exclude ChiNext, STAR, BJ)
print()
print('[1] 筛选主板股票')
stocks = pro.stock_basic(list_status='L', fields='ts_code,symbol,name,industry,market')
main_board = stocks[stocks['symbol'].str.match(r'^(600|601|603|605|000|001|002)', na=False)]
print(f'  主板股票数量: {len(main_board)}')

# Get yesterday trading data
print()
print('[2] 昨日交易数据')
daily = pro.daily(trade_date=yesterday)
if not daily.empty:
    daily_main = daily[daily['ts_code'].isin(main_board['ts_code'])]
    print(f'  主板有交易股票数: {len(daily_main)}')

# Screening criteria
print()
print('[3] 初筛条件')
print('  - 主板股票 (排除创业板/科创板/北交所)')
print('  - 涨幅 3%-9% (排除涨停)')
print('  - 成交额 > 1亿元')
print('  - 排除ST股票')

# Apply filters
if not daily.empty:
    # Exclude limit-up (>9.9%)
    filtered = daily_main[daily_main['pct_chg'] < 9.9]
    # Only positive change >3%
    filtered = filtered[filtered['pct_chg'] > 3]
    # Amount > 100M
    filtered = filtered[filtered['amount'] > 100000000]
    
    # Get top 20
    top20 = filtered.nlargest(20, 'pct_chg')
    
    print()
    print(f'[4] 初筛结果: {len(top20)} 只')
    print(f'  {"代码":<12} {"名称":<10} {"收盘价":<8} {"涨幅":<8} {"成交额(亿)"}')
    print('  ' + '-'*60)
    for _, row in top20.iterrows():
        name = main_board[main_board['ts_code']==row['ts_code']]['name'].values
        name = name[0] if len(name) > 0 else row['ts_code']
        amount = row['amount']/100000000
        print(f'  {row["ts_code"]:<12} {name:<10} {row["close"]:<8.2f} {row["pct_chg"]:>+6.2f}% {amount:>8.2f}')

# Additional screening: Volume surge
print()
print('[5] 成交量突增筛选 (放量>2倍)')
day_before = (datetime.now() - timedelta(days=2)).strftime('%Y%m%d')
daily_yesterday = pro.daily(trade_date=yesterday)
daily_2days = pro.daily(trade_date=day_before)

if not daily_yesterday.empty and not daily_2days.empty:
    merged = daily_yesterday[daily_yesterday['ts_code'].isin(main_board['ts_code'])]
    merged = merged.merge(daily_2days[['ts_code', 'vol']], on='ts_code', suffixes=('', '_2'))
    merged['vol_ratio'] = merged['vol'] / merged['vol_2'].replace(0, 1)
    
    # Volume surge > 2x and positive change
    surge = merged[(merged['vol_ratio'] > 2) & (merged['pct_chg'] > 0)]
    surge = surge.nlargest(10, 'vol_ratio')
    
    print(f'  {"代码":<12} {"名称":<10} {"涨幅":<8} {"成交量倍数"}')
    print('  ' + '-'*45)
    for _, row in surge.iterrows():
        name = main_board[main_board['ts_code']==row['ts_code']]['name'].values
        name = name[0] if len(name) > 0 else row['ts_code']
        print(f'  {row["ts_code"]:<12} {name:<10} {row["pct_chg"]:>+6.2f}% {row["vol_ratio"]:>8.2f}x')

print()
print('='*60)
print('初筛完成!')
print('='*60)
