//
//  PersonDetailView.swift
//  HistoryGogo
//
//  人物详情视图 - SwiftUI
//

import SwiftUI

struct PersonDetailView: View {
    
    @StateObject private var viewModel: PersonDetailViewModel
    @State private var selectedTab: DetailTab = .biography
    
    init(personId: String) {
        _viewModel = StateObject(wrappedValue: PersonDetailViewModel(personId: personId))
    }
    
    enum DetailTab: String, CaseIterable {
        case biography = "生平"
        case works = "作品"
        case achievements = "成就"
        
        var icon: String {
            switch self {
            case .biography: return "person.text.rectangle"
            case .works: return "book.closed"
            case .achievements: return "star.fill"
            }
        }
    }
    
    var body: some View {
        ScrollView {
            if let person = viewModel.person {
                VStack(alignment: .leading, spacing: 20) {
                    // 头部个人信息卡片
                    personHeaderCard(person)
                    
                    // 基本信息
                    basicInfoSection(person)
                    
                    Divider()
                    
                    // Tab切换
                    tabSelector
                    
                    // Tab内容
                    tabContent(person)
                    
                    // 统计信息
                    statisticsSection(person)
                }
                .padding()
            } else if viewModel.isLoading {
                LoadingView(message: "加载人物详情...")
            } else {
                EmptyStateView(
                    icon: "person.crop.circle.badge.exclamationmark",
                    title: "加载失败",
                    message: "无法加载人物详情"
                )
            }
        }
        .navigationTitle("人物详情")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            refreshButton
        }
        .alert("错误", isPresented: $viewModel.showError) {
            Button("确定", role: .cancel) {}
        } message: {
            Text(viewModel.errorMessage ?? "未知错误")
        }
        .task {
            await viewModel.loadDetail()
        }
    }
    
    // MARK: - View Components
    
    private func personHeaderCard(_ person: PersonDetail) -> some View {
        VStack(spacing: 16) {
            // 头像和基本信息
            HStack(alignment: .top, spacing: 16) {
                // 头像占位符
                ZStack {
                    Circle()
                        .fill(
                            LinearGradient(
                                colors: [Color.blue, Color.purple],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .frame(width: 80, height: 80)
                    
                    Image(systemName: personTypeIcon(person.personType))
                        .font(.system(size: 36))
                        .foregroundColor(.white)
                }
                
                VStack(alignment: .leading, spacing: 8) {
                    // 姓名
                    Text(person.name)
                        .font(.title)
                        .fontWeight(.bold)
                    
                    // 别名
                    if let alias = person.alias, !alias.isEmpty {
                        Text("字号：\(alias)")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                    
                    // 人物类型标签
                    HStack {
                        Label(person.personType, systemImage: personTypeIcon(person.personType))
                            .font(.caption)
                            .padding(.horizontal, 10)
                            .padding(.vertical, 5)
                            .background(Color.blue.opacity(0.2))
                            .foregroundColor(.blue)
                            .cornerRadius(6)
                        
                        if let position = person.position {
                            Text(position)
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                }
                
                Spacer()
            }
            
            // 生卒年信息
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("生卒年")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text(viewModel.lifespanDescription)
                        .font(.headline)
                }
                
                Spacer()
                
                if let lifespan = viewModel.lifespanYears {
                    VStack(alignment: .trailing, spacing: 4) {
                        Text("享年")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Text("\(lifespan)岁")
                            .font(.headline)
                            .foregroundColor(.blue)
                    }
                }
            }
            .padding()
            .background(Color(.secondarySystemBackground))
            .cornerRadius(10)
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color(.systemBackground))
                .shadow(color: Color.black.opacity(0.1), radius: 8, x: 0, y: 2)
        )
    }
    
    private func basicInfoSection(_ person: PersonDetail) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("基本信息")
                .font(.headline)
            
            VStack(spacing: 10) {
                if let emperors = person.relatedEmperors, !emperors.isEmpty {
                    InfoRow(
                        icon: "crown.fill",
                        label: "侍奉皇帝",
                        value: "\(emperors.count)位"
                    )
                }
                
                if let eventCount = person.eventCount {
                    InfoRow(
                        icon: "calendar",
                        label: "参与事件",
                        value: "\(eventCount)个"
                    )
                }
                
                if let workCount = person.workCount {
                    InfoRow(
                        icon: "book.closed",
                        label: "作品数量",
                        value: "\(workCount)部"
                    )
                }
            }
            .padding()
            .background(Color(.secondarySystemBackground))
            .cornerRadius(12)
        }
    }
    
    private var tabSelector: some View {
        HStack(spacing: 0) {
            ForEach(DetailTab.allCases, id: \.self) { tab in
                Button {
                    withAnimation(.easeInOut(duration: 0.2)) {
                        selectedTab = tab
                    }
                } label: {
                    VStack(spacing: 6) {
                        Image(systemName: tab.icon)
                            .font(.title3)
                        Text(tab.rawValue)
                            .font(.subheadline)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 12)
                    .foregroundColor(selectedTab == tab ? .blue : .gray)
                    .background(
                        selectedTab == tab ?
                        Color.blue.opacity(0.1) : Color.clear
                    )
                }
            }
        }
        .background(Color(.secondarySystemBackground))
        .cornerRadius(10)
    }
    
    @ViewBuilder
    private func tabContent(_ person: PersonDetail) -> some View {
        switch selectedTab {
        case .biography:
            biographyContent(person)
        case .works:
            worksContent(person)
        case .achievements:
            achievementsContent(person)
        }
    }
    
    private func biographyContent(_ person: PersonDetail) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            if let biography = person.biography {
                Text(biography)
                    .font(.body)
                    .lineSpacing(6)
                    .foregroundColor(.primary)
            } else {
                EmptyStateView(
                    icon: "doc.text",
                    title: "暂无生平资料",
                    message: nil
                )
                .frame(height: 200)
            }
            
            // 风格特点（适用于文学家、艺术家）
            if let style = person.style {
                VStack(alignment: .leading, spacing: 8) {
                    Text("风格特点")
                        .font(.headline)
                    
                    Text(style)
                        .font(.body)
                        .lineSpacing(4)
                }
                .padding()
                .background(Color.purple.opacity(0.1))
                .cornerRadius(10)
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.05), radius: 4)
    }
    
    private func worksContent(_ person: PersonDetail) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            if let works = person.works, !works.isEmpty {
                ForEach(works, id: \.self) { work in
                    HStack {
                        Image(systemName: "book.fill")
                            .foregroundColor(.blue)
                        Text(work)
                            .font(.body)
                        Spacer()
                    }
                    .padding()
                    .background(Color(.secondarySystemBackground))
                    .cornerRadius(8)
                }
            } else {
                EmptyStateView(
                    icon: "book.closed",
                    title: "暂无作品记录",
                    message: nil
                )
                .frame(height: 200)
            }
        }
    }
    
    private func achievementsContent(_ person: PersonDetail) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            if let achievements = person.achievements {
                VStack(alignment: .leading, spacing: 8) {
                    HStack {
                        Image(systemName: "star.circle.fill")
                            .foregroundColor(.gold)
                            .font(.title2)
                        Text("主要成就")
                            .font(.headline)
                    }
                    
                    Text(achievements)
                        .font(.body)
                        .lineSpacing(6)
                }
                .padding()
                .background(
                    LinearGradient(
                        colors: [Color.gold.opacity(0.1), Color.gold.opacity(0.05)],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
                .cornerRadius(12)
                .overlay(
                    RoundedRectangle(cornerRadius: 12)
                        .stroke(Color.gold.opacity(0.3), lineWidth: 1)
                )
            } else {
                EmptyStateView(
                    icon: "star",
                    title: "暂无成就记录",
                    message: nil
                )
                .frame(height: 200)
            }
        }
    }
    
    private func statisticsSection(_ person: PersonDetail) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("数据统计")
                .font(.headline)
            
            HStack(spacing: 15) {
                StatisticCard(
                    icon: "calendar",
                    title: "参与事件",
                    value: "\(person.eventCount ?? 0)",
                    color: .blue
                )
                
                StatisticCard(
                    icon: "book.closed",
                    title: "创作作品",
                    value: "\(viewModel.worksCount)",
                    color: .purple
                )
                
                if let emperors = person.relatedEmperors {
                    StatisticCard(
                        icon: "crown",
                        title: "侍奉朝代",
                        value: "\(emperors.count)",
                        color: .orange
                    )
                }
            }
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
    
    // MARK: - Helper Methods
    
    private func personTypeIcon(_ type: String) -> String {
        switch type {
        case "皇帝": return "crown.fill"
        case "文臣": return "book.fill"
        case "武将": return "shield.fill"
        case "文学家": return "pencil"
        case "艺术家": return "paintbrush.fill"
        case "思想家": return "brain"
        case "科学家": return "atom"
        case "宗室": return "person.2.fill"
        case "僧侣": return "leaf.fill"
        case "商人": return "cart.fill"
        default: return "person.fill"
        }
    }
}

// MARK: - Supporting Views

struct StatisticCard: View {
    let icon: String
    let title: String
    let value: String
    let color: Color
    
    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(color)
            
            Text(value)
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(.primary)
            
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(color.opacity(0.1))
        .cornerRadius(12)
    }
}

// MARK: - Preview

struct PersonDetailView_Previews: PreviewProvider {
    static var previews: some View {
        NavigationView {
            PersonDetailView(personId: "person_001")
        }
    }
}
