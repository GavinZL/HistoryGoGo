//
//  APIService.swift
//  HistoryGogo
//
//  API服务 - 封装所有API调用
//

import Foundation

/// API服务协议
protocol APIServiceProtocol {
    // 朝代相关
    func fetchDynasties() async throws -> [Dynasty]
    func fetchDynasty(id: String) async throws -> Dynasty
    
    // 皇帝相关
    func fetchEmperors(dynastyId: String?, skip: Int, limit: Int) async throws -> [EmperorSummary]
    func fetchEmperorDetail(id: String) async throws -> EmperorDetail
    
    // 事件相关
    func fetchEvents(dynastyId: String?, emperorId: String?, eventType: String?, skip: Int, limit: Int) async throws -> [EventSummary]
    func fetchEventDetail(id: String) async throws -> EventDetail
    
    // 人物相关
    func fetchPersons(dynastyId: String?, personType: String?, skip: Int, limit: Int) async throws -> [PersonSummary]
    func fetchPersonDetail(id: String) async throws -> PersonDetail
    
    // 时间轴相关
    func fetchTimeline(dynastyId: String) async throws -> TimelineResponse
}

/// API服务实现
class APIService: APIServiceProtocol {
    
    // MARK: - Properties
    
    static let shared = APIService()
    private let networkManager = NetworkManager.shared
    
    private init() {}
    
    // MARK: - Dynasty API
    
    /// 获取朝代列表
    func fetchDynasties() async throws -> [Dynasty] {
        return try await networkManager.get("/dynasties")
    }
    
    /// 获取朝代详情
    func fetchDynasty(id: String) async throws -> Dynasty {
        return try await networkManager.get("/dynasties/\(id)")
    }
    
    // MARK: - Emperor API
    
    /// 获取皇帝列表
    func fetchEmperors(
        dynastyId: String? = nil,
        skip: Int = 0,
        limit: Int = 20
    ) async throws -> [EmperorSummary] {
        var parameters: [String: String] = [
            "skip": String(skip),
            "limit": String(limit)
        ]
        
        if let dynastyId = dynastyId {
            parameters["dynasty_id"] = dynastyId
        }
        
        return try await networkManager.get("/emperors", parameters: parameters)
    }
    
    /// 获取皇帝详情
    func fetchEmperorDetail(id: String) async throws -> EmperorDetail {
        return try await networkManager.get("/emperors/\(id)")
    }
    
    // MARK: - Event API
    
    /// 获取事件列表
    func fetchEvents(
        dynastyId: String? = nil,
        emperorId: String? = nil,
        eventType: String? = nil,
        skip: Int = 0,
        limit: Int = 20
    ) async throws -> [EventSummary] {
        var parameters: [String: String] = [
            "skip": String(skip),
            "limit": String(limit)
        ]
        
        if let dynastyId = dynastyId {
            parameters["dynasty_id"] = dynastyId
        }
        
        if let emperorId = emperorId {
            parameters["emperor_id"] = emperorId
        }
        
        if let eventType = eventType {
            parameters["event_type"] = eventType
        }
        
        return try await networkManager.get("/events", parameters: parameters)
    }
    
    /// 获取事件详情
    func fetchEventDetail(id: String) async throws -> EventDetail {
        return try await networkManager.get("/events/\(id)")
    }
    
    // MARK: - Person API
    
    /// 获取人物列表
    func fetchPersons(
        dynastyId: String? = nil,
        personType: String? = nil,
        skip: Int = 0,
        limit: Int = 20
    ) async throws -> [PersonSummary] {
        var parameters: [String: String] = [
            "skip": String(skip),
            "limit": String(limit)
        ]
        
        if let dynastyId = dynastyId {
            parameters["dynasty_id"] = dynastyId
        }
        
        if let personType = personType {
            parameters["person_type"] = personType
        }
        
        return try await networkManager.get("/persons", parameters: parameters)
    }
    
    /// 获取人物详情
    func fetchPersonDetail(id: String) async throws -> PersonDetail {
        return try await networkManager.get("/persons/\(id)")
    }
    
    // MARK: - Timeline API
    
    /// 获取时间轴数据
    func fetchTimeline(dynastyId: String) async throws -> TimelineResponse {
        return try await networkManager.get("/timeline/\(dynastyId)")
    }
}

// MARK: - Mock Service for Testing

/// Mock API服务（用于测试和预览）
class MockAPIService: APIServiceProtocol {
    
    func fetchDynasties() async throws -> [Dynasty] {
        // 模拟网络延迟
        try await Task.sleep(nanoseconds: 500_000_000) // 0.5秒
        return Dynasty.samples
    }
    
    func fetchDynasty(id: String) async throws -> Dynasty {
        try await Task.sleep(nanoseconds: 500_000_000)
        return Dynasty.sample
    }
    
    func fetchEmperors(dynastyId: String?, skip: Int, limit: Int) async throws -> [EmperorSummary] {
        try await Task.sleep(nanoseconds: 500_000_000)
        return [EmperorSummary.sample]
    }
    
    func fetchEmperorDetail(id: String) async throws -> EmperorDetail {
        try await Task.sleep(nanoseconds: 500_000_000)
        return EmperorDetail(
            id: "ming_taizu",
            dynastyId: "ming",
            name: "朱元璋",
            templeName: "明太祖",
            reignTitle: "洪武",
            birthDate: Date(),
            deathDate: Date(),
            reignStart: Date(),
            reignEnd: Date(),
            reignDuration: 30,
            dynastyOrder: 1,
            biography: "明朝开国皇帝",
            achievements: "建立明朝",
            portraitURL: nil,
            dataSource: "mock",
            eventCount: 10,
            personCount: 50
        )
    }
    
    func fetchEvents(dynastyId: String?, emperorId: String?, eventType: String?, skip: Int, limit: Int) async throws -> [EventSummary] {
        try await Task.sleep(nanoseconds: 500_000_000)
        return EventSummary.samples
    }
    
    func fetchEventDetail(id: String) async throws -> EventDetail {
        try await Task.sleep(nanoseconds: 500_000_000)
        return EventDetail.sample
    }
    
    func fetchPersons(dynastyId: String?, personType: String?, skip: Int, limit: Int) async throws -> [PersonSummary] {
        try await Task.sleep(nanoseconds: 500_000_000)
        return PersonSummary.samples
    }
    
    func fetchPersonDetail(id: String) async throws -> PersonDetail {
        try await Task.sleep(nanoseconds: 500_000_000)
        return PersonDetail.sample
    }
    
    func fetchTimeline(dynastyId: String) async throws -> TimelineResponse {
        try await Task.sleep(nanoseconds: 1_000_000_000) // 1秒
        return TimelineResponse.sample
    }
}
