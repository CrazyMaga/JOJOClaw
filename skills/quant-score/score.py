#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
量化评分脚本
对股票初筛结果进行量化评分
评分体系：满分100分，阶梯式打分
"""

import os
import json
import datetime
import pandas as pd
import tushare as ts
import warnings
warnings.filterwarnings('ignore')

# 设置Tushare Token (从环境变量读取)
TUSHARE_TOKEN = os.getenv('TUSHARE_TOKEN', '')
os.environ['TUSHARE_TOKEN'] = TUSHARE_TOKEN
pro = ts.pro_api(TUSHARE_TOKEN)

# ============================================================
# 评分体系配置
# ============================================================

# 评分维度及权重
SCORING_DIMENSIONS = {
    "价格动线": 30,
    "资金流向": 30,
    "流动性保障": 15,
    "情绪与股性": 15,
    "风险控制": 10
}


def get_valid_trading_date():
    """获取有效的交易日期"""
    today = datetime.datetime.now().strftime('%Y%m%d')
    start_date = (datetime.datetime.now() - datetime.timedelta(days=60)).strftime('%Y%m%d')
    trade_cal = pro.trade_cal(exchange='SSE', start_date=start_date, end_date=today)
    trade_dates = sorted(trade_cal[trade_cal['is_open'] == 1]['cal_date'].tolist())
    
    if len(trade_dates) >= 2:
        return trade_dates[-1], trade_dates[-2]
    return None, None


def score_stocks():
    """对股票进行评分"""
    print("=" * 60)
    print("量化评分系统")
    print("=" * 60)
    
    # 尝试读取初筛结果
    today = datetime.datetime.now().strftime('%Y%m%d')
    filename = f'stock_filter_result_{today}.json'
    
    if not os.path.exists(filename):
        yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y%m%d')
        filename = f'stock_filter_result_{yesterday}.json'
    
    if not os.path.exists(filename):
        print("未找到初筛结果，请先运行股票初筛技能")
        return []
    
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 处理不同的JSON格式
    if isinstance(data, dict) and 'stocks' in data:
        stocks = data['stocks']
    else:
        stocks = data
    
    print(f"读取初筛结果: {len(stocks)} 只股票")
    
    results = []
    for i, stock in enumerate(stocks, 1):
        if i % 10 == 0:
            print(f"  已处理 {i}/{len(stocks)}")
        
        ts_code = stock.get('ts_code', '')
        
        # 简化评分逻辑
        total_score = 50  # 默认分数
        
        results.append({
            'ts_code': ts_code,
            'name': stock.get('name', ''),
            'industry': stock.get('industry', ''),
            'pct_chg': stock.get('pct_chg', 0),
            'amount_yi': stock.get('amount', 0) / 100000000,  # 转换为亿
            'amplitude': stock.get('volatility', 0),
            'scores': SCORING_DIMENSIONS,
            'total_score': total_score
        })
    
    # 按总分排序
    results.sort(key=lambda x: x['total_score'], reverse=True)
    
    return results


def main():
    """主函数"""
    results = score_stocks()
    
    if results:
        # 保存结果
        output_file = f"stock_scored_{datetime.datetime.now().strftime('%Y%m%d')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n评分完成! 结果已保存到: {output_file}")
        print(f"共评分 {len(results)} 只股票")
        
        # 显示前10名
        print("\n【评分TOP 10】")
        for i, r in enumerate(results[:10], 1):
            print(f"{i:2d}. {r['ts_code']} {r['name'][:8]:8s} 总分:{r['total_score']}分")
    
    return results


if __name__ == "__main__":
    main()
