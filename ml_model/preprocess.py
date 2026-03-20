import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import joblib
import os

class HeartDataPreprocessor:
    """
    心脏病数据预处理类
    实现数据清洗、特征工程、标准化和编码等功能
    """
    
    def __init__(self):
        # 定义数值型特征和分类型特征，根据现有数据集调整
        self.numeric_features = ['age', 'cigsPerDay', 'totChol', 'sysBP', 'diaBP', 'BMI', 'heartRate', 'glucose']
        self.categorical_features = ['male', 'education', 'currentSmoker', 'BPMeds', 'prevalentStroke', 'prevalentHyp', 'diabetes']
        
        # 创建预处理管道
        self.preprocessor = None
        
    def fit(self, X):
        """
        拟合预处理器
        
        参数:
            X (DataFrame): 训练数据
        """
        # 数值特征处理管道：缺失值填充 + 标准化
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])
        
        # 分类特征处理管道：缺失值填充 + One-hot编码
        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
        ])
        
        # 组合所有特征处理管道
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, self.numeric_features),
                ('cat', categorical_transformer, self.categorical_features)
            ],
            remainder='drop'  # 明确设置remainder参数，避免使用默认的passthrough
        )
        
        # 拟合预处理器
        self.preprocessor.fit(X)
        return self
    
    def transform(self, X):
        """
        转换数据
        
        参数:
            X (DataFrame): 需要转换的数据
            
        返回:
            转换后的数据
        """
        if self.preprocessor is None:
            raise ValueError("预处理器尚未拟合，请先调用fit方法")
        
        return self.preprocessor.transform(X)
    
    def fit_transform(self, X):
        """
        拟合并转换数据
        
        参数:
            X (DataFrame): 需要拟合和转换的数据
            
        返回:
            转换后的数据
        """
        return self.fit(X).transform(X)
    
    def save(self, filepath):
        """
        保存预处理器
        
        参数:
            filepath (str): 保存路径
        """
        if self.preprocessor is None:
            raise ValueError("预处理器尚未拟合，请先调用fit方法")
        
        # 保存预处理器
        joblib.dump(self.preprocessor, filepath)
        
    def load(self, filepath):
        """
        加载预处理器
        
        参数:
            filepath (str): 加载路径
        """
        self.preprocessor = joblib.load(filepath)
        return self
    
    def get_feature_names(self):
        """
        获取转换后的特征名称
        
        返回:
            特征名称列表
        """
        if self.preprocessor is None:
            raise ValueError("预处理器尚未拟合，请先调用fit方法")
        
        try:
            # 尝试使用新版本的 get_feature_names_out 方法
            return list(self.preprocessor.get_feature_names_out())
        except AttributeError:
            # 如果不支持，则使用旧版本的方法
            # 获取数值特征名称
            numeric_features = self.numeric_features
            
            # 获取分类特征名称
            categorical_features = []
            onehot = self.preprocessor.named_transformers_['cat'].named_steps['onehot']
            for i, category in enumerate(self.categorical_features):
                categories = onehot.categories_[i]
                for cat in categories:
                    categorical_features.append(f"{category}_{cat}")
            
            # 合并所有特征名称
            return numeric_features + categorical_features

def load_data(filepath):
    """
    加载心脏病数据集
    
    参数:
        filepath (str): 数据文件路径
        
    返回:
        X (DataFrame): 特征数据
        y (Series): 目标变量
    """
    # 加载数据
    data = pd.read_csv(filepath)
    
    # 分离特征和目标变量
    X = data.drop('TenYearCHD', axis=1)
    y = data['TenYearCHD']
    
    return X, y

def clean_data(X):
    """
    数据清洗
    
    参数:
        X (DataFrame): 原始特征数据
        
    返回:
        清洗后的特征数据
    """
    # 复制数据，避免修改原始数据
    X_clean = X.copy()
    
    # 处理异常值（用IQR方法）
    for col in X_clean.select_dtypes(include=[np.number]).columns:
        Q1 = X_clean[col].quantile(0.25)
        Q3 = X_clean[col].quantile(0.75)
        IQR = Q3 - Q1
        
        # 将超出范围的值设为边界值
        X_clean.loc[X_clean[col] < (Q1 - 1.5 * IQR), col] = Q1 - 1.5 * IQR
        X_clean.loc[X_clean[col] > (Q3 + 1.5 * IQR), col] = Q3 + 1.5 * IQR
    
    return X_clean 