# -*- coding: utf-8 -*-
"""
股票初筛技能
使用Tushare对A股进行筛选，剔除不满足条件的股票

筛选条件（剔除以下股票）：
1. ST/*ST
2. 当日涨停或跌停
3. 创业板、科创板、北交所
4. 近10个交易日日均振幅 < 3%

处理方式：逐个比对每一只股票
"""
import tushare as ts
import os
from datetime import datetime, timedelta
import json

# 设置Tushare Token
TUSHARE_TOKEN = "e71c793f44bc9d99bdd321ec7dc1ddbba53faf1a63278fabeae21b44"
os.environ['TUSHARE_TOKEN'] = TUSHARE_TOKEN
pro = ts.pro_api(TUSHARE_TOKEN)

today = datetime.now().strftime('%Y-%m-%d')
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')

print('='*70)
print('  股票初筛报告', today)
print('='*70)

# Get all stocks
print()
print('[1] 获取所有A股')
stocks = pro.stock_basic(list_status='L', fields='ts_code,symbol,name,market')
print(f'  A股总数: {len(stocks)}')

# Get yesterday trading data
print()
print('[2] 获取昨日交易数据')
daily = pro.daily(trade_date=yesterday)
print(f'  昨日有行情股票数: {len(daily)}')

# Get 10 days trading data for volatility
print()
print('[3] 获取近10日交易数据')
days_10 = []
for i in range(1, 11):
    day = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
    days_10.append(day)

daily_10d = []
for day in days_10:
    df = pro.daily(trade_date=day)
    if not df.empty:
        daily_10d.append(df)
        print(f'  {day}: {len(df)}只')

# Calculate average volatility for each stock
print()
print('[4] 计算近10日日均振幅')
volatility_dict = {}

for df in daily_10d:
    for _, row in df.iterrows():
        ts_code = row['ts_code']
        # 振幅 = (最高价 - 最低价) / 开盘价 * 100
        if row['open'] > 0:
            vol = (row['high'] - row['low']) / row['open'] * 100
            if ts_code not in volatility_dict:
                volatility_dict[ts_code] = []
            volatility_dict[ts_code].append(vol)

# Calculate average volatility
avg_volatility = {}
for ts_code, vols in volatility_dict.items():
    avg_volatility[ts_code] = sum(vols) / len(vols)

print(f'  计算了 {len(avg_volatility)} 只股票的10日均振幅')

# 逐个比对筛选
print()
print('[5] 逐个比对筛选中...')

result = []
total = len(stocks)

for idx, stock in stocks.iterrows():
    ts_code = stock['ts_code']
    symbol = stock['symbol']
    name = stock['name']
    
    # 条件1: 排除ST/*ST
    if 'ST' in name or 'st' in name:
        continue
    
    # 条件2: 排除创业板(300/301)、科创板(688)、北交所(8/4)
    if symbol.startswith(('300', '301', '688', '8', '4')):
        continue
    
    # 条件3: 必须在主板 (上海600/601/603/605, 深圳000/001/002)
    if not symbol.startswith(('600', '601', '603', '605', '000', '001', '002')):
        continue
    
    # 条件4: 近10日日均振幅 < 3% - 剔除
    if ts_code in avg_volatility:
        if avg_volatility[ts_code] < 3:
            continue
    else:
        continue  # 没有10日数据则跳过
    
    # 获取该股票昨日行情
    stock_daily = daily[daily['ts_code'] == ts_code]
    if stock_daily.empty:
        continue
    
    row = stock_daily.iloc[0]
    pct_chg = row['pct_chg']
    
    # 条件5: 排除当日涨停(>=9.9%)或跌停(<= -9.9%)
    if pct_chg >= 9.9 or pct_chg <= -9.9:
        continue
    
    # 满足所有条件，加入结果
    result.append({
        'ts_code': ts_code,
        'name': name,
        'close': float(row['close']),
        'pct_chg': float(pct_chg),
        'amount': float(row['amount'] / 10000),  # 转换为万元
        'volatility': float(avg_volatility.get(ts_code, 0))
    })

print(f'  比对完成!')

# 按涨幅排序
result = sorted(result, key=lambda x: x['pct_chg'], reverse=True)

print()
print('[6] 初筛结果: {} 只股票'.format(len(result)))

# 保存结果到文件
output_file = os.path.join(os.path.dirname(__file__), 'stock_filter_result.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'date': today,
        'total_count': len(result),
        'stocks': result
    }, f, ensure_ascii=False, indent=2)

print(f'  结果已保存到: {output_file}')

# 显示前50只
top50 = result[:50]

print()
print('[7] 初筛结果 (前50只)')
print()
print(f'{"排名":<4} {"代码":<12} {"名称":<10} {"收盘":<8} {"涨幅":<8} {"10日均振幅(%)"}')
print('-'*60)

for rank, item in enumerate(top50, 1):
    print(f'{rank:<4} {item["ts_code"]:<12} {item["name"]:<10} {item["close"]:<8.2f} {item["pct_chg"]:>+6.2f}% {item["volatility"]:>10.2f}%')

print()
print('='*70)
print('初筛完成!')
print('='*70)
