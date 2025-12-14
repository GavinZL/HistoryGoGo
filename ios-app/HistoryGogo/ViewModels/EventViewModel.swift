//
//  EventViewModel.swift
//  HistoryGogo
//
//  事件ViewModel - MVVM架构
//

import Foundation
import Combine

/// 事件列表ViewModel
@MainActor
class EventListViewModel: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var events: [EventSummary] = []
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    @Published var showError: Bool = false
    @Published var selectedEventType: String?
    
    // MARK: - Properties
    
    private let apiService: APIServiceProtocol
    private var currentPage: Int = 0
    private let pageSize: Int = 20
    var canLoadMore: Bool = true
    
    // MARK: - Initialization
    
    init(apiService: APIServiceProtocol = APIService.shared) {
        self.apiService = apiService
    }
    
    // MARK: - Public Methods
    
    /// 加载事件列表
    func loadEvents(
        dynastyId: String? = nil,
        emperorId: String? = nil,
        eventType: String? = nil,
        refresh: Bool = false
    ) async {
        if refresh {
            currentPage = 0
            events = []
            canLoadMore = true
        }
        
        guard canLoadMore else { return }
        
        isLoading = true
        errorMessage = nil
        showError = false
        
        do {
            let loadedEvents = try await apiService.fetchEvents(
                dynastyId: dynastyId,
                emperorId: emperorId,
                eventType: eventType ?? selectedEventType,
                skip: currentPage * pageSize,
                limit: pageSize
            )
            
            if loadedEvents.isEmpty {
                canLoadMore = false
            } else {
                events.append(contentsOf: loadedEvents)
                currentPage += 1
            }
            
        } catch let error as APIError {
            handleError(error)
        } catch {
            handleError(.unknown)
        }
        
        isLoading = false
    }
    
    /// 按事件类型筛选
    func filterByType(_ type: String?, dynastyId: String? = nil) async {
        selectedEventType = type
        await loadEvents(dynastyId: dynastyId, eventType: type, refresh: true)
    }
    
    /// 刷新数据
    func refresh(dynastyId: String? = nil) async {
        await loadEvents(dynastyId: dynastyId, refresh: true)
    }
    
    // MARK: - Private Methods
    
    private func handleError(_ error: APIError) {
        errorMessage = error.localizedDescription
        showError = true
    }
}

/// 事件详情ViewModel
@MainActor
class EventDetailViewModel: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var event: EventDetail?
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    @Published var showError: Bool = false
    
    // MARK: - Properties
    
    private let apiService: APIServiceProtocol
    let eventId: String
    
    // MARK: - Initialization
    
    init(eventId: String, apiService: APIServiceProtocol = APIService.shared) {
        self.eventId = eventId
        self.apiService = apiService
    }
    
    // MARK: - Public Methods
    
    /// 加载事件详情
    func loadDetail() async {
        isLoading = true
        errorMessage = nil
        showError = false
        
        do {
            event = try await apiService.fetchEventDetail(id: eventId)
        } catch let error as APIError {
            handleError(error)
        } catch {
            handleError(.unknown)
        }
        
        isLoading = false
    }
    
    /// 刷新数据
    func refresh() async {
        await loadDetail()
    }
    
    // MARK: - Private Methods
    
    private func handleError(_ error: APIError) {
        errorMessage = error.localizedDescription
        showError = true
    }
}

// MARK: - Computed Properties

extension EventDetailViewModel {
    /// 事件时间描述
    var timeDescription: String {
        guard let evt = event else { return "" }
        
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy年MM月dd日"
        
        let start = formatter.string(from: evt.startDate)
        if let end = evt.endDate {
            let endStr = formatter.string(from: end)
            return "\(start) - \(endStr)"
        }
        return start
    }
    
    /// 事件持续天数
    var durationDays: Int? {
        return event?.duration
    }
}
