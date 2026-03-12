"""
股票交易自动化系统 - 增强版
初始资金：10万元
交易规则：T+1，印花税0.05%，佣金0.03%，最低买入100股
奖惩规则：盈利+100元，亏损-200元，低于5万任务失败
"""

import tushare as ts
import datetime
import json
import os

TUSHARE_TOKEN = "03eed883a368f22668fd2e781d1002fe2445dc3bde2c48db43a8f6b9"

class StockTrader:
    def __init__(self, initial_capital=100000):
        self.initial_capital = initial_capital  # 初始资金
        self.capital = initial_capital          # 当前总资金
        self.cash = initial_capital             # 可用现金
        self.positions = {}                     # 持仓
        self.trade_history = []                 # 交易记录
        self.daily_recommendations = []         # 每日推荐
        self.daily_pnl = 0                      # 当日盈亏
        self.total_pnl = 0                      # 总盈亏
        self.trading_rules = {                  # 交易规则（可动态调整）
            'buy_trigger': -2.0,                # 买入触发：跌2%
            'sell_trigger': 3.0,                # 卖出触发：涨3%
            'max_position_per_stock': 20000,    # 单只股票最大持仓2万
            'min_cash_reserve': 30000,          # 最低现金储备3万
            'profit_reward': 100,               # 盈利奖励
            'loss_penalty': 200,                # 亏损惩罚
            'min_shares': 100                   # 最低买入100股
        }
        self.ts = None
        self._init_tushare()
        
    def _init_tushare(self):
        """初始化Tushare"""
        try:
            ts.set_token(TUSHARE_TOKEN)
            self.ts = ts.pro_api()
            print(f"[系统] 交易系统初始化成功")
            print(f"[系统] 初始资金: {self.initial_capital}元")
            print(f"[系统] 任务目标: 资金不低于50000元")
            print(f"[系统] 奖惩规则: 盈利+{self.trading_rules['profit_reward']}元, 亏损-{self.trading_rules['loss_penalty']}元")
        except Exception as e:
            print(f"[错误] Tushare初始化失败: {e}")
    
    def check_task_status(self):
        """检查任务状态"""
        portfolio_value = self.get_portfolio_value()
        if portfolio_value < 50000:
            print(f"[任务失败] 当前资金{portfolio_value:.2f}元低于50000元阈值！")
            return False
        return True
    
    def apply_daily_reward_penalty(self):
        """应用每日奖惩"""
        yesterday_pnl = self.daily_pnl
        
        if yesterday_pnl > 0:
            # 盈利奖励
            self.cash += self.trading_rules['profit_reward']
            self.capital += self.trading_rules['profit_reward']
            print(f"[奖励] 昨日盈利{yesterday_pnl:.2f}元，奖励{self.trading_rules['profit_reward']}元！")
        elif yesterday_pnl < 0:
            # 亏损惩罚
            self.cash -= self.trading_rules['loss_penalty']
            self.capital -= self.trading_rules['loss_penalty']
            print(f"[惩罚] 昨日亏损{abs(yesterday_pnl):.2f}元，扣除{self.trading_rules['loss_penalty']}元！")
        
        # 重置当日盈亏
        self.daily_pnl = 0
    
    def adjust_trading_rules(self, performance):
        """根据盈亏动态调整交易规则"""
        old_rules = self.trading_rules.copy()
        
        if performance > 1000:  # 盈利超过1000元
            # 激进策略
            self.trading_rules['buy_trigger'] = -1.5  # 跌1.5%就买入
            self.trading_rules['sell_trigger'] = 2.5  # 涨2.5%就卖出
            self.trading_rules['max_position_per_stock'] = 25000
            print("[策略调整] 盈利良好，切换激进策略")
        elif performance < -500:  # 亏损超过500元
            # 保守策略
            self.trading_rules['buy_trigger'] = -3.0  # 跌3%才买入
            self.trading_rules['sell_trigger'] = 4.0  # 涨4%才卖出
            self.trading_rules['max_position_per_stock'] = 15000
            print("[策略调整] 亏损较多，切换保守策略")
        else:
            # 平衡策略
            self.trading_rules['buy_trigger'] = -2.0
            self.trading_rules['sell_trigger'] = 3.0
            self.trading_rules['max_position_per_stock'] = 20000
            print("[策略调整] 保持平衡策略")
        
        return old_rules != self.trading_rules
    
    def get_daily_recommendations(self):
        """获取每日推荐股票"""
        try:
            yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y%m%d")
            df_daily = self.ts.daily(trade_date=yesterday)
            df_daily = df_daily[~df_daily['ts_code'].str.startswith(('300', '301', '688'))]
            df_daily['score'] = df_daily['pct_chg'] * df_daily['vol'] / 10000
            top10 = df_daily.nlargest(10, 'score')
            self.daily_recommendations = top10['ts_code'].tolist()
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
            return None
    
    def can_trade(self, ts_code):
        """检查是否可以交易（T+1）"""
        if ts_code not in self.positions:
            return True
        position = self.positions[ts_code]
        buy_date = datetime.datetime.strptime(position['buy_date'], "%Y%m%d")
        today = datetime.datetime.now()
        return (today - buy_date).days >= 1
    
    def calculate_buy_cost(self, amount):
        """计算买入成本"""
        commission = max(amount * 0.0003, 5)
        return commission
    
    def calculate_sell_cost(self, amount):
        """计算卖出成本"""
        stamp_tax = amount * 0.0005
        commission = max(amount * 0.0003, 5)
        return stamp_tax + commission
    
    def buy(self, ts_code, price, quantity):
        """买入股票（最低100股）"""
        if quantity < self.trading_rules['min_shares']:
            print(f"[买入失败] 数量不足{self.trading_rules['min_shares']}股")
            return False
        
        # 100股整数倍
        quantity = (quantity // 100) * 100
        if quantity < 100:
            return False
        
        amount = price * quantity
        cost = self.calculate_buy_cost(amount)
        total_cost = amount + cost
        
        # 检查单只股票持仓上限
        if ts_code in self.positions:
            current_position_value = self.positions[ts_code]['quantity'] * price
            if current_position_value + amount > self.trading_rules['max_position_per_stock']:
                print(f"[买入失败] 将超过单只股票持仓上限")
                return False
        
        if total_cost > self.cash:
            print(f"[买入失败] 资金不足")
            return False
        
        # 保留最低现金储备
        if self.cash - total_cost < self.trading_rules['min_cash_reserve']:
            print(f"[买入失败] 需保留{self.trading_rules['min_cash_reserve']}元现金储备")
            return False
        
        self.cash -= total_cost
        today = datetime.datetime.now().strftime("%Y%m%d")
        
        if ts_code in self.positions:
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
        
        msg = f"[买入] {ts_code} 价格:{price:.2f} 数量:{quantity}股 金额:{amount:.2f} 手续费:{cost:.2f} 剩余现金:{self.cash:.2f}"
        print(msg)
        return True
    
    def sell(self, ts_code, price, quantity):
        """卖出股票（最低100股，必须是100的整数倍）"""
        if ts_code not in self.positions:
            print(f"[卖出失败] 没有持有{ts_code}")
            return False
        
        if not self.can_trade(ts_code):
            print(f"[卖出失败] {ts_code} T+1限制")
            return False
        
        position = self.positions[ts_code]
        if quantity > position['quantity']:
            quantity = position['quantity']
        
        # 必须是100股的整数倍
        quantity = (quantity // 100) * 100
        
        if quantity < self.trading_rules['min_shares']:
            print(f"[卖出失败] 卖出数量不足{self.trading_rules['min_shares']}股")
            return False
        
        amount = price * quantity
        cost = self.calculate_sell_cost(amount)
        net_amount = amount - cost
        
        # 计算盈亏
        profit = (price - position['cost_price']) * quantity
        self.daily_pnl += profit
        self.total_pnl += profit
        
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
            'profit': profit,
            'cash_after': self.cash
        }
        self.trade_history.append(trade_record)
        
        msg = f"[卖出] {ts_code} 价格:{price:.2f} 数量:{quantity}股 金额:{amount:.2f} 手续费:{cost:.2f} 盈亏:{profit:.2f} 剩余现金:{self.cash:.2f}"
        print(msg)
        return True
    
    def auto_trade_decision(self, ts_code, price_data):
        """自动交易决策"""
        if not price_data:
            return None
        
        pct_chg = price_data['pct_chg']
        current_price = price_data['close']
        
        rules = self.trading_rules
        
        if ts_code in self.positions:
            position = self.positions[ts_code]
            profit_pct = (current_price - position['cost_price']) / position['cost_price'] * 100
            
            if profit_pct >= rules['sell_trigger'] and self.can_trade(ts_code):
                # 计算卖出数量（50%持仓，且必须是100的整数倍）
                sell_qty = position['quantity'] // 2
                sell_qty = (sell_qty // 100) * 100  # 确保100的整数倍
                
                if sell_qty < self.trading_rules['min_shares']:
                    # 如果50%不足100股，尝试卖出全部
                    sell_qty = (position['quantity'] // 100) * 100
                
                if sell_qty >= self.trading_rules['min_shares']:
                    return ('sell', sell_qty)
        else:
            if pct_chg <= rules['buy_trigger'] and self.cash > 10000:
                max_shares = min(1000, int(10000 / current_price))
                buy_qty = (max_shares // 100) * 100
                if buy_qty >= 100:
                    return ('buy', buy_qty)
        
        return None
    
    def get_portfolio_value(self):
        """计算总资产"""
        total_value = self.cash
        for ts_code, position in self.positions.items():
            price_data = self.query_stock_price(ts_code)
            if price_data:
                market_value = position['quantity'] * price_data['close']
                total_value += market_value
        return total_value
    
    def generate_daily_report(self):
        """生成每日交易简报（含动态规则）"""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        portfolio_value = self.get_portfolio_value()
        profit_loss = portfolio_value - self.initial_capital
        profit_pct = profit_loss / self.initial_capital * 100
        
        # 应用每日奖惩
        self.apply_daily_reward_penalty()
        
        # 调整交易规则
        rule_changed = self.adjust_trading_rules(self.daily_pnl)
        
        # 检查任务状态
        task_status = self.check_task_status()
        
        report = f"""
═══════════════════════════════════════
📊 每日交易简报 - {today}
═══════════════════════════════════════

💰 资金状况
• 初始资金: {self.initial_capital:,.2f} 元
• 当前总资产: {portfolio_value:,.2f} 元
• 总盈亏: {profit_loss:,.2f} 元 ({profit_pct:+.2f}%)
• 当日盈亏: {self.daily_pnl:,.2f} 元
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
        
        today_trades = [t for t in self.trade_history if t['time'].startswith(today)]
        report += f"""
📝 今日交易 ({len(today_trades)}笔)
"""
        if today_trades:
            for trade in today_trades:
                report += f"• {trade['time']} {trade['action']} {trade['ts_code']} {trade['quantity']}股 价格{trade['price']:.2f}\n"
        else:
            report += "• 今日无交易\n"
        
        # 动态交易规则
        rules = self.trading_rules
        report += f"""
⚙️ 当前交易规则
• 买入触发: 跌{abs(rules['buy_trigger'])}%
• 卖出触发: 涨{rules['sell_trigger'])}%
• 单股最大持仓: {rules['max_position_per_stock']}元
• 最低现金储备: {rules['min_cash_reserve']}元
• 最低买入: {rules['min_shares']}股
"""
        
        if rule_changed:
            report += "• [今日调整] 策略已根据盈亏动态调整！\n"
        
        report += f"""
🎯 任务状态: {'✅ 正常运行' if task_status else '❌ 任务失败（资金低于5万）'}

═══════════════════════════════════════
"""
        
        return report, task_status

# 全局实例
trader = None

def init_trader():
    global trader
    trader = StockTrader(initial_capital=100000)
    return trader

if __name__ == "__main__":
    trader = init_trader()
