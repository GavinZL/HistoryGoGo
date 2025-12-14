//
//  Person.swift
//  HistoryGogo
//
//  历史人物数据模型
//

import Foundation

/// 人物类型枚举
enum PersonType: String, Codable, CaseIterable {
    case emperor = "皇帝"
    case official = "文臣"
    case general = "武将"
    case writer = "文学家"
    case artist = "艺术家"
    case thinker = "思想家"
    case scientist = "科学家"
    case royal = "宗室"
    case monk = "僧侣"
    case merchant = "商人"
    case other = "其他"
    
    var displayName: String {
        return self.rawValue
    }
    
    /// 人物类型图标
    var icon: String {
        switch self {
        case .emperor: return "crown.fill"
        case .official: return "book.fill"
        case .general: return "shield.fill"
        case .writer: return "pencil"
        case .artist: return "paintbrush.fill"
        case .thinker: return "brain"
        case .scientist: return "atom"
        case .royal: return "person.2.fill"
        case .monk: return "leaf.fill"
        case .merchant: return "cart.fill"
        case .other: return "person.fill"
        }
    }
}

/// 人物摘要信息（用于列表展示）
struct PersonSummary: Identifiable, Codable {
    let id: String
    let name: String
    let personType: String
    let alias: String?
    let birthDate: Date?
    let deathDate: Date?
    let dynastyId: String
    
    enum CodingKeys: String, CodingKey {
        case id = "person_id"
        case name
        case personType = "person_type"
        case alias
        case birthDate = "birth_date"
        case deathDate = "death_date"
        case dynastyId = "dynasty_id"
    }
    
    /// 生卒年描述
    var lifespanDescription: String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy"
        
        var result = ""
        if let birth = birthDate {
            result += formatter.string(from: birth)
        } else {
            result += "?"
        }
        
        result += " - "
        
        if let death = deathDate {
            result += formatter.string(from: death)
        } else {
            result += "?"
        }
        
        return result
    }
}

/// 人物详细信息
struct PersonDetail: Identifiable, Codable {
    let id: String
    let dynastyId: String
    let name: String
    let personType: String
    let alias: String?
    let birthDate: Date?
    let deathDate: Date?
    let position: String?
    let biography: String?
    let achievements: String?
    let dataSource: String?
    let relatedEmperors: [String]?
    let style: String?
    let works: [String]?
    let eventCount: Int?
    let workCount: Int?
    
    enum CodingKeys: String, CodingKey {
        case id = "person_id"
        case dynastyId = "dynasty_id"
        case name
        case personType = "person_type"
        case alias
        case birthDate = "birth_date"
        case deathDate = "death_date"
        case position
        case biography
        case achievements
        case dataSource = "data_source"
        case relatedEmperors = "related_emperors"
        case style
        case works
        case eventCount = "event_count"
        case workCount = "work_count"
    }
    
    /// 寿命
    var lifespan: Int? {
        guard let birth = birthDate, let death = deathDate else { return nil }
        let calendar = Calendar.current
        let components = calendar.dateComponents([.year], from: birth, to: death)
        return components.year
    }
    
    /// 完整称呼（包含别名）
    var fullName: String {
        if let aliasStr = alias, !aliasStr.isEmpty {
            return "\(name)（\(aliasStr)）"
        }
        return name
    }
}

// MARK: - Sample Data

extension PersonSummary {
    static let sample = PersonSummary(
        id: "person_001",
        name: "郑和",
        personType: "武将",
        alias: "三宝太监",
        birthDate: Date(timeIntervalSince1970: -19000000000),
        deathDate: Date(timeIntervalSince1970: -17000000000),
        dynastyId: "ming"
    )
    
    static let samples: [PersonSummary] = [
        PersonSummary(
            id: "person_001",
            name: "郑和",
            personType: "武将",
            alias: "三宝太监",
            birthDate: Date(timeIntervalSince1970: -19000000000),
            deathDate: Date(timeIntervalSince1970: -17000000000),
            dynastyId: "ming"
        ),
        PersonSummary(
            id: "person_002",
            name: "王阳明",
            personType: "思想家",
            alias: "王守仁",
            birthDate: Date(timeIntervalSince1970: -15000000000),
            deathDate: Date(timeIntervalSince1970: -14000000000),
            dynastyId: "ming"
        )
    ]
}

extension PersonDetail {
    static let sample = PersonDetail(
        id: "person_001",
        dynastyId: "ming",
        name: "郑和",
        personType: "武将",
        alias: "三宝太监",
        birthDate: Date(timeIntervalSince1970: -19000000000),
        deathDate: Date(timeIntervalSince1970: -17000000000),
        position: "钦差正使",
        biography: "郑和，本姓马，小名三宝，云南昆阳人。明朝著名航海家、外交家。",
        achievements: "七次下西洋，促进了中国与东南亚、南亚、西亚、东非等地区的贸易和文化交流。",
        dataSource: "baidu,wiki",
        relatedEmperors: ["ming_chengzu"],
        style: nil,
        works: ["郑和航海图"],
        eventCount: 5,
        workCount: 1
    )
}
