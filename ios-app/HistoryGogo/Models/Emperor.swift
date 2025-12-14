//
//  Emperor.swift
//  HistoryGogo
//
//  皇帝数据模型
//

import Foundation

/// 皇帝模型
struct Emperor: Identifiable, Codable {
    /// 唯一标识符
    let id: String
    /// 所属朝代ID
    let dynastyId: String
    /// 姓名
    let name: String
    /// 庙号
    let templeName: String?
    /// 年号
    let reignTitle: String?
    /// 出生日期
    let birthDate: Date?
    /// 去世日期
    let deathDate: Date?
    /// 在位开始时间
    let reignStart: Date
    /// 在位结束时间
    let reignEnd: Date?
    /// 在位年数
    let reignDuration: Int?
    /// 朝代内顺序
    let dynastyOrder: Int
    /// 生平简介
    let biography: String?
    /// 主要成就
    let achievements: String?
    /// 画像URL
    let portraitURL: String?
    /// 数据来源
    let dataSource: String?
    
    // MARK: - Coding Keys
    
    enum CodingKeys: String, CodingKey {
        case id = "emperor_id"
        case dynastyId = "dynasty_id"
        case name
        case templeName = "temple_name"
        case reignTitle = "reign_title"
        case birthDate = "birth_date"
        case deathDate = "death_date"
        case reignStart = "reign_start"
        case reignEnd = "reign_end"
        case reignDuration = "reign_duration"
        case dynastyOrder = "dynasty_order"
        case biography
        case achievements
        case portraitURL = "portrait_url"
        case dataSource = "data_source"
    }
    
    // MARK: - Computed Properties
    
    /// 完整称号（庙号 + 姓名）
    var fullTitle: String {
        if let temple = templeName {
            return "\(temple) \(name)"
        }
        return name
    }
    
    /// 在位时间描述
    var reignPeriod: String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy年"
        
        let start = formatter.string(from: reignStart)
        if let end = reignEnd {
            let endStr = formatter.string(from: end)
            return "\(start) - \(endStr)"
        }
        return start
    }
    
    /// 寿命（年）
    var lifespan: Int? {
        guard let birth = birthDate, let death = deathDate else { return nil }
        let calendar = Calendar.current
        let components = calendar.dateComponents([.year], from: birth, to: death)
        return components.year
    }
}

// MARK: - Summary Model

/// 皇帝摘要信息（用于列表展示）
struct EmperorSummary: Identifiable, Codable {
    let id: String
    let name: String
    let templeName: String?
    let reignTitle: String?
    let reignStart: Date
    let reignEnd: Date?
    let reignDuration: Int?
    let dynastyOrder: Int
    let portraitURL: String?
    
    enum CodingKeys: String, CodingKey {
        case id = "emperor_id"
        case name
        case templeName = "temple_name"
        case reignTitle = "reign_title"
        case reignStart = "reign_start"
        case reignEnd = "reign_end"
        case reignDuration = "reign_duration"
        case dynastyOrder = "dynasty_order"
        case portraitURL = "portrait_url"
    }
    
    var fullTitle: String {
        if let temple = templeName {
            return "\(temple) \(name)"
        }
        return name
    }
}

// MARK: - Detail Model

/// 皇帝详细信息（包含关联数据）
struct EmperorDetail: Identifiable, Codable {
    let id: String
    let dynastyId: String
    let name: String
    let templeName: String?
    let reignTitle: String?
    let birthDate: Date?
    let deathDate: Date?
    let reignStart: Date
    let reignEnd: Date?
    let reignDuration: Int?
    let dynastyOrder: Int
    let biography: String?
    let achievements: String?
    let portraitURL: String?
    let dataSource: String?
    let eventCount: Int?
    let personCount: Int?
    
    enum CodingKeys: String, CodingKey {
        case id = "emperor_id"
        case dynastyId = "dynasty_id"
        case name
        case templeName = "temple_name"
        case reignTitle = "reign_title"
        case birthDate = "birth_date"
        case deathDate = "death_date"
        case reignStart = "reign_start"
        case reignEnd = "reign_end"
        case reignDuration = "reign_duration"
        case dynastyOrder = "dynasty_order"
        case biography
        case achievements
        case portraitURL = "portrait_url"
        case dataSource = "data_source"
        case eventCount = "event_count"
        case personCount = "person_count"
    }
}

// MARK: - Sample Data

extension Emperor {
    /// 示例数据
    static let sample = Emperor(
        id: "ming_taizu",
        dynastyId: "ming",
        name: "朱元璋",
        templeName: "明太祖",
        reignTitle: "洪武",
        birthDate: Date(timeIntervalSince1970: -20000000000),
        deathDate: Date(timeIntervalSince1970: -18000000000),
        reignStart: Date(timeIntervalSince1970: -19000000000),
        reignEnd: Date(timeIntervalSince1970: -18000000000),
        reignDuration: 30,
        dynastyOrder: 1,
        biography: "明朝开国皇帝，原名朱重八，后改名朱元璋。出身贫寒，参加红巾军起义，最终统一天下，建立明朝。",
        achievements: "建立明朝，实行一系列改革措施，加强中央集权，稳定社会秩序。",
        portraitURL: nil,
        dataSource: "baidu,wiki"
    )
}

extension EmperorSummary {
    static let sample = EmperorSummary(
        id: "ming_taizu",
        name: "朱元璋",
        templeName: "明太祖",
        reignTitle: "洪武",
        reignStart: Date(timeIntervalSince1970: -19000000000),
        reignEnd: Date(timeIntervalSince1970: -18000000000),
        reignDuration: 30,
        dynastyOrder: 1,
        portraitURL: nil
    )
}
