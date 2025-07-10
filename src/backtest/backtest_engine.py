"""
回测引擎
提供策略回测和性能评估功能
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

from ..strategy.base_strategy import BaseStrategy
from ..utils.config import config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, initial_capital: float = 1000000):
        """
        初始化回测引擎
        
        Args:
            initial_capital: 初始资金
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = {}  # 当前持仓
        self.trades = []     # 交易记录
        self.portfolio_values = []  # 组合价值历史
        self.daily_returns = []     # 日收益率历史
        
        # 获取回测参数
        backtest_params = config.get_backtest_params()
        self.commission = backtest_params.get('commission', 0.0003)
        self.slippage = backtest_params.get('slippage', 0.0001)
        self.max_position_size = backtest_params.get('max_position_size', 0.2)
        self.stop_loss = backtest_params.get('stop_loss', 0.1)
        
        logger.info(f"回测引擎初始化: 初始资金={initial_capital}")
    
    def run_backtest(
        self,
        strategy: BaseStrategy,
        data: Dict[str, pd.DataFrame],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        运行回测
        
        Args:
            strategy: 策略对象
            data: 股票数据字典 {symbol: DataFrame}
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            回测结果字典
        """
        logger.info(f"开始回测策略: {strategy.name}")
        
        # 重置状态
        self.reset()
        strategy.reset()
        
        # 处理日期范围
        if not start_date:
            start_date = config.get("backtest.start_date", "2020-01-01")
        if not end_date:
            end_date = config.get("backtest.end_date", "2023-12-31")
        
        # 获取所有数据的日期范围
        all_dates = self._get_common_dates(data, start_date, end_date)
        
        # 按日期遍历
        for date in all_dates:
            self._process_date(strategy, data, date)
        
        # 计算回测结果
        results = self._calculate_results(strategy, all_dates)
        
        logger.info(f"回测完成: 最终资金={self.current_capital:.2f}")
        
        return results
    
    def _get_common_dates(
        self,
        data: Dict[str, pd.DataFrame],
        start_date: str,
        end_date: str
    ) -> List[datetime]:
        """获取所有数据的公共日期"""
        common_dates = None
        
        for symbol, df in data.items():
            if df.empty:
                continue
            
            # 过滤日期范围
            mask = (df.index >= start_date) & (df.index <= end_date)
            df_filtered = df[mask]
            
            if common_dates is None:
                common_dates = set(df_filtered.index)
            else:
                common_dates = common_dates.intersection(set(df_filtered.index))
        
        return sorted(list(common_dates)) if common_dates else []
    
    def _process_date(
        self,
        strategy: BaseStrategy,
        data: Dict[str, pd.DataFrame],
        date: datetime
    ):
        """处理单个交易日"""
        current_prices = {}
        
        # 获取当日价格
        for symbol, df in data.items():
            if date in df.index:
                current_prices[symbol] = df.loc[date, 'close']
        
        # 生成信号
        signals = {}
        for symbol, df in data.items():
            if date in df.index:
                # 获取历史数据（用于计算技术指标）
                hist_data = df[df.index <= date]
                if len(hist_data) > 20:  # 确保有足够的历史数据
                    signal_df = strategy.generate_signals(hist_data)
                    if date in signal_df.index:
                        signals[symbol] = signal_df.loc[date, 'signal']
        
        # 执行交易
        self._execute_trades(strategy, signals, current_prices, date)
        
        # 更新组合价值
        self._update_portfolio_value(current_prices, date)
    
    def _execute_trades(
        self,
        strategy: BaseStrategy,
        signals: Dict[str, float],
        prices: Dict[str, float],
        date: datetime
    ):
        """执行交易"""
        for symbol, signal in signals.items():
            if symbol not in prices:
                continue
            
            current_price = prices[symbol]
            
            # 计算目标仓位
            target_quantity = strategy.calculate_position_size(
                signal, current_price, self.current_capital
            )
            
            # 获取当前持仓
            current_quantity = self.positions.get(symbol, 0)
            
            # 计算需要交易的股数
            trade_quantity = target_quantity - current_quantity
            
            if trade_quantity != 0:
                # 计算交易成本
                trade_value = abs(trade_quantity) * current_price
                commission_cost = trade_value * self.commission
                slippage_cost = trade_value * self.slippage
                total_cost = commission_cost + slippage_cost
                
                # 检查资金是否足够
                if trade_quantity > 0:  # 买入
                    required_capital = trade_value + total_cost
                    if required_capital <= self.current_capital:
                        self._execute_buy(symbol, trade_quantity, current_price, total_cost, date)
                else:  # 卖出
                    self._execute_sell(symbol, abs(trade_quantity), current_price, total_cost, date)
    
    def _execute_buy(self, symbol: str, quantity: int, price: float, cost: float, date: datetime):
        """执行买入"""
        trade_value = quantity * price
        self.current_capital -= (trade_value + cost)
        
        if symbol not in self.positions:
            self.positions[symbol] = 0
        self.positions[symbol] += quantity
        
        # 记录交易
        self.trades.append({
            'date': date,
            'symbol': symbol,
            'action': 'BUY',
            'quantity': quantity,
            'price': price,
            'value': trade_value,
            'cost': cost,
            'capital': self.current_capital
        })
        
        logger.debug(f"买入: {symbol}, 数量: {quantity}, 价格: {price:.2f}")
    
    def _execute_sell(self, symbol: str, quantity: int, price: float, cost: float, date: datetime):
        """执行卖出"""
        trade_value = quantity * price
        self.current_capital += (trade_value - cost)
        
        if symbol in self.positions:
            self.positions[symbol] -= quantity
            if self.positions[symbol] == 0:
                del self.positions[symbol]
        
        # 记录交易
        self.trades.append({
            'date': date,
            'symbol': symbol,
            'action': 'SELL',
            'quantity': quantity,
            'price': price,
            'value': trade_value,
            'cost': cost,
            'capital': self.current_capital
        })
        
        logger.debug(f"卖出: {symbol}, 数量: {quantity}, 价格: {price:.2f}")
    
    def _update_portfolio_value(self, prices: Dict[str, float], date: datetime):
        """更新组合价值"""
        # 计算持仓市值
        position_value = 0
        for symbol, quantity in self.positions.items():
            if symbol in prices:
                position_value += quantity * prices[symbol]
        
        # 总价值 = 现金 + 持仓市值
        total_value = self.current_capital + position_value
        
        self.portfolio_values.append({
            'date': date,
            'cash': self.current_capital,
            'position_value': position_value,
            'total_value': total_value
        })
        
        # 计算日收益率
        if len(self.portfolio_values) > 1:
            prev_value = self.portfolio_values[-2]['total_value']
            daily_return = (total_value - prev_value) / prev_value
            self.daily_returns.append(daily_return)
        else:
            self.daily_returns.append(0.0)
    
    def _calculate_results(self, strategy: BaseStrategy, dates: List[datetime]) -> Dict[str, Any]:
        """计算回测结果"""
        if not self.portfolio_values:
            return {}
        
        # 转换为DataFrame
        portfolio_df = pd.DataFrame(self.portfolio_values)
        portfolio_df.set_index('date', inplace=True)
        
        # 计算收益率
        total_return = (portfolio_df['total_value'].iloc[-1] - self.initial_capital) / self.initial_capital
        
        # 计算年化收益率
        days = (dates[-1] - dates[0]).days
        annual_return = (1 + total_return) ** (365 / days) - 1 if days > 0 else 0
        
        # 计算夏普比率
        daily_returns_series = pd.Series(self.daily_returns[1:])  # 跳过第一天
        sharpe_ratio = daily_returns_series.mean() / daily_returns_series.std() * np.sqrt(252) if daily_returns_series.std() > 0 else 0
        
        # 计算最大回撤
        cumulative_returns = (1 + daily_returns_series).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # 交易统计
        trades_df = pd.DataFrame(self.trades)
        total_trades = len(self.trades)
        winning_trades = len(trades_df[trades_df['action'] == 'SELL']) if not trades_df.empty else 0
        
        results = {
            'strategy_name': strategy.name,
            'initial_capital': self.initial_capital,
            'final_capital': portfolio_df['total_value'].iloc[-1],
            'total_return': total_return,
            'annual_return': annual_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'win_rate': winning_trades / total_trades if total_trades > 0 else 0,
            'portfolio_history': portfolio_df,
            'trades': self.trades,
            'daily_returns': self.daily_returns
        }
        
        return results
    
    def reset(self):
        """重置回测引擎"""
        self.current_capital = self.initial_capital
        self.positions = {}
        self.trades = []
        self.portfolio_values = []
        self.daily_returns = []
        logger.info("回测引擎已重置")
    
    def plot_results(self, results: Dict[str, Any], save_path: Optional[str] = None):
        """绘制回测结果"""
        if not results or 'portfolio_history' not in results:
            logger.warning("没有回测结果可绘制")
            return
        
        portfolio_df = results['portfolio_history']
        
        # 创建子图
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 1. 组合价值曲线
        axes[0, 0].plot(portfolio_df.index, portfolio_df['total_value'], label='组合价值')
        axes[0, 0].plot(portfolio_df.index, portfolio_df['cash'], label='现金', alpha=0.7)
        axes[0, 0].set_title('组合价值变化')
        axes[0, 0].set_ylabel('价值 (元)')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # 2. 收益率曲线
        cumulative_returns = (1 + pd.Series(results['daily_returns'])).cumprod()
        axes[0, 1].plot(portfolio_df.index[1:], cumulative_returns, label='累计收益率')
        axes[0, 1].set_title('累计收益率')
        axes[0, 1].set_ylabel('收益率')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        
        # 3. 回撤曲线
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        axes[1, 0].fill_between(portfolio_df.index[1:], drawdown, 0, alpha=0.3, color='red')
        axes[1, 0].plot(portfolio_df.index[1:], drawdown, color='red')
        axes[1, 0].set_title('回撤曲线')
        axes[1, 0].set_ylabel('回撤')
        axes[1, 0].grid(True)
        
        # 4. 日收益率分布
        daily_returns_series = pd.Series(results['daily_returns'][1:])
        axes[1, 1].hist(daily_returns_series, bins=50, alpha=0.7, edgecolor='black')
        axes[1, 1].set_title('日收益率分布')
        axes[1, 1].set_xlabel('日收益率')
        axes[1, 1].set_ylabel('频次')
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"回测结果图表已保存: {save_path}")
        
        plt.show()


# 全局回测引擎实例
backtest_engine = BacktestEngine() 