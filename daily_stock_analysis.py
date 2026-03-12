#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日股市分析报告生成脚本
"""

import os
import sys
import json
import tushare as ts
import pandas as pd
from datetime import datetime, timedelta
import requests

# 获取Tushare token
token = os.getenv('TUSHARE_TOKEN')
if not token:
    print("错误: 未设置TUSHARE_TOKEN环境变量")
    sys.exit(1)

# 初始化pro接口
pro = ts.pro_api(token)

# 获取当前日期和前一天的日期
today = datetime.now().strftime('%Y%m%d')
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
trade_date = yesterday  # 使用昨天作为交易日

print(f"=== 每日股市分析报告 ===")
print(f"报告日期: {today}")
print(f"数据日期: {trade_date}")
print()

# ============================================================
# 1. 获取上证指数行情
# ============================================================
print("【1. 上证指数行情】")
try:
    # 获取上证指数日线数据
    sh_index = pro.index_daily(ts_code='000001.SH', start_date=trade_date, end_date=trade_date)
    if not sh_index.empty:
        row = sh_index.iloc[0]
        print(f"  日期: {row['trade_date']}")
        print(f"  开盘: {row['open']:.2f}")
        print(f"  收盘: {row['close']:.2f}")
        print(f"  最高: {row['high']:.2f}")
        print(f"  最低: {row['low']:.2f}")
        print(f"  涨跌额: {row.get('change', 0):.2f}")
        pct_chg = row.get('pct_chg', 0)
        print(f"  涨跌幅: {pct_chg:.2f}%")
        print(f"  成交量: {row['vol']/10000:.2f}万手")
        print(f"  成交额: {row['amount']/10000:.2f}亿元")
    else:
        print("  暂无数据")
except Exception as e:
    print(f"  获取上证指数数据失败: {e}")

print()

# ============================================================
# 2. 获取股票列表并筛选非创业板/科创板股票
# ============================================================
print("【2. 主板股票筛选】")
try:
    # 获取所有上市股票
    stocks = pro.stock_basic(list_status='L', fields='ts_code,symbol,name,area,industry,list_date,market')
    
    # 筛选主板股票（排除创业板300/301开头，科创板688开头，北交所8开头）
    # 主板股票: 上海600/601/603/605开头, 深圳000/001/002开头
    main_board = stocks[
        (stocks['symbol'].str.match(r'^(600|601|603|605|000|001|002)'))
    ].copy()
    
    print(f"  全市场股票总数: {len(stocks)}")
    print(f"  主板股票数量: {len(main_board)}")
    print(f"  主板占比: {len(main_board)/len(stocks)*100:.1f}%")
except Exception as e:
    print(f"  获取股票列表失败: {e}")
    main_board = pd.DataFrame()

print()

# ============================================================
# 3. 分析大宗交易、资金流向、股东增减持
# ============================================================

# 3.1 大宗交易
print("【3.1 大宗交易数据】")
try:
    block_trade = pro.block_trade(trade_date=trade_date)
    if not block_trade.empty:
        print(f"  大宗交易笔数: {len(block_trade)}")
        total_amount = block_trade['amount'].sum()
        print(f"  总成交金额: {total_amount/10000:.2f}万元")
        
        # 按股票统计
        top_stocks = block_trade.groupby('ts_code').agg({
            'amount': 'sum',
            'vol': 'sum',
            'name': 'first'
        }).sort_values('amount', ascending=False).head(5)
        
        print("  大宗交易金额TOP5:")
        for idx, (ts_code, row) in enumerate(top_stocks.iterrows(), 1):
            print(f"    {idx}. {row['name']}({ts_code}): {row['amount']/10000:.2f}万元")
    else:
        print("  暂无大宗交易数据")
except Exception as e:
    print(f"  获取大宗交易数据失败: {e}")

print()

# 3.2 资金流向
print("【3.2 资金流向数据】")
try:
    # 获取个股资金流向
    moneyflow = pro.moneyflow(trade_date=trade_date)
    if not moneyflow.empty:
        # 计算主力资金净流入（大单+特大单）
        moneyflow['main_net'] = moneyflow['buy_l_amount'] - moneyflow['sell_l_amount'] + \
                               moneyflow['buy_elg_amount'] - moneyflow['sell_elg_amount']
        
        # 获取净流入TOP10
        inflow_top = moneyflow.nlargest(5, 'main_net')[['ts_code', 'main_net']]
        print("  主力资金净流入TOP5:")
        for idx, row in inflow_top.iterrows():
            stock_name = main_board[main_board['ts_code'] == row['ts_code']]['name'].values
            name = stock_name[0] if len(stock_name) > 0 else row['ts_code']
            print(f"    {name}: {row['main_net']/10000:.2f}万元")
        
        # 获取净流出TOP10
        outflow_top = moneyflow.nsmallest(5, 'main_net')[['ts_code', 'main_net']]
        print("  主力资金净流出TOP5:")
        for idx, row in outflow_top.iterrows():
            stock_name = main_board[main_board['ts_code'] == row['ts_code']]['name'].values
            name = stock_name[0] if len(stock_name) > 0 else row['ts_code']
            print(f"    {name}: {row['main_net']/10000:.2f}万元")
    else:
        print("  暂无资金流向数据")
except Exception as e:
    print(f"  获取资金流向数据失败: {e}")

print()

# 3.3 股东增减持
print("【3.3 股东增减持数据】")
try:
    # 获取股东增减持数据
    holder_trade = pro.stk_holdertrade(start_date=trade_date, end_date=trade_date)
    if not holder_trade.empty:
        print(f"  增减持记录数: {len(holder_trade)}")
        
        # 增持记录
        buy_records = holder_trade[holder_trade['in_de'] == '增持']
        # 减持记录
        sell_records = holder_trade[holder_trade['in_de'] == '减持']
        
        print(f"  增持记录: {len(buy_records)}条")
        print(f"  减持记录: {len(sell_records)}条")
        
        if not buy_records.empty:
            print("  重要增持:")
            top_buy = buy_records.nlargest(3, 'change_vol')[['ts_code', 'name', 'change_vol', 'in_de']]
            for idx, row in top_buy.iterrows():
                print(f"    {row['name']}({row['ts_code']}): {row['in_de']}{row['change_vol']/10000:.2f}万股")
        
        if not sell_records.empty:
            print("  重要减持:")
            top_sell = sell_records.nlargest(3, 'change_vol')[['ts_code', 'name', 'change_vol', 'in_de']]
            for idx, row in top_sell.iterrows():
                print(f"    {row['name']}({row['ts_code']}): {row['in_de']}{row['change_vol']/10000:.2f}万股")
    else:
        print("  暂无股东增减持数据")
except Exception as e:
    print(f"  获取股东增减持数据失败: {e}")

print()

# ============================================================
# 4. 挑选潜力股并分析财务数据
# ============================================================
print("【4. 潜力股筛选与财务分析】")
try:
    # 获取主板股票的每日指标数据
    daily_basic = pro.daily_basic(trade_date=trade_date)
    
    # 筛选主板股票
    main_board_codes = main_board['ts_code'].tolist()
    main_daily = daily_basic[daily_basic['ts_code'].isin(main_board_codes)].copy()
    
    if not main_daily.empty:
        # 筛选条件：
        # 1. 市盈率在5-50之间（排除过高和负值）
        # 2. 市净率>0且<10
        # 3. 换手率>1%（有活跃度）
        # 4. 成交额>5000万
        
        filtered = main_daily[
            (main_daily['pe'] > 5) & (main_daily['pe'] < 50) &
            (main_daily['pb'] > 0) & (main_daily['pb'] < 10) &
            (main_daily['turnover_rate'] > 1) &
            (main_daily['amount'] > 5000)
        ].copy()
        
        # 按成交额排序取前10
        potential_stocks = filtered.nlargest(10, 'amount')
        
        print(f"  筛选条件: PE(5-50), PB(0-10), 换手率>1%, 成交额>5000万")
        print(f"  符合条件的股票: {len(filtered)}只")
        print(f"  推荐关注TOP10:")
        print()
        
        for idx, row in potential_stocks.iterrows():
            stock_info = main_board[main_board['ts_code'] == row['ts_code']]
            name = stock_info['name'].values[0] if not stock_info.empty else row['ts_code']
            industry = stock_info['industry'].values[0] if not stock_info.empty else '未知'
            
            print(f"  {list(potential_stocks.index).index(idx)+1}. {name} ({row['ts_code']})")
            print(f"     行业: {industry}")
            print(f"     市盈率PE: {row['pe']:.2f}")
            print(f"     市净率PB: {row['pb']:.2f}")
            print(f"     换手率: {row['turnover_rate']:.2f}%")
            print(f"     成交额: {row['amount']/10000:.2f}万元")
            print(f"     总市值: {row['total_mv']/10000:.2f}亿元")
            print()
        
        # 获取这些股票的财务指标
        print("  【财务指标分析】")
        for idx, row in potential_stocks.head(5).iterrows():
            try:
                fina = pro.fina_indicator(ts_code=row['ts_code'], limit=1)
                if not fina.empty:
                    f = fina.iloc[0]
                    stock_info = main_board[main_board['ts_code'] == row['ts_code']]
                    name = stock_info['name'].values[0] if not stock_info.empty else row['ts_code']
                    
                    print(f"  {name}:")
                    print(f"    ROE(净资产收益率): {f.get('roe', 'N/A')}%" if f.get('roe') else "    ROE: N/A")
                    print(f"    毛利率: {f.get('grossprofit_margin', 'N/A')}%" if f.get('grossprofit_margin') else "    毛利率: N/A")
                    print(f"    净利率: {f.get('netprofit_margin', 'N/A')}%" if f.get('netprofit_margin') else "    净利率: N/A")
                    print(f"    资产负债率: {f.get('debt_to_assets', 'N/A')}%" if f.get('debt_to_assets') else "    资产负债率: N/A")
                    print()
            except Exception as e:
                continue
    else:
        print("  暂无每日指标数据")
except Exception as e:
    print(f"  筛选潜力股失败: {e}")

print()

# ============================================================
# 5. 获取黄金价格
# ============================================================
print("【5. 黄金价格】")
try:
    # 获取上海黄金交易所数据
    sge_gold = pro.sge_daily(trade_date=trade_date, symbol='Au99.99')
    if not sge_gold.empty:
        row = sge_gold.iloc[0]
        print(f"  Au99.99黄金:")
        print(f"    开盘价: {row['open']:.2f}元/克")
        print(f"    收盘价: {row['close']:.2f}元/克")
        print(f"    最高价: {row['high']:.2f}元/克")
        print(f"    最低价: {row['low']:.2f}元/克")
        print(f"    成交量: {row['vol']:.2f}千克")
    else:
        print("  暂无黄金数据")
except Exception as e:
    print(f"  获取黄金价格失败: {e}")

print()

# ============================================================
# 6. 市场总结
# ============================================================
print("【6. 市场总结】")
try:
    # 获取市场每日交易统计
    daily_info = pro.daily_info(trade_date=trade_date)
    if not daily_info.empty:
        sh_data = daily_info[daily_info['exchange'] == 'SSE']
        sz_data = daily_info[daily_info['exchange'] == 'SZSE']
        
        if not sh_data.empty:
            print("  上海市场:")
            print(f"    成交金额: {sh_data.iloc[0]['amount']/100000000:.2f}亿元")
        if not sz_data.empty:
            print("  深圳市场:")
            print(f"    成交金额: {sz_data.iloc[0]['amount']/100000000:.2f}亿元")
except Exception as e:
    print(f"  获取市场统计失败: {e}")

print()
print("=" * 50)
print("报告生成完毕")
print("=" * 50)
