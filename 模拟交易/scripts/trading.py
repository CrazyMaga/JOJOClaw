#!/usr/bin/env python3
"""
A股模拟交易脚本 - 完整流程版
支持买入、卖出、查询资产、查看交易记录
自动获取实时股价，执行完整交易校验
"""

import json
import os
import sys
import re
import requests
from datetime import datetime, time

# 数据文件路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(os.path.dirname(SCRIPT_DIR), "data", "trading.json")

# 交易费用率
STAMP_DUTY = 0.001  # 印花税 (卖出时)
COMMISSION = 0.0002  # 佣金 (万分之2)
TRANSFER_FEE_SH = 0.00001  # 过户费 (沪市，万分之0.1)
TRANSFER_FEE_SZ = 0  # 深市过户费含在佣金中

# 涨跌幅限制
LIMIT_UP_ST = 0.05   # ST股票 ±5%
LIMIT_UP_MAIN = 0.10  # 主板 ±10%
LIMIT_UP_CY = 0.20   # 创业板/科创板 ±20%

# 交易时间
MARKET_OPEN_MORNING = time(9, 30)
MARKET_CLOSE_MORNING = time(11, 30)
MARKET_OPEN_AFTERNOON = time(13, 0)
MARKET_CLOSE = time(14, 57)

