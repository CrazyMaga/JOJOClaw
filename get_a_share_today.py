import akshare as ak

print('='*70)
print('今日 A 股市场行情')
print('='*70)

# 获取实时行情
try:
    df = ak.stock_zh_a_spot_em()
    
    # 主要指数
    print('\n【主要指数】')
    indices = {
        '上证指数': 'sh000001',
        '深证成指': 'sz399001',
        '创业板指': 'sz399006',
        '科创50': 'sh000688'
    }
    
    for name, code in indices.items():
        try:
            idx_df = ak.stock_zh_index_daily(symbol=code)
            if len(idx_df) > 0:
                latest = idx_df.iloc[-1]
                prev = idx_df.iloc[-2] if len(idx_df) > 1 else latest
                change = latest['close'] - prev['close']
                pct = (change / prev['close']) * 100
                print(f"{name}: {latest['close']:.2f} ({change:+.2f}, {pct:+.2f}%)")
        except:
            pass
    
    # 涨跌统计
    print('\n【涨跌统计】')
    up = len(df[df['涨跌幅'] > 0])
    down = len(df[df['涨跌幅'] < 0])
    flat = len(df[df['涨跌幅'] == 0])
    print(f'上涨: {up} 家')
    print(f'下跌: {down} 家')
    print(f'平盘: {flat} 家')
    
    # 成交额统计
    total_amount = df['成交额'].sum() / 100000000
    print(f'\n总成交额: {total_amount:.2f} 亿元')
    
except Exception as e:
    print(f'Error: {e}')

print('\n' + '='*70)
print('数据来源: 东方财富 | 更新时间: 2026-03-10')
print('='*70)
