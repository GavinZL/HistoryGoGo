//
//  SearchView.swift
//  HistoryGogo
//
//  全局搜索视图 - SwiftUI
//

import SwiftUI

struct SearchView: View {
    
    @StateObject private var viewModel = SearchViewModel()
    @State private var searchText = ""
    @State private var selectedCategory: SearchCategory = .all
    @FocusState private var isSearchFieldFocused: Bool
    
    enum SearchCategory: String, CaseIterable {
        case all = "全部"
        case emperor = "皇帝"
        case event = "事件"
        case person = "人物"
        
        var icon: String {
            switch self {
            case .all: return "magnifyingglass"
            case .emperor: return "crown"
            case .event: return "calendar"
            case .person: return "person.3"
            }
        }
    }
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // 搜索栏
                searchBar
                
                // 分类选择
                categoryPicker
                
                Divider()
                
                // 搜索结果
                searchResults
            }
            .navigationTitle("搜索")
            .navigationBarTitleDisplayMode(.large)
        }
    }
    
    // MARK: - View Components
    
    private var searchBar: some View {
        HStack(spacing: 12) {
            HStack {
                Image(systemName: "magnifyingglass")
                    .foregroundColor(.secondary)
                
                TextField("搜索皇帝、事件、人物...", text: $searchText)
                    .focused($isSearchFieldFocused)
                    .textFieldStyle(.plain)
                    .submitLabel(.search)
                    .onSubmit {
                        performSearch()
                    }
                
                if !searchText.isEmpty {
                    Button {
                        searchText = ""
                        viewModel.clearResults()
                    } label: {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(.secondary)
                    }
                }
            }
            .padding(10)
            .background(Color(.secondarySystemBackground))
            .cornerRadius(10)
            
            if isSearchFieldFocused {
                Button("取消") {
                    searchText = ""
                    isSearchFieldFocused = false
                    viewModel.clearResults()
                }
                .transition(.move(edge: .trailing))
            }
        }
        .padding()
        .animation(.easeInOut(duration: 0.2), value: isSearchFieldFocused)
    }
    
    private var categoryPicker: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 12) {
                ForEach(SearchCategory.allCases, id: \.self) { category in
                    CategoryChip(
                        title: category.rawValue,
                        icon: category.icon,
                        isSelected: selectedCategory == category
                    )
                    .onTapGesture {
                        selectedCategory = category
                        if !searchText.isEmpty {
                            performSearch()
                        }
                    }
                }
            }
            .padding(.horizontal)
            .padding(.vertical, 8)
        }
    }
    
    @ViewBuilder
    private var searchResults: some View {
        if viewModel.isLoading {
            LoadingView(message: "搜索中...")
        } else if searchText.isEmpty {
            searchPlaceholder
        } else if viewModel.hasResults {
            resultsList
        } else {
            EmptyStateView(
                icon: "magnifyingglass",
                title: "未找到结果",
                message: "尝试使用其他关键词"
            )
        }
    }
    
    private var searchPlaceholder: some View {
        VStack(spacing: 16) {
            Image(systemName: "doc.text.magnifyingglass")
                .font(.system(size: 60))
                .foregroundColor(.gray)
            
            Text("输入关键词开始搜索")
                .font(.headline)
                .foregroundColor(.secondary)
            
            VStack(alignment: .leading, spacing: 8) {
                Text("搜索提示：")
                    .font(.subheadline)
                    .fontWeight(.medium)
                
                suggestionItem("搜索皇帝：朱元璋、朱棣...")
                suggestionItem("搜索事件：靖难之役、郑和下西洋...")
                suggestionItem("搜索人物：郑和、王阳明...")
            }
            .padding()
            .background(Color(.secondarySystemBackground))
            .cornerRadius(12)
            .padding(.horizontal)
        }
        .frame(maxHeight: .infinity)
    }
    
    private func suggestionItem(_ text: String) -> some View {
        HStack {
            Image(systemName: "lightbulb.fill")
                .foregroundColor(.yellow)
                .font(.caption)
            Text(text)
                .font(.caption)
                .foregroundColor(.secondary)
        }
    }
    
    private var resultsList: some View {
        List {
            // 皇帝结果
            if !viewModel.emperorResults.isEmpty && (selectedCategory == .all || selectedCategory == .emperor) {
                Section {
                    ForEach(viewModel.emperorResults.prefix(5), id: \.id) { emperor in
                        NavigationLink {
                            EmperorDetailView(emperorId: emperor.id)
                        } label: {
                            SearchResultRow(
                                icon: "crown.fill",
                                title: emperor.fullTitle,
                                subtitle: emperor.reignTitle ?? "",
                                iconColor: .yellow
                            )
                        }
                    }
                } header: {
                    Text("皇帝 (\(viewModel.emperorResults.count))")
                }
            }
            
            // 事件结果
            if !viewModel.eventResults.isEmpty && (selectedCategory == .all || selectedCategory == .event) {
                Section {
                    ForEach(viewModel.eventResults.prefix(5), id: \.id) { event in
                        NavigationLink {
                            EventDetailView(eventId: event.id)
                        } label: {
                            SearchResultRow(
                                icon: "calendar",
                                title: event.title,
                                subtitle: event.eventType,
                                iconColor: .blue
                            )
                        }
                    }
                } header: {
                    Text("事件 (\(viewModel.eventResults.count))")
                }
            }
            
            // 人物结果
            if !viewModel.personResults.isEmpty && (selectedCategory == .all || selectedCategory == .person) {
                Section {
                    ForEach(viewModel.personResults.prefix(5), id: \.id) { person in
                        NavigationLink {
                            PersonDetailView(personId: person.id)
                        } label: {
                            SearchResultRow(
                                icon: "person.fill",
                                title: person.name,
                                subtitle: person.personType,
                                iconColor: .green
                            )
                        }
                    }
                } header: {
                    Text("人物 (\(viewModel.personResults.count))")
                }
            }
        }
        .listStyle(.insetGrouped)
    }
    
    // MARK: - Actions
    
    private func performSearch() {
        guard !searchText.isEmpty else { return }
        
        Task {
            await viewModel.search(
                keyword: searchText,
                category: selectedCategory
            )
        }
    }
}

