import tushare as ts
import datetime

TUSHARE_TOKEN = "03eed883a368f22668fd2e781d1002fe2445dc3bde2c48db43a8f6b9"

def get_detailed_stock_analysis():
    """获取详细股票分析数据"""
    try:
        ts.set_token(TUSHARE_TOKEN)
        pro = ts.pro_api()
        
        # 获取昨天日期
        yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y%m%d")
        
        # 推荐股票列表
        stocks = [
            ("601778.SH", "晶科科技"),
            ("601868.SH", "中国能建"),
            ("002506.SZ", "协鑫集成"),
            ("601016.SH", "节能风电"),
            ("002467.SZ", "二六三")
        ]
        
        print("=== 推荐股票详细分析 ===\n")
        
        for code, name in stocks:
            try:
                # 获取日线数据
                df = pro.daily(ts_code=code, trade_date=yesterday)
                if not df.empty:
                    row = df.iloc[0]
                    open_price = row['open']
                    high = row['high']
                    low = row['low']
                    close = row['close']
                    pre_close = row['pre_close']
                    change = row['change']
                    pct_chg = row['pct_chg']
                    vol = row['vol']
                    amount = row['amount']
                    
                    print(f"【{code} {name}】")
                    print(f"  昨收: {pre_close:.2f} 元")
                    print(f"  开盘: {open_price:.2f} 元")
                    print(f"  最高: {high:.2f} 元")
                    print(f"  最低: {low:.2f} 元")
                    print(f"  收盘: {close:.2f} 元")
                    print(f"  涨跌: {change:.2f} 元 ({pct_chg:+.2f}%)")
                    print(f"  成交量: {vol/10000:.0f} 万手")
                    print(f"  成交额: {amount/10000:.0f} 万元")
                    
                    # 简单预测
                    if pct_chg > 9:
                        print(f"  📈 预测: 强势涨停，次日可能高开，关注是否能连板")
                    elif pct_chg > 5:
                        print(f"  📈 预测: 强势上涨，次日可能惯性冲高，注意获利回吐")
                    elif pct_chg > 0:
                        print(f"  📊 预测: 温和上涨，次日可能震荡整理")
                    else:
                        print(f"  📉 预测: 需要观察，次日可能继续调整")
                    
                    print()
            except Exception as e:
                print(f"  获取 {code} 数据失败: {e}\n")
        
        print("=== 分析完成 ===")
        
    except Exception as e:
        print(f"分析失败: {str(e)}")

if __name__ == "__main__":
    get_detailed_stock_analysis()
