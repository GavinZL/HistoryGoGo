//
//  Theme.swift
//  HistoryGogo
//
//  历史主题样式系统
//  定义统一的颜色、字体、间距、圆角等设计规范
//

import SwiftUI

// MARK: - 主题颜色系统

/// 应用主题颜色配置
struct AppTheme {
    
    // MARK: - 历史主题配色
    
    /// 颜色定义
    struct Colors {
        // 主色调
        static let palaceRed = Color(red: 139/255, green: 0, blue: 0)           // 故宫红 #8B0000
        static let bronzeGreen = Color(red: 74/255, green: 124/255, blue: 89/255) // 青铜绿 #4A7C59
        static let gold = Color(red: 218/255, green: 165/255, blue: 32/255)     // 金黄 #DAA520
        static let paperWhite = Color(red: 245/255, green: 245/255, blue: 220/255) // 宣纸白 #F5F5DC
        static let inkBlack = Color(red: 44/255, green: 44/255, blue: 44/255)   // 墨黑 #2C2C2C
        
        // 扩展色系
        static let imperialYellow = Color(red: 255/255, green: 213/255, blue: 0) // 帝王黄
        static let jadeGreen = Color(red: 0, green: 168/255, blue: 107/255)     // 翡翠绿
        static let cinnabarRed = Color(red: 227/255, green: 38/255, blue: 54/255) // 朱砂红
        static let sapphireBlue = Color(red: 15/255, green: 82/255, blue: 186/255) // 青金石蓝
        
        // 功能色
        static let success = Color.green
        static let warning = Color.orange
        static let error = Color.red
        static let info = Color.blue
        
        // 背景色系
        static let primaryBackground = Color(UIColor.systemBackground)
        static let secondaryBackground = Color(UIColor.secondarySystemBackground)
        static let tertiaryBackground = Color(UIColor.tertiarySystemBackground)
        
        // 文字色系
        static let primaryText = inkBlack
        static let secondaryText = Color(UIColor.secondaryLabel)
        static let tertiaryText = Color(UIColor.tertiaryLabel)
        static let placeholderText = Color(UIColor.placeholderText)
        
        // 分隔线
        static let separator = Color(UIColor.separator)
        static let opaqueSeparator = Color(UIColor.opaqueSeparator)
        
        // 卡片颜色
        static let cardBackground = Color.white
        static let cardShadow = Color.black.opacity(0.1)
    }
    
    // MARK: - 朝代主题色
    
    /// 朝代专属配色方案
    struct DynastyColors {
        static func gradient(for dynasty: String) -> LinearGradient {
            let colors = colorPair(for: dynasty)
            return LinearGradient(
                colors: colors,
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        }
        
        static func colorPair(for dynasty: String) -> [Color] {
            switch dynasty {
            case "秦朝":
                return [Color.black, Color.gray]
            case "汉朝":
                return [Colors.cinnabarRed, Colors.cinnabarRed.opacity(0.7)]
            case "唐朝":
                return [Colors.imperialYellow, Colors.gold]
            case "宋朝":
                return [Colors.jadeGreen, Colors.bronzeGreen]
            case "元朝":
                return [Colors.sapphireBlue, Color.blue]
            case "明朝":
                return [Colors.palaceRed, Colors.palaceRed.opacity(0.8)]
            case "清朝":
                return [Colors.gold, Colors.imperialYellow]
            default:
                return [Color.gray, Color.gray.opacity(0.7)]
            }
        }
        
        static func primaryColor(for dynasty: String) -> Color {
            colorPair(for: dynasty).first ?? Color.gray
        }
    }
    
    // MARK: - 事件类型配色
    
    /// 事件类型颜色映射
    struct EventColors {
        static func color(for type: String) -> Color {
            switch type {
            case "政治":
                return Colors.sapphireBlue
            case "军事":
                return Colors.cinnabarRed
            case "文化":
                return Color.purple
            case "经济":
                return Colors.gold
            case "外交":
                return Colors.jadeGreen
            case "科技":
                return Color.cyan
            case "宗教":
                return Color.orange
            default:
                return Color.gray
            }
        }
        
