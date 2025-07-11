# QuantL - 量化分析平台

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

## 📖 项目简介

QuantL 是一个基于 Python 的量化分析平台，专注于金融数据的获取、分析和策略回测。项目采用模块化设计，提供完整的数据处理流程和策略开发框架。

## ✨ 主要功能

### 📊 数据管理
- **多源数据获取**: 支持 akshare、tushare 等数据源
- **股票数据**: 历史行情、实时数据、基本面数据
- **指数数据**: 主要指数历史数据
- **基金数据**: 基金净值、持仓信息
- **数据缓存**: 智能缓存机制，提高数据获取效率

### 🔍 数据分析
- **技术指标**: 常用技术指标计算
- **统计分析**: 收益率分析、风险指标
- **可视化**: 交互式图表展示

### 📈 策略回测
- **策略框架**: 灵活的策略开发框架
- **回测引擎**: 历史数据回测
- **绩效评估**: 夏普比率、最大回撤等指标

### 🎯 风险管理
- **仓位管理**: 动态仓位控制
- **止损止盈**: 风险控制机制
- **组合优化**: 投资组合优化

## 🚀 快速开始

### 环境要求
- Python 3.8+
- pip

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/ioyy900205/quantL.git
cd quantL
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境**
```bash
# 复制配置文件模板
cp config/config.example.yaml config/config.yaml
# 编辑配置文件，设置数据源等参数
```

4. **运行示例**
```bash
python main.py
```

## 📁 项目结构

```
quantL/
├── src/                    # 源代码目录
│   ├── data/              # 数据模块
│   │   ├── downloader.py  # 数据下载器
│   │   └── __init__.py
│   ├── analysis/          # 分析模块
│   ├── strategy/          # 策略模块
│   ├── backtest/          # 回测模块
│   ├── visualization/     # 可视化模块
│   └── utils/             # 工具模块
├── config/                # 配置文件
├── data/                  # 数据存储目录
├── logs/                  # 日志文件
├── outputs/               # 输出结果
├── tests/                 # 测试文件
├── docs/                  # 文档
├── main.py               # 主程序入口
├── requirements.txt      # 依赖包列表
└── README.md            # 项目说明
```

## 🔧 使用指南

### 数据下载示例

```python
from src.data.downloader import DataDownloader

# 创建下载器实例
downloader = DataDownloader()

# 下载单只股票数据
df = downloader.download_stock_data(
    stock_code="000001",
    start_date="2023-01-01",
    end_date="2023-12-31"
)

# 批量下载股票数据
stock_codes = ["000001", "000002", "000858"]
results = downloader.download_stock_batch(stock_codes)
```

### 策略开发示例

```python
from src.strategy.base import BaseStrategy

class MyStrategy(BaseStrategy):
    def __init__(self):
        super().__init__()
    
    def generate_signals(self, data):
        # 实现您的策略逻辑
        return signals
```

## 🤝 贡献指南

我们欢迎所有形式的贡献！无论是代码贡献、文档改进、问题报告还是功能建议，都非常欢迎。

### 如何贡献

1. **Fork 项目**
2. **创建功能分支**: `git checkout -b feature/AmazingFeature`
3. **提交更改**: `git commit -m 'Add some AmazingFeature'`
4. **推送到分支**: `git push origin feature/AmazingFeature`
5. **创建 Pull Request**

### 贡献类型

- 🐛 **Bug 修复**: 报告或修复问题
- ✨ **新功能**: 添加新功能或改进
- 📚 **文档**: 改进文档和示例
- 🧪 **测试**: 添加或改进测试
- 🔧 **工具**: 改进开发工具和流程

## 📞 联系方式

### 项目维护者
- **姓名**: 刘亮
- **邮箱**: liuliang@gpu22.unidev.ai
- **GitHub**: [@ioyy900205](https://github.com/ioyy900205)

### 交流渠道
- **Issues**: [GitHub Issues](https://github.com/ioyy900205/quantL/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ioyy900205/quantL/discussions)

### 反馈建议
我们非常重视您的反馈和建议！如果您有：
- 🚀 功能建议
- 🐛 问题报告
- 📖 文档改进
- 💡 使用体验分享

请随时通过以下方式联系我们：
- 在 GitHub Issues 中提交问题
- 发送邮件到项目维护者
- 参与 GitHub Discussions 讨论

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE) - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者！

### 开源依赖
- [akshare](https://github.com/akfamily/akshare) - 金融数据接口
- [pandas](https://pandas.pydata.org/) - 数据处理
- [numpy](https://numpy.org/) - 数值计算
- [matplotlib](https://matplotlib.org/) - 数据可视化

---

⭐ 如果这个项目对您有帮助，请给我们一个 Star！ 