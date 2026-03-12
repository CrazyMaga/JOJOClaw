import tushare as ts

# 设置 Token
ts.set_token('a8045f6bdc487eddca70b235c8b16cc0e2b3fbcb862b2c48755f73fd')

# 获取上证指数行情 (指数代码：000001.SH)
print('上证指数 (000001.SH) 今日行情')
print('='*60)

try:
    df = ts.pro_bar(ts_code='000001.SH', start_date='20260310', end_date='20260310', freq='daily')
    if len(df) > 0:
        row = df.iloc[0]
        print(f"交易日期: {row['trade_date']}")
        print(f"开盘价: {row['open']}")
        print(f"最高价: {row['high']}")
        print(f"最低价: {row['low']}")
        print(f"收盘价: {row['close']}")
        print(f"前收盘价: {row['pre_close']}")
        print(f"涨跌额: {row['change']}")
        print(f"涨跌幅: {row['pct_chg']}%")
        print(f"成交量: {row['vol']}")
        print(f"成交额: {row['amount']}")
    else:
        print('暂无今日数据，可能市场未开盘或数据未更新')
except Exception as e:
    print(f'获取数据失败: {e}')
