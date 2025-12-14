//
//  Event.swift
//  HistoryGogo
//
//  历史事件数据模型
//

import Foundation

/// 事件类型枚举
enum EventType: String, Codable, CaseIterable {
    case political = "政治"
    case military = "军事"
    case cultural = "文化"
    case economic = "经济"
    case diplomatic = "外交"
    case natural = "自然灾害"
    case technological = "科技"
    case other = "其他"
    
    var displayName: String {
        return self.rawValue
    }
    
    /// 事件类型对应的颜色
    var color: String {
        switch self {
        case .political: return "blue"
        case .military: return "red"
        case .cultural: return "purple"
        case .economic: return "green"
        case .diplomatic: return "orange"
        case .natural: return "brown"
        case .technological: return "cyan"
        case .other: return "gray"
        }
    }
}

/// 事件摘要信息（用于列表展示）
struct EventSummary: Identifiable, Codable {
    let id: String
    let title: String
    let eventType: String
    let startDate: Date
    let endDate: Date?
    let location: String?
    let dynastyId: String
    let emperorId: String?
    
    enum CodingKeys: String, CodingKey {
        case id = "event_id"
        case title
        case eventType = "event_type"
        case startDate = "start_date"
        case endDate = "end_date"
        case location
        case dynastyId = "dynasty_id"
        case emperorId = "emperor_id"
    }
    
    /// 事件年份
    var year: Int {
        let calendar = Calendar.current
        return calendar.component(.year, from: startDate)
    }
    
    /// 时间描述
    var timeDescription: String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy年MM月"
        
        if let end = endDate {
            return "\(formatter.string(from: startDate)) - \(formatter.string(from: end))"
        }
        return formatter.string(from: startDate)
    }
}

/// 事件详细信息
struct EventDetail: Identifiable, Codable {
    let id: String
    let dynastyId: String
    let emperorId: String?
    let title: String
    let eventType: String
    let startDate: Date
    let endDate: Date?
    let location: String?
    let description: String?
    let participants: String?
    let casualties: String?
    let result: String?
    let significance: String?
    let dataSource: String?
    let relatedPersons: [String]?
    let personCount: Int?
    
    enum CodingKeys: String, CodingKey {
        case id = "event_id"
        case dynastyId = "dynasty_id"
        case emperorId = "emperor_id"
        case title
        case eventType = "event_type"
        case startDate = "start_date"
        case endDate = "end_date"
        case location
        case description
        case participants
        case casualties
        case result
        case significance
        case dataSource = "data_source"
        case relatedPersons = "related_persons"
        case personCount = "person_count"
    }
    
    /// 事件持续时间（天）
    var duration: Int? {
        guard let end = endDate else { return nil }
        let calendar = Calendar.current
        let components = calendar.dateComponents([.day], from: startDate, to: end)
        return components.day
    }
}

// MARK: - Sample Data

extension EventSummary {
    static let sample = EventSummary(
        id: "event_001",
        title: "靖难之役",
        eventType: "军事",
        startDate: Date(timeIntervalSince1970: -18000000000),
        endDate: Date(timeIntervalSince1970: -17900000000),
        location: "北京",
        dynastyId: "ming",
        emperorId: "ming_chengzu"
    )
    
    static let samples: [EventSummary] = [
        EventSummary(
            id: "event_001",
            title: "靖难之役",
            eventType: "军事",
            startDate: Date(timeIntervalSince1970: -18000000000),
            endDate: Date(timeIntervalSince1970: -17900000000),
            location: "北京",
            dynastyId: "ming",
            emperorId: "ming_chengzu"
        ),
        EventSummary(
            id: "event_002",
            title: "永乐大典编纂",
            eventType: "文化",
            startDate: Date(timeIntervalSince1970: -17800000000),
            endDate: nil,
            location: "南京",
            dynastyId: "ming",
            emperorId: "ming_chengzu"
        )
    ]
}

extension EventDetail {
    static let sample = EventDetail(
        id: "event_001",
        dynastyId: "ming",
        emperorId: "ming_chengzu",
        title: "靖难之役",
        eventType: "军事",
        startDate: Date(timeIntervalSince1970: -18000000000),
        endDate: Date(timeIntervalSince1970: -17900000000),
        location: "北京",
        description: "靖难之役是明朝初年，燕王朱棣起兵反对建文帝的一场战争。",
        participants: "朱棣、朱允炆",
        casualties: "数十万",
        result: "朱棣获胜，登基称帝",
        significance: "改变了明朝的政治格局，朱棣成为明成祖。",
        dataSource: "baidu,wiki",
        relatedPersons: ["person_001", "person_002"],
        personCount: 2
    )
}
