//
//  EmperorListView.swift
//  HistoryGogo
//
//  皇帝列表视图 - SwiftUI
//

import SwiftUI

struct EmperorListView: View {
    
    @StateObject private var viewModel = EmperorListViewModel()
    let dynastyId: String = "ming"
    
    var body: some View {
        NavigationView {
            List {
                ForEach(viewModel.emperors) { emperor in
                    NavigationLink {
                        EmperorDetailView(emperorId: emperor.id)
                    } label: {
                        EmperorRow(emperor: emperor)
                    }
                }
                
                if viewModel.canLoadMore {
                    loadMoreButton
                }
            }
            .listStyle(.plain)
            .navigationTitle("明朝皇帝")
            .toolbar {
                refreshButton
            }
            .overlay {
                if viewModel.isLoading && viewModel.emperors.isEmpty {
                    ProgressView()
                }
            }
            .alert("错误", isPresented: $viewModel.showError) {
                Button("确定", role: .cancel) {}
            } message: {
                Text(viewModel.errorMessage ?? "未知错误")
            }
            .task {
                await viewModel.loadEmperors(dynastyId: dynastyId)
            }
        }
    }
    
    private var loadMoreButton: some View {
        HStack {
            Spacer()
            if viewModel.isLoading {
                ProgressView()
            } else {
                Button("加载更多") {
                    Task {
                        await viewModel.loadEmperors(dynastyId: dynastyId)
                    }
                }
            }
            Spacer()
        }
        .padding()
    }
    
    private var refreshButton: some ToolbarContent {
        ToolbarItem(placement: .navigationBarTrailing) {
            Button {
                Task {
                    await viewModel.refresh(dynastyId: dynastyId)
                }
            } label: {
                Image(systemName: "arrow.clockwise")
            }
        }
    }
}

struct EmperorRow: View {
    let emperor: EmperorSummary
    
    var body: some View {
        HStack(spacing: 12) {
            // 顺序数字
            Text("\(emperor.dynastyOrder)")
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(.white)
                .frame(width: 50, height: 50)
                .background(
                    Circle()
                        .fill(Color.red.opacity(0.8))
                )
            
            VStack(alignment: .leading, spacing: 4) {
                // 庙号和姓名
                Text(emperor.fullTitle)
                    .font(.headline)
                
                // 年号
                if let reignTitle = emperor.reignTitle {
                    Text("年号：\(reignTitle)")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
                
                // 在位时间
                HStack {
                    Image(systemName: "calendar")
                        .font(.caption)
                    Text(formatReign(emperor))
                        .font(.caption)
                }
                .foregroundColor(.secondary)
            }
            
            Spacer()
            
            Image(systemName: "chevron.right")
                .font(.caption)
                .foregroundColor(.gray)
        }
        .padding(.vertical, 8)
    }
    
    private func formatReign(_ emperor: EmperorSummary) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy年"
        
        let start = formatter.string(from: emperor.reignStart)
        if let end = emperor.reignEnd {
            let endStr = formatter.string(from: end)
            return "\(start) - \(endStr)"
        }
        return start
    }
}

// MARK: - Detail View

struct EmperorDetailView: View {
    
    @StateObject private var viewModel: EmperorDetailViewModel
    
    init(emperorId: String) {
        _viewModel = StateObject(wrappedValue: EmperorDetailViewModel(emperorId: emperorId))
    }
    
    var body: some View {
        ScrollView {
            if let emperor = viewModel.emperor {
                VStack(alignment: .leading, spacing: 20) {
                    // 头部信息
                    headerSection(emperor)
                    
                    Divider()
                    
                    // 基本信息
                    basicInfoSection(emperor)
                    
                    Divider()
                    
                    // 生平简介
                    if let biography = emperor.biography {
                        sectionView(title: "生平简介", content: biography)
                    }
                    
                    // 主要成就
                    if let achievements = emperor.achievements {
                        sectionView(title: "主要成就", content: achievements)
                    }
                    
                    // 统计信息
                    statisticsSection(emperor)
                }
                .padding()
            } else if viewModel.isLoading {
                ProgressView()
                    .padding()
            }
        }
        .navigationTitle("皇帝详情")
        .navigationBarTitleDisplayMode(.inline)
        .alert("错误", isPresented: $viewModel.showError) {
            Button("确定", role: .cancel) {}
        } message: {
            Text(viewModel.errorMessage ?? "未知错误")
        }
        .task {
            await viewModel.loadDetail()
        }
    }
    
    private func headerSection(_ emperor: EmperorDetail) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                VStack(alignment: .leading) {
                    Text(emperor.name)
                        .font(.largeTitle)
                        .fontWeight(.bold)
                    
                    if let temple = emperor.templeName {
                        Text(temple)
                            .font(.title2)
                            .foregroundColor(.secondary)
                    }
                }
                
                Spacer()
                
                Image(systemName: "crown.fill")
                    .font(.system(size: 40))
                    .foregroundColor(.yellow)
            }
            
            if let reignTitle = emperor.reignTitle {
                Text("年号：\(reignTitle)")
                    .font(.headline)
            }
        }
    }
    
    private func basicInfoSection(_ emperor: EmperorDetail) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("基本信息")
                .font(.headline)
            
            Grid(alignment: .leading, horizontalSpacing: 20, verticalSpacing: 8) {
                GridRow {
                    Text("在位时间")
                        .foregroundColor(.secondary)
                    Text(viewModel.reignPeriodDescription)
                }
                
                if let duration = emperor.reignDuration {
                    GridRow {
                        Text("在位年数")
                            .foregroundColor(.secondary)
                        Text("\(duration)年")
                    }
                }
                
                if let lifespan = viewModel.lifespanYears {
                    GridRow {
                        Text("享年")
                            .foregroundColor(.secondary)
                        Text("\(lifespan)岁")
                    }
                }
            }
        }
    }
    
    private func sectionView(title: String, content: String) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.headline)
            
            Text(content)
                .font(.body)
                .foregroundColor(.primary)
        }
    }
    
    private func statisticsSection(_ emperor: EmperorDetail) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("相关统计")
                .font(.headline)
            
            HStack(spacing: 30) {
                StatCard(title: "相关事件", value: "\(emperor.eventCount ?? 0)")
                StatCard(title: "相关人物", value: "\(emperor.personCount ?? 0)")
            }
        }
    }
}

struct StatCard: View {
    let title: String
    let value: String
    
    var body: some View {
        VStack {
            Text(value)
                .font(.title)
                .fontWeight(.bold)
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(Color(.secondarySystemBackground))
        .cornerRadius(10)
    }
}

// MARK: - Previews

struct EmperorListView_Previews: PreviewProvider {
    static var previews: some View {
        EmperorListView()
    }
}
