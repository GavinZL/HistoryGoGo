//
//  EmperorViewModel.swift
//  HistoryGogo
//
//  皇帝ViewModel - MVVM架构
//

import Foundation
import Combine

/// 皇帝列表ViewModel
@MainActor
class EmperorListViewModel: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var emperors: [EmperorSummary] = []
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    @Published var showError: Bool = false
    
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
    
    /// 加载皇帝列表
    func loadEmperors(dynastyId: String? = nil, refresh: Bool = false) async {
        if refresh {
            currentPage = 0
            emperors = []
            canLoadMore = true
        }
        
        guard canLoadMore else { return }
        
        isLoading = true
        errorMessage = nil
        showError = false
        
        do {
            let loadedEmperors = try await apiService.fetchEmperors(
                dynastyId: dynastyId,
                skip: currentPage * pageSize,
                limit: pageSize
            )
            
            if loadedEmperors.isEmpty {
                canLoadMore = false
            } else {
                emperors.append(contentsOf: loadedEmperors)
                currentPage += 1
            }
            
        } catch let error as APIError {
            handleError(error)
        } catch {
            handleError(.unknown)
        }
        
        isLoading = false
    }
    
    /// 刷新数据
    func refresh(dynastyId: String? = nil) async {
        await loadEmperors(dynastyId: dynastyId, refresh: true)
    }
    
    // MARK: - Private Methods
    
    private func handleError(_ error: APIError) {
        errorMessage = error.localizedDescription
        showError = true
    }
}

/// 皇帝详情ViewModel
@MainActor
class EmperorDetailViewModel: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var emperor: EmperorDetail?
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    @Published var showError: Bool = false
    
    // MARK: - Properties
    
    private let apiService: APIServiceProtocol
    let emperorId: String
    
    // MARK: - Initialization
    
    init(emperorId: String, apiService: APIServiceProtocol = APIService.shared) {
        self.emperorId = emperorId
        self.apiService = apiService
    }
    
    // MARK: - Public Methods
    
    /// 加载皇帝详情
    func loadDetail() async {
        isLoading = true
        errorMessage = nil
        showError = false
        
        do {
            emperor = try await apiService.fetchEmperorDetail(id: emperorId)
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

extension EmperorDetailViewModel {
    /// 在位时间描述
    var reignPeriodDescription: String {
        guard let emp = emperor else { return "" }
        
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy年"
        
        let start = formatter.string(from: emp.reignStart)
        if let end = emp.reignEnd {
            let endStr = formatter.string(from: end)
            return "\(start) - \(endStr)"
        }
        return start
    }
    
    /// 生平年数
    var lifespanYears: Int? {
        guard let emp = emperor,
              let birth = emp.birthDate,
              let death = emp.deathDate else { return nil }
        
        let calendar = Calendar.current
        let components = calendar.dateComponents([.year], from: birth, to: death)
        return components.year
    }
}
