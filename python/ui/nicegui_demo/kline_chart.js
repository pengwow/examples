/**
 * K线图表Vue组件 - 包装klinecharts库
 */

export default {
  template: `
    <div ref="chartContainer" :style="{ height: height }"></div>
  `,
  
  props: {
    symbol: {
      type: String,
      default: 'AAPL'
    },
    period: {
      type: String,
      default: 'day'
    },
    theme: {
      type: String,
      default: 'dark'
    },
    height: {
      type: String,
      default: '600px'
    },
    data: {
      type: Array,
      default: () => []
    }
  },
  
  data() {
    return {
      chart: null,
      currentSymbol: this.symbol,
      currentPeriod: this.period,
      currentTheme: this.theme
    };
  },
  
  watch: {
    symbol(newVal) {
      if (newVal !== this.currentSymbol) {
        this.currentSymbol = newVal;
        this.$emit('symbol-change', { symbol: newVal });
        this.requestData();
      }
    },
    
    period(newVal) {
      if (newVal !== this.currentPeriod) {
        this.currentPeriod = newVal;
        this.$emit('period-change', { period: newVal });
        this.requestData();
      }
    },
    
    theme(newVal) {
      if (newVal !== this.currentTheme) {
        this.currentTheme = newVal;
        this.updateTheme();
      }
    },
    
    data: {
      handler(newVal) {
        if (this.chart && newVal.length > 0) {
          this.chart.applyNewData(newVal);
        }
      },
      deep: true
    }
  },
  
  mounted() {
    this.initChart();
    this.requestData();
    
    // 监听窗口大小变化
    window.addEventListener('resize', this.handleResize);
  },
  
  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize);
    if (this.chart) {
      this.chart.dispose();
    }
  },
  
  methods: {
    initChart() {
      // 动态加载klinecharts库
      this.loadKLineCharts().then(() => {
        if (window.klinecharts) {
          this.chart = window.klinecharts.init(this.$refs.chartContainer);
          this.updateTheme();
          
          // 添加默认指标
          this.chart.createIndicator('MA', true, { id: 'candle_pane' });
          this.chart.createIndicator('VOL');
          
          // 订阅图表事件
          this.chart.subscribeAction('onTooltipIconClick', (data) => {
            console.log('Tooltip icon clicked:', data);
          });
        }
      }).catch(error => {
        console.error('Failed to load klinecharts:', error);
      });
    },
    
    loadKLineCharts() {
      return new Promise((resolve, reject) => {
        if (window.klinecharts) {
          resolve();
          return;
        }
        
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/klinecharts/dist/klinecharts.min.js';
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
      });
    },
    
    updateTheme() {
      if (!this.chart) return;
      
      const themeStyles = this.currentTheme === 'dark' ? {
        grid: {
          show: true,
          horizontal: {
            show: true,
            size: 1,
            color: '#292929',
            style: 'dashed'
          },
          vertical: {
            show: true,
            size: 1,
            color: '#292929',
            style: 'dashed'
          }
        },
        candle: {
          type: 'area',
          tooltip: {
            showRule: 'always',
            showType: 'standard',
            labels: ['时间: ', '开: ', '收: ', '低: ', '高: ', '成交量: '],
            text: {
              size: 12,
              color: '#D9D9D9'
            }
          },
          area: {
            lineColor: '#1677FF',
            backgroundColor: [{ offset: 0, color: 'rgba(22, 119, 255, 0.01)' }, { offset: 1, color: 'rgba(22, 119, 255, 0.2)' }]
          },
          bar: {
            upColor: '#26A69A',
            downColor: '#EF5350',
            noChangeColor: '#888888'
          }
        },
        indicator: {
          tooltip: {
            showRule: 'always',
            showType: 'standard',
            labels: ['MA5: ', 'MA10: ', 'MA30: ', 'MA60: '],
            text: {
              size: 12,
              color: '#D9D9D9'
            }
          }
        },
        xAxis: {
          axisLine: {
            show: true,
            color: '#292929'
          },
          tickLine: {
            show: true,
            length: 5,
            color: '#292929'
          },
          tickText: {
            show: true,
            color: '#848E9C',
            size: 12
          }
        },
        yAxis: {
          axisLine: {
            show: true,
            color: '#292929'
          },
          tickLine: {
            show: true,
            length: 5,
            color: '#292929'
          },
          tickText: {
            show: true,
            color: '#848E9C',
            size: 12
          }
        },
        crosshair: {
          show: true,
          horizontal: {
            show: true,
            line: {
              show: true,
              style: 'dashed',
              dashValue: [4, 2],
              size: 1,
              color: '#888888'
            },
            text: {
              show: true,
              color: '#D9D9D9',
              size: 12,
              backgroundColor: '#505050'
            }
          },
          vertical: {
            show: true,
            line: {
              show: true,
              style: 'dashed',
              dashValue: [4, 2],
              size: 1,
              color: '#888888'
            },
            text: {
              show: true,
              color: '#D9D9D9',
              size: 12,
              backgroundColor: '#505050'
            }
          }
        }
      } : {
        grid: {
          show: true,
          horizontal: {
            show: true,
            size: 1,
            color: '#F0F0F0',
            style: 'dashed'
          },
          vertical: {
            show: true,
            size: 1,
            color: '#F0F0F0',
            style: 'dashed'
          }
        },
        candle: {
          type: 'area',
          tooltip: {
            showRule: 'always',
            showType: 'standard',
            labels: ['时间: ', '开: ', '收: ', '低: ', '高: ', '成交量: '],
            text: {
              size: 12,
              color: '#333333'
            }
          },
          area: {
            lineColor: '#1677FF',
            backgroundColor: [{ offset: 0, color: 'rgba(22, 119, 255, 0.01)' }, { offset: 1, color: 'rgba(22, 119, 255, 0.2)' }]
          },
          bar: {
            upColor: '#26A69A',
            downColor: '#EF5350',
            noChangeColor: '#888888'
          }
        },
        indicator: {
          tooltip: {
            showRule: 'always',
            showType: 'standard',
            labels: ['MA5: ', 'MA10: ', 'MA30: ', 'MA60: '],
            text: {
              size: 12,
              color: '#333333'
            }
          }
        },
        xAxis: {
          axisLine: {
            show: true,
            color: '#F0F0F0'
          },
          tickLine: {
            show: true,
            length: 5,
            color: '#F0F0F0'
          },
          tickText: {
            show: true,
            color: '#666666',
            size: 12
          }
        },
        yAxis: {
          axisLine: {
            show: true,
            color: '#F0F0F0'
          },
          tickLine: {
            show: true,
            length: 5,
            color: '#F0F0F0'
          },
          tickText: {
            show: true,
            color: '#666666',
            size: 12
          }
        },
        crosshair: {
          show: true,
          horizontal: {
            show: true,
            line: {
              show: true,
              style: 'dashed',
              dashValue: [4, 2],
              size: 1,
              color: '#888888'
            },
            text: {
              show: true,
              color: '#333333',
              size: 12,
              backgroundColor: '#FFFFFF'
            }
          },
          vertical: {
            show: true,
            line: {
              show: true,
              style: 'dashed',
              dashValue: [4, 2],
              size: 1,
              color: '#888888'
            },
            text: {
              show: true,
              color: '#333333',
              size: 12,
              backgroundColor: '#FFFFFF'
            }
          }
        }
      };
      
      this.chart.setStyles(themeStyles);
    },
    
    requestData() {
      this.$emit('data-request', {
        symbol: this.currentSymbol,
        period: this.currentPeriod
      });
    },
    
    handleResize() {
      if (this.chart) {
        this.chart.resize();
      }
    },
    
    addIndicator(indicator) {
      if (this.chart) {
        this.chart.createIndicator(indicator, true);
      }
    },
    
    removeIndicator(indicator) {
      if (this.chart) {
        this.chart.removeIndicator(indicator);
      }
    },
    
    resize() {
      this.handleResize();
    }
  }
};
