# -*- coding: utf-8 -*-
"""
股票量化评分系统
综合评分 = 涨幅分 + 成交量分 + 资金流向分 + 形态分
"""
import tushare as ts
import os
from datetime import datetime, timedelta
import pandas as pd

token = os.getenv('TUSHARE_TOKEN')
pro = ts.pro_api(token)

today = datetime.now().strftime('%Y-%m-%d')
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
day_before = (datetime.now() - timedelta(days=2)).strftime('%Y%m%d')

print('='*70)
print('  股票量化评分报告', today)
print('='*70)

# Get main board stocks
stocks = pro.stock_basic(list_status='L', fields='ts_code,symbol,name,industry,market')
main_board = stocks[stocks['symbol'].str.match(r'^(600|601|603|605|000|001|002)', na=False)]
main_codes = main_board['ts_code'].tolist()

# Get trading data
daily_y = pro.daily(trade_date=yesterday)
daily_2 = pro.daily(trade_date=day_before)

if daily_y.empty or daily_2.empty:
    print('Data not available')
    exit(1)

# Filter main board
daily_y = daily_y[daily_y['ts_code'].isin(main_codes)]
daily_2 = daily_2[daily_2['ts_code'].isin(main_codes)]

# Merge data
df = daily_y.merge(daily_2[['ts_code', 'vol', 'close', 'pct_chg']], 
                   on='ts_code', suffixes=('', '_2'))

# Calculate metrics
# 1. 涨幅得分 (0-25)
df['pct_score'] = df['pct_chg'].clip(0, 10) / 10 * 25

# 2. 成交量突增得分 (0-25)
df['vol_ratio'] = df['vol'] / df['vol_2'].replace(0, 1)
df['vol_score'] = df['vol_ratio'].clip(0, 5) / 5 * 25

# 3. 成交额得分 (0-25)
df['amount_score'] = (df['amount'] / df['amount'].max() * 25).fillna(0)

# 4. 形态得分 - 阳线+放量 (0-25)
df['shape_score'] = 0
df.loc[(df['close'] > df['open']) & (df['vol'] > df['vol_2']), 'shape_score'] = 25

# Total score
df['total_score'] = df['pct_score'] + df['vol_score'] + df['amount_score'] + df['shape_score']

# Filter: exclude limit-up stocks, positive change
df_filtered = df[(df['pct_chg'] < 9.9) & (df['pct_chg'] > 0)]

# Get top 15
top_stocks = df_filtered.nlargest(15, 'total_score')

print()
print('[量化评分 TOP 15]')
print(f'{"排名":<4} {"代码":<12} {"名称":<10} {"收盘":<8} {"涨幅":<8} {"量比":<6} {"总分":<6}')
print('-'*70)

for rank, (_, row) in enumerate(top_stocks.iterrows(), 1):
    name = main_board[main_board['ts_code']==row['ts_code']]['name'].values
    name = name[0] if len(name) > 0 else row['ts_code']
    print(f'{rank:<4} {row["ts_code"]:<12} {name:<10} {row["close"]:<8.2f} {row["pct_chg"]:>+6.2f}% {row["vol_ratio"]:>5.2f}x {row["total_score"]:>5.1f}')

# Detailed analysis for top 5
print()
print('[TOP 5 详细分析]')
print('='*70)

for rank, (_, row) in enumerate(top_stocks.head(5).iterrows(), 1):
    name = main_board[main_board['ts_code']==row['ts_code']]['name'].values
    name = name[0] if len(name) > 0 else row['ts_code']
    industry = main_board[main_board['ts_code']==row['ts_code']]['industry'].values
    industry = industry[0] if len(industry) > 0 else '未知'
    
    print(f'''
{rank}. {name} ({row['ts_code']})
   行业: {industry}
   收盘价: {row['close']:.2f}
   涨跌幅: {row['pct_chg']:+.2f}%
   成交量: {row['vol']/10000:.2f}万手
   成交量倍数: {row['vol_ratio']:.2f}x
   成交额: {row['amount']/100000000:.2f}亿元
   
   量化得分:
   - 涨幅分: {row['pct_score']:.1f}/25
   - 成交量分: {row['vol_score']:.1f}/25
   - 成交额分: {row['amount_score']:.1f}/25
   - 形态分: {row['shape_score']:.1f}/25
   - 总分: {row['total_score']:.1f}/100
''')

# Get moneyflow data if available
print()
print('[资金流向参考]')
try:
    moneyflow = pro.moneyflow(trade_date=yesterday)
    if not moneyflow.empty:
        mf = moneyflow[moneyflow['ts_code'].isin(top_stocks.head(5)['ts_code'])]
        if not mf.empty:
            for _, m in mf.iterrows():
                name = main_board[main_board['ts_code']==m['ts_code']]['name'].values
                name = name[0] if len(name) > 0 else m['ts_code']
                print(f'  {name}: 主力净流入 {m.get("main_net", 0)/10000:.2f}万元')
except:
    print('  资金流向数据获取失败')

print()
print('='*70)
print('量化评分完成!')
print('='*70)
