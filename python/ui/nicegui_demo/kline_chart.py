"""
K线图表自定义组件 - 包装klinecharts库
"""

from nicegui.element import Element
from nicegui.events import GenericEventArguments, handle_event
from typing import Optional, Dict, List, Callable, Any


class KLineChart(Element, component='kline_chart.js'):
    """
    K线图表组件，基于klinecharts库
    
    支持功能：
    - K线图表渲染
    - 多周期切换
    - 技术指标显示
    - 主题切换
    - 数据实时更新
    """
    
    def __init__(
        self,
        symbol: str = 'AAPL',
        period: str = 'day',
        theme: str = 'dark',
        height: str = '600px'
    ) -> None:
        super().__init__()
        self._props['symbol'] = symbol
        self._props['period'] = period
        self._props['theme'] = theme
        self._props['height'] = height
        self._props['data'] = []
        
        # 注册事件处理器
        self.on('period-change', self._handle_period_change)
        self.on('symbol-change', self._handle_symbol_change)
        self.on('data-request', self._handle_data_request)
    
    def _handle_period_change(self, e: GenericEventArguments) -> None:
        """处理周期变更事件"""
        if hasattr(self, '_period_callback'):
            self._period_callback(e.args)
    
    def _handle_symbol_change(self, e: GenericEventArguments) -> None:
        """处理股票代码变更事件"""
        if hasattr(self, '_symbol_callback'):
            self._symbol_callback(e.args)
    
    def _handle_data_request(self, e: GenericEventArguments) -> None:
        """处理数据请求事件"""
        if hasattr(self, '_data_callback'):
            self._data_callback(e.args)
    
    def on_period_change(self, callback: Callable[[Dict], None]) -> 'KLineChart':
        """注册周期变更回调"""
        self._period_callback = callback
        return self
    
    def on_symbol_change(self, callback: Callable[[Dict], None]) -> 'KLineChart':
        """注册股票代码变更回调"""
        self._symbol_callback = callback
        return self
    
    def on_data_request(self, callback: Callable[[Dict], None]) -> 'KLineChart':
        """注册数据请求回调"""
        self._data_callback = callback
        return self
    
    def set_data(self, data: List[Dict[str, Any]]) -> None:
        """设置K线数据"""
        self._props['data'] = data
        self.update()
    
    def set_theme(self, theme: str) -> None:
        """设置主题"""
        self._props['theme'] = theme
        self.update()
    
    def set_period(self, period: str) -> None:
        """设置周期"""
        self._props['period'] = period
        self.update()
    
    def set_symbol(self, symbol: str) -> None:
        """设置股票代码"""
        self._props['symbol'] = symbol
        self.update()
    
    def add_indicator(self, indicator: str) -> None:
        """添加技术指标"""
        self.run_method('addIndicator', indicator)
    
    def remove_indicator(self, indicator: str) -> None:
        """移除技术指标"""
        self.run_method('removeIndicator', indicator)
    
    def resize(self) -> None:
        """调整图表大小"""
        self.run_method('resize')
