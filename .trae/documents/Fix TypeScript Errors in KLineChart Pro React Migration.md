# 修复KLineChart Pro React迁移中的TypeScript错误

## 错误1：缺少lodash类型声明
- **问题**：找不到'lodash/set'和'lodash/cloneDeep'的声明文件
- **修复方法**：安装@types/lodash作为开发依赖

## 错误2：不兼容的watermark属性类型
- **问题**：ChartProComponentProps扩展了Required<...>，使watermark变为必填，但我们添加了可选标记
- **修复方法**：移除Required工具类型，显式定义具有正确可选/必填状态的属性

## 错误3：无法分配给只读的'current'属性
- **问题**：priceUnitDomRef.current = priceUnitDom失败，因为current是只读的
- **修复方法**：使用正确的类型初始化useRef，并移除不必要的赋值

## 错误4：Button组件中的无效样式类型
- **问题**：ButtonProps.style接受字符串，但React按钮只接受React.CSSProperties
- **修复方法**：将ButtonProps.style类型更改为只接受React.CSSProperties

## 实施步骤：
1. 安装@types/lodash
2. 修复ChartProComponentProps接口定义
3. 修复ChartProComponent中的useRef初始化和使用
4. 修复Button组件的样式类型定义
5. 运行开发服务器测试修复效果