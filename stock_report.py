import tushare as ts
import pandas as pd

pro = ts.pro_api('e71c793f44bc9d99bdd321ec7dc1ddbba53faf1a63278fabeae21b44')

# 1. 获取上证指数昨日行情 (2026-03-11)
print("="*60)
print("1. 上证指数昨日行情 (2026-03-11):")
print("="*60)
df_sh = pro.index_daily(ts_code='000001.SH', start_date='20260311', end_date='20260311')
if not df_sh.empty:
    row = df_sh.iloc[0]
    print(f"开盘: {row['open']:.2f}")
    print(f"最高: {row['high']:.2f}")
    print(f"最低: {row['low']:.2f}")
    print(f"收盘: {row['close']:.2f}")
    print(f"涨跌幅: {row['pct_chg']:.2f}%")
    print(f"成交量: {row['vol']/10000:.2f}万手")
    print(f"成交额: {row['amount']/100000000:.2f}亿元")

# 2. 获取黄金价格
print("\n" + "="*60)
print("2. 黄金价格:")
print("="*60)
# 尝试贵金属现货
try:
    df_silver = pro.fut_daily(ts_code='AG2406.SHF', start_date='20260311', end_date='20260311')
    if not df_silver.empty:
        row = df_silver.iloc[0]
        print(f"白银AG2406:")
        print(f"  开盘: {row['open']:.2f}")
        print(f"  最高: {row['high']:.2f}")
        print(f"  最低: {row['low']:.2f}")
        print(f"  收盘: {row['close']:.2f}")
        print(f"  涨跌幅: {row['pct_chg']:.2f}%")
except:
    pass

# 尝试黄金期货
for code in ['AU2406.SHF', 'AU2409.SHF', 'AU2503.SHF']:
    df_gold = pro.fut_daily(ts_code=code, start_date='20260311', end_date='20260311')
    if not df_gold.empty:
        row = df_gold.iloc[0]
        print(f"\n黄金期货{code}:")
        print(f"  开盘: {row['open']:.2f}")
        print(f"  最高: {row['high']:.2f}")
        print(f"  最低: {row['low']:.2f}")
        print(f"  收盘: {row['close']:.2f}")
        print(f"  涨跌幅: {row['pct_chg']:.2f}%")
        break
else:
    print("黄金期货数据获取失败")

# 3. 获取昨日涨停股票 (2026-03-11)
print("\n" + "="*60)
print("3. 昨日涨停股票 (排除用):")
print("="*60)
df_limit = pro.daily(trade_date='20260311')
limit_up = df_limit[df_limit['pct_chg'] >= 9.9]
limit_up_codes = set(limit_up['ts_code'].tolist())
print(f"昨日涨停股票数量: {len(limit_up_codes)}")

# 4. 获取前天(2026-03-10)涨停的股票 (也要排除)
print("\n" + "="*60)
print("4. 前天涨停股票 (排除用):")
print("="*60)
df_limit_2 = pro.daily(trade_date='20260310')
limit_up_2 = df_limit_2[df_limit_2['pct_chg'] >= 9.9]
limit_up_2_codes = set(limit_up_2['ts_code'].tolist())
print(f"前天涨停股票数量: {len(limit_up_2_codes)}")

# 5. 合并排除列表
exclude_codes = limit_up_codes | limit_up_2_codes
print(f"需要排除的股票总数: {len(exclude_codes)}")

# 6. 获取昨日上涨股票，排除创业板/科创板和涨停股
print("\n" + "="*60)
print("5. 短线精选 (排除创业板/科创板/北交所/涨停股):")
print("="*60)
df_yesterday = pro.daily(trade_date='20260311')
# 过滤: 上涨但未涨停
df_filtered = df_yesterday[(df_yesterday['pct_chg'] > 0) & (df_yesterday['pct_chg'] < 9.9)]
# 排除涨停股
df_filtered = df_filtered[~df_filtered['ts_code'].isin(exclude_codes)]
# 排除创业板(300,301开头)和科创板(688开头)
df_filtered = df_filtered[~df_filtered['ts_code'].str.startswith('300')]
df_filtered = df_filtered[~df_filtered['ts_code'].str.startswith('301')]
df_filtered = df_filtered[~df_filtered['ts_code'].str.startswith('688')]
# 排除北交所(.BJ结尾)
df_filtered = df_filtered[~df_filtered['ts_code'].str.endswith('BJ')]
# 按涨幅排序
df_filtered = df_filtered.sort_values('pct_chg', ascending=False).head(20)

# 获取前天收盘价
df_before = pro.daily(trade_date='20260310')
results = []
for _, row in df_filtered.iterrows():
    code = row['ts_code']
    # 获取股票基本信息
    try:
        info = pro.stock_basic(ts_code=code, fields='ts_code,name,industry')
        name = info.iloc[0]['name'] if not info.empty else ''
        industry = info.iloc[0]['industry'] if 'industry' in info.columns else ''
    except:
        name = ''
        industry = ''
    
    # 前天收盘价
    before_row = df_before[df_before['ts_code'] == code]
    if before_row.empty:
        continue
    close_before = before_row.iloc[0]['close']
    
    results.append({
        'code': code,
        'name': name,
        'industry': industry,
        '前天收盘': close_before,
        '昨日开盘': row['open'],
        '昨日最高': row['high'],
        '昨日收盘': row['close'],
        '昨日涨幅': row['pct_chg']
    })

df_results = pd.DataFrame(results)
print(df_results.head(10).to_string())

# 保存结果供后续使用
df_results.head(10).to_csv('stock_selection.csv', index=False, encoding='utf-8-sig')
print("\n短线精选10只已保存")