        static func gradient(for type: String) -> LinearGradient {
            let baseColor = color(for: type)
            return LinearGradient(
                colors: [baseColor, baseColor.opacity(0.7)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        }
    }
    
    // MARK: - 人物类型配色
    
    /// 人物类型颜色映射
    struct PersonColors {
        static func color(for type: String) -> Color {
            switch type {
            case "皇帝":
                return Colors.imperialYellow
            case "文臣":
                return Colors.bronzeGreen
            case "武将":
                return Colors.cinnabarRed
            case "文人":
                return Color.purple
            case "思想家":
                return Colors.sapphireBlue
            case "科学家":
                return Color.cyan
            case "艺术家":
                return Color.pink
            default:
                return Color.gray
            }
        }
        
        static func icon(for type: String) -> String {
            switch type {
            case "皇帝":
                return "crown.fill"
            case "文臣", "文人":
                return "book.fill"
            case "武将":
                return "shield.fill"
            case "思想家":
                return "brain.head.profile"
            case "科学家":
                return "flask.fill"
            case "艺术家":
                return "paintbrush.fill"
            default:
                return "person.fill"
            }
        }
    }
    
    // MARK: - 字体系统
    
    /// 字体配置
    struct Fonts {
        // 标题字体
        static let largeTitle = Font.largeTitle.weight(.bold)
        static let title1 = Font.title.weight(.bold)
        static let title2 = Font.title2.weight(.semibold)
        static let title3 = Font.title3.weight(.semibold)
        
        // 正文字体
        static let headline = Font.headline
        static let body = Font.body
        static let callout = Font.callout
        static let subheadline = Font.subheadline
        static let footnote = Font.footnote
        static let caption = Font.caption
        static let caption2 = Font.caption2
        
        // 自定义字体
        static let dynastyTitle = Font.system(size: 28, weight: .heavy, design: .serif)
        static let emperorName = Font.system(size: 24, weight: .bold, design: .default)
        static let eventTitle = Font.system(size: 20, weight: .semibold, design: .default)
        static let personName = Font.system(size: 22, weight: .bold, design: .default)
        
        // 数字字体（用于年份等）
        static let yearNumber = Font.system(size: 18, weight: .medium, design: .monospaced)
        static let statisticNumber = Font.system(size: 32, weight: .bold, design: .rounded)
    }
    
    // MARK: - 间距系统
    
    /// 间距配置
    struct Spacing {
        static let xxs: CGFloat = 2
        static let xs: CGFloat = 4
        static let sm: CGFloat = 8
        static let md: CGFloat = 12
        static let lg: CGFloat = 16
        static let xl: CGFloat = 20
        static let xxl: CGFloat = 24
        static let xxxl: CGFloat = 32
        
        // 卡片间距
        static let cardPadding: CGFloat = 16
        static let cardSpacing: CGFloat = 12
        
        // 列表间距
        static let listItemSpacing: CGFloat = 8
        static let listSectionSpacing: CGFloat = 16
        
        // 页面边距
        static let horizontalPadding: CGFloat = 16
        static let verticalPadding: CGFloat = 12
    }
    
    // MARK: - 圆角系统
    
    /// 圆角配置
    struct CornerRadius {
        static let xs: CGFloat = 4
        static let sm: CGFloat = 8
        static let md: CGFloat = 12
        static let lg: CGFloat = 16
        static let xl: CGFloat = 20
        static let xxl: CGFloat = 24
        
        // 特定组件
        static let button: CGFloat = 8
        static let card: CGFloat = 12
        static let sheet: CGFloat = 16
        static let avatar: CGFloat = 8
    }
    
    // MARK: - 阴影系统
    
    /// 阴影配置
    struct Shadows {
        static let small = Shadow(
            color: Colors.cardShadow,
            radius: 4,
            x: 0,
            y: 2
        )
        
        static let medium = Shadow(
            color: Colors.cardShadow,
            radius: 8,
            x: 0,
            y: 4
        )
        
        static let large = Shadow(
            color: Colors.cardShadow,
            radius: 16,
            x: 0,
            y: 8
        )
        
        struct Shadow {
            let color: Color
            let radius: CGFloat
            let x: CGFloat
            let y: CGFloat
        }
    }
    
    // MARK: - 尺寸系统
    
    /// 尺寸配置
    struct Sizes {
        // 图标尺寸
        static let iconXS: CGFloat = 16
        static let iconSM: CGFloat = 20
        static let iconMD: CGFloat = 24
        static let iconLG: CGFloat = 32
        static let iconXL: CGFloat = 40
        
        // 头像尺寸
        static let avatarSM: CGFloat = 40
        static let avatarMD: CGFloat = 60
        static let avatarLG: CGFloat = 80
        static let avatarXL: CGFloat = 120
        
        // 按钮尺寸
        static let buttonHeight: CGFloat = 44
        static let buttonHeightSM: CGFloat = 36
        static let buttonHeightLG: CGFloat = 52
        
        // 卡片最小高度
        static let cardMinHeight: CGFloat = 100
        static let cardMaxWidth: CGFloat = 400
    }
    
    // MARK: - 动画系统
    
    /// 动画配置
    struct Animations {
        static let fast = Animation.easeInOut(duration: 0.2)
        static let normal = Animation.easeInOut(duration: 0.3)
        static let slow = Animation.easeInOut(duration: 0.5)
        
        static let spring = Animation.spring(response: 0.3, dampingFraction: 0.7)
        static let springBouncy = Animation.spring(response: 0.4, dampingFraction: 0.6)
        
        // 页面转场
        static let pageTransition = Animation.easeInOut(duration: 0.25)
    }
}

// MARK: - View扩展：便捷应用主题样式

extension View {
    /// 应用卡片样式
    func cardStyle() -> some View {
        self
            .background(AppTheme.Colors.cardBackground)
            .cornerRadius(AppTheme.CornerRadius.card)
            .shadow(
                color: AppTheme.Shadows.medium.color,
                radius: AppTheme.Shadows.medium.radius,
                x: AppTheme.Shadows.medium.x,
                y: AppTheme.Shadows.medium.y
            )
    }
    
