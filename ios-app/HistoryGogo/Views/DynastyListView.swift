//
//  DynastyListView.swift
//  HistoryGogo
//
//  朝代选择视图 - SwiftUI
//

import SwiftUI

struct DynastyListView: View {
    
    @StateObject private var viewModel = DynastyListViewModel()
    @State private var selectedDynasty: Dynasty?
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            ZStack {
                if viewModel.isLoading {
                    LoadingView(message: "加载朝代列表...")
                } else if !viewModel.dynasties.isEmpty {
                    dynastyList
                } else {
                    EmptyStateView(
                        icon: "building.columns",
                        title: "暂无朝代数据"
                    )
                }
            }
            .navigationTitle("选择朝代")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                refreshButton
            }
            .alert("错误", isPresented: $viewModel.showError) {
                Button("确定", role: .cancel) {}
            } message: {
                Text(viewModel.errorMessage ?? "未知错误")
            }
            .task {
                await viewModel.loadDynasties()
            }
        }
    }
    
    // MARK: - View Components
    
    private var dynastyList: some View {
        ScrollView {
            LazyVStack(spacing: 16) {
                ForEach(viewModel.dynasties) { dynasty in
                    DynastyCard(dynasty: dynasty)
                        .onTapGesture {
                            selectedDynasty = dynasty
                        }
                }
            }
            .padding()
        }
        .refreshable {
            await viewModel.refresh()
        }
    }
    
    private var refreshButton: some ToolbarContent {
        ToolbarItem(placement: .navigationBarTrailing) {
            Button {
                Task {
                    await viewModel.refresh()
                }
            } label: {
                Image(systemName: "arrow.clockwise")
            }
        }
    }
}

// MARK: - Dynasty List ViewModel

@MainActor
class DynastyListViewModel: ObservableObject {
    @Published var dynasties: [Dynasty] = []
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    @Published var showError: Bool = false
    
    private let apiService: APIServiceProtocol
    
    init(apiService: APIServiceProtocol = APIService.shared) {
        self.apiService = apiService
    }
    
    func loadDynasties() async {
        isLoading = true
        errorMessage = nil
        showError = false
        
        do {
            dynasties = try await apiService.fetchDynasties()
        } catch let error as APIError {
            errorMessage = error.localizedDescription
            showError = true
        } catch {
            errorMessage = "未知错误"
            showError = true
        }
        
        isLoading = false
    }
    
    func refresh() async {
        await loadDynasties()
    }
}

// MARK: - Dynasty Card

struct DynastyCard: View {
    let dynasty: Dynasty
    
    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // 头部 - 朝代名称和标识
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(dynasty.name)
                        .font(.title)
                        .fontWeight(.bold)
                        .foregroundColor(.white)
                    
                    Text(dynasty.timeSpan)
                        .font(.subheadline)
                        .foregroundColor(.white.opacity(0.9))
                }
                
                Spacer()
                
                Image(systemName: "building.columns.fill")
                    .font(.system(size: 40))
                    .foregroundColor(.white.opacity(0.3))
            }
            .padding()
            .background(
                LinearGradient(
                    colors: dynastyGradient,
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
            )
            
            // 内容区域
            VStack(alignment: .leading, spacing: 12) {
                // 基本信息
                if let founder = dynasty.founder {
                    InfoItem(icon: "crown.fill", label: "开国皇帝", value: founder)
                }
                
                if let capital = dynasty.capital {
                    InfoItem(icon: "mappin.circle.fill", label: "国都", value: capital)
                }
                
                InfoItem(
                    icon: "calendar.circle.fill",
                    label: "持续时间",
                    value: "\(dynasty.duration)年"
                )
                
                // 简介
                if let description = dynasty.description {
                    Divider()
                    
                    Text(description)
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                        .lineLimit(3)
                }
            }
            .padding()
            .background(Color(.systemBackground))
        }
        .clipShape(RoundedRectangle(cornerRadius: 16))
        .shadow(color: Color.black.opacity(0.1), radius: 8, x: 0, y: 4)
        .overlay(
            RoundedRectangle(cornerRadius: 16)
                .stroke(Color.gray.opacity(0.2), lineWidth: 1)
        )
    }
    
    // 根据朝代名称返回不同的渐变色
    private var dynastyGradient: [Color] {
        switch dynasty.name {
        case "明朝":
            return [Color.palaceRed, Color.palaceRed.opacity(0.8)]
        case "清朝":
            return [Color.gold, Color.gold.opacity(0.8)]
        case "唐朝":
            return [Color.orange, Color.red]
        case "宋朝":
            return [Color.blue, Color.purple]
        default:
            return [Color.gray, Color.gray.opacity(0.7)]
        }
    }
}

struct InfoItem: View {
    let icon: String
    let label: String
    let value: String
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .foregroundColor(.blue)
                .frame(width: 24)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(label)
                    .font(.caption)
                    .foregroundColor(.secondary)
                Text(value)
                    .font(.body)
                    .fontWeight(.medium)
            }
            
            Spacer()
        }
    }
}

// MARK: - Preview

struct DynastyListView_Previews: PreviewProvider {
    static var previews: some View {
        DynastyListView()
    }
}
