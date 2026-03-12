import tushare as ts

pro = ts.pro_api('e71c793f44bc9d99bdd321ec7dc1ddbba53faf1a63278fabeae21b44')

# Get stock names for our 5 recommendations
stocks = ['002445.SZ', '600135.SH', '600172.SH', '603017.SH', '603421.SH', '000839.SZ', '002969.SZ', '002298.SZ', '002335.SZ', '600330.SH']

df = pro.stock_basic(ts_code=','.join(stocks), fields='ts_code,name')
print(df.to_string(index=False))
