# HistoryGogo iOS客户端

## 项目概述

基于SwiftUI和MVVM架构的历史学习App iOS客户端，展示中国历史朝代、皇帝、事件和人物信息。

## 技术栈

- **语言**: Swift 5.0+
- **UI框架**: SwiftUI
- **架构**: MVVM (Model-View-ViewModel)
- **设计原则**: SOLID
- **最低系统**: iOS 15.0+
- **网络**: URLSession + async/await
- **数据解析**: Codable

## 项目结构

```
ios-app/HistoryGogo/
├── Models/                    # 数据模型层
│   ├── Dynasty.swift         # 朝代模型
│   ├── Emperor.swift         # 皇帝模型
│   ├── Event.swift           # 事件模型
│   ├── Person.swift          # 人物模型
│   ├── Timeline.swift        # 时间轴模型
│   └── APIResponse.swift     # API响应模型
│
├── ViewModels/               # 视图模型层 (MVVM)
│   ├── TimelineViewModel.swift      # 时间轴ViewModel
│   ├── EmperorViewModel.swift       # 皇帝ViewModel
│   ├── EventViewModel.swift         # 事件ViewModel
│   └── PersonViewModel.swift        # 人物ViewModel
│
├── Views/                    # 视图层
│   ├── TimelineView.swift           # 时间轴视图
│   ├── EmperorListView.swift        # 皇帝列表视图
│   ├── Components/                   # 通用组件
│   │   └── LoadingView.swift        # 加载状态视图
│   └── HistoryGogoApp.swift         # App入口
│
├── Services/                 # 服务层
│   ├── NetworkManager.swift  # 网络管理器
│   └── APIService.swift      # API服务封装
│
├── Utils/                    # 工具类
│   ├── Extensions.swift      # 扩展方法
│   ├── Constants.swift       # 常量定义
│   └── Theme.swift           # 主题样式系统
│
└── Resources/               # 资源文件
```

## MVVM架构说明

### Model（数据模型）
- 定义数据结构，遵循`Codable`协议
- 包含计算属性和辅助方法
- 提供示例数据用于预览和测试

### View（视图）
- 使用SwiftUI声明式语法
- 只负责UI展示，不包含业务逻辑
- 通过`@StateObject`或`@ObservedObject`观察ViewModel

### ViewModel（视图模型）
- 继承`ObservableObject`
- 使用`@Published`属性发布状态变化
- 处理业务逻辑和数据转换
- 调用Service层获取数据
- 管理加载状态和错误处理

## SOLID原则应用

### 单一职责原则 (SRP)
- 每个类只负责一个功能
- Model只包含数据，ViewModel只处理逻辑，View只负责展示

### 开闭原则 (OCP)
- 使用协议（Protocol）定义接口
- 便于扩展新功能而不修改现有代码

### 里氏替换原则 (LSP)
- Service遵循协议，可以互相替换
- 提供MockAPIService用于测试

### 接口隔离原则 (ISP)
- 定义细粒度的协议
- 避免臃肿的接口定义

### 依赖倒置原则 (DIP)
- ViewModel依赖Service协议而非具体实现
- 通过依赖注入提高可测试性

## 核心功能

### 1. 时间轴视图
- 垂直滚动时间线
- 显示皇帝在位时间段
- 标注历史事件
- 支持下拉刷新

### 2. 皇帝列表
- 按朝代顺序展示皇帝
- 分页加载支持
- 详情页展示完整信息

### 3. 事件列表
- 按时间排序展示历史事件
- 支持按类型筛选
- 显示事件详情

### 4. 人物列表
- 展示历史人物信息
- 按类型分类
- 显示人物作品和成就

## API集成

### 网络层设计

```swift
// 网络管理器（单例）
NetworkManager.shared

// API服务（单例）
APIService.shared

// 使用示例
let emperors = try await APIService.shared.fetchEmperors(dynastyId: "ming")
```

### 错误处理

```swift
enum APIError: Error {
    case invalidURL
    case networkError(Error)
    case decodingError(Error)
    case serverError(Int, String)
    case noData
    case unknown
}
```

## 数据模型

### 朝代 (Dynasty)
```swift
struct Dynasty {
    let id: String
    let name: String
    let startYear: Int
    let endYear: Int
    // ...
}
```

### 皇帝 (Emperor)
```swift
struct Emperor {
    let id: String
    let name: String
    let templeName: String?
    let reignStart: Date
    // ...
}
```

### 事件 (Event)
```swift
struct Event {
    let id: String
    let title: String
    let eventType: String
    let startDate: Date
    // ...
}
```

### 人物 (Person)
```swift
struct Person {
    let id: String
    let name: String
    let personType: String
    let biography: String?
    // ...
}
```

## 使用说明

### 前置条件

