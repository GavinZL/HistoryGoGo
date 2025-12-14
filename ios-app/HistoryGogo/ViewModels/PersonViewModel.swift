//
//  PersonViewModel.swift
//  HistoryGogo
//
//  人物ViewModel - MVVM架构
//

import Foundation
import Combine

/// 人物列表ViewModel
@MainActor
class PersonListViewModel: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var persons: [PersonSummary] = []
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    @Published var showError: Bool = false
    @Published var selectedPersonType: String?
    
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
    
    /// 加载人物列表
    func loadPersons(
        dynastyId: String? = nil,
        personType: String? = nil,
        refresh: Bool = false
    ) async {
        if refresh {
            currentPage = 0
            persons = []
            canLoadMore = true
        }
        
        guard canLoadMore else { return }
        
        isLoading = true
        errorMessage = nil
        showError = false
        
        do {
            let loadedPersons = try await apiService.fetchPersons(
                dynastyId: dynastyId,
                personType: personType ?? selectedPersonType,
                skip: currentPage * pageSize,
                limit: pageSize
            )
            
            if loadedPersons.isEmpty {
                canLoadMore = false
            } else {
                persons.append(contentsOf: loadedPersons)
                currentPage += 1
            }
            
        } catch let error as APIError {
            handleError(error)
        } catch {
            handleError(.unknown)
        }
        
        isLoading = false
    }
    
    /// 按人物类型筛选
    func filterByType(_ type: String?, dynastyId: String? = nil) async {
        selectedPersonType = type
        await loadPersons(dynastyId: dynastyId, personType: type, refresh: true)
    }
    
    /// 刷新数据
    func refresh(dynastyId: String? = nil) async {
        await loadPersons(dynastyId: dynastyId, refresh: true)
    }
    
    // MARK: - Private Methods
    
    private func handleError(_ error: APIError) {
        errorMessage = error.localizedDescription
        showError = true
    }
}

/// 人物详情ViewModel
@MainActor
class PersonDetailViewModel: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var person: PersonDetail?
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    @Published var showError: Bool = false
    
    // MARK: - Properties
    
    private let apiService: APIServiceProtocol
    let personId: String
    
    // MARK: - Initialization
    
    init(personId: String, apiService: APIServiceProtocol = APIService.shared) {
        self.personId = personId
        self.apiService = apiService
    }
    
    // MARK: - Public Methods
    
    /// 加载人物详情
    func loadDetail() async {
        isLoading = true
        errorMessage = nil
        showError = false
        
        do {
            person = try await apiService.fetchPersonDetail(id: personId)
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

extension PersonDetailViewModel {
    /// 生卒年描述
    var lifespanDescription: String {
        guard let p = person else { return "" }
        
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy年"
        
        var result = ""
        if let birth = p.birthDate {
            result += formatter.string(from: birth)
        } else {
            result += "?"
        }
        
        result += " - "
        
        if let death = p.deathDate {
            result += formatter.string(from: death)
        } else {
            result += "?"
        }
        
        return result
    }
    
    /// 寿命年数
    var lifespanYears: Int? {
        guard let p = person,
              let birth = p.birthDate,
              let death = p.deathDate else { return nil }
        
        let calendar = Calendar.current
        let components = calendar.dateComponents([.year], from: birth, to: death)
        return components.year
    }
    
    /// 作品数量
    var worksCount: Int {
        return person?.works?.count ?? 0
    }
}
