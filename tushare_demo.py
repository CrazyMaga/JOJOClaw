import tushare as ts

ts.set_token("03eed883a368f22668fd2e781d1002fe2445dc3bde2c48db43a8f6b9")
pro = ts.pro_api()

def get_stock_info(ts_code="000001.SZ"):
    try:
        df = pro.stock_basic(ts_code=ts_code)
        return df.to_json(orient="records")
    except Exception as e:
        return f"获取数据失败：{str(e)}"

if __name__ == "__main__":
    print(get_stock_info())
