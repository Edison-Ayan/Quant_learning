import pandas as pd
from Tool.get_csv_data_akshare import get_stock_data_skshare, get_indices_data_akshare
from Tool.feature_engineering import feature_engineering

class DataLoader:
    def __init__(self, use_local_data=True):
        """初始化数据加载器"""
        self.use_local_data = use_local_data
        self.stock_datas = None
        self.index_datas = None
        
    def load_stock_data(self, stock_codes=["600519", "002230", "000333"]):
        """加载股票数据"""
        self.stock_datas = get_stock_data_skshare(stock_codes, use_local_data=self.use_local_data)
        return self.stock_datas
        
    def load_index_data(self, index_codes=["000001", "399001", "000300"]):
        """加载指数数据"""
        self.index_datas = get_indices_data_akshare(index_codes, use_local_data=self.use_local_data)
        return self.index_datas
        
    def split_train_test(self, data, train_year_threshold=2021):
        """将数据分割为训练集和测试集"""
        data.index = pd.to_datetime(data.index)
        train = data[data.index.year <= train_year_threshold]
        test = data[data.index.year > train_year_threshold]
        
        # 应用特征工程
        train = feature_engineering(train)
        test = feature_engineering(test)
        
        return train, test