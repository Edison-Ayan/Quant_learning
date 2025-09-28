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
#log_return被添加到DataFrame

# # 收盘价走势图
# plt.figure(figsize=(12,5))
# plt.plot(df.index, df['close'], label='收盘价')
# plt.title(f"{ts_code} 日线收盘价")
# plt.xlabel('日期')
# plt.ylabel('价格')
# plt.grid(True)
# plt.legend()
# plt.tight_layout()
# plt.show()

# # 对数收益率走势
# plt.figure(figsize=(12,3))
# plt.plot(df.index, df['log_return'], label='对数收益率', color='orange')
# plt.axhline(0, linestyle='--', color='gray')
# plt.title(f"{ts_code} 日对数收益率")
# plt.grid(True)
# plt.tight_layout()
# plt.show()

#参数设置
# stock_list = ['000001.SZ','600519.SH','002415.SZ']

# os.makedirs('data',exist_ok=True)
# for code in stock_list:
#     df = pro.daily(ts_code=code,start_date=start_date,end_date=end_date)
#     df['trade_date'] = pd.to_datetime(df['trade_date'])
#     df = df.sort_values(by='trade_date')
#     df.set_index('trade_date',inplace=True)
#     df.to_csv(f'data/{code}_daily.csv')
#     print(f'数据已保存至data/{code}_daily.csv')

#保存为Parquet格式
# df.to_parquet('data/000001.SZ_daily.parquet')
# print("数据概况：")
# print(df.describe())

# print("\n最大涨幅（对数收益）:", df['log_return'].max())
# print("最大跌幅（对数收益）:", df['log_return'].min())
# print("平均日收益:", df['log_return'].mean())
# print("波动率:", df['log_return'].std())

