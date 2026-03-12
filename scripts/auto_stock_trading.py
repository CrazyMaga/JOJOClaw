import os
import json
import pandas as pd
import tushare as ts
from datetime import datetime, timedelta

# 配置文件路径
CONFIG_PATH = os.path.expanduser("~/.openclaw/workspace/data/stock_trading_config.json")
POSITIONS_PATH = os.path.expanduser("~/.openclaw/workspace/data/stock_positions.json")
HISTORY_PATH = os.path.expanduser("~/.openclaw/workspace/data/stock_trading_history.json")

# 初始化tushare
token = os.getenv('TUSHARE_TOKEN') or ts.get_token()
if not token:
    print("错误: 未设置TUSHARE_TOKEN环境变量")
    exit(1)
pro = ts.pro_api(token)

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_today_str():
    return datetime.now().strftime('%Y%m%d')

def get_today_trade_date():
    """获取今日交易日"""
    today = get_today_str()
    df = pro.trade_cal(exchange='SSE', start_date=today, end_date=today)
    if df.empty or df.iloc[0]['is_open'] == 0:
        return None
    return today

def get_top10_stocks():
    """获取今日推荐的10只股票（基于涨幅榜）"""
    today = get_today_str()
    try:
        # 获取上一个交易日
        cal = pro.trade_cal(exchange='SSE', end_date=today, limit=10)
        cal = cal[cal['is_open']==1]
        if cal.empty:
            print("未找到交易日")
            return []
        last_trade_date = cal.iloc[0]['cal_date']
        
        # 使用日线行情接口获取数据
        df = pro.daily(trade_date=last_trade_date, fields='ts_code,open,high,low,close,pre_close,change,pct_chg,vol,amount')
        
        # 转换amount为数值类型
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        df['pct_chg'] = pd.to_numeric(df['pct_chg'], errors='coerce')
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        
        # 获取股票基本信息
        df_basic = pro.stock_basic(exchange='', list_status='L', fields='ts_code,name')
        
        # 合并数据
        df_merged = df.merge(df_basic, on='ts_code', how='left')
        
        # 筛选条件：成交额大于1亿，非ST股票
        df_merged = df_merged[df_merged['amount'] > 100000]  # 千元单位
        df_merged = df_merged[~df_merged['name'].str.contains('ST', na=False)]
        
        # 按成交额排序，取前10
        df_top = df_merged.nlargest(10, 'amount')
        
        return df_top[['ts_code', 'name', 'open', 'high', 'low', 'close', 'pre_close', 'change', 'pct_chg', 'vol', 'amount']].to_dict('records')
    except Exception as e:
        print(f"获取股票列表失败: {e}")
        return []

def calculate_fees(amount, is_buy=True):
    """计算交易费用"""
    config = load_json(CONFIG_PATH)
    fees = config['fees']
    
    # 佣金
    commission = max(amount * fees['commission'], fees['min_commission'])
    
    # 印花税（仅卖出收取）
    stamp_tax = amount * fees['stamp_tax'] if not is_buy else 0
    
    total_fees = commission + stamp_tax
    return {
        'commission': round(commission, 2),
        'stamp_tax': round(stamp_tax, 2),
        'total': round(total_fees, 2)
    }

def can_sell(ts_code, buy_date):
    """检查是否可以卖出（T+1规则）"""
    today = get_today_str()
    buy_dt = datetime.strptime(buy_date, '%Y-%m-%d')
    today_dt = datetime.strptime(today, '%Y%m%d')
    return (today_dt - buy_dt).days >= 1

