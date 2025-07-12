# 基本面数据使用指南

## 概述

本项目支持下载和分析多种基本面数据，包括财务报表、估值指标、行业分类等。这些数据可以用于基本面分析、价值投资策略等。

## 数据类型

### 1. 财务报表数据 (Financial Statements)

#### 支持的报表类型：
- **利润表** (`income`): 营业收入、净利润、毛利率等
- **资产负债表** (`balance`): 总资产、负债、股东权益等
- **现金流量表** (`cash_flow`): 经营活动现金流、投资活动现金流等

#### 使用方法：
```python
# 下载单个股票的利润表
income_df = downloader.download_financial_statement(
    stock_code="000001",
    statement_type="income",
    period="annual"  # annual 或 quarterly
)

# 批量下载财务报表
fundamental_data = downloader.download_fundamental_batch(
    stock_codes=["000001", "000002", "000858"],
    data_types=["financial"]
)
```

### 2. 估值指标数据 (Valuation Indicators)

#### 包含的指标：
- **PE (市盈率)**: 股价与每股收益的比率
- **PB (市净率)**: 股价与每股净资产的比率
- **PS (市销率)**: 股价与每股销售额的比率
- **市值 (Market Cap)**: 公司总市值
- **ROE (净资产收益率)**: 净利润与股东权益的比率

#### 使用方法：
```python
# 下载估值指标
valuation_df = downloader.download_valuation_indicators(
    stock_code="000001",
    start_date="2020-01-01",
    end_date="2023-12-31"
)
```

### 3. 行业分类数据 (Industry Classification)

#### 包含的信息：
- **申万行业分类**: 标准化的行业分类体系
- **个股行业信息**: 每只股票所属的行业、概念等

#### 使用方法：
```python
# 下载行业分类数据
industry_df = downloader.download_industry_classification()

# 下载个股行业信息
industry_info = downloader.download_stock_industry_info("000001")
```

## 命令行使用

### 下载基本面数据
```bash
# 下载所有基本面数据
python main.py --fundamental

# 下载完整数据（包括基本面）
python main.py --download
```

### 运行基本面分析示例
```bash
python examples/fundamental_analysis.py
```

### 运行测试
```bash
# 使用测试运行脚本（推荐）
python run_tests.py --all                    # 运行所有测试
python run_tests.py --fundamental            # 只运行基本面数据测试
python run_tests.py --example                # 只运行示例程序

# 直接运行测试文件
python tests/test_downloader.py              # 运行所有单元测试
python -m pytest tests/                      # 使用pytest运行测试
```

## 数据分析示例

### 1. 财务分析
```python
def analyze_financial_health(fundamental_data):
    """分析财务健康状况"""
    results = {}
    
    for stock_code, stock_data in fundamental_data.items():
        if "financial_income" in stock_data:
            income_df = stock_data["financial_income"]
            
            # 分析营业收入增长
            if "营业收入" in income_df.columns:
                revenue_growth = calculate_growth_rate(income_df["营业收入"])
                
                # 分析净利润增长
                if "净利润" in income_df.columns:
                    profit_growth = calculate_growth_rate(income_df["净利润"])
                    
                    results[stock_code] = {
                        "revenue_growth": revenue_growth,
                        "profit_growth": profit_growth
                    }
    
    return results
```

### 2. 估值分析
```python
def find_undervalued_stocks(valuation_data):
    """寻找被低估的股票"""
    undervalued = []
    
    for stock_code, data in valuation_data.items():
        pe = data.get("pe_ratio")
        pb = data.get("pb_ratio")
        
        # 筛选条件：PE < 15 且 PB < 2
        if pe and pb and pe < 15 and pb < 2:
            undervalued.append({
                "stock_code": stock_code,
                "pe": pe,
                "pb": pb
            })
    
    return undervalued
```

### 3. 行业分析
```python
def analyze_industry_performance(fundamental_data, industry_data):
    """分析行业表现"""
    industry_stats = {}
    
    for stock_code, stock_data in fundamental_data.items():
        if "industry" in stock_data:
            industry = stock_data["industry"].get("所属行业", "未知")
            
            if industry not in industry_stats:
                industry_stats[industry] = {
                    "stocks": [],
                    "avg_pe": [],
                    "avg_pb": []
                }
            
            industry_stats[industry]["stocks"].append(stock_code)
            
            # 添加估值指标
            if "valuation" in stock_data:
                valuation = stock_data["valuation"]
                if not valuation.empty:
                    latest = valuation.iloc[-1]
                    if latest.get("pe"):
                        industry_stats[industry]["avg_pe"].append(latest["pe"])
                    if latest.get("pb"):
                        industry_stats[industry]["avg_pb"].append(latest["pb"])
    
    # 计算平均值
    for industry, stats in industry_stats.items():
        if stats["avg_pe"]:
            stats["avg_pe"] = np.mean(stats["avg_pe"])
        if stats["avg_pb"]:
            stats["avg_pb"] = np.mean(stats["avg_pb"])
    
    return industry_stats
```

## 数据文件结构

下载的数据会保存在以下目录：

```
data/
├── raw_data/
│   ├── 000001_income_annual.csv      # 财务报表
│   ├── 000001_valuation.csv          # 估值指标
│   ├── 000001_industry_info.csv      # 行业信息
│   └── ...
└── cache_data/
    ├── stock_list.csv                # 股票列表
    └── industry_classification.csv   # 行业分类
```

## 注意事项

1. **数据频率**: 财务报表数据通常按季度或年度发布，更新频率较低
2. **数据延迟**: 基本面数据可能有1-3个月的延迟
3. **数据质量**: 部分股票可能缺少某些财务数据，需要做好异常处理
4. **请求限制**: 避免过于频繁的请求，建议在批量下载时增加适当的延时

## 扩展功能

### 自定义分析指标
```python
def calculate_custom_metrics(fundamental_data):
    """计算自定义财务指标"""
    metrics = {}
    
    for stock_code, stock_data in fundamental_data.items():
        if "financial_income" in stock_data and "financial_balance" in stock_data:
            income_df = stock_data["financial_income"]
            balance_df = stock_data["financial_balance"]
            
            # 计算ROE
            if "净利润" in income_df.columns and "股东权益" in balance_df.columns:
                roe = income_df["净利润"].iloc[-1] / balance_df["股东权益"].iloc[-1]
                metrics[stock_code] = {"ROE": roe}
    
    return metrics
```

### 基本面筛选策略
```python
def fundamental_screening(fundamental_data, criteria):
    """基本面筛选"""
    qualified_stocks = []
    
    for stock_code, stock_data in fundamental_data.items():
        if meets_criteria(stock_data, criteria):
            qualified_stocks.append(stock_code)
    
    return qualified_stocks
```

通过以上功能，你可以进行全面的基本面分析，为投资决策提供数据支持。 