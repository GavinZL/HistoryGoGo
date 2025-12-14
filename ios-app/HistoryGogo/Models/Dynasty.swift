//
//  Dynasty.swift
//  HistoryGogo
//
//  朝代数据模型
//

import Foundation

/// 朝代模型
struct Dynasty: Identifiable, Codable {
    /// 唯一标识符
    let id: String
    /// 朝代名称
    let name: String
    /// 起始年份
    let startYear: Int
    /// 结束年份
    let endYear: Int
    /// 国都
    let capital: String?
    /// 开国皇帝
    let founder: String?
    /// 朝代简介
    let description: String?
    /// 创建时间
    let createdAt: Date?
    /// 更新时间
    let updatedAt: Date?
    
    // MARK: - Coding Keys
    
    enum CodingKeys: String, CodingKey {
        case id = "dynasty_id"
        case name
        case startYear = "start_year"
        case endYear = "end_year"
        case capital
        case founder
        case description
        case createdAt = "created_at"
        case updatedAt = "updated_at"
    }
    
    // MARK: - Computed Properties
    
    /// 朝代持续时间（年）
    var duration: Int {
        return endYear - startYear
    }
    
    /// 时间跨度描述
    var timeSpan: String {
        return "\(startYear)年 - \(endYear)年"
    }
    
    /// 是否是当前选中的朝代（明朝）
    var isMing: Bool {
        return id == "ming"
    }
}

// MARK: - Sample Data

extension Dynasty {
    /// 示例数据（用于预览和测试）
    static let sample = Dynasty(
        id: "ming",
        name: "明朝",
        startYear: 1368,
        endYear: 1644,
        capital: "北京",
        founder: "朱元璋",
        description: "明朝是中国历史上最后一个由汉族建立的大一统中原王朝",
        createdAt: Date(),
        updatedAt: Date()
    )
    
    /// 示例列表
    static let samples: [Dynasty] = [
        Dynasty(
            id: "ming",
            name: "明朝",
            startYear: 1368,
            endYear: 1644,
            capital: "北京",
            founder: "朱元璋",
            description: "明朝是中国历史上最后一个由汉族建立的大一统中原王朝",
            createdAt: Date(),
            updatedAt: Date()
        ),
        Dynasty(
            id: "qing",
            name: "清朝",
            startYear: 1644,
            endYear: 1912,
            capital: "北京",
            founder: "努尔哈赤",
            description: "清朝是中国历史上最后一个封建王朝",
            createdAt: Date(),
            updatedAt: Date()
        )
    ]
}
