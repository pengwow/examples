// 1. 从React库中导入useEffect钩子函数
// useEffect用于处理组件的副作用，如DOM操作、数据获取、订阅等
import { useEffect } from 'react' 

// 2. 从klinecharts库中导入init和dispose函数
// init：用于初始化K线图表
// dispose：用于销毁K线图表，释放资源
import { init, dispose } from 'klinecharts' 

// 3. 定义并导出一个默认的函数组件
// 这是React函数组件的基本形式
export default () => { 

  // 4. 使用useEffect钩子函数
  // useEffect接受两个参数：回调函数和依赖数组
  // 空依赖数组[]表示该副作用只在组件挂载时执行一次，卸载时执行清理函数
  useEffect(() => { 

    // 5. 初始化K线图表
    // 参数'chart'是DOM元素的id，图表将渲染到该元素中
    // init函数返回一个图表实例对象
    const chart = init('chart') 

    // 6. 空值检查
    // 确保chart实例存在，防止后续操作出错
    if (chart) {
      
      // 7. 设置交易对/股票代码
      // ticker属性用于标识当前显示的交易对或股票
      chart.setSymbol({ ticker: 'TestSymbol' }) 

      // 8. 设置时间周期
      // span: 1 表示1个单位
      // type: 'day' 表示日K线
      // 其他可选值如：'minute'（分钟）、'week'（周）、'month'（月）等
      chart.setPeriod({ span: 1, type: 'day' }) 

      // 9. 设置数据加载器
      // 用于指定如何获取K线数据
      chart.setDataLoader({ 
        
        // 10. 定义getBars函数，用于获取K线数据
        // 该函数接收一个包含callback回调函数的对象参数
        getBars: ({ callback}) => { 
          
          // 11. 调用callback函数，传入K线数据数组
          // 每个数组元素代表一根K线，包含以下属性：
          // - timestamp: 时间戳（毫秒）
          // - open: 开盘价
          // - high: 最高价
          // - low: 最低价
          // - close: 收盘价
          // - volume: 成交量
          callback([ 
            // 12-22. 以下是10根K线的测试数据
            { timestamp: 1517846400000, open: 7424.6, high: 7511.3, low: 6032.3, close: 7310.1, volume: 224461 }, 
            { timestamp: 1517932800000, open: 7310.1, high: 8499.9, low: 6810, close: 8165.4, volume: 148807 }, 
            { timestamp: 1518019200000, open: 8166.7, high: 8700.8, low: 7400, close: 8245.1, volume: 24467 }, 
            { timestamp: 1518105600000, open: 8244, high: 8494, low: 7760, close: 8364, volume: 29834 }, 
            { timestamp: 1518192000000, open: 8363.6, high: 9036.7, low: 8269.8, close: 8311.9, volume: 28203 }, 
            { timestamp: 1518278400000, open: 8301, high: 8569.4, low: 7820.2, close: 8426, volume: 59854 }, 
            { timestamp: 1518364800000, open: 8426, high: 8838, low: 8024, close: 8640, volume: 54457 }, 
            { timestamp: 1518451200000, open: 8640, high: 8976.8, low: 8360, close: 8500, volume: 51156 }, 
            { timestamp: 1518537600000, open: 8504.9, high: 9307.3, low: 8474.3, close: 9307.3, volume: 49118 }, 
            { timestamp: 1518624000000, open: 9307.3, high: 9897, low: 9182.2, close: 9774, volume: 48092 } 
          ]) 
        } 
      }) 
    }

    // 13. 返回清理函数
    // 当组件卸载时，该函数会被调用
    return () => { 
      // 14. 销毁K线图表，释放资源
      // 防止内存泄漏
      dispose('chart') 
    } 
  }, []) // 15. 空依赖数组，表示该useEffect只在组件挂载和卸载时执行

  // 16. 组件的返回值，即JSX
  // 返回一个id为'chart'的div元素，用于渲染K线图表
  // 设置了div的宽高为600px
  return <div id="chart" style={{ width: 600, height: 600 }}/> 
}