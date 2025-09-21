import pandas as pd
import matplotlib.pyplot as plt
import os
from matplotlib.dates import DateFormatter, WeekdayLocator, DayLocator, MONDAY
from matplotlib.patches import Rectangle
import matplotlib.dates as mdates
from datetime import datetime
from CUSUM_filter import getTEvents
from getDailyVol import getDailyVol

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


# ... existing code ...

def plot_sz_stock_kline(df, symbol):
    """
    绘制A股股票K线图，并正确设置横纵坐标
    
    参数:
    df (pandas.DataFrame): 包含OHLC数据的DataFrame，索引为日期
    symbol (str): 股票代码
    """
    # 创建图形和坐标轴
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12), gridspec_kw={'height_ratios': [3, 1]})
    
    # 设置横坐标为日期格式
    mondays = WeekdayLocator(MONDAY)  # 主要刻度为周一
    alldays = DayLocator()  # 次要刻度为每一天
    weekFormatter = DateFormatter('%Y-%m-%d')  # 主刻度格式
    
    # 为两个子图设置相同的X轴
    ax1.xaxis.set_major_locator(mondays)
    ax1.xaxis.set_minor_locator(alldays)
    ax1.xaxis.set_major_formatter(weekFormatter)
    ax2.xaxis.set_major_locator(mondays)
    ax2.xaxis.set_minor_locator(alldays)
    ax2.xaxis.set_major_formatter(weekFormatter)
    
    # 旋转和对齐日期标签以避免重叠
    fig.autofmt_xdate()
    
    # 绘制K线图
    for i in range(len(df)):
        date = df.index[i]
        open_price = df.loc[date, 'open']
        close_price = df.loc[date, 'close']
        high_price = df.loc[date, 'high']
        low_price = df.loc[date, 'low']
        volume = df.loc[date, 'vol']
        
        # 确定K线颜色（收盘价高于或等于开盘价为红色，否则为绿色）
        color = 'red' if close_price >= open_price else 'green'
        
        # 绘制蜡烛线
        ax1.plot([date, date], [low_price, high_price], color=color, linewidth=1)
        ax1.bar(date, abs(close_price - open_price), bottom=min(open_price, close_price), 
                width=0.6, color=color)
        
        # 绘制成交量柱状图
        ax2.bar(date, volume, width=0.6, color=color)
    
    # 计算并标记CUSUM事件
    vol_series = getDailyVol(df['close'], span0=30)
    # 增加阈值倍数，默认为1.5，可以根据需要调整为2.0或更高
    threshold_multiplier = 20
    h = vol_series * threshold_multiplier  # 使用每日回报的标准差的倍数作为阈值
    
    # 输出波动率和阈值信息，便于调试
    
    t_events = getTEvents(df['close'], h)
    
    if len(t_events) > 0:
        # 找出在数据时间范围内的事件
        valid_events = t_events[t_events.isin(df.index)]
        
        if len(valid_events) > 0:
            # 获取这些事件对应的最高价，用于放置标记
            event_prices = df.loc[valid_events, 'high'] * 1.02  # 在最高价上方2%处标记
            
            # 绘制事件点标记
            ax1.scatter(valid_events, event_prices, color='blue', marker='^', s=100, zorder=5, 
                      label=f'CUSUM事件 ({len(valid_events)}个)')
            ax1.legend()
            print(f"在K线图上标记了 {len(valid_events)} 个CUSUM事件点")
    
    # 设置图表标题和坐标轴标签
    stock_name = "平安银行"  # 000001.SZ对应的股票名称
    ax1.set_title(f'{stock_name}({symbol}) 日线图', fontsize=16)
    ax1.set_ylabel('价格 (元)', fontsize=12)
    ax2.set_ylabel('成交量', fontsize=12)
    ax2.set_xlabel('日期', fontsize=12)
    
    # 设置网格线
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax2.grid(True, linestyle='--', alpha=0.7)
    
    # 设置坐标轴范围
    ax1.set_xlim(df.index.min() - pd.Timedelta(days=1), df.index.max() + pd.Timedelta(days=1))
    price_range = df['high'].max() - df['low'].min()
    ax1.set_ylim(df['low'].min() - price_range * 0.05, df['high'].max() + price_range * 0.05)
    
    plt.tight_layout()
    
    # 创建保存目录（如果不存在）
    os.makedirs('data', exist_ok=True)
    
    # 保存图片
    image_path = f'data/{symbol}_daily_k_line.png'
    plt.savefig(image_path, dpi=300)
    print(f"K线图已保存至：{image_path}")
    
    plt.show()

def main():
    # 股票代码
    ts_code = "000001.SZ"
    
    # 数据文件路径
    csv_path = f'data/{ts_code}_data.csv'
    
    # 检查文件是否存在
    if not os.path.exists(csv_path):
        print(f"错误：数据文件 {csv_path} 不存在。")
        return
    
    # 读取数据
    print(f"正在读取数据文件：{csv_path}")
    df = pd.read_csv(csv_path, parse_dates=['trade_time'], index_col='trade_time')
    
    # 按时间排序
    df = df.sort_index()
    
    print(f"数据形状：{df.shape}")
    print(f"数据时间范围：{df.index.min()} 至 {df.index.max()}")
    print("数据前5行：")
    print(df.head())
    
    # 绘制K线图
    print("\n正在绘制K线图...")
    plot_sz_stock_kline(df, ts_code)
    
    print("\nK线图绘制完成！")


if __name__ == "__main__":
    main()