import akshare as ak

print('上证指数 (000001.SH) 今日行情')
print('='*60)

try:
    # 获取上证指数实时行情
    df = ak.stock_zh_index_daily(symbol='sh000001')
    if df is not None and len(df) > 0:
        # 获取最近5个交易日数据
        recent = df.tail(5)
        print(recent.to_string())
        print()
        # 最新数据
        latest = df.iloc[-1]
        print(f"最新交易日: {latest.name}")
        print(f"开盘价: {latest['open']}")
        print(f"收盘价: {latest['close']}")
        print(f"最高价: {latest['high']}")
        print(f"最低价: {latest['low']}")
        print(f"成交量: {latest['volume']}")
    else:
        print('暂无数据')
except Exception as e:
    print(f'错误: {e}')
    import traceback
    traceback.print_exc()
