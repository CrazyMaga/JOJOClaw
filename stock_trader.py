"""
股票交易自动化系统
初始资金：10万元
交易规则：T+1，印花税0.05%，佣金0.03%
"""

import tushare as ts
import datetime
import time
import json
import os

TUSHARE_TOKEN = "03eed883a368f22668fd2e781d1002fe2445dc3bde2c48db43a8f6b9"

class StockTrader:
    def __init__(self, initial_capital=100000):
        self.capital = initial_capital  # 初始资金
        self.cash = initial_capital     # 可用现金
        self.positions = {}             # 持仓 {股票代码: {数量, 成本价, 买入日期}}
        self.trade_history = []         # 交易记录
        self.daily_recommendations = [] # 每日推荐股票
        self.ts = None
        self._init_tushare()
        
    def _init_tushare(self):
        """初始化Tushare"""
        try:
            ts.set_token(TUSHARE_TOKEN)
            self.ts = ts.pro_api()
            print(f"[系统] Tushare初始化成功，初始资金: {self.capital}元")
        except Exception as e:
            print(f"[错误] Tushare初始化失败: {e}")
    
    def get_daily_recommendations(self):
        """获取每日推荐股票（开盘前）"""
        try:
            today = datetime.datetime.now().strftime("%Y%m%d")
            
            # 获取昨日数据筛选潜力股
            yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y%m%d")
            df_daily = self.ts.daily(trade_date=yesterday)
            
            # 排除创业板和科创板
            df_daily = df_daily[~df_daily['ts_code'].str.startswith(('300', '301', '688'))]
            
            # 按涨跌幅和成交量排序
            df_daily['score'] = df_daily['pct_chg'] * df_daily['vol'] / 10000
            top10 = df_daily.nlargest(10, 'score')
            
            self.daily_recommendations = top10['ts_code'].tolist()
            
            print(f"[推荐] 今日推荐股票: {self.daily_recommendations}")
            return self.daily_recommendations
            
        except Exception as e:
            print(f"[错误] 获取推荐股票失败: {e}")
            return []
    
    def query_stock_price(self, ts_code):
        """查询股票当前价格"""
        try:
            df = self.ts.daily(ts_code=ts_code, limit=1)
            if not df.empty:
                return {
                    'open': df.iloc[0]['open'],
                    'high': df.iloc[0]['high'],
                    'low': df.iloc[0]['low'],
                    'close': df.iloc[0]['close'],
                    'pre_close': df.iloc[0]['pre_close'],
                    'pct_chg': df.iloc[0]['pct_chg']
                }
            return None
        except Exception as e:
            print(f"[错误] 查询{ts_code}价格失败: {e}")
            return None
    
    def can_trade(self, ts_code):
        """检查是否可以交易（T+1规则）"""
        if ts_code not in self.positions:
            return True  # 没有持仓可以买入
        
        position = self.positions[ts_code]
        buy_date = datetime.datetime.strptime(position['buy_date'], "%Y%m%d")
        today = datetime.datetime.now()
        
        # T+1: 买入后下一个交易日才能卖出
        if (today - buy_date).days >= 1:
            return True
        return False
    
    def calculate_buy_cost(self, amount):
        """计算买入成本（佣金）"""
        commission = max(amount * 0.0003, 5)  # 佣金0.03%，最低5元
        return commission
    
    def calculate_sell_cost(self, amount):
        """计算卖出成本（印花税+佣金）"""
        stamp_tax = amount * 0.0005  # 印花税0.05%
        commission = max(amount * 0.0003, 5)  # 佣金0.03%，最低5元
        return stamp_tax + commission
    
    def buy(self, ts_code, price, quantity):
        """买入股票"""
        amount = price * quantity
        cost = self.calculate_buy_cost(amount)
        total_cost = amount + cost
        
        if total_cost > self.cash:
            print(f"[买入失败] 资金不足，需要{total_cost}元，可用{self.cash}元")
            return False
        
        # 执行买入
        self.cash -= total_cost
        today = datetime.datetime.now().strftime("%Y%m%d")
        
        if ts_code in self.positions:
            # 加仓，更新成本价
            old_qty = self.positions[ts_code]['quantity']
            old_cost = self.positions[ts_code]['cost_price']
            new_qty = old_qty + quantity
            new_cost = (old_qty * old_cost + quantity * price) / new_qty
            self.positions[ts_code] = {
                'quantity': new_qty,
                'cost_price': new_cost,
                'buy_date': today
            }
        else:
            # 新建仓
            self.positions[ts_code] = {
                'quantity': quantity,
                'cost_price': price,
                'buy_date': today
            }
        
        trade_record = {
            'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'action': '买入',
            'ts_code': ts_code,
            'price': price,
            'quantity': quantity,
            'amount': amount,
            'cost': cost,
            'cash_after': self.cash
        }
        self.trade_history.append(trade_record)
        
        print(f"[买入] {ts_code} 价格:{price} 数量:{quantity} 金额:{amount:.2f} 手续费:{cost:.2f} 剩余现金:{self.cash:.2f}")
        return True
    
    def sell(self, ts_code, price, quantity):
        """卖出股票"""
        if ts_code not in self.positions:
            print(f"[卖出失败] 没有持有{ts_code}")
            return False
        
        if not self.can_trade(ts_code):
            print(f"[卖出失败] {ts_code} T+1限制，今日不能卖出")
            return False
        
        position = self.positions[ts_code]
        if quantity > position['quantity']:
            print(f"[卖出失败] 持仓不足，持有{position['quantity']}股，尝试卖出{quantity}股")
            return False
        
        amount = price * quantity
        cost = self.calculate_sell_cost(amount)
        net_amount = amount - cost
        
        # 执行卖出
        self.cash += net_amount
        position['quantity'] -= quantity
        
        if position['quantity'] == 0:
            del self.positions[ts_code]
        
        trade_record = {
            'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'action': '卖出',
            'ts_code': ts_code,
            'price': price,
            'quantity': quantity,
            'amount': amount,
            'cost': cost,
            'cash_after': self.cash
        }
        self.trade_history.append(trade_record)
        
        print(f"[卖出] {ts_code} 价格:{price} 数量:{quantity} 金额:{amount:.2f} 手续费:{cost:.2f} 剩余现金:{self.cash:.2f}")
        return True
    
    def auto_trade_decision(self, ts_code, price_data):
        """自动交易决策（简化版）"""
        if not price_data:
            return None
        
        pct_chg = price_data['pct_chg']
        current_price = price_data['close']
        
        # 简单策略：涨超3%卖出，跌超2%买入
        if ts_code in self.positions:
            # 有持仓，考虑卖出
            position = self.positions[ts_code]
            profit_pct = (current_price - position['cost_price']) / position['cost_price'] * 100
            
            if profit_pct >= 3 and self.can_trade(ts_code):
                # 盈利3%以上，卖出50%
                sell_qty = position['quantity'] // 2
                if sell_qty > 0:
                    return ('sell', sell_qty)
        else:
            # 无持仓，考虑买入
            if pct_chg <= -2 and self.cash > 10000:
                # 跌2%以上，买入
                buy_qty = min(1000, int(10000 / current_price / 100) * 100)  # 买入不超过1万元，100股整数
                if buy_qty > 0:
                    return ('buy', buy_qty)
        
        return None
    
    def get_portfolio_value(self):
        """计算当前持仓市值"""
        total_value = self.cash
        for ts_code, position in self.positions.items():
            price_data = self.query_stock_price(ts_code)
            if price_data:
                market_value = position['quantity'] * price_data['close']
                total_value += market_value
        return total_value
    
    def generate_daily_report(self):
        """生成每日交易简报"""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        portfolio_value = self.get_portfolio_value()
        profit_loss = portfolio_value - self.capital
        profit_pct = profit_loss / self.capital * 100
        
        report = f"""
═══════════════════════════════════════
📊 每日交易简报 - {today}
═══════════════════════════════════════

💰 资金状况
• 初始资金: {self.capital:,.2f} 元
• 当前总资产: {portfolio_value:,.2f} 元
• 盈亏金额: {profit_loss:,.2f} 元 ({profit_pct:+.2f}%)
• 可用现金: {self.cash:,.2f} 元

📈 持仓情况
"""
        
        if self.positions:
            for ts_code, position in self.positions.items():
                price_data = self.query_stock_price(ts_code)
                if price_data:
                    current_price = price_data['close']
                    market_value = position['quantity'] * current_price
                    profit = (current_price - position['cost_price']) * position['quantity']
                    report += f"• {ts_code}: {position['quantity']}股 成本{position['cost_price']:.2f} 现价{current_price:.2f} 市值{market_value:.2f} 盈亏{profit:.2f}\n"
        else:
            report += "• 当前无持仓\n"
        
        report += f"""
📝 今日交易记录 ({len([t for t in self.trade_history if t['time'].startswith(today)])}笔)
"""
        
        today_trades = [t for t in self.trade_history if t['time'].startswith(today)]
        if today_trades:
            for trade in today_trades:
                report += f"• {trade['time']} {trade['action']} {trade['ts_code']} {trade['quantity']}股 价格{trade['price']:.2f}\n"
        else:
            report += "• 今日无交易\n"
        
        report += """
═══════════════════════════════════════
"""
        
        return report

# 全局交易实例
trader = None

def init_trader():
    """初始化交易系统"""
    global trader
    trader = StockTrader(initial_capital=100000)
    print("[系统] 股票交易系统初始化完成，初始资金: 100000元")
    return trader

if __name__ == "__main__":
    # 测试
    trader = init_trader()
    recommendations = trader.get_daily_recommendations()
    print(f"今日推荐: {recommendations}")