    /// 应用主按钮样式
    func primaryButtonStyle() -> some View {
        self
            .font(AppTheme.Fonts.headline)
            .foregroundColor(.white)
            .frame(height: AppTheme.Sizes.buttonHeight)
            .background(AppTheme.Colors.palaceRed)
            .cornerRadius(AppTheme.CornerRadius.button)
    }
    
    /// 应用次要按钮样式
    func secondaryButtonStyle() -> some View {
        self
            .font(AppTheme.Fonts.headline)
            .foregroundColor(AppTheme.Colors.palaceRed)
            .frame(height: AppTheme.Sizes.buttonHeight)
            .background(AppTheme.Colors.palaceRed.opacity(0.1))
            .cornerRadius(AppTheme.CornerRadius.button)
            .overlay(
                RoundedRectangle(cornerRadius: AppTheme.CornerRadius.button)
                    .stroke(AppTheme.Colors.palaceRed, lineWidth: 1)
            )
    }
    
    /// 应用标签样式
    func tagStyle(color: Color = AppTheme.Colors.palaceRed) -> some View {
        self
            .font(AppTheme.Fonts.caption)
            .foregroundColor(color)
            .padding(.horizontal, AppTheme.Spacing.sm)
            .padding(.vertical, AppTheme.Spacing.xxs)
            .background(color.opacity(0.1))
            .cornerRadius(AppTheme.CornerRadius.xs)
    }
    
    /// 应用徽章样式
    func badgeStyle(color: Color = AppTheme.Colors.palaceRed) -> some View {
        self
            .font(AppTheme.Fonts.caption2)
            .foregroundColor(.white)
            .padding(.horizontal, AppTheme.Spacing.xs)
            .padding(.vertical: AppTheme.Spacing.xxs)
            .background(color)
            .cornerRadius(AppTheme.CornerRadius.xs)
    }
}

// MARK: - 暗黑模式支持

extension AppTheme {
    /// 暗黑模式颜色配置
    struct DarkModeColors {
        // 主色调在暗黑模式下略微调亮
        static let palaceRed = Color(red: 180/255, green: 20/255, blue: 20/255)
        static let bronzeGreen = Color(red: 100/255, green: 160/255, blue: 120/255)
        static let gold = Color(red: 238/255, green: 185/255, blue: 52/255)
        
