"""
接口测试脚本 for DataDownloader
"""
import os
import sys
import pandas as pd

# 将项目根目录添加到Python路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.downloader import DataDownloader
from src.utils.config import config

def get_test_downloader() -> DataDownloader:
    """
    创建一个用于测试的 Downloader 实例，并将其数据路径指向测试目录。
    """
    downloader = DataDownloader()
    
    # 获取当前测试文件的目录，并创建测试数据子目录
    test_dir = os.path.dirname(__file__)
    raw_data_path = os.path.join(test_dir, 'test_data', 'raw_data')
    cache_data_path = os.path.join(test_dir, 'test_data', 'cache_data')

    # 确保目录存在
    os.makedirs(raw_data_path, exist_ok=True)
    os.makedirs(cache_data_path, exist_ok=True)

    # 直接修改实例的路径属性
    downloader.raw_data_path = raw_data_path
    downloader.cache_data_path = cache_data_path
    
    print(f"测试数据将保存在: {os.path.join(test_dir, 'test_data')}")
    return downloader


def test_downloader_interfaces():
    """
    对 DataDownloader 中的每个方法进行接口连通性测试。
    """
    downloader = get_test_downloader()

    # --- 测试参数 ---
    stock_code = '000001'  # 平安银行
    index_code = '000300'  # 沪深300
    start_date = '2024-01-01'
    end_date = '2024-01-05'

    # --- 执行测试 ---
    
    print("\n" + "="*20 + " 1. 测试获取股票列表 " + "="*20)
    stock_list_df = downloader.get_stock_list()
    if not stock_list_df.empty:
        print("✅ 股票列表获取成功！")
        print(stock_list_df.head())
    else:
        print("❌ 股票列表获取失败。")

    print("\n" + "="*20 + " 2. 测试下载单只股票历史行情 " + "="*20)
    stock_data_df = downloader.download_stock_data(
        stock_code=stock_code,
        start_date=start_date,
        end_date=end_date
    )
    if not stock_data_df.empty:
        print(f"✅ {stock_code} 历史行情下载成功！")
        print(stock_data_df)
    else:
        print(f"❌ {stock_code} 历史行情下载失败。")

    print("\n" + "="*20 + " 3. 测试下载指数历史行情 " + "="*20)
    index_data_df = downloader.download_index_data(
        index_code=index_code,
        start_date=start_date,
        end_date=end_date
    )
    if not index_data_df.empty:
        print(f"✅ {index_code} 指数行情下载成功！")
        print(index_data_df)
    else:
        print(f"❌ {index_code} 指数行情下载失败。")
        
    print("\n" + "="*20 + " 4. 测试批量下载股票数据 " + "="*20)
    batch_result = downloader.download_stock_batch(
        stock_codes=[stock_code, '600519'],
        start_date=start_date,
        end_date=end_date
    )
    if batch_result:
        print("✅ 批量下载成功！")
        for code, df in batch_result.items():
            print(f"--- {code} ---")
            print(df.head())
    else:
        print("❌ 批量下载失败。")


if __name__ == '__main__':
    # 为了在终端获得更好的可读性，配置 pandas
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    
    test_downloader_interfaces() 