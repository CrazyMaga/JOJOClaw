#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
量化评分脚本 (增强版)
对股票初筛结果进行量化评分
评分体系：满分100分，可细化到小数点后一位
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


def get_trading_dates():
    """获取交易日列表"""
    today = datetime.datetime.now().strftime('%Y%m%d')
    start_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y%m%d')
    trade_cal = pro.trade_cal(exchange='SSE', start_date=start_date, end_date=today)
    trade_dates = sorted(trade_cal[trade_cal['is_open'] == 1]['cal_date'].tolist())
    return trade_dates[-10:] if len(trade_dates) >= 10 else trade_dates


def get_bulk_daily(trade_dates):
    """批量获取多日行情"""
    all_data = []
    for date in trade_dates:
        try:
            df = pro.daily(trade_date=date)
            if not df.empty:
                df['trade_date'] = date
                all_data.append(df)
        except:
            pass
    return pd.concat(all_data) if all_data else None


def get_bulk_basic():
    """批量获取股票基本信息"""
    try:
        return pro.stock_basic(fields='ts_code,name,industry,market,list_date')
    except:
        return None


def score_stocks():
    """对股票进行评分"""
    print("=" * 60)
    print("量化评分系统 (增强版)")
    print("=" * 60)
    
    # 读取初筛结果
    today = datetime.datetime.now().strftime('%Y%m%d')
    filename = f'stock_filter_result_{today}.json'
    
    if not os.path.exists(filename):
        yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y%m%d')
        filename = f'stock_filter_result_{yesterday}.json'
    
    if not os.path.exists(filename):
        alt_filename = os.path.join(os.path.dirname(__file__), '..', 'stock-filter', 'stock_filter_result.json')
        alt_filename = os.path.normpath(alt_filename)
        if os.path.exists(alt_filename):
            filename = alt_filename
    
    if not os.path.exists(filename):
        print("未找到初筛结果，请先运行股票初筛技能")
        return []
    
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, dict) and 'stocks' in data:
        stocks = data['stocks']
    else:
        stocks = data
    
    print(f"读取初筛结果: {len(stocks)} 只股票")
    
    # 批量获取数据
    dates = get_trading_dates()
    print(f"获取交易日: {dates[-5:]}")
    
    bulk_data = get_bulk_daily(dates)
    stock_basic = get_bulk_basic()
    
    results = []
    for i, stock in enumerate(stocks, 1):
        if i % 100 == 0:
            print(f"  已处理 {i}/{len(stocks)}")
        
        ts_code = stock.get('ts_code', '')
        
        # 初始化各项得分
        scores = {}
        
        if bulk_data is not None:
            stock_data = bulk_data[bulk_data['ts_code'] == ts_code].sort_values('trade_date', ascending=False)
            
            # ========== 1. 流动性保障 (15分) ==========
            amount = stock.get('amount', 0)
            if amount >= 100000000:
                scores['流动性保障'] = 15.0
            elif amount >= 50000000:
                scores['流动性保障'] = 12.0 + (amount - 50000000) / 50000000 * 3
            elif amount >= 20000000:
                scores['流动性保障'] = 8.0 + (amount - 20000000) / 30000000 * 4
            elif amount >= 10000000:
                scores['流动性保障'] = 5.0 + (amount - 10000000) / 10000000 * 3
            else:
                scores['流动性保障'] = amount / 10000000 * 5
            scores['流动性保障'] = round(min(scores['流动性保障'], 15.0), 1)
            
            # ========== 2. 相对强度 (15分) - 近5日涨幅 ==========
            if len(stock_data) >= 2:
                change_5d = (stock_data['close'].iloc[0] - stock_data['close'].iloc[-1]) / stock_data['close'].iloc[-1] * 100
                if change_5d > 10:
                    scores['相对强度'] = 15.0
                elif change_5d > 7:
                    scores['相对强度'] = 12.0 + (change_5d - 7) / 3 * 3
                elif change_5d > 5:
                    scores['相对强度'] = 10.0 + (change_5d - 5) / 2 * 2
                elif change_5d > 3:
                    scores['相对强度'] = 7.0 + (change_5d - 3) / 2 * 3
                elif change_5d > 0:
                    scores['相对强度'] = 3.0 + change_5d / 3 * 4
                else:
                    scores['相对强度'] = max(0, 3.0 + change_5d / 10 * 3)
            else:
                scores['相对强度'] = 0.0
            scores['相对强度'] = round(scores['相对强度'], 1)
            
            # ========== 3. 趋势强度 (20分) - 均线多头排列 ==========
            if len(stock_data) >= 20:
                prices = stock_data.head(20)['close'].values
                ma5 = prices[:5].mean()
                ma10 = prices[:10].mean()
                ma20 = prices.mean()
                current = prices[0]
                
                # 多头排列得分
                if current > ma5 > ma10 > ma20:
                    scores['趋势强度'] = 20.0
                elif current > ma5 > ma10:
                    scores['趋势强度'] = 16.0 + (current - ma5) / ma5 * 4
                elif current > ma5:
                    scores['趋势强度'] = 12.0 + (current - ma5) / ma5 * 4
                elif current > ma10:
                    scores['趋势强度'] = 8.0 + (current - ma10) / ma10 * 4
                else:
                    scores['趋势强度'] = max(0, 5.0 + (current - ma20) / ma20 * 5)
            elif len(stock_data) >= 10:
                prices = stock_data.head(10)['close'].values
                ma5 = prices[:5].mean()
                ma10 = prices.mean()
                current = prices[0]
                
                if current > ma5 > ma10:
                    scores['趋势强度'] = 16.0
                elif current > ma5:
                    scores['趋势强度'] = 10.0 + (current - ma5) / ma5 * 6
                else:
                    scores['趋势强度'] = max(0, 5.0 + (current - ma10) / ma10 * 5)
            else:
                scores['趋势强度'] = 5.0
            scores['趋势强度'] = round(min(max(scores['趋势强度'], 0), 20.0), 1)
            
            # ========== 4. 资金活跃度 (15分) - 近5日平均成交额 ==========
            if len(stock_data) >= 5:
                avg_amount = stock_data.head(5)['amount'].mean()
                if avg_amount >= 100000000:
                    scores['资金活跃度'] = 15.0
                elif avg_amount >= 50000000:
                    scores['资金活跃度'] = 12.0 + (avg_amount - 50000000) / 50000000 * 3
                elif avg_amount >= 20000000:
                    scores['资金活跃度'] = 8.0 + (avg_amount - 20000000) / 30000000 * 4
                elif avg_amount >= 10000000:
                    scores['资金活跃度'] = 5.0 + (avg_amount - 10000000) / 10000000 * 3
                else:
                    scores['资金活跃度'] = avg_amount / 10000000 * 5
            else:
                scores['资金活跃度'] = 3.0
            scores['资金活跃度'] = round(min(scores['资金活跃度'], 15.0), 1)
            
            # ========== 5. 股性活跃 (15分) - 近期涨停次数 + 涨停幅度 ==========
            if len(stock_data) >= 5:
                limit_ups = stock_data[stock_data['pct_chg'] >= 9.9]
                limit_up_count = len(limit_ups)
                
                # 涨停次数得分
                if limit_up_count >= 3:
                    base_score = 12.0
                elif limit_up_count == 2:
                    base_score = 9.0
                elif limit_up_count == 1:
                    base_score = 6.0
                else:
                    base_score = 2.0
                
                # 涨停幅度额外加分
                if not limit_ups.empty:
                    max_limit_up = limit_ups['pct_chg'].max()
                    amplitude_bonus = min((max_limit_up - 9.9) / 0.1 * 0.5, 3.0)
                    scores['股性活跃'] = round(base_score + amplitude_bonus, 1)
                else:
                    scores['股性活跃'] = base_score
            else:
                scores['股性活跃'] = 1.0
            scores['股性活跃'] = round(min(scores['股性活跃'], 15.0), 1)
            
            # ========== 6. 风险控制 (20分) - 近10日最大回撤 + 波动率 ==========
            if len(stock_data) >= 10:
                prices = stock_data.head(10)['close'].values
                max_price = prices.max()
                min_price = prices.min()
                drawdown = (max_price - min_price) / max_price * 100
                
                # 回撤得分
                if drawdown <= 8:
                    drawdown_score = 12.0
                elif drawdown <= 15:
                    drawdown_score = 10.0 + (15 - drawdown) / 7 * 2
                elif drawdown <= 25:
                    drawdown_score = 6.0 + (25 - drawdown) / 10 * 4
                else:
                    drawdown_score = max(0, 6.0 - (drawdown - 25) / 10 * 6)
                
                # 波动率得分 (低波动更好)
                volatility = prices.std() / prices.mean() * 100
                if volatility <= 3:
                    vol_score = 8.0
                elif volatility <= 5:
                    vol_score = 6.0 + (5 - volatility) / 2 * 2
                elif volatility <= 8:
                    vol_score = 4.0 + (8 - volatility) / 3 * 2
                else:
                    vol_score = max(0, 4.0 - (volatility - 8) / 4 * 4)
                
                scores['风险控制'] = round(drawdown_score + vol_score, 1)
            else:
                scores['风险控制'] = 8.0
            scores['风险控制'] = round(min(scores['风险控制'], 20.0), 1)
            
            # ========== 7. 行业动量 (加分项, 5分) ==========
            if stock_basic is not None:
                stock_info = stock_basic[stock_basic['ts_code'] == ts_code]
                if not stock_info.empty:
                    industry = stock_info.iloc[0].get('industry', '')
                    # 热门行业加分
                    hot_industries = ['电力设备', '新能源', '半导体', '汽车', '医药', '计算机']
                    if industry in hot_industries:
                        scores['行业动量'] = 5.0
                    else:
                        scores['行业动量'] = 2.0
                else:
                    scores['行业动量'] = 0.0
            else:
                scores['行业动量'] = 0.0
            scores['行业动量'] = round(scores['行业动量'], 1)
        
        # 计算总分
        total_score = sum(scores.values())
        
        results.append({
            'ts_code': ts_code,
            'name': stock.get('name', ''),
            'industry': stock.get('industry', ''),
            'pct_chg': stock.get('pct_chg', 0),
            'amount': stock.get('amount', 0),
            'scores': scores,
            'total_score': round(total_score, 1)
        })
    
    # 按总分排序
    results.sort(key=lambda x: x['total_score'], reverse=True)
    
    return results


def main():
    """主函数"""
    results = score_stocks()
    
    if results:
        output_file = os.path.join(os.path.dirname(__file__), 'stock_scored_result.json')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n评分完成! 结果已保存到: {output_file}")
        print(f"共评分 {len(results)} 只股票")
        
        print("\n【评分TOP 10】")
        for i, r in enumerate(results[:10], 1):
            print(f"{i:2d}. {r['ts_code']} {r['name'][:8]:8s} 总分:{r['total_score']:5.1f}分")
        
        # 分数分布
        score_dist = {}
        for r in results:
            s = round(r['total_score'])
            score_dist[s] = score_dist.get(s, 0) + 1
        
        print("\n【分数分布 (前15)】")
        for s in sorted(score_dist.keys(), reverse=True)[:15]:
            print(f"  {s}分: {score_dist[s]}只")
    
    return results


if __name__ == "__main__":
    main()
