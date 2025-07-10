# 量化分析项目 (QuantL)

基于akshare的量化分析项目，提供完整的量化投资分析框架。

## 📋 项目简介

QuantL是一个基于Python的量化投资分析框架，集成了数据获取、技术分析、策略回测、可视化展示等功能。项目采用模块化设计，易于扩展和维护。

## 🏗️ 项目结构

```
quantL/
├── 📁 data/                   # 数据存储目录
│   ├── raw/                  # 原始数据
│   ├── processed/            # 处理后的数据
│   └── cache/                # 缓存数据
├── 📁 src/                   # 源代码
│   ├── 📁 data/              # 数据获取和处理模块
│   │   └── downloader.py     # 基于akshare的数据下载器
│   ├── 📁 analysis/          # 分析模块
│   │   └── technical_indicators.py  # 技术指标计算
│   ├── 📁 strategy/          # 策略模块
│   │   ├── base_strategy.py  # 策略基类
│   │   └── dual_ma_strategy.py  # 双均线策略
│   ├── 📁 backtest/          # 回测模块
│   │   └── backtest_engine.py  # 回测引擎
│   ├── 📁 visualization/     # 可视化模块
│   │   └── charts.py         # 图表绘制
│   └── 📁 utils/             # 工具函数
│       ├── config.py         # 配置管理
│       └── logger.py         # 日志管理
├── 📁 config/                # 配置文件
│   └── config.yaml           # 项目配置
├── 📁 notebooks/             # Jupyter notebooks
│   └── 01_data_download.ipynb  # 数据下载示例
├── 📁 tests/                 # 测试文件
│   └── test_downloader.py    # 数据下载器测试
├── 📁 logs/                  # 日志文件
├── 📁 outputs/               # 输出文件
├── 📄 requirements.txt       # 依赖包
├── 📄 main.py               # 主程序入口
├── 📄 example.py            # 示例脚本
└── 📄 README.md             # 项目说明
```

## ✨ 功能特性

- 📊 **数据获取**: 基于akshare的股票、指数、基金数据下载
- 📈 **技术分析**: 移动平均线、MACD、RSI、布林带、KDJ等指标
- 🎯 **量化策略**: 双均线策略（可扩展其他策略）
- 📉 **回测分析**: 完整的回测引擎，支持交易成本、滑点等
- 📊 **可视化**: K线图、技术指标图、回测结果图等
- ⚙️ **配置管理**: 统一的配置文件和参数管理
- 📝 **日志系统**: 完整的日志记录和错误处理
- 🔧 **模块化设计**: 易于扩展和维护

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+
- pip

### 2. 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd quantL

# 安装依赖包
pip install -r requirements.txt
```

### 3. 配置项目

编辑 `config/config.yaml` 文件，根据需要调整配置参数：

```yaml
# 股票池配置
stock_pool:
  default:
    - "000001"  # 平安银行
    - "000002"  # 万科A
    - "600519"  # 贵州茅台

# 回测配置
backtest:
  initial_capital: 1000000  # 初始资金
  commission: 0.0003        # 手续费
```

### 4. 运行示例

```bash
# 运行完整流程
python main.py --all

# 或者分步运行
python main.py --download    # 下载数据
python main.py --analyze     # 技术分析
python main.py --strategy    # 运行策略
python main.py --backtest    # 回测
python main.py --visualize   # 生成图表

# 运行示例脚本
python example.py
```

## 📖 使用指南

### 数据下载

```python
from src.data.downloader import downloader

# 下载单只股票数据
df = downloader.download_stock_data(
    stock_code='000001',
    start_date='2023-01-01',
    end_date='2023-12-31'
)

# 批量下载股票数据
stock_data = downloader.download_stock_batch(
    stock_codes=['000001', '000002'],
    start_date='2023-01-01',
    end_date='2023-12-31'
)
```

### 技术分析

```python
from src.analysis.technical_indicators import technical_indicators

# 计算所有技术指标
df_with_indicators = technical_indicators.calculate_all_indicators(df)

# 生成交易信号
df_with_signals = technical_indicators.generate_signals(df_with_indicators)
```

### 策略回测

```python
from src.strategy.dual_ma_strategy import DualMAStrategy
from src.backtest.backtest_engine import backtest_engine

# 创建策略
strategy = DualMAStrategy({
    'short_ma': 5,
    'long_ma': 20,
    'position_size': 0.1
})

# 运行回测
results = backtest_engine.run_backtest(
    strategy=strategy,
    data=stock_data,
    start_date='2023-01-01',
    end_date='2023-12-31'
)
```

### 可视化

```python
from src.visualization.charts import chart_maker

# 绘制K线图
chart_maker.plot_candlestick(df, title="股票K线图")

# 绘制技术指标图
chart_maker.plot_technical_indicators(df_with_indicators)

# 绘制回测结果
backtest_engine.plot_results(results)
```

## 📊 支持的技术指标

- **移动平均线**: MA、EMA
- **MACD**: 指数平滑移动平均线
- **RSI**: 相对强弱指标
- **布林带**: Bollinger Bands
- **KDJ**: 随机指标
- **ATR**: 平均真实波幅
- **成交量指标**: OBV、成交量比率

## 🎯 支持的策略

- **双均线策略**: 基于短期和长期移动平均线交叉
- **可扩展**: 基于策略基类，易于实现新策略

## 📈 回测功能

- 支持多股票组合回测
- 考虑交易成本和滑点
- 计算关键指标：收益率、夏普比率、最大回撤
- 生成详细的交易记录和持仓报告

## 📊 可视化功能

- K线图（支持成交量）
- 技术指标图
- 回测结果图
- 交易分析图
- 交互式图表（Plotly）

## ⚙️ 配置说明

主要配置项包括：

- **数据源配置**: akshare参数、数据路径
- **股票池配置**: 默认股票列表、行业分类
- **技术指标参数**: 各指标的周期和阈值
- **策略参数**: 策略相关参数
- **回测参数**: 初始资金、交易成本、风险控制
- **可视化配置**: 图表样式、颜色主题

## 🧪 测试

```bash
# 运行测试
python -m pytest tests/

# 运行特定测试
python tests/test_downloader.py
```

## 📝 日志

项目使用统一的日志系统，日志文件保存在 `logs/` 目录下：

- 控制台输出：实时显示运行状态
- 文件记录：详细的操作日志

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [akshare](https://github.com/akfamily/akshare) - 开源金融数据接口
- [pandas](https://pandas.pydata.org/) - 数据分析库
- [matplotlib](https://matplotlib.org/) - 绘图库
- [talib](https://mrjbq7.github.io/ta-lib/) - 技术分析库

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件
- 项目讨论区

---

**注意**: 本项目仅供学习和研究使用，不构成投资建议。投资有风险，入市需谨慎。 