//
//  Timeline.swift
//  HistoryGogo
//
//  时间轴数据模型
//

import Foundation

/// 时间轴上的事件
struct TimelineEvent: Identifiable, Codable {
    let id: String
    let title: String
    let eventType: String
    let location: String?
    
    enum CodingKeys: String, CodingKey {
        case id = "event_id"
        case title
        case eventType = "event_type"
        case location
    }
}

/// 时间轴上的皇帝信息
struct TimelineEmperor: Codable {
    let emperorId: String
    let name: String
    let templeName: String?
    let reignStart: Date
    let reignEnd: Date?
    
    enum CodingKeys: String, CodingKey {
        case emperorId = "emperor_id"
        case name
        case templeName = "temple_name"
        case reignStart = "reign_start"
        case reignEnd = "reign_end"
    }
    
    var displayName: String {
        if let temple = templeName {
            return temple
        }
        return name
    }
}

/// 时间线上的单个时间点
struct TimelineItem: Identifiable, Codable {
    var id: Int { year }
    
    let year: Int
    let events: [TimelineEvent]
    let emperor: TimelineEmperor?
    
    /// 该年是否有重要事件
    var hasEvents: Bool {
        return !events.isEmpty
    }
    
    /// 事件数量
    var eventCount: Int {
        return events.count
    }
}

/// 完整的时间轴响应
struct TimelineResponse: Codable {
    let dynastyId: String
    let dynastyName: String
    let startYear: Int
    let endYear: Int
    let timeline: [TimelineItem]
    let totalEvents: Int
    let totalEmperors: Int
    
    enum CodingKeys: String, CodingKey {
        case dynastyId = "dynasty_id"
        case dynastyName = "dynasty_name"
        case startYear = "start_year"
        case endYear = "end_year"
        case timeline
        case totalEvents = "total_events"
        case totalEmperors = "total_emperors"
    }
    
    /// 时间跨度（年）
    var duration: Int {
        return endYear - startYear
    }
    
    /// 按年份获取时间轴项
    func item(for year: Int) -> TimelineItem? {
        return timeline.first { $0.year == year }
    }
}

// MARK: - Sample Data

extension TimelineEvent {
    static let sample = TimelineEvent(
        id: "event_001",
        title: "明朝建立",
        eventType: "政治",
        location: "南京"
    )
}

extension TimelineEmperor {
    static let sample = TimelineEmperor(
        emperorId: "ming_taizu",
        name: "朱元璋",
        templeName: "明太祖",
        reignStart: Date(timeIntervalSince1970: -19000000000),
        reignEnd: Date(timeIntervalSince1970: -18000000000)
    )
}

extension TimelineItem {
    static let sample = TimelineItem(
        year: 1368,
        events: [
            TimelineEvent(id: "event_001", title: "明朝建立", eventType: "政治", location: "南京")
        ],
        emperor: TimelineEmperor.sample
    )
    
    static let samples: [TimelineItem] = [
        TimelineItem(
            year: 1368,
            events: [
                TimelineEvent(id: "event_001", title: "明朝建立", eventType: "政治", location: "南京")
            ],
            emperor: TimelineEmperor.sample
        ),
        TimelineItem(
            year: 1369,
            events: [],
            emperor: TimelineEmperor.sample
        ),
        TimelineItem(
            year: 1370,
            events: [
                TimelineEvent(id: "event_002", title: "北伐蒙古", eventType: "军事", location: "北方")
            ],
            emperor: TimelineEmperor.sample
        )
    ]
}

extension TimelineResponse {
    static let sample = TimelineResponse(
        dynastyId: "ming",
        dynastyName: "明朝",
        startYear: 1368,
        endYear: 1644,
        timeline: TimelineItem.samples,
        totalEvents: 150,
        totalEmperors: 16
    )
}
