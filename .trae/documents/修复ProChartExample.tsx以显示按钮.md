## 全面转换KLineChart Pro为React组件

### 问题分析
从错误信息可以看出，当前的转换方法存在问题：
1. 保留了Solid.js特有的组件：`<For>`, `<Show>`等
2. 使用了Solid.js特有的API：`createSignal`, `createEffect`, `onMount`等
3. 组件类型定义与React不兼容
4. JSX语法差异：Solid.js使用`class`，React使用`className`
5. 组件返回类型不兼容

### 解决方案
制定全面的转换计划，逐个转换每个组件：

#### 1. 转换基础组件库
逐个转换`component/`目录下的组件：
- `button/index.tsx`：将Solid.js组件转换为React组件
- `checkbox/index.tsx`：将Solid.js组件转换为React组件
- `empty/index.tsx`：将Solid.js组件转换为React组件
- `input/index.tsx`：将Solid.js组件转换为React组件
- `list/index.tsx`：将Solid.js组件转换为React组件
- `loading/index.tsx`：将Solid.js组件转换为React组件
- `modal/index.tsx`：将Solid.js组件转换为React组件
- `select/index.tsx`：将Solid.js组件转换为React组件
- `switch/index.tsx`：将Solid.js组件转换为React组件

#### 2. 转换Widget组件
逐个转换`widget/`目录下的功能组件：
- `drawing-bar/index.tsx`：将Solid.js组件转换为React组件
- `indicator-modal/index.tsx`：将Solid.js组件转换为React组件
- `indicator-setting-modal/index.tsx`：将Solid.js组件转换为React组件
- `period-bar/index.tsx`：将Solid.js组件转换为React组件
- `screenshot-modal/index.tsx`：将Solid.js组件转换为React组件
- `setting-modal/index.tsx`：将Solid.js组件转换为React组件
- `symbol-search-modal/index.tsx`：将Solid.js组件转换为React组件
- `timezone-modal/index.tsx`：将Solid.js组件转换为React组件

#### 3. 转换核心图表组件
- 继续完善`ChartProComponent.tsx`的转换
- 确保所有Solid.js API都转换为React API

#### 4. 转换工具函数和类型定义
- 转换`i18n/index.ts`：将Solid.js的i18n转换为React可用的i18n
- 转换`types.ts`：确保类型定义与React兼容

#### 5. 更新入口文件
- 更新`index.ts`：确保导出的是React组件
- 更新样式导入：确保样式能在React中正常加载

#### 6. 测试和调试
- 运行项目，确保所有组件都能正常渲染
- 修复可能出现的样式和功能问题

### 转换策略
1. **替换Solid.js API为React API**：
   - `createSignal` → `useState`
   - `createEffect` → `useEffect`
   - `onMount` → `useEffect(() => {}, [])`
   - `onCleanup` → `useEffect`清理函数
   - `<Show when={condition}>` → `{condition && <Component />}`
   - `<For each={list}>` → `list.map(item => <Component key={item.id} {...item} />)`
   - `createResource` → React的数据获取方案

2. **修复JSX语法**：
   - `class` → `className`
   - 修复组件返回类型
   - 修复组件类型定义

3. **确保类型安全**：
   - 使用React的组件类型定义
   - 确保props和state的类型正确

### 预期效果
转换完成后，KLineChart Pro将完全使用React实现，所有组件都能正常渲染和工作，不再依赖Solid.js。