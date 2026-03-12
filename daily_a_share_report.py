"""
每日 A 股行情查询脚本 - 使用 Tushare + AkShare 备用
"""

import tushare as ts
import akshare as ak
import datetime
import sys
import os

# Tushare Token
TUSHARE_TOKEN = "03eed883a368f22668fd2e781d1002fe2445dc3bde2c48db43a8f6b9"

def get_yesterday_a_share_summary():
    """查询昨日 A 股整体行情摘要"""
    try:
        ts.set_token(TUSHARE_TOKEN)
        pro = ts.pro_api()
        
        # 获取昨天日期
        yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y%m%d")
        yesterday_fmt = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        
        print(f"=== {yesterday_fmt} A 股行情摘要 ===\n")
        
        # 使用 AkShare 获取主要指数（更可靠）
        print("【主要指数】")
        try:
            df_index = ak.index_zh_a_spot_em()
            if not df_index.empty:
                # 上证指数
                sh_data = df_index[df_index['代码'] == '000001']
                if not sh_data.empty:
                    sh_close = sh_data.iloc[0]['最新价']
                    sh_pct = sh_data.iloc[0]['涨跌幅']
                    sign = "+" if sh_pct >= 0 else ""
                    print(f"  上证指数: {sh_close} ({sign}{sh_pct}%)")
                
                # 深证成指
                sz_data = df_index[df_index['代码'] == '399001']
                if not sz_data.empty:
                    sz_close = sz_data.iloc[0]['最新价']
                    sz_pct = sz_data.iloc[0]['涨跌幅']
                    sign = "+" if sz_pct >= 0 else ""
                    print(f"  深证成指: {sz_close} ({sign}{sz_pct}%)")
                
                # 创业板指
                cy_data = df_index[df_index['代码'] == '399006']
                if not cy_data.empty:
                    cy_close = cy_data.iloc[0]['最新价']
                    cy_pct = cy_data.iloc[0]['涨跌幅']
                    sign = "+" if cy_pct >= 0 else ""
                    print(f"  创业板指: {cy_close} ({sign}{cy_pct}%)")
        except Exception as e:
            print(f"  指数数据获取失败: {e}")
        
        # 查询涨跌统计
        print("\n【涨跌统计】")
        try:
            df_daily = pro.daily(trade_date=yesterday)
            if not df_daily.empty:
                up_count = len(df_daily[df_daily['pct_chg'] > 0])
                down_count = len(df_daily[df_daily['pct_chg'] < 0])
                flat_count = len(df_daily[df_daily['pct_chg'] == 0])
                total = len(df_daily)
                
                print(f"  上涨: {up_count} 只")
                print(f"  下跌: {down_count} 只")
                print(f"  平盘: {flat_count} 只")
                print(f"  总计: {total} 只")
        except Exception as e:
            print(f"  涨跌统计获取失败: {e}")
        
        # 使用 AkShare 获取涨停股票
        print("\n【涨幅榜 TOP5】")
        try:
            df_spot = ak.stock_zh_a_spot_em()
            if not df_spot.empty:
                top5 = df_spot.nlargest(5, '涨跌幅')
                for i, (_, row) in enumerate(top5.iterrows(), 1):
                    code = row['代码']
                    name = row['名称']
                    price = row['最新价']
                    pct = row['涨跌幅']
                    sign = "+" if pct >= 0 else ""
                    print(f"  {i}. {code} {name}: {price} ({sign}{pct}%)")
        except Exception as e:
            print(f"  涨幅榜获取失败: {e}")
        
        print("\n" + "="*40)
        print(f"数据日期: {yesterday_fmt}")
        print("数据来源: Tushare Pro + AkShare")
        
    except Exception as e:
        print(f"查询失败: {str(e)}")

if __name__ == "__main__":
    get_yesterday_a_share_summary()
