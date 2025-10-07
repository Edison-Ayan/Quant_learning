from sklearn.feature_selection import SelectKBest, f_regression

class FeatureSelector:
    def __init__(self):
        """初始化特征选择器"""
        self.k_best = None
        
    def select_features(self, train, test, k=43, p_value_threshold=0.05):
        """选择重要特征"""
        # 分离特征和目标变量
        X_train = train.drop('target', axis=1)
        y_train = train.target
        X_test = test.drop('target', axis=1)
        y_test = test.target
        
        # 使用f_regression作为分数函数初始化SelectKBest
        self.k_best = SelectKBest(score_func=f_regression, k=k)
        
        # 拟合变换
        self.k_best.fit(X_train, y_train)
        
        # 获取特征名称及索引位置
        feature_indices = self.k_best.get_support(indices=True)
        feature_names = X_train.columns[feature_indices]
        
        # 获取p值
        p_values = self.k_best.pvalues_
        
        # 创建特征列
        features = []
        
        # 只选择p值小于阈值的特征变量
        for feature, pvalue in zip(feature_names, p_values):
            if pvalue < p_value_threshold:
                features.append(feature)
        
        print(f"特征变量选取：{len(features)} 个")
        print(features)
        
        # 筛选特征
        X_train_kbest = X_train[features]
        X_test_kbest = X_test[features]
        
        return X_train_kbest, y_train, X_test_kbest, y_test, features