1. **启动API服务**
```bash
cd /Users/master/Documents/AI-Project/HistoryGogo/server
source venv/bin/activate
python main.py
```

2. **配置API地址**

在`Constants.swift`中配置API基础URL：
```swift
enum API {
    static let developmentBaseURL = "http://localhost:8000/api/v1"
}
```

### 在Xcode中运行

1. 使用Xcode打开项目：
   - 创建新的iOS App项目
   - 将代码文件拖入项目
   - 设置部署目标为iOS 15.0+

2. 选择模拟器或真机设备

3. 点击运行按钮 (Cmd + R)

### Mock模式测试

不依赖API服务器，使用Mock数据：

```swift
// 在ViewModel初始化时传入MockAPIService
let viewModel = TimelineViewModel(apiService: MockAPIService())
```

## 设计风格

### 历史主题配色

项目采用统一的主题系统（`Theme.swift`），提供完整的设计规范：

- **主色调**: 故宫红 (#8B0000) - `AppTheme.Colors.palaceRed`
- **辅助色**: 青铜绿 (#4A7C59) - `AppTheme.Colors.bronzeGreen`
- **背景色**: 宣纸白 (#F5F5DC) - `AppTheme.Colors.paperWhite`
- **文字色**: 墨黑 (#2C2C2C) - `AppTheme.Colors.inkBlack`
- **强调色**: 金黄 (#DAA520) - `AppTheme.Colors.gold`

#### 扩展色系
- 帝王黄 - `AppTheme.Colors.imperialYellow`
- 翡翠绿 - `AppTheme.Colors.jadeGreen`
- 朱砂红 - `AppTheme.Colors.cinnabarRed`
- 青金石蓝 - `AppTheme.Colors.sapphireBlue`

### 主题系统使用

```swift
// 使用主题颜色
Text("标题")
    .foregroundColor(AppTheme.Colors.palaceRed)
    .font(AppTheme.Fonts.title1)

// 使用预定义样式
Text("按钮")
    .primaryButtonStyle()  // 主按钮样式

// 朝代专属配色
Rectangle()
    .fill(AppTheme.DynastyColors.gradient(for: "明朝"))

// 事件类型配色
Circle()
    .fill(AppTheme.EventColors.color(for: "军事"))
```

### 设计规范

**间距系统**：
- `AppTheme.Spacing.sm/md/lg/xl` - 统一的间距规范
- `AppTheme.Spacing.cardPadding` - 卡片内边距

**圆角系统**：
- `AppTheme.CornerRadius.button/card/sheet` - 组件圆角

**字体系统**：
- `AppTheme.Fonts.dynastyTitle` - 朝代标题字体
- `AppTheme.Fonts.emperorName` - 皇帝姓名字体
- `AppTheme.Fonts.yearNumber` - 年份数字字体

**阴影系统**：
- `AppTheme.Shadows.small/medium/large` - 三级阴影

### UI组件

- 使用SF Symbols图标系统
- 卡片式布局（`.cardStyle()`修饰符）
- 统一的圆角和阴影效果
- 流畅的动画过渡（`AppTheme.Animations`）
- 暗黑模式适配支持

## 性能优化

### 列表优化
- 使用`LazyVStack`懒加载
- 分页加载数据
- 图片异步加载

### 内存管理
- 合理使用`@StateObject`和`@ObservedObject`
- 及时释放不再使用的资源
- 图片缓存管理

### 网络优化
- 并发请求优化
- 请求缓存策略
- 离线数据支持

## 测试

### 单元测试
```swift
// 测试ViewModel逻辑
func testFetchEmperors() async throws {
    let mockService = MockAPIService()
    let viewModel = EmperorListViewModel(apiService: mockService)
    await viewModel.loadEmperors()
    XCTAssertFalse(viewModel.emperors.isEmpty)
}
```

### UI测试
- 使用SwiftUI Preview进行快速迭代
- 每个View都提供Preview

## 扩展计划

### 短期计划
- 完善所有详情页面
- 添加搜索功能
- 实现收藏功能
- 添加夜间模式

### 长期计划
- 支持多朝代切换
- 添加AR历史场景
- 社交分享功能
- 离线阅读支持

## 注意事项

1. **网络配置**: 确保模拟器或设备可以访问localhost:8000
2. **API兼容性**: API响应格式需与Model定义匹配
3. **错误处理**: 所有网络请求都应处理错误情况
4. **代码风格**: 遵循Swift官方编码规范
5. **性能测试**: 在真机上测试滚动性能

## 开发团队

- **架构设计**: MVVM + SOLID原则
- **UI/UX**: SwiftUI + 历史主题设计
- **网络层**: URLSession + async/await
- **数据层**: Codable + 依赖注入

## 许可证

本项目仅用于学习和非商业用途。