def execute_trade():
    """执行自动交易"""
    config = load_json(CONFIG_PATH)
    positions_data = load_json(POSITIONS_PATH)
    history = load_json(HISTORY_PATH)
    
    account = config['account']
    positions = positions_data['positions']
    buy_queue = positions_data['buy_queue']
    today = datetime.now().strftime('%Y-%m-%d')
    
    trade_log = []
    notifications = []
    
    # 1. 获取今日推荐股票
    print("="*60)
    print("【1】查询今日推荐10只股票的实时行情")
    print("="*60)
    
    top_stocks = get_top10_stocks()
    if not top_stocks:
        print("未能获取股票行情数据")
        return
    
    print(f"\n获取到 {len(top_stocks)} 只推荐股票:\n")
    print(f"{'代码':<12} {'名称':<10} {'最新价':<10} {'涨跌幅':<10} {'成交额(万)':<12}")
    print("-"*60)
    for s in top_stocks:
        amount_wan = s['amount'] / 100  # 转换为万元
        print(f"{s['ts_code']:<12} {s['name']:<10} {s['close']:<10.2f} {s['pct_chg']:<10.2f}% {amount_wan:<12.2f}")
    
    # 2. 根据涨跌判断买卖
    print("\n" + "="*60)
    print("【2】根据涨跌自动判断买卖")
    print("="*60)
    
    buy_candidates = []
    sell_candidates = []
    
    # 检查持仓，判断是否需要卖出
    for pos in positions[:]:
        ts_code = pos['ts_code']
        buy_price = pos['buy_price']
        buy_date = pos['buy_date']
        volume = pos['volume']
        
        # 获取当前价格
        cal = pro.trade_cal(exchange='SSE', end_date=get_today_str(), limit=5)
        cal = cal[cal['is_open']==1]
        last_trade_date = cal.iloc[0]['cal_date']
        df_rt = pro.daily(ts_code=ts_code, trade_date=last_trade_date, fields='ts_code,close,pct_chg')
        if df_rt.empty:
            continue
        
        current_price = df_rt.iloc[0]['close']
        pct_chg = df_rt.iloc[0]['pct_chg']
        
        # 计算持仓盈亏
        profit_pct = (current_price - buy_price) / buy_price * 100
        
        # 检查T+1规则
        if not can_sell(ts_code, buy_date):
            print(f"  {ts_code} {pos['name']}: 涨跌幅{pct_chg:.2f}%, 持仓盈亏{profit_pct:.2f}% - T+1限制，今日不可卖出")
            continue
        
        # 涨3%以上卖出
        if profit_pct >= config['strategy']['sell_threshold']:
            sell_candidates.append({
                'ts_code': ts_code,
                'name': pos['name'],
                'buy_price': buy_price,
                'current_price': current_price,
                'volume': volume,
                'profit_pct': profit_pct,
                'buy_date': buy_date
            })
    
    # 检查推荐股票，判断是否需要买入
    for s in top_stocks:
        ts_code = s['ts_code']
        name = s['name']
        pct_chg = s['pct_chg']
        current_price = s['close']
        
        # 跌2%以上买入
        if pct_chg <= config['strategy']['buy_threshold']:
            # 检查是否已持仓
            existing = [p for p in positions if p['ts_code'] == ts_code]
            if not existing:
                buy_candidates.append({
                    'ts_code': ts_code,
                    'name': name,
                    'current_price': current_price,
                    'pct_chg': pct_chg
                })
    
    print(f"\n卖出候选: {len(sell_candidates)} 只")
    for c in sell_candidates:
        print(f"  {c['ts_code']} {c['name']}: 持仓盈亏 +{c['profit_pct']:.2f}%")
    
    print(f"\n买入候选: {len(buy_candidates)} 只")
    for c in buy_candidates:
        print(f"  {c['ts_code']} {c['name']}: 跌幅 {c['pct_chg']:.2f}%")
    
    # 3. 执行交易并计算手续费
    print("\n" + "="*60)
    print("【3】执行交易并计算手续费")
    print("="*60)
    
    # 执行卖出
    for sell in sell_candidates:
        ts_code = sell['ts_code']
        volume = sell['volume']
        sell_price = sell['current_price']
        buy_price = sell['buy_price']
        
        sell_amount = sell_price * volume
        fees = calculate_fees(sell_amount, is_buy=False)
        net_amount = sell_amount - fees['total']
        
        profit = (sell_price - buy_price) * volume - fees['total']
        
        # 更新账户
        account['available_cash'] += net_amount
        
        # 移除持仓
        positions = [p for p in positions if p['ts_code'] != ts_code]
        
        # 记录交易
        trade_record = {
            'date': today,
            'ts_code': ts_code,
            'name': sell['name'],
            'action': 'SELL',
            'price': sell_price,
            'volume': volume,
            'amount': round(sell_amount, 2),
            'fees': fees,
            'profit': round(profit, 2),
            'profit_pct': round(sell['profit_pct'], 2)
        }
        history.append(trade_record)
        trade_log.append(trade_record)
        
        msg = f"【卖出】{ts_code} {sell['name']} - 价格:{sell_price:.2f} 数量:{volume} 金额:{sell_amount:.2f} 手续费:{fees['total']:.2f} 盈亏:{profit:.2f}"
        print(f"  ✓ {msg}")
        notifications.append(msg)
    
    # 执行买入
    for buy in buy_candidates:
        if len(positions) >= config['strategy']['max_positions']:
            print(f"  已达到最大持仓数量限制({config['strategy']['max_positions']}只)，停止买入")
            break
        
        ts_code = buy['ts_code']
        buy_price = buy['current_price']
        
        # 计算买入金额
        trade_amount = min(config['strategy']['trade_amount_per_buy'], account['available_cash'] * 0.9)
        if trade_amount < 10000:  # 最小买入金额1万
            print(f"  可用资金不足，停止买入")
            break
        
        volume = int(trade_amount / buy_price / 100) * 100  # 100股为单位
        if volume < 100:
            continue
        
        actual_amount = buy_price * volume
        fees = calculate_fees(actual_amount, is_buy=True)
        total_cost = actual_amount + fees['total']
        
        if total_cost > account['available_cash']:
            continue
        
        # 更新账户
        account['available_cash'] -= total_cost
        
        # 添加持仓
        positions.append({
            'ts_code': ts_code,
            'name': buy['name'],
            'buy_price': buy_price,
            'volume': volume,
            'buy_date': today,
            'cost': total_cost
        })
        
        # 添加到买入队列（用于T+1检查）
        buy_queue.append({
            'ts_code': ts_code,
            'buy_date': today
        })
        
        # 记录交易
        trade_record = {
            'date': today,
            'ts_code': ts_code,
            'name': buy['name'],
            'action': 'BUY',
            'price': buy_price,
            'volume': volume,
            'amount': round(actual_amount, 2),
            'fees': fees
        }
        history.append(trade_record)
        trade_log.append(trade_record)
        
        msg = f"【买入】{ts_code} {buy['name']} - 价格:{buy_price:.2f} 数量:{volume} 金额:{actual_amount:.2f} 手续费:{fees['total']:.2f}"
        print(f"  ✓ {msg}")
        notifications.append(msg)
    
    # 4. T+1规则说明
    print("\n" + "="*60)
    print("【4】T+1规则检查")
    print("="*60)
    print("  今日买入的股票，需下一个交易日才能卖出")
    print(f"  今日买入队列: {len([b for b in buy_queue if b['buy_date'] == today])} 只")
    for b in buy_queue:
        if b['buy_date'] == today:
            print(f"    - {b['ts_code']} (买入日期: {b['buy_date']}, 可卖出日期: 明天)")
    
    # 清理过期的买入队列记录
    buy_queue = [b for b in buy_queue if (datetime.strptime(today, '%Y-%m-%d') - datetime.strptime(b['buy_date'], '%Y-%m-%d')).days < 2]
    
    # 5. 同步通知
    print("\n" + "="*60)
    print("【5】交易通知")
    print("="*60)
    if notifications:
        for msg in notifications:
            print(f"  📢 {msg}")
    else:
        print("  今日无交易")
    
    # 6. 记录交易历史
    print("\n" + "="*60)
    print("【6】交易历史记录")
    print("="*60)
    print(f"  本次交易记录数: {len(trade_log)}")
    print(f"  累计交易记录数: {len(history)}")
    
    # 更新持仓市值
    total_position_value = 0
    cal = pro.trade_cal(exchange='SSE', end_date=get_today_str(), limit=5)
    cal = cal[cal['is_open']==1]
    last_trade_date = cal.iloc[0]['cal_date']
    for pos in positions:
        df_rt = pro.daily(ts_code=pos['ts_code'], trade_date=last_trade_date, fields='ts_code,close')
        if not df_rt.empty:
            current_price = df_rt.iloc[0]['close']
            total_position_value += current_price * pos['volume']
    
    account['total_value'] = account['available_cash'] + total_position_value
    account['total_profit'] = account['total_value'] - config['account']['initial_capital']
    account['total_profit_pct'] = (account['total_profit'] / config['account']['initial_capital']) * 100
    
    # 保存数据
    config['account'] = account
    save_json(CONFIG_PATH, config)
    save_json(POSITIONS_PATH, {'positions': positions, 'buy_queue': buy_queue, 'date': today})
    save_json(HISTORY_PATH, history)
    
    # 输出账户总结
    print("\n" + "="*60)
    print("【账户总结】")
    print("="*60)
    print(f"  初始资金: {config['account']['initial_capital']:.2f}")
    print(f"  可用现金: {account['available_cash']:.2f}")
    print(f"  持仓市值: {total_position_value:.2f}")
    print(f"  总资产:   {account['total_value']:.2f}")
    print(f"  总盈亏:   {account['total_profit']:.2f} ({account['total_profit_pct']:.2f}%)")
    print(f"  当前持仓: {len(positions)} 只")
    if positions:
        print("\n  持仓明细:")
        cal = pro.trade_cal(exchange='SSE', end_date=get_today_str(), limit=5)
        cal = cal[cal['is_open']==1]
        last_trade_date = cal.iloc[0]['cal_date']
        for pos in positions:
            df_rt = pro.daily(ts_code=pos['ts_code'], trade_date=last_trade_date, fields='ts_code,close')
            current_price = df_rt.iloc[0]['close'] if not df_rt.empty else pos['buy_price']
            profit_pct = (current_price - pos['buy_price']) / pos['buy_price'] * 100
            print(f"    {pos['ts_code']} {pos['name']}: {pos['volume']}股 成本{pos['buy_price']:.2f} 现价{current_price:.2f} 盈亏{profit_pct:+.2f}%")

if __name__ == '__main__':
    execute_trade()
