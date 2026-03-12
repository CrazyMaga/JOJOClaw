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
    
    # 涨幅榜前10
    print('\n【涨幅榜 TOP 10】')
    top10 = df.nlargest(10, '涨跌幅')[['名称', '最新价', '涨跌幅', '成交额']]
    for idx, row in top10.iterrows():
        print(f"{row['名称']}: {row['最新价']} ({row['涨跌幅']:+.2f}%) - 成交: {row['成交额']/10000:.0f}万")
    
    # 跌幅榜前5
    print('\n【跌幅榜 TOP 5】')
    bottom5 = df.nsmallest(5, '涨跌幅')[['名称', '最新价', '涨跌幅']]
    for idx, row in bottom5.iterrows():
        print(f"{row['名称']}: {row['最新价']} ({row['涨跌幅']:+.2f}%)")
    
except Exception as e:
    print(f'Error: {e}')

print('\n' + '='*70)
print('数据来源: 东方财富 | 更新时间: 2026-03-10')
print('='*70)
