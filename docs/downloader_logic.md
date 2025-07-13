# DataDownloader 逻辑说明文档

本文档旨在详细阐述 `DataDownloader` 类的设计理念、核心功能及使用方法，帮助开发者更好地理解和使用该工具。

## 1. 设计目标

`DataDownloader` 类是一个专注于提供**技术面分析**所需金融数据的工具。它的核心目标是：
- **简洁高效**：提供清晰、简单的接口，专门用于获取股票和指数的历史行情、资金流向等技术面关键数据。
- **稳定可靠**：基于 `akshare` 库，并内置了日志记录和异常处理机制，以确保数据下载过程的稳定性。
- **数据持久化**：能够自动将下载的数据以 CSV 格式保存到本地，方便后续的读取和分析，避免重复下载。

## 2. 核心功能详解

`DataDownloader` 类主要包含以下几个公共方法：

### 2.1 `get_stock_list()`
- **功能**：获取当前市场上所有A股的股票列表。这是进行批量数据处理的基础。
- **实现逻辑**：调用 `akshare` 的 `stock_info_a_code_name()` 接口，该接口只返回股票代码和名称，效率较高。
- **数据存储**：下载的列表会以 `stock_list.csv` 的形式缓存在 `cache_data` 目录下。

### 2.2 `download_stock_data(...)`
- **功能**：获取单只股票的日线、周线或月线级别的历史行情数据。
- **参数**：
    - `stock_code`: 股票代码 (e.g., '000001')。
    - `start_date`, `end_date`: 日期范围。
    - `period`: 周期 ('daily', 'weekly', 'monthly')。
    - `adjust`: 复权类型 ('qfq', 'hfq')。
- **实现逻辑**：
    1. 调用 `akshare` 的 `stock_zh_a_hist` 接口获取原始数据。
    2. 对返回的DataFrame进行清洗：重命名列（如 '日期' -> 'date'），并将日期列设为索引。
    3. 将清洗后的数据保存到 `raw_data` 目录下的 CSV 文件中。
- **返回值**：一个包含OHLCV、成交额、换手率等信息的 `pandas.DataFrame`。

### 2.3 `download_stock_batch(...)`
- **功能**：对 `download_stock_data` 的封装，用于批量下载多只股票的历史行情。
- **实现逻辑**：通过循环遍历输入的股票代码列表，逐个调用 `download_stock_data` 方法。为了防止请求过于频繁，每次调用后会暂停0.5秒。
- **返回值**：一个字典，键为股票代码，值为对应的历史行情 `DataFrame`。

### 2.4 `download_index_data(...)`
- **功能**：获取如沪深300、上证50等主要指数的历史行情数据。
- **实现逻辑**：调用 `akshare` 的 `index_zh_a_hist` 接口，后续的数据清洗和存储流程与 `download_stock_data` 类似。
- **返回值**：一个包含指数OHLCV等信息的 `pandas.DataFrame`。

### 2.5 `download_money_flow(...)`
- **功能**：获取单只股票的每日资金流向数据，是判断主力资金动态的重要技术指标。
- **实现逻辑**：调用 `akshare` 的 `stock_individual_fund_flow` 接口，并对返回数据进行标准化处理。
- **返回值**：一个包含主力净流入、超大单净流入等资金流详情的 `pandas.DataFrame`。

## 3. 数据存储机制

- **`_save_data(...)`**: 这是一个内部私有方法，负责所有数据的持久化存储。
- **存储路径**：
    - **原始数据 (`raw_data`)**: 存放需要重复使用的原始时间序列数据，如个股行情、指数行情、资金流数据等。文件名通常以 `代码_类型.csv` 的格式命名。
    - **缓存数据 (`cache_data`)**: 存放不经常变动但会频繁使用的数据，如 `stock_list.csv`。
- **路径配置**：所有的数据存储路径都通过 `src/utils/config.py` 进行统一管理，方便修改和维护。在本次测试中，该路径被临时指向了 `tests/test_data` 目录。

## 4. 如何使用

以下是一个简单的使用示例：

```python
from src.data.downloader import DataDownloader

# 1. 初始化下载器
downloader = DataDownloader()

# 2. 获取股票列表
stock_list = downloader.get_stock_list()
print("股票总数:", len(stock_list))

# 3. 下载单只股票的行情和资金流数据
stock_df = downloader.download_stock_data(stock_code='000001', start_date='2024-01-01', end_date='2024-01-31')
money_flow_df = downloader.download_money_flow(stock_code='000001')

print("\n平安银行 1月份历史行情:")
print(stock_df.head())

print("\n平安银行 资金流向:")
print(money_flow_df.head())
``` 