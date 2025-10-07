import tushare as ts
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt

ts.set_token('4802ae7acc89b1e849a7c9d39078c638213502e945c5c1d886ed877d')
pro = ts.pro_api()

# 参数设置
ts_code = '000001.SZ'  # 平安银行
start_date = '20250101'
end_date = '20250601'

# 下载日线行情数据
df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)

# 数据清洗与格式调整
df['trade_date'] = pd.to_datetime(df['trade_date'])
df = df.sort_values('trade_date')
df.set_index('trade_date', inplace=True)

# 保存为本地CSV
os.makedirs('data', exist_ok=True)
csv_path = f'data/{ts_code}_daily.csv'
df.to_csv(csv_path)
print(f"数据保存至：{csv_path}")

#重读数据
df = pd.read_csv(csv_path,index_col=['trade_date'],parse_dates=True)
print("缺失值统计：\n",df.isnull().sum())
df.dropna(inplace=True)

df['log_return'] = np.log(df['close']/df['close'].shift(1))
df.dropna(inplace=True)