def load_data():
    """加载交易数据"""
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    """保存交易数据"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ========== 步骤1: 交易时间检查 ==========
def check_trading_time():
    """检查当前是否为交易时间"""
    if os.environ.get('TRADING_TEST') == '1':
        return True, "测试模式，跳过交易时间检查"
    
    now = datetime.now().time()
    
    # 9:15-9:25 集合竞价
    if time(9, 15) <= now <= time(9, 25):
        return True, "集合竞价时段 (9:15-9:25)"
    # 9:30-11:30 上午连续竞价
    if MARKET_OPEN_MORNING <= now <= MARKET_CLOSE_MORNING:
        return True, "连续竞价时段 (9:30-11:30)"
    # 13:00-14:57 下午连续竞价
    if MARKET_OPEN_AFTERNOON <= now <= MARKET_CLOSE:
        return True, "连续竞价时段 (13:00-14:57)"
    
    return False, f"不在交易时间内，当前时间: {now.strftime('%H:%M:%S')} (交易时间: 9:15-9:25, 9:30-11:30, 13:00-14:57)"

# ========== 步骤2: 获取实时股价 ==========
def get_realtime_price(stock_code):
    """从腾讯财经获取实时股价"""
    # 转换股票代码格式
    if stock_code.startswith('6'):
        code = f'sh{stock_code}'  # 沪市
    elif stock_code.startswith('0') or stock_code.startswith('3'):
        code = f'sz{stock_code}'  # 深市
    else:
        return None, f"不支持的股票代码: {stock_code}"
    
    try:
        url = f"https://qt.gtimg.cn/q={code}"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        # 使用latin1解码（腾讯返回GBK编码的字节流）
        text = resp.content.decode('latin1')
        
        if not text or text == 'null':
            return None, "未获取到股票数据"
        
        # 解析数据 v_sh600000="1~股票名称~代码~当前价格~昨收~今开~..."
        parts = text.split('~')
        if len(parts) >= 5:
            current_price = float(parts[3])
            pre_close = float(parts[4])
            return current_price, pre_close
        
        return None, "股票数据解析失败"
    except Exception as e:
        return None, f"获取股价失败: {str(e)}"

# ========== 步骤3: 涨跌幅限制检查 ==========
def get_stock_type(stock_code):
    """判断股票类型"""
    if stock_code.startswith('ST') or '*ST' in stock_code:
        return 'ST'
    elif stock_code.startswith('688'):
        return '科创板'
    elif stock_code.startswith('300'):
        return '创业板'
    else:
        return '主板'

def check_price_limit(stock_code, price, pre_close):
    """检查涨跌幅限制"""
    if not pre_close:
        return True, "昨收价未知，跳过涨跌幅检查"
    
    stock_type = get_stock_type(stock_code)
    
    if stock_type == 'ST':
        limit_pct = LIMIT_UP_ST
    elif stock_type in ['创业板', '科创板']:
        limit_pct = LIMIT_UP_CY
    else:
        limit_pct = LIMIT_UP_MAIN
    
    limit_up = pre_close * (1 + limit_pct)
    limit_down = pre_close * (1 - limit_pct)
    
    # 涨停价和跌停价不允许交易
    if price >= limit_up:
        return False, f"涨停价禁止交易! 委托价:{price:.2f} >= 涨停价:{limit_up:.2f}"
    if price <= limit_down:
        return False, f"跌停价禁止交易! 委托价:{price:.2f} <= 跌停价:{limit_down:.2f}"
    
    return True, f"涨跌幅检查通过 [{stock_type} {int(limit_pct*100)}%]"

# ========== 步骤4: 交易单位检查 ==========
def check_trading_unit(stock_code, quantity):
    """检查交易单位"""
    stock_type = get_stock_type(stock_code)
    
    if stock_type == '科创板':
        if quantity < 200:
            return False, f"科创板买入最低200股，当前: {quantity}"
        if (quantity - 200) % 1 != 0:
            return False, f"科创板买入数量须为200或其整数倍，当前: {quantity}"
    else:
        if quantity % 100 != 0:
            return False, f"{stock_type}买入必须为100股整数倍，当前: {quantity}"
    
    return True, f"交易单位检查通过 ({stock_type})"

# ========== 步骤5: T+1 制度检查 ==========
def check_t1_restriction(stock_code, quantity, data, is_buy=True):
    """检查T+1交易制度 - 区分今日买入和历史持仓"""
    if is_buy:
        return True, "买入不受T+1限制"
    
    positions = data.get('positions', {})
    if stock_code not in positions:
        return True, "无持仓"
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 获取该股票的所有持仓批次
    position_lots = data.get('_position_lots', {}).get(stock_code, [])
    
    if not position_lots:
        # 兼容旧数据：没有分批次记录，则检查是否有今日买入记录
        position_info = data.get('_position_info', {}).get(stock_code, {})
        buy_date = position_info.get('buy_date')
        
        if buy_date == today:
            return False, f"T+1限制！该股票全部于今日买入，当前持仓{positions[stock_code]}股，今日不能卖出"
        return True, "T+1检查通过"
    
    # 计算今日买入的股数
    today_buy_qty = sum(lot.get('quantity', 0) for lot in position_lots if lot.get('buy_date') == today)
    total_qty = positions[stock_code]
    sellable_qty = total_qty - today_buy_qty
    
    if quantity > sellable_qty:
        return False, f"T+1限制！该股票今日买入{today_buy_qty}股，可卖出{sellable_qty}股，您要卖出{quantity}股，超出可卖出数量"
    
    return True, f"T+1检查通过 (总持仓:{total_qty}股, 今日买入:{today_buy_qty}股, 可卖出:{sellable_qty}股)"

# ========== 步骤6: 资金充足性检查 ==========
def check_available_cash(stock_code, quantity, price, data, is_buy=True):
    """检查资金充足性"""
    # 计算所需资金
    commission = quantity * price * COMMISSION
    transfer_fee = quantity * price * TRANSFER_FEE_SH if stock_code.startswith('6') else 0
    
    if is_buy:
        total_cost = quantity * price + commission + transfer_fee
        if total_cost > data['available_cash']:
            return False, f"资金不足! 需要: {total_cost:.2f}元，可用: {data['available_cash']:.2f}元"
        return True, f"资金检查通过 (需要: {total_cost:.2f}元，可用: {data['available_cash']:.2f}元)"
    else:
        # 卖出时计算印花税
        stamp_duty = quantity * price * STAMP_DUTY
        total_fee = commission + stamp_duty + transfer_fee
        net_proceeds = quantity * price - total_fee
        return True, f"资金检查通过 (预计净得: {net_proceeds:.2f}元)"

# ========== 步骤6-8: 执行交易 ==========
def execute_buy(stock_code, quantity, price=None):
    """执行买入 - 完整流程"""
    print("=" * 50)
    print(f"【买入交易】股票: {stock_code}, 数量: {quantity}股")
    print("=" * 50)
    
    # 步骤1: 交易时间检查
    print("\n[步骤1] 交易时间检查...")
    valid, msg = check_trading_time()
    print(f"  {msg}")
    if not valid:
        return False, msg
    
    # 步骤2: 获取实时股价
    print("\n[步骤2] 获取实时股价...")
    current_price, pre_close = get_realtime_price(stock_code)
    if current_price is None:
        return False, pre_close  # 错误信息
    
    price_info = f"{current_price:.2f}元"
    if pre_close:
        price_info += f", 昨收: {pre_close:.2f}元"
    print(f"  {price_info}")
    
    # 如果未指定价格，使用当前市价
    if price is None:
        price = current_price
    else:
        print(f"  使用指定价格: {price:.2f}元")
    
    # 步骤3: 涨跌幅限制检查
    print("\n[步骤3] 涨跌幅限制检查...")
    valid, msg = check_price_limit(stock_code, price, pre_close)
    print(f"  {msg}")
    if not valid:
        return False, msg
    
    # 步骤4: 交易单位检查
    print("\n[步骤4] 交易单位检查...")
    valid, msg = check_trading_unit(stock_code, quantity)
    print(f"  {msg}")
    if not valid:
        return False, msg
    
    # 加载数据
    data = load_data()
    
    # 步骤5: 资金充足性检查
    print("\n[步骤5] 资金充足性检查...")
    valid, msg = check_available_cash(stock_code, quantity, price, data, is_buy=True)
    print(f"  {msg}")
    if not valid:
        return False, msg
    
    # 步骤6: 执行买入
    print("\n[步骤6] 执行买入...")
    commission = quantity * price * COMMISSION
    transfer_fee = quantity * price * TRANSFER_FEE_SH if stock_code.startswith('6') else 0
    total_fee = commission + transfer_fee
    total_cost = quantity * price + total_fee
    
    # 更新可用资金
    data['available_cash'] -= total_cost
    
    # 更新持仓
    if 'positions' not in data:
        data['positions'] = {}
    data['positions'][stock_code] = data['positions'].get(stock_code, 0) + quantity
    
    # 更新成本
    if '_cost_basis' not in data:
        data['_cost_basis'] = {}
    old_cost = data['_cost_basis'].get(stock_code, 0)
    data['_cost_basis'][stock_code] = old_cost + quantity * price
    
    # 记录持仓买入日期和批次（T+1检查用）
    if '_position_info' not in data:
        data['_position_info'] = {}
    today = datetime.now().strftime("%Y-%m-%d")
    data['_position_info'][stock_code] = {
        'buy_date': today,
        'quantity': data['positions'][stock_code]
    }
    
    # 记录持仓批次（用于更精确的T+1检查）
    if '_position_lots' not in data:
        data['_position_lots'] = {}
    if stock_code not in data['_position_lots']:
        data['_position_lots'][stock_code] = []
    # 添加新买入批次
    data['_position_lots'][stock_code].append({
        'buy_date': today,
        'quantity': quantity,
        'price': price
    })
    
    # 步骤7: 费用计算
    print("\n[步骤7] 费用计算...")
    print(f"  成交金额: {quantity * price:.2f}元")
    print(f"  佣金(万2): {commission:.2f}元")
    if transfer_fee > 0:
        print(f"  过户费(万0.1): {transfer_fee:.2f}元")
    print(f"  手续费合计: {total_fee:.2f}元")
    print(f"  实际扣款: {total_cost:.2f}元")
    
    # 步骤8: 更新资产和记录
    print("\n[步骤8] 更新资产和交易记录...")
    
    # 更新总资产
    data['total_assets'] = data['available_cash']
    for code, qty in data['positions'].items():
        cost = data['_cost_basis'].get(code, 0)
        avg_price = cost / qty if qty > 0 else 0
        data['total_assets'] += qty * avg_price
    
    # 记录交易
    transaction = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "买入",
        "stock": stock_code,
        "quantity": quantity,
        "price": price,
        "amount": quantity * price,
        "fee": total_fee,
        "commission": commission,
        "transfer_fee": transfer_fee
    }
    data['transactions'].append(transaction)
    
    save_data(data)
    
    print(f"  交易记录已保存")
    print(f"\n{'=' * 50}")
    print(f"【买入成功】")
    print(f"  股票: {stock_code}")
    print(f"  数量: {quantity}股")
    print(f"  价格: {price:.2f}元")
    print(f"  金额: {quantity * price:.2f}元")
    print(f"  手续费: {total_fee:.2f}元")
    print(f"  可用资金: {data['available_cash']:.2f}元")
    print(f"  总资产: {data['total_assets']:.2f}元")
    print(f"{'=' * 50}")
    
    return True, f"买入成功! 股票:{stock_code}, 数量:{quantity}股, 价格:{price:.2f}元"

def execute_sell(stock_code, quantity, price=None):
    """执行卖出 - 完整流程"""
    print("=" * 50)
    print(f"【卖出交易】股票: {stock_code}, 数量: {quantity}股")
    print("=" * 50)
    
    # 步骤1: 交易时间检查
    print("\n[步骤1] 交易时间检查...")
    valid, msg = check_trading_time()
    print(f"  {msg}")
    if not valid:
        return False, msg
    
    # 步骤2: 获取实时股价
    print("\n[步骤2] 获取实时股价...")
    current_price, pre_close = get_realtime_price(stock_code)
    if current_price is None:
        return False, pre_close
    
    price_info = f"{current_price:.2f}元"
    if pre_close:
        price_info += f", 昨收: {pre_close:.2f}元"
    print(f"  {price_info}")
    
    # 如果未指定价格，使用当前市价
    if price is None:
        price = current_price
    else:
        print(f"  使用指定价格: {price:.2f}元")
    
    # 步骤3: 涨跌幅限制检查
    print("\n[步骤3] 涨跌幅限制检查...")
    valid, msg = check_price_limit(stock_code, price, pre_close)
    print(f"  {msg}")
    if not valid:
        return False, msg
    
    # 加载数据
    data = load_data()
    
    # 步骤4: 交易单位检查 (卖出可为零股)
    print("\n[步骤4] 交易单位检查...")
    print(f"  卖出可为零股，检查持仓...")
    
    # 步骤5: 持仓检查
    print("\n[步骤5] 持仓检查...")
    positions = data.get('positions', {})
    if stock_code not in positions or positions[stock_code] < quantity:
        return False, f"持仓不足! 当前持有: {positions.get(stock_code, 0)}股, 需要卖出: {quantity}股"
    print(f"  持仓检查通过 (持有: {positions[stock_code]}股)")
    
    # 步骤5.5: T+1制度检查
    print("\n[步骤5.5] T+1制度检查...")
    valid, msg = check_t1_restriction(stock_code, quantity, data, is_buy=False)
    print(f"  {msg}")
    if not valid:
        return False, msg
    
    # 步骤6: 执行卖出
    print("\n[步骤6] 执行卖出...")
    
    # 步骤7: 费用计算
    print("\n[步骤7] 费用计算...")
    commission = quantity * price * COMMISSION
    stamp_duty = quantity * price * STAMP_DUTY
    transfer_fee = quantity * price * TRANSFER_FEE_SH if stock_code.startswith('6') else 0
    total_fee = commission + stamp_duty + transfer_fee
    net_proceeds = quantity * price - total_fee
    
    print(f"  成交金额: {quantity * price:.2f}元")
    print(f"  佣金(万2): {commission:.2f}元")
    print(f"  印花税(千1): {stamp_duty:.2f}元")
    if transfer_fee > 0:
        print(f"  过户费(万0.1): {transfer_fee:.2f}元")
    print(f"  手续费合计: {total_fee:.2f}元")
    print(f"  净得资金: {net_proceeds:.2f}元")
    
    # 步骤8: 更新资产和记录
    print("\n[步骤8] 更新资产和交易记录...")
    
    # 更新持仓
    data['positions'][stock_code] -= quantity
    if data['positions'][stock_code] == 0:
        del data['positions'][stock_code]
        data['_cost_basis'].pop(stock_code, None)
        data['_position_lots'].pop(stock_code, None)
    else:
        data['_cost_basis'][stock_code] -= quantity * price
    
    # 更新持仓批次（优先卖出非今日买入的）
    if '_position_lots' in data and stock_code in data['_position_lots']:
        today = datetime.now().strftime("%Y-%m-%d")
        remaining_qty = quantity
        
        # 按日期排序，先卖老的
        lots = data['_position_lots'][stock_code]
        lots.sort(key=lambda x: x.get('buy_date', ''))
        
        for lot in lots[:]:
            if remaining_qty <= 0:
                break
            if lot.get('buy_date') != today:
                # 卖出非今日的
                sell_qty = min(lot.get('quantity', 0), remaining_qty)
                lot['quantity'] -= sell_qty
                remaining_qty -= sell_qty
                if lot['quantity'] <= 0:
                    lots.remove(lot)
        
        # 如果还有要卖的且今日还有份额，卖今日的
        if remaining_qty > 0:
            for lot in lots[:]:
                if remaining_qty <= 0:
                    break
                if lot.get('buy_date') == today:
                    sell_qty = min(lot.get('quantity', 0), remaining_qty)
                    lot['quantity'] -= sell_qty
                    remaining_qty -= sell_qty
                    if lot['quantity'] <= 0:
                        lots.remove(lot)
        
        # 清理空批次
        data['_position_lots'][stock_code] = [l for l in lots if l.get('quantity', 0) > 0]
    
    # 更新可用资金
    data['available_cash'] += net_proceeds
    
    # 更新总资产
    data['total_assets'] = data['available_cash']
    for code, qty in data['positions'].items():
        cost = data['_cost_basis'].get(code, 0)
        avg_price = cost / qty if qty > 0 else 0
        data['total_assets'] += qty * avg_price
    
    # 记录交易
    transaction = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "卖出",
        "stock": stock_code,
        "quantity": quantity,
        "price": price,
        "amount": quantity * price,
        "fee": total_fee,
        "commission": commission,
        "stamp_duty": stamp_duty,
        "transfer_fee": transfer_fee,
        "net_proceeds": net_proceeds
    }
    data['transactions'].append(transaction)
    
    save_data(data)
    
    print(f"  交易记录已保存")
    print(f"\n{'=' * 50}")
    print(f"【卖出成功】")
    print(f"  股票: {stock_code}")
    print(f"  数量: {quantity}股")
    print(f"  价格: {price:.2f}元")
    print(f"  成交金额: {quantity * price:.2f}元")
    print(f"  手续费: {total_fee:.2f}元")
    print(f"  净得资金: {net_proceeds:.2f}元")
    print(f"  可用资金: {data['available_cash']:.2f}元")
    print(f"  总资产: {data['total_assets']:.2f}元")
    print(f"{'=' * 50}")
    
    return True, f"卖出成功! 股票:{stock_code}, 数量:{quantity}股, 价格:{price:.2f}元"

def show_status():
    """显示资产状况"""
    data = load_data()
    
    result = f"=== 当前资产状况 ===\n"
    result += f"总资产: {data['total_assets']:.2f} 元\n"
    result += f"可用资金: {data['available_cash']:.2f} 元\n"
    
    if data['positions']:
        result += f"\n持仓情况:\n"
        for code, qty in data['positions'].items():
            cost = data['_cost_basis'].get(code, 0)
            avg_price = cost / qty if qty > 0 else 0
            result += f"  {code}: {qty}股 (成本价: {avg_price:.2f})\n"
    else:
        result += f"\n暂无持仓\n"
    
    return result

def show_history():
    """显示交易历史"""
    data = load_data()
    
    if not data['transactions']:
        return "暂无交易记录"
    
    result = f"=== 交易记录 ===\n"
    result += f"=" * 60 + "\n"
    for t in data['transactions']:
        result += f"{t['time']} | {t['type']} | {t['stock']} | {t['quantity']}股 @ {t['price']:.2f}\n"
    
    return result

def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python trading.py buy <股票代码> <数量> [价格]")
        print("  python trading.py sell <股票代码> <数量> [价格]")
        print("  python trading.py status")
        print("  python trading.py history")
        print("  python trading.py price <股票代码>  # 查询实时价格")
        return
    
    action = sys.argv[1]
    
    if action == "buy" and len(sys.argv) >= 4:
        stock_code = sys.argv[2]
        quantity = int(sys.argv[3])
        price = float(sys.argv[4]) if len(sys.argv) > 4 else None
        success, msg = execute_buy(stock_code, quantity, price)
        print(msg)
    elif action == "sell" and len(sys.argv) >= 4:
        stock_code = sys.argv[2]
        quantity = int(sys.argv[3])
        price = float(sys.argv[4]) if len(sys.argv) > 4 else None
        success, msg = execute_sell(stock_code, quantity, price)
        print(msg)
    elif action == "status":
        print(show_status())
    elif action == "history":
        print(show_history())
    elif action == "price" and len(sys.argv) == 3:
        stock_code = sys.argv[2]
        current_price, pre_close = get_realtime_price(stock_code)
        if current_price:
            print(f"股票: {stock_code}")
            print(f"当前价: {current_price:.2f}元")
            if pre_close:
                pct = (current_price - pre_close) / pre_close * 100
                print(f"昨收价: {pre_close:.2f}元")
                print(f"涨跌幅: {pct:+.2f}%")
        else:
            print(pre_close)
    else:
        print("参数错误")

if __name__ == "__main__":
    main()