// MARK: - Search ViewModel

@MainActor
class SearchViewModel: ObservableObject {
    @Published var emperorResults: [EmperorSummary] = []
    @Published var eventResults: [EventSummary] = []
    @Published var personResults: [PersonSummary] = []
    @Published var isLoading = false
    
    private let apiService: APIServiceProtocol
    
    init(apiService: APIServiceProtocol = APIService.shared) {
        self.apiService = apiService
    }
    
    var hasResults: Bool {
        !emperorResults.isEmpty || !eventResults.isEmpty || !personResults.isEmpty
    }
    
    func search(keyword: String, category: SearchView.SearchCategory) async {
        isLoading = true
        clearResults()
        
        do {
            switch category {
            case .all:
                await searchAll(keyword: keyword)
            case .emperor:
                emperorResults = try await searchEmperors(keyword: keyword)
            case .event:
                eventResults = try await searchEvents(keyword: keyword)
            case .person:
                personResults = try await searchPersons(keyword: keyword)
            }
        } catch {
            // 处理错误
            print("搜索错误: \(error)")
        }
        
        isLoading = false
    }
    
    private func searchAll(keyword: String) async {
        async let emperors = searchEmperors(keyword: keyword)
        async let events = searchEvents(keyword: keyword)
        async let persons = searchPersons(keyword: keyword)
        
        do {
            let (e, ev, p) = try await (emperors, events, persons)
            emperorResults = e
            eventResults = ev
            personResults = p
        } catch {
            print("搜索失败: \(error)")
        }
    }
    
    private func searchEmperors(keyword: String) async throws -> [EmperorSummary] {
        let allEmperors = try await apiService.fetchEmperors(skip: 0, limit: 100)
        return allEmperors.filter { emperor in
            emperor.name.contains(keyword) ||
            (emperor.templeName?.contains(keyword) ?? false) ||
            (emperor.reignTitle?.contains(keyword) ?? false)
        }
    }
    
    private func searchEvents(keyword: String) async throws -> [EventSummary] {
        let allEvents = try await apiService.fetchEvents(skip: 0, limit: 100)
        return allEvents.filter { event in
            event.title.contains(keyword) ||
            event.eventType.contains(keyword) ||
            (event.location?.contains(keyword) ?? false)
        }
    }
    
    private func searchPersons(keyword: String) async throws -> [PersonSummary] {
        let allPersons = try await apiService.fetchPersons(skip: 0, limit: 100)
        return allPersons.filter { person in
            person.name.contains(keyword) ||
            person.personType.contains(keyword) ||
            (person.alias?.contains(keyword) ?? false)
        }
    }
    
    func clearResults() {
        emperorResults = []
        eventResults = []
        personResults = []
    }
}

// MARK: - Supporting Views

struct CategoryChip: View {
    let title: String
    let icon: String
    let isSelected: Bool
    
    var body: some View {
        Label(title, systemImage: icon)
            .font(.subheadline)
            .padding(.horizontal, 16)
            .padding(.vertical, 8)
            .background(isSelected ? Color.blue : Color(.secondarySystemBackground))
            .foregroundColor(isSelected ? .white : .primary)
            .cornerRadius(20)
    }
}

struct SearchResultRow: View {
    let icon: String
    let title: String
    let subtitle: String
    let iconColor: Color
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .foregroundColor(iconColor)
                .frame(width: 24)
            
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.body)
                    .fontWeight(.medium)
                
                Text(subtitle)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
    }
}

// MARK: - Preview

struct SearchView_Previews: PreviewProvider {
    static var previews: some View {
        SearchView()
    }
}
