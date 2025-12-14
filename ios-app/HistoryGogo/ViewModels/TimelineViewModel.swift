//
//  TimelineViewModel.swift
//  HistoryGogo
//
//  时间轴ViewModel - MVVM架构
//

import Foundation
import Combine

/// 时间轴ViewModel
@MainActor
class TimelineViewModel: ObservableObject {
    
    // MARK: - Published Properties
    
    /// 当前朝代
    @Published var dynasty: Dynasty?
    /// 时间轴数据
    @Published var timelineData: TimelineResponse?
    /// 加载状态
    @Published var isLoading: Bool = false
    /// 错误信息
    @Published var errorMessage: String?
    /// 是否显示错误提示
    @Published var showError: Bool = false
    
    // MARK: - Properties
    
    private let apiService: APIServiceProtocol
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Initialization
    
    init(apiService: APIServiceProtocol = APIService.shared) {
        self.apiService = apiService
    }
    
    // MARK: - Public Methods
    
    /// 加载时间轴数据
    func loadTimeline(dynastyId: String) async {
        isLoading = true
        errorMessage = nil
        showError = false
        
        do {
            // 并发加载朝代信息和时间轴数据
            async let dynastyTask = apiService.fetchDynasty(id: dynastyId)
            async let timelineTask = apiService.fetchTimeline(dynastyId: dynastyId)
            
            let (loadedDynasty, loadedTimeline) = try await (dynastyTask, timelineTask)
            
            self.dynasty = loadedDynasty
            self.timelineData = loadedTimeline
            
        } catch let error as APIError {
            handleError(error)
        } catch {
            handleError(.unknown)
        }
        
        isLoading = false
    }
    
    /// 刷新数据
    func refresh(dynastyId: String) async {
        await loadTimeline(dynastyId: dynastyId)
    }
    
    /// 获取指定年份的时间轴项
    func timelineItem(for year: Int) -> TimelineItem? {
        return timelineData?.timeline.first { $0.year == year }
    }
    
    /// 按事件类型筛选
    func filterEvents(by type: String) -> [TimelineItem] {
        guard let timeline = timelineData?.timeline else { return [] }
        
        return timeline.filter { item in
            item.events.contains { $0.eventType == type }
        }
    }
    
    // MARK: - Private Methods
    
    private func handleError(_ error: APIError) {
        errorMessage = error.localizedDescription
        showError = true
    }
}

// MARK: - Computed Properties

extension TimelineViewModel {
    /// 时间跨度描述
    var timeSpan: String {
        guard let data = timelineData else { return "" }
        return "\(data.startYear)年 - \(data.endYear)年"
    }
    
    /// 总事件数
    var totalEvents: Int {
        return timelineData?.totalEvents ?? 0
    }
    
    /// 总皇帝数
    var totalEmperors: Int {
        return timelineData?.totalEmperors ?? 0
    }
    
    /// 有事件的年份列表
    var yearsWithEvents: [Int] {
        guard let timeline = timelineData?.timeline else { return [] }
        return timeline.filter { $0.hasEvents }.map { $0.year }
    }
}
