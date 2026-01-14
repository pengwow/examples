"""
K线图表演示应用 - 基于NiceGUI框架
"""

from nicegui import ui, app
from nicegui.element import Element
import json
from typing import Dict, List, Any
from datetime import datetime, timedelta


class KLineDemo:
    """K线图表演示应用主类"""
    
    def __init__(self):
        self.current_symbol = 'AAPL'
        self.current_period = 'day'
        self.current_theme = 'dark'
        self.chart_data = []
        self.mcp_results = []
        self.chart_instance = None
        
        # 周期选项
        self.periods = [
            {'value': '1min', 'label': '1分'},
            {'value': '5min', 'label': '5分'},
            {'value': '15min', 'label': '15分'},
            {'value': '30min', 'label': '30分'},
            {'value': '1hour', 'label': '1小时'},
            {'value': '4hour', 'label': '4小时'},
            {'value': 'day', 'label': '日线'},
            {'value': 'week', 'label': '周线'},
            {'value': 'month', 'label': '月线'}
        ]
        
        # 主题选项
        self.themes = [
            {'value': 'dark', 'label': '深色'},
            {'value': 'light', 'label': '浅色'}
        ]
        
        # 股票代码选项
        self.symbols = [
            {'value': 'AAPL', 'label': 'AAPL', 'name': 'Apple Inc.'},
            {'value': 'GOOGL', 'label': 'GOOGL', 'name': 'Alphabet Inc.'},
            {'value': 'MSFT', 'label': 'MSFT', 'name': 'Microsoft Corp.'},
            {'value': 'AMZN', 'label': 'AMZN', 'name': 'Amazon.com Inc.'},
            {'value': 'TSLA', 'label': 'TSLA', 'name': 'Tesla Inc.'},
            {'value': 'META', 'label': 'META', 'name': 'Meta Platforms Inc.'}
        ]
        
        # 技术指标
        self.indicators = [
            {'value': 'MA', 'label': 'MA'},
            {'value': 'EMA', 'label': 'EMA'},
            {'value': 'BOLL', 'label': 'BOLL'},
            {'value': 'SAR', 'label': 'SAR'},
            {'value': 'VOL', 'label': 'VOL'},
            {'value': 'MACD', 'label': 'MACD'},
            {'value': 'KDJ', 'label': 'KDJ'},
            {'value': 'RSI', 'label': 'RSI'}
        ]
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        with ui.column().classes('w-full h-screen bg-gray-900'):
            # 顶部工具栏
            self.setup_toolbar()
            
            # 主内容区域
            with ui.row().classes('w-full flex-1 overflow-hidden'):
                # 左侧面板
                self.setup_left_panel()
                
                # 中间图表区域
                self.setup_chart_area()
                
                # 右侧面板
                self.setup_right_panel()
            
            # 底部状态栏
            self.setup_status_bar()
        
        # 所有UI元素创建完成后，初始化图表
        self.inject_kline_chart()
    
    def setup_toolbar(self):
        """设置顶部工具栏"""
        with ui.row().classes('w-full bg-gray-800 px-4 py-2 items-center justify-between border-b border-gray-700'):
            # 左侧：菜单和股票信息
            with ui.row().classes('items-center gap-3'):
                # 菜单按钮
                ui.button(icon='menu').props('flat dense').classes('text-white')
                
                # 分隔线
                ui.separator().props('vertical').classes('h-6 bg-gray-600')
                
                # 股票代码选择
                self.symbol_select = ui.select(
                    options=[s['label'] for s in self.symbols],
                    value='AAPL',
                    on_change=self.on_symbol_change
                ).props('dense dark outlined').classes('w-24')
                
                # 股票名称
                self.symbol_name = ui.label('Apple Inc.').classes('text-white text-sm')
            
            # 中间：周期选择
            with ui.row().classes('items-center gap-1'):
                for period in self.periods:
                    period_label = period['label']
                    period_value = period['value']
                    ui.button(period_label, on_click=lambda p=period_value: self.on_period_click(p)).props(
                        f'flat dense {"bg-blue-600 text-white" if period_value == self.current_period else "text-gray-300"}'
                    ).classes('text-xs px-2 py-1').bind_text_from(self, 'current_period', 
                        lambda p: period_value == p and period_label or period_label)
            
            # 右侧：工具按钮
            with ui.row().classes('items-center gap-2'):
                # 技术指标
                ui.button(icon='show_chart', on_click=self.show_indicator_modal).props('flat dense').classes('text-white')
                
                # 主题切换
                ui.button(icon='brightness_4', on_click=self.toggle_theme).props('flat dense').classes('text-white')
                
                # 设置
                ui.button(icon='settings', on_click=self.show_settings).props('flat dense').classes('text-white')
                
                # 全屏
                ui.button(icon='fullscreen', on_click=self.toggle_fullscreen).props('flat dense').classes('text-white')
    
    def setup_left_panel(self):
        """设置左侧面板"""
        with ui.card().classes('w-64 h-full bg-gray-800 border-r border-gray-700'):
            ui.label('市场概览').classes('text-white font-bold mb-3')
            
            # 市场数据
            with ui.column().classes('w-full gap-2'):
                self.market_price = ui.label('--').classes('text-2xl font-bold text-green-400')
                self.market_change = ui.label('--').classes('text-sm text-green-400')
                self.market_volume = ui.label('成交量: --').classes('text-sm text-gray-400')
            
            ui.separator().classes('bg-gray-700 my-3')
            
            # 快捷操作
            ui.label('快捷操作').classes('text-white font-bold mb-2')
            with ui.column().classes('w-full gap-2'):
                ui.button('刷新数据', on_click=self.refresh_data).props('outline').classes('w-full')
                ui.button('导出数据', on_click=self.export_data).props('outline').classes('w-full')
            
            ui.separator().classes('bg-gray-700 my-3')
            
            # 技术指标
            ui.label('技术指标').classes('text-white font-bold mb-2')
            with ui.column().classes('w-full gap-1'):
                for indicator in self.indicators:
                    indicator_value = indicator['value']
                    ui.button(indicator['label'], on_click=lambda: self.add_indicator(indicator_value)).props(
                        'flat dense'
                    ).classes('w-full text-left text-gray-300 text-sm')
    
    def setup_chart_area(self):
        """设置图表区域"""
        with ui.card().classes('flex-1 h-full bg-gray-900 border-0'):
            # 图表容器
            self.chart_element = ui.element('div').classes('w-full h-full')
    
    def setup_right_panel(self):
        """设置右侧面板"""
        with ui.card().classes('w-72 h-full bg-gray-800 border-l border-gray-700'):
            ui.label('交易详情').classes('text-white font-bold mb-3')
            
            # 交易信息
            with ui.column().classes('w-full gap-2'):
                with ui.row().classes('w-full justify-between'):
                    ui.label('开盘:').classes('text-gray-400 text-sm')
                    self.open_price = ui.label('--').classes('text-white text-sm')
                
                with ui.row().classes('w-full justify-between'):
                    ui.label('最高:').classes('text-gray-400 text-sm')
                    self.high_price = ui.label('--').classes('text-white text-sm')
                
                with ui.row().classes('w-full justify-between'):
                    ui.label('最低:').classes('text-gray-400 text-sm')
                    self.low_price = ui.label('--').classes('text-white text-sm')
                
                with ui.row().classes('w-full justify-between'):
                    ui.label('收盘:').classes('text-gray-400 text-sm')
                    self.close_price = ui.label('--').classes('text-white text-sm')
                
                with ui.row().classes('w-full justify-between'):
                    ui.label('成交量:').classes('text-gray-400 text-sm')
                    self.volume = ui.label('--').classes('text-white text-sm')
            
            ui.separator().classes('bg-gray-700 my-3')
            
    def setup_status_bar(self):
        """设置底部状态栏"""
        with ui.row().classes('w-full bg-gray-800 px-4 py-1 items-center justify-between border-t border-gray-700'):
            ui.label('就绪').classes('text-gray-400 text-xs')
            ui.label(f'数据点: {len(self.chart_data)}').classes('text-gray-400 text-xs')
            ui.label('连接正常').classes('text-green-400 text-xs')
    
    def inject_kline_chart(self):
        """注入K线图表HTML和JavaScript"""
        # 生成假数据
        data = self.generate_mock_data()
        self.chart_data = data
        
        print(f"Generated {len(data)} data points")
        if data:
            print(f"First data point: {data[0]}")
            print(f"Last data point: {data[-1]}")
            # 更新UI显示
            if data[-1]:
                self.market_price.text = f"{data[-1]['close']:.2f}"
                self.open_price.text = f"{data[-1]['open']:.2f}"
                self.high_price.text = f"{data[-1]['high']:.2f}"
                self.low_price.text = f"{data[-1]['low']:.2f}"
                self.close_price.text = f"{data[-1]['close']:.2f}"
                self.volume.text = f"{data[-1]['volume']:,}"
        
        # 转换数据为JavaScript格式
        chart_data_js = json.dumps(data)
        print(f"Chart data JS length: {len(chart_data_js)}")
        
        # 添加klinecharts库到head
        ui.add_head_html('<script src="https://cdn.jsdelivr.net/npm/klinecharts/dist/klinecharts.min.js"></script>')
        
        # 延迟执行初始化，确保DOM和库都已加载
        def init_chart():
            script = f'''
            (function() {{
                console.log('Initializing K-line chart...');
                if (typeof klinecharts === 'undefined') {{
                    console.error('klinecharts library not loaded');
                    return;
                }}
                
                // 创建图表容器
                var container = document.querySelector('[id*="{self.chart_element.id}"]');
                if (!container) {{
                    console.error('Chart container not found');
                    return;
                }}
                
                container.id = 'kline-chart';
                container.style.width = '100%';
                container.style.height = '100%';
                
                // 初始化图表
                var chart = klinecharts.init('kline-chart');
                
                if (!chart) {{
                    console.error('Failed to initialize chart');
                    return;
                }}
                
                console.log('Chart initialized successfully');
                
                // 设置深色主题样式
                chart.setStyles({{
                    grid: {{
                        show: true,
                        size: 1,
                        color: '#2a2a2a'
                    }},
                    candle: {{
                        type: 'candle',
                        bar: {{
                            upColor: '#26A69A',
                            downColor: '#EF5350',
                            noChangeColor: '#888888'
                        }},
                        tooltip: {{
                            showRule: 'always',
                            showType: 'standard',
                            labels: ['时间: ', '开: ', '收: ', '低: ', '高: ', '成交量: '],
                            text: {{
                                size: 12,
                                color: '#D9D9D9',
                                family: 'Helvetica Neue',
                                weight: 'normal'
                            }},
                            rect: {{
                                padding: 8,
                                offsetLeft: 0,
                                offsetTop: 0,
                                offsetRight: 0,
                                offsetBottom: 0,
                                borderSize: 1,
                                borderColor: '#505050',
                                borderRadius: 4,
                                color: 'rgba(22, 33, 51, 0.9)'
                            }}
                        }}
                    }},
                    indicator: {{
                        tooltip: {{
                            showRule: 'always',
                            showType: 'standard',
                            text: {{
                                size: 12,
                                color: '#D9D9D9',
                                family: 'Helvetica Neue',
                                weight: 'normal'
                            }},
                            rect: {{
                                padding: 8,
                                offsetLeft: 0,
                                offsetTop: 0,
                                offsetRight: 0,
                                offsetBottom: 0,
                                borderSize: 1,
                                borderColor: '#505050',
                                borderRadius: 4,
                                color: 'rgba(22, 33, 51, 0.9)'
                            }}
                        }}
                    }},
                    xAxis: {{
                        axisLine: {{
                            show: true,
                            color: '#505050'
                        }},
                        tickText: {{
                            show: true,
                            color: '#D9D9D9',
                            size: 12
                        }},
                        tickLine: {{
                            show: true,
                            length: 5,
                            color: '#505050'
                        }}
                    }},
                    yAxis: {{
                        position: 'right',
                        axisLine: {{
                            show: true,
                            color: '#505050'
                        }},
                        tickText: {{
                            show: true,
                            color: '#D9D9D9',
                            size: 12
                        }},
                        tickLine: {{
                            show: true,
                            length: 5,
                            color: '#505050'
                        }}
                    }},
                    crosshair: {{
                        show: true,
                        horizontal: {{
                            show: true,
                            line: {{
                                show: true,
                                style: 'dashed',
                                dashValue: [4, 2],
                                size: 1,
                                color: '#888888'
                            }},
                            text: {{
                                show: true,
                                size: 12,
                                color: '#D9D9D9',
                                backgroundColor: '#505050',
                                borderRadius: 2,
                                padding: [3, 5],
                                borderSize: 1,
                                borderColor: '#505050'
                            }}
                        }},
                        vertical: {{
                            show: true,
                            line: {{
                                show: true,
                                style: 'dashed',
                                dashValue: [4, 2],
                                size: 1,
                                color: '#888888'
                            }},
                            text: {{
                                show: true,
                                size: 12,
                                color: '#D9D9D9',
                                backgroundColor: '#505050',
                                borderRadius: 2,
                                padding: [3, 5],
                                borderSize: 1,
                                borderColor: '#505050'
                            }}
                        }}
                    }}
                }});
                
                // 创建技术指标
                chart.createIndicator('MA', false, {{ id: 'candle_pane' }});
                chart.createIndicator('VOL');
                chart.createIndicator('MACD');
                
                // 加载数据
                var chartDataList = {chart_data_js};
                console.log('Chart data loaded:', chartDataList);
                console.log('Data length:', chartDataList ? chartDataList.length : 0);
                chart.applyNewData(chartDataList);
                console.log('Chart data applied');
                
                // 暴露全局函数供Python调用
                window.updateKlineData = function(newData) {{
                    console.log('Updating chart data, length:', newData ? newData.length : 0);
                    chart.applyNewData(newData);
                }};
                
                window.addKlineIndicator = function(indicator) {{
                    console.log('Adding indicator:', indicator);
                    chart.createIndicator(indicator);
                }};
                
                window.setKlineTheme = function(theme) {{
                    if (theme === 'light') {{
                        chart.setStyles({{
                            grid: {{
                                show: true,
                                size: 1,
                                color: '#E0E0E0'
                            }},
                            candle: {{
                                bar: {{
                                    upColor: '#26A69A',
                                    downColor: '#EF5350',
                                    noChangeColor: '#888888'
                                }}
                            }},
                            xAxis: {{
                                axisLine: {{
                                    show: true,
                                    color: '#E0E0E0'
                                }},
                                tickText: {{
                                    show: true,
                                    color: '#666666'
                                }},
                                tickLine: {{
                                    show: true,
                                    color: '#E0E0E0'
                                }}
                            }},
                            yAxis: {{
                                axisLine: {{
                                    show: true,
                                    color: '#E0E0E0'
                                }},
                                tickText: {{
                                    show: true,
                                    color: '#666666'
                                }},
                                tickLine: {{
                                    show: true,
                                    color: '#E0E0E0'
                                }}
                            }}
                        }});
                    }} else {{
                        chart.setStyles({{
                            grid: {{
                                show: true,
                                size: 1,
                                color: '#2a2a2a'
                            }},
                            candle: {{
                                bar: {{
                                    upColor: '#26A69A',
                                    downColor: '#EF5350',
                                    noChangeColor: '#888888'
                                }}
                            }},
                            xAxis: {{
                                axisLine: {{
                                    show: true,
                                    color: '#505050'
                                }},
                                tickText: {{
                                    show: true,
                                    color: '#D9D9D9'
                                }},
                                tickLine: {{
                                    show: true,
                                    color: '#505050'
                                }}
                            }},
                            yAxis: {{
                                axisLine: {{
                                    show: true,
                                    color: '#505050'
                                }},
                                tickText: {{
                                    show: true,
                                    color: '#D9D9D9'
                                }},
                                tickLine: {{
                                    show: true,
                                    color: '#505050'
                                }}
                            }}
                        }});
                    }}
                }};
            }})();
            '''
            ui.run_javascript(script)
        
        # 使用定时器延迟初始化，确保DOM和库都已加载
        ui.timer(1.0, init_chart, once=True)
    
    def on_symbol_change(self, e):
        """处理股票代码变更"""
        label = e.value
        symbol = next((s['value'] for s in self.symbols if s['label'] == label), 'AAPL')
        self.current_symbol = symbol
        symbol_name = next((s['name'] for s in self.symbols if s['label'] == label), '')
        self.symbol_name.text = symbol_name
        self.refresh_data()
    
    def on_period_click(self, period):
        """处理周期点击"""
        self.current_period = period
        self.refresh_data()
    
    def toggle_theme(self):
        """切换主题"""
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        ui.run_javascript(f'window.setKlineTheme("{self.current_theme}")')
    
    def toggle_fullscreen(self):
        """切换全屏"""
        ui.run_javascript('''
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen();
            } else {
                document.exitFullscreen();
            }
        ''')
    
    def show_indicator_modal(self):
        """显示技术指标模态框"""
        with ui.dialog() as dialog, ui.card():
            ui.label('技术指标').classes('text-lg font-bold mb-4')
            with ui.row().classes('gap-2 flex-wrap'):
                for indicator in self.indicators:
                    indicator_value = indicator['value']
                    ui.button(indicator['label'], on_click=lambda: self.add_indicator(indicator_value)).props('outline')
            ui.button('关闭', on_click=dialog.close).props('outline')
        dialog.open()
    
    def show_settings(self):
        """显示设置模态框"""
        with ui.dialog() as dialog, ui.card():
            ui.label('设置').classes('text-lg font-bold mb-4')
            ui.label('设置功能开发中...').classes('text-gray-500')
            ui.button('关闭', on_click=dialog.close).props('outline')
        dialog.open()
    
    def refresh_data(self):
        """刷新数据"""
        data = self.generate_mock_data()
        self.chart_data = data
        
        # 更新UI显示
        if data and data[-1]:
            self.market_price.text = f"{data[-1]['close']:.2f}"
            self.open_price.text = f"{data[-1]['open']:.2f}"
            self.high_price.text = f"{data[-1]['high']:.2f}"
            self.low_price.text = f"{data[-1]['low']:.2f}"
            self.close_price.text = f"{data[-1]['close']:.2f}"
            self.volume.text = f"{data[-1]['volume']:,}"
        
        # 使用JavaScript更新图表数据
        chart_data_js = json.dumps(data)
        ui.run_javascript(f'window.updateKlineData({chart_data_js})')
    
    def add_indicator(self, indicator: str):
        """添加技术指标"""
        ui.run_javascript(f'window.addKlineIndicator("{indicator}")')
    
    def export_data(self):
        """导出数据"""
        data_str = json.dumps(self.chart_data, ensure_ascii=False, indent=2)
        self.mcp_output.value = data_str
    
    def generate_mock_data(self) -> List[Dict[str, Any]]:
        """生成模拟K线数据"""
        import random
        
        # 根据周期确定数据点数量
        period_map = {
            '1min': 240,
            '5min': 288,
            '15min': 192,
            '30min': 192,
            '1hour': 240,
            '4hour': 180,
            'day': 365,
            'week': 104,
            'month': 60
        }
        
        count = period_map.get(self.current_period, 365)
        
        # 基础价格
        base_prices = {
            'AAPL': 150.0,
            'GOOGL': 130.0,
            'MSFT': 300.0,
            'AMZN': 140.0,
            'TSLA': 200.0,
            'META': 250.0
        }
        
        base_price = base_prices.get(self.current_symbol, 100.0)
        
        # 生成时间戳
        now = datetime.now()
        timestamp = now
        
        # 根据周期调整时间间隔
        period_minutes = {
            '1min': 1,
            '5min': 5,
            '15min': 15,
            '30min': 30,
            '1hour': 60,
            '4hour': 240,
            'day': 1440,
            'week': 10080,
            'month': 43200
        }
        
        interval = period_minutes.get(self.current_period, 1440)
        
        data = []
        price = base_price
        
        for i in range(count):
            # 生成随机价格变动
            change = random.uniform(-2, 2)
            open_price = price
            close_price = price + change
            high_price = max(open_price, close_price) + random.uniform(0, 1)
            low_price = min(open_price, close_price) - random.uniform(0, 1)
            volume = random.randint(1000000, 10000000)
            
            # 转换为毫秒时间戳
            ts = int(timestamp.timestamp() * 1000)
            
            data.append({
                'timestamp': ts,
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': volume
            })
            
            price = close_price
            timestamp = timestamp - timedelta(minutes=interval)
        
        # 按时间排序（从旧到新）
        data.reverse()
        
        return data
    



# 创建应用实例
@ui.page('/')
def main_page():
    """主页面"""
    KLineDemo()


# 启动应用
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title='K线图表演示',
        port=8080,
        reload=True,
        uvicorn_reload_includes='*.js,*.css,*.html'
    )
