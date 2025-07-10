"""
数据下载器测试
"""

import unittest
import pandas as pd
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.downloader import DataDownloader


class TestDataDownloader(unittest.TestCase):
    """数据下载器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.downloader = DataDownloader()
    
    def test_download_stock_data(self):
        """测试股票数据下载"""
        # 测试下载单只股票数据
        df = self.downloader.download_stock_data(
            stock_code='000001',
            start_date='2023-01-01',
            end_date='2023-01-10'
        )
        
        # 检查数据不为空
        self.assertFalse(df.empty)
        
        # 检查必要的列存在
        required_columns = ['open', 'close', 'high', 'low', 'volume']
        for col in required_columns:
            self.assertIn(col, df.columns)
        
        # 检查数据类型
        self.assertIsInstance(df.index, pd.DatetimeIndex)
    
    def test_download_stock_batch(self):
        """测试批量股票数据下载"""
        stock_codes = ['000001', '000002']
        
        result = self.downloader.download_stock_batch(
            stock_codes=stock_codes,
            start_date='2023-01-01',
            end_date='2023-01-10'
        )
        
        # 检查返回的字典
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), len(stock_codes))
        
        # 检查每只股票的数据
        for code in stock_codes:
            self.assertIn(code, result)
            self.assertFalse(result[code].empty)
    
    def test_download_index_data(self):
        """测试指数数据下载"""
        df = self.downloader.download_index_data(
            index_code='000300',
            start_date='2023-01-01',
            end_date='2023-01-10'
        )
        
        # 检查数据不为空
        self.assertFalse(df.empty)
        
        # 检查数据类型
        self.assertIsInstance(df.index, pd.DatetimeIndex)
    
    def test_get_stock_list(self):
        """测试获取股票列表"""
        df = self.downloader.get_stock_list()
        
        # 检查数据不为空
        self.assertFalse(df.empty)
        
        # 检查包含股票代码列
        self.assertTrue(any('代码' in col for col in df.columns))


if __name__ == '__main__':
    unittest.main() 