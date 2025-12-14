//
//  Extensions.swift
//  HistoryGogo
//
//  常用扩展
//

import Foundation
import SwiftUI

// MARK: - Date Extensions

extension Date {
    /// 格式化为年份
    func toYearString() -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy年"
        return formatter.string(from: self)
    }
    
    /// 格式化为年月
    func toYearMonthString() -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy年MM月"
        return formatter.string(from: self)
    }
    
    /// 格式化为完整日期
    func toFullDateString() -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy年MM月dd日"
        return formatter.string(from: self)
    }
    
    /// 获取年份
    var year: Int {
        return Calendar.current.component(.year, from: self)
    }
}

// MARK: - String Extensions

extension String {
    /// 是否为空字符串
    var isEmptyOrWhitespace: Bool {
        return self.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
    }
    
    /// 移除HTML标签
    var removingHTMLTags: String {
        return self.replacingOccurrences(of: "<[^>]+>", with: "", options: .regularExpression)
    }
}

// MARK: - Color Extensions

extension Color {
    /// 故宫红
    static let palaceRed = Color(red: 139/255, green: 0, blue: 0)
    
    /// 青铜绿
    static let bronzeGreen = Color(red: 74/255, green: 124/255, blue: 89/255)
    
    /// 宣纸白
    static let paperWhite = Color(red: 245/255, green: 245/255, blue: 220/255)
    
    /// 墨黑
    static let inkBlack = Color(red: 44/255, green: 44/255, blue: 44/255)
    
    /// 金黄
    static let gold = Color(red: 218/255, green: 165/255, blue: 32/255)
}

// MARK: - View Extensions

extension View {
    /// 当条件满足时应用修饰符
    @ViewBuilder
    func `if`<Transform: View>(
        _ condition: Bool,
        transform: (Self) -> Transform
    ) -> some View {
        if condition {
            transform(self)
        } else {
            self
        }
    }
    
    /// 隐藏视图
    @ViewBuilder
    func hidden(_ shouldHide: Bool) -> some View {
        if shouldHide {
            self.hidden()
        } else {
            self
        }
    }
}

// MARK: - Array Extensions

extension Array where Element: Identifiable {
    /// 移除重复元素
    func removingDuplicates() -> [Element] {
        var seen = Set<Element.ID>()
        return filter { seen.insert($0.id).inserted }
    }
}
