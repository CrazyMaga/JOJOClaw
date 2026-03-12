import akshare as ak
import pandas as pd

print('今日 A 股市场行情概览')
print('='*70)

# 1. 主要指数
print('\n【主要指数】')
indices = {
    '上证指数': 'sh000001',
    '深证成指': 'sz399001', 
    '创业板指': 'sz399006',
    '科创50': 'sh000688'
}

for name, code in indices.items():
    try:
        df = ak.stock_zh_index_daily(symbol=code)
        if len(df) > 0:
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            change = latest['close'] - prev['close']
            change_pct = (change / prev['close']) * 100
            print(f"{name}: {latest['close']:.2f} ({change:+.2f}, {change_pct:+.2f}%)")
    except:
        pass

# 2. 涨跌家数统计
print('\n【市场涨跌统计】')
try:
    # 获取当日所有股票行情
    df_all = ak.stock_zh_a_spot_em()
    up_count = len(df_all[df_all['涨跌幅'] > 0])
    down_count = len(df_all[df_all['涨跌幅'] < 0])
    flat_count = len(df_all[df_all['涨跌幅'] == 0])
    print(f"上涨: {up_count} 家")
    print(f"下跌: {down_count} 家")  
    print(f"平盘: {flat_count} 家")
except Exception as e:
    print(f"统计失败: {e}")

print('\n' + '='*70)