        // 背景色
        static let primaryBackground = Color(UIColor.systemBackground)
        static let secondaryBackground = Color(UIColor.secondarySystemBackground)
        static let cardBackground = Color(UIColor.secondarySystemBackground)
        
        // 文字色自动适配
        static let primaryText = Color(UIColor.label)
        static let secondaryText = Color(UIColor.secondaryLabel)
    }
    
    /// 根据当前颜色方案返回适配的颜色
    static func adaptiveColor(
        light: Color,
        dark: Color,
        colorScheme: ColorScheme
    ) -> Color {
        colorScheme == .dark ? dark : light
    }
}

// MARK: - 预览辅助

#if DEBUG
struct ThemePreview: View {
    var body: some View {
        ScrollView {
            VStack(spacing: AppTheme.Spacing.lg) {
                // 颜色预览
                colorSection
                
                // 字体预览
                fontSection
                
                // 组件样式预览
                componentSection
                
                // 朝代颜色预览
                dynastyColorSection
            }
            .padding()
        }
    }
    
    var colorSection: some View {
        VStack(alignment: .leading, spacing: AppTheme.Spacing.md) {
            Text("主题颜色")
                .font(AppTheme.Fonts.title2)
            
            HStack(spacing: AppTheme.Spacing.sm) {
                ColorSwatch(color: AppTheme.Colors.palaceRed, name: "故宫红")
                ColorSwatch(color: AppTheme.Colors.bronzeGreen, name: "青铜绿")
                ColorSwatch(color: AppTheme.Colors.gold, name: "金黄")
            }
        }
    }
    
    var fontSection: some View {
        VStack(alignment: .leading, spacing: AppTheme.Spacing.sm) {
            Text("字体系统")
                .font(AppTheme.Fonts.title2)
            
            Text("大标题样式")
                .font(AppTheme.Fonts.largeTitle)
            Text("朝代标题样式")
                .font(AppTheme.Fonts.dynastyTitle)
            Text("正文样式")
                .font(AppTheme.Fonts.body)
        }
    }
    
    var componentSection: some View {
        VStack(spacing: AppTheme.Spacing.md) {
            Text("组件样式")
                .font(AppTheme.Fonts.title2)
            
            Text("主按钮")
                .primaryButtonStyle()
                .padding(.horizontal)
            
            Text("次要按钮")
                .secondaryButtonStyle()
                .padding(.horizontal)
            
            Text("标签样式")
                .tagStyle()
        }
    }
    
    var dynastyColorSection: some View {
        VStack(alignment: .leading, spacing: AppTheme.Spacing.sm) {
            Text("朝代配色")
                .font(AppTheme.Fonts.title2)
            
            ForEach(["秦朝", "汉朝", "唐朝", "宋朝", "元朝", "明朝", "清朝"], id: \.self) { dynasty in
                HStack {
                    Text(dynasty)
                        .foregroundColor(.white)
                        .padding()
                        .frame(maxWidth: .infinity)
                        .background(AppTheme.DynastyColors.gradient(for: dynasty))
                        .cornerRadius(AppTheme.CornerRadius.md)
                }
            }
        }
    }
}

struct ColorSwatch: View {
    let color: Color
    let name: String
    
    var body: some View {
        VStack {
            RoundedRectangle(cornerRadius: AppTheme.CornerRadius.sm)
                .fill(color)
                .frame(width: 60, height: 60)
            
            Text(name)
                .font(AppTheme.Fonts.caption)
                .foregroundColor(AppTheme.Colors.secondaryText)
        }
    }
}

struct ThemePreview_Previews: PreviewProvider {
    static var previews: some View {
        Group {
            ThemePreview()
                .preferredColorScheme(.light)
            
            ThemePreview()
                .preferredColorScheme(.dark)
        }
    }
}
#endif
