// 1. 从React库中导入useEffect和useRef钩子函数
// useEffect用于处理组件的副作用，如DOM操作、数据获取、订阅等
// useRef用于保存DOM元素的引用
import { useEffect, useRef } from 'react'

// 2. 从KLineChart Pro库中导入必要的类
// KLineChartPro：主类，用于创建K线图表实例
// DefaultDatafeed：默认数据提供类，用于获取K线数据
// 引入样式文件
import { KLineChartPro, DefaultDatafeed } from '@klinecharts/pro'
import '@klinecharts/pro/dist/klinecharts-pro.css'

// 3. 定义并导出一个默认的函数组件
export default () => {
  // 创建一个ref用于保存图表容器元素
  const containerRef = useRef<HTMLDivElement>(null)

  // 4. 使用useEffect钩子函数
  // useEffect接受两个参数：回调函数和依赖数组
  // 空依赖数组[]表示该副作用只在组件挂载时执行一次，卸载时执行清理函数
  useEffect(() => {
    // 确保容器元素存在
    if (!containerRef.current) return

    // 5. 创建KLineChart Pro实例
    // 使用new关键字实例化，传入配置选项
    new KLineChartPro({
      // 指定图表容器元素
      container: containerRef.current,
      // 初始化标的信息
      symbol: {
        exchange: 'XNYS',
        market: 'stocks',
        name: 'Alibaba Group Holding Limited American Depositary Shares, each represents eight Ordinary Shares',
        shortName: 'BABA',
        ticker: 'BABA',
        priceCurrency: 'usd',
        type: 'ADRC',
      },
      // 初始化周期
      period: { multiplier: 15, timespan: 'minute', text: '15m' },
      // 清空副指标配置，只显示主图表
      // 这样就不会出现重复的组件
      subIndicators: [],
      // 使用默认的数据接入
      // 注意：实际使用中需要去 `https://polygon.io/` 申请 API key
      // 这里使用空字符串作为API key，实际运行时会无法获取数据
      datafeed: new DefaultDatafeed(``)
    })

    // 6. 返回清理函数
    // 当组件卸载时，该函数会被调用
    return () => {
      // 注意：KLineChartPro实例不需要手动销毁，组件卸载时会自动清理
    }
  }, [])

  // 7. 组件的返回值，即JSX
  // 返回一个div元素，用于渲染K线图表
  // 设置了div的宽高为800px x 600px
  return (
    <div ref={containerRef} style={{ width: 800, height: 600 }}/>
  )
}
