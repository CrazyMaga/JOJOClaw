#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
每日量化评分报告生成脚本
- 读取量化评分结果
- 输出前20只股票的详细信息
- 通过telegram发送报告
"""

import os
import sys
import json
import datetime
import tushare as ts
import warnings
warnings.filterwarnings('ignore')

# 设置控制台输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 设置Tushare Token (从环境变量读取)
TUSHARE_TOKEN = os.getenv('TUSHARE_TOKEN', '')
os.environ['TUSHARE_TOKEN'] = TUSHARE_TOKEN
pro = ts.pro_api(TUSHARE_TOKEN)


def get_latest_scored_file():
    """获取最新的量化评分结果文件"""
    # 优先读取 skills/quant-score 目录下的文件
    scored_file = 'skills/quant-score/stock_scored_result.json'
    if os.path.exists(scored_file):
        return scored_file
    
    # 备选：读取根目录的文件
    today = datetime.datetime.now().strftime('%Y%m%d')
    filename = f'stock_scored_{today}.json'
    if os.path.exists(filename):
        return filename
    
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y%m%d')
    filename = f'stock_scored_{yesterday}.json'
    if os.path.exists(filename):
        return filename
    
    return None


def get_valid_trading_date():
    """获取有效的交易日期（昨天和前天）"""
    today = datetime.datetime.now().strftime('%Y%m%d')
    start_date = (datetime.datetime.now() - datetime.timedelta(days=60)).strftime('%Y%m%d')
    trade_cal = pro.trade_cal(exchange='SSE', start_date=start_date, end_date=today)
    trade_dates = sorted(trade_cal[trade_cal['is_open'] == 1]['cal_date'].tolist())
    
    # 获取昨天有数据的交易日（跳过今天）
    yesterday = None
    day_before = None
    
    # 从后往前找，找到有数据的日期
    for i in range(len(trade_dates) - 1, -1, -1):
        date = trade_dates[i]
        # 跳过今天（因为可能没收盘没数据）
        if date == today:
            continue
        if yesterday is None:
            yesterday = date
        elif day_before is None:
            day_before = date
            break
    
    print(f"最近交易日: {trade_dates[-5:]}")
    print(f"使用日期: yesterday={yesterday}, day_before={day_before}")
    
    if yesterday and day_before:
        return yesterday, day_before
    return None, None


def get_stock_details(stock, yesterday, day_before):
    """获取股票详细数据"""
    ts_code = stock.get('ts_code', '')
    
    try:
        df_y = pro.daily(ts_code=ts_code, trade_date=yesterday)
        
        if not df_y.empty:
            y = df_y.iloc[0]
            return {
                'yesterday_open': float(y['open']),
                'yesterday_high': float(y['high']),
                'yesterday_close': float(y['close']),
                'yesterday_pct_chg': float(y['pct_chg']),
                'day_before_close': 0
            }
    except Exception as e:
        pass
    
    return {
        'yesterday_open': 0,
        'yesterday_high': 0,
        'yesterday_close': 0,
        'yesterday_pct_chg': stock.get('pct_chg', 0),
        'day_before_close': 0
    }


def generate_report():
    """生成报告"""
    print("=" * 60)
    print("每日量化评分报告生成")
    print("=" * 60)
    
    scored_file = get_latest_scored_file()
    if not scored_file:
        print("未找到量化评分结果文件")
        return None
    
    print(f"读取文件: {scored_file}")
    
    with open(scored_file, 'r', encoding='utf-8') as f:
        stocks = json.load(f)
    
    if not stocks:
        print("量化评分结果为空")
        return None
    
    top20 = stocks[:20]
    
    yesterday, day_before = get_valid_trading_date()
    if not yesterday:
        print("无法获取有效的交易日期")
        return None
    
    print(f"使用日期: yesterday={yesterday}, day_before={day_before}")
    
    results = []
    for stock in top20:
        ts_code = stock['ts_code']
        name = stock['name']
        total_score = stock['total_score']
        
        details = get_stock_details(stock, yesterday, day_before)
        
        results.append({
            'rank': len(results) + 1,
            'ts_code': ts_code,
            'name': name,
            'total_score': total_score,
            'day_before_close': details.get('day_before_close', 0),
            'yesterday_open': details.get('yesterday_open', 0),
            'yesterday_high': details.get('yesterday_high', 0),
            'yesterday_close': details.get('yesterday_close', 0),
            'yesterday_pct_chg': details.get('yesterday_pct_chg', 0)
        })
    
    return {
        'generated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'data_date': yesterday,
        'stocks': results
    }


def format_telegram_message(report):
    """格式化telegram消息"""
    if not report:
        return "未生成报告"
    
    lines = []
    lines.append("📊 *每日量化评分报告*")
    lines.append(f"📅 生成时间: {report['generated_at']}")
    lines.append(f"📈 数据日期: {report['data_date']}")
    lines.append("")
    lines.append("*量化评分 TOP 20*")
    lines.append("")
    
    for stock in report['stocks']:
        lines.append(
            f"{stock['rank']:2d}. *{stock['ts_code']} {stock['name']}* "
            f"得分: `{stock['total_score']}`分"
        )
        lines.append(
            f"    昨开: `{stock['yesterday_open']:.2f}` "
            f"昨收: `{stock['yesterday_close']:.2f}` "
            f"最高: `{stock['yesterday_high']:.2f}` "
            f"涨幅: `{stock['yesterday_pct_chg']:+.2f}%`"
        )
        lines.append("")
    
    return "\n".join(lines)


def main():
    """主函数"""
    report = generate_report()
    
    if not report:
        print("报告生成失败")
        sys.exit(1)
    
    message = format_telegram_message(report)
    print(message)
    
    # 保存消息到文件
    with open('daily_report_message.txt', 'w', encoding='utf-8') as f:
        f.write(message)
    
    print("\n消息已保存到 daily_report_message.txt")


if __name__ == "__main__":
    main()
