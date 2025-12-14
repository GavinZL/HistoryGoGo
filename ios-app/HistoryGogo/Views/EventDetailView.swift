//
//  EventDetailView.swift
//  HistoryGogo
//
//  事件详情视图 - SwiftUI
//

import SwiftUI

struct EventDetailView: View {
    
    @StateObject private var viewModel: EventDetailViewModel
    
    init(eventId: String) {
        _viewModel = StateObject(wrappedValue: EventDetailViewModel(eventId: eventId))
    }
    
    var body: some View {
        ScrollView {
            if let event = viewModel.event {
                VStack(alignment: .leading, spacing: 20) {
                    // 头部信息
                    headerSection(event)
                    
                    Divider()
                    
                    // 基本信息卡片
                    basicInfoCard(event)
                    
                    Divider()
                    
                    // 事件描述
                    if let description = event.description {
                        contentSection(title: "事件描述", content: description)
                    }
                    
                    // 参与人物
                    if let participants = event.participants {
                        contentSection(title: "参与人物", content: participants)
                    }
                    
                    // 伤亡情况
                    if let casualties = event.casualties {
                        contentSection(title: "伤亡情况", content: casualties, color: .red)
                    }
                    
                    // 事件结果
                    if let result = event.result {
                        contentSection(title: "事件结果", content: result, color: .blue)
                    }
                    
                    // 历史意义
                    if let significance = event.significance {
                        significanceSection(significance)
                    }
                    
                    // 相关人物列表
                    if let persons = event.relatedPersons, !persons.isEmpty {
                        relatedPersonsSection(persons)
                    }
                }
                .padding()
            } else if viewModel.isLoading {
                LoadingView(message: "加载事件详情...")
            } else {
                EmptyStateView(
                    icon: "calendar.badge.exclamationmark",
                    title: "加载失败",
                    message: "无法加载事件详情"
                )
            }
        }
        .navigationTitle("事件详情")
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
    
    private func headerSection(_ event: EventDetail) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            // 事件标题
            Text(event.title)
                .font(.largeTitle)
                .fontWeight(.bold)
                .foregroundColor(.primary)
            
            // 事件类型和时间
            HStack {
                // 类型标签
                Label(event.eventType, systemImage: eventTypeIcon(event.eventType))
                    .font(.subheadline)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 6)
                    .background(eventTypeColor(event.eventType).opacity(0.2))
                    .foregroundColor(eventTypeColor(event.eventType))
                    .cornerRadius(8)
                
                Spacer()
            }
            
            // 时间描述
            HStack(spacing: 8) {
                Image(systemName: "calendar")
                    .foregroundColor(.secondary)
                Text(viewModel.timeDescription)
                    .font(.headline)
                    .foregroundColor(.secondary)
            }
            
            // 地点
            if let location = event.location {
                HStack(spacing: 8) {
                    Image(systemName: "location.fill")
                        .foregroundColor(.secondary)
                    Text(location)
                        .font(.headline)
                        .foregroundColor(.secondary)
                }
            }
        }
    }
    
    private func basicInfoCard(_ event: EventDetail) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("基本信息")
                .font(.headline)
                .foregroundColor(.primary)
            
            VStack(spacing: 8) {
                if let duration = viewModel.durationDays {
                    InfoRow(
                        icon: "clock.fill",
                        label: "持续时间",
                        value: "\(duration)天"
                    )
                }
                
                if let personCount = event.personCount {
                    InfoRow(
                        icon: "person.3.fill",
                        label: "相关人物",
                        value: "\(personCount)人"
                    )
                }
                
                InfoRow(
                    icon: "doc.text.fill",
                    label: "数据来源",
                    value: event.dataSource ?? "未知"
                )
            }
            .padding()
            .background(Color(.secondarySystemBackground))
            .cornerRadius(12)
        }
    }
    
    private func contentSection(
        title: String,
        content: String,
        color: Color = .primary
    ) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.headline)
                .foregroundColor(.primary)
            
            Text(content)
                .font(.body)
                .foregroundColor(color)
                .lineSpacing(4)
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.05), radius: 4, x: 0, y: 2)
    }
    
    private func significanceSection(_ significance: String) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: "star.fill")
                    .foregroundColor(.gold)
                Text("历史意义")
                    .font(.headline)
            }
            
            Text(significance)
                .font(.body)
                .foregroundColor(.primary)
                .lineSpacing(4)
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
    }
    
    private func relatedPersonsSection(_ personIds: [String]) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("相关人物")
                .font(.headline)
            
            VStack(spacing: 8) {
                ForEach(personIds.prefix(5), id: \.self) { personId in
                    HStack {
                        Image(systemName: "person.circle.fill")
                            .foregroundColor(.blue)
                        Text(personId)
                            .font(.subheadline)
                        Spacer()
                        Image(systemName: "chevron.right")
                            .font(.caption)
                            .foregroundColor(.gray)
                    }
                    .padding()
                    .background(Color(.secondarySystemBackground))
                    .cornerRadius(8)
                }
                
                if personIds.count > 5 {
                    Text("还有 \(personIds.count - 5) 位相关人物...")
                        .font(.caption)
                        .foregroundColor(.secondary)
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
    
    private func eventTypeIcon(_ type: String) -> String {
        switch type {
        case "政治": return "building.columns.fill"
        case "军事": return "shield.fill"
        case "文化": return "book.fill"
        case "经济": return "chart.line.uptrend.xyaxis"
        case "外交": return "globe.asia.australia.fill"
        case "自然灾害": return "cloud.bolt.rain.fill"
        case "科技": return "atom"
        default: return "calendar"
        }
    }
    
    private func eventTypeColor(_ type: String) -> Color {
        switch type {
        case "政治": return .blue
        case "军事": return .red
        case "文化": return .purple
        case "经济": return .green
        case "外交": return .orange
        case "自然灾害": return .brown
        case "科技": return .cyan
        default: return .gray
        }
    }
}

// MARK: - Supporting Views

struct InfoRow: View {
    let icon: String
    let label: String
    let value: String
    
    var body: some View {
        HStack {
            Image(systemName: icon)
                .foregroundColor(.blue)
                .frame(width: 24)
            
            Text(label)
                .font(.subheadline)
                .foregroundColor(.secondary)
            
            Spacer()
            
            Text(value)
                .font(.subheadline)
                .fontWeight(.medium)
                .foregroundColor(.primary)
        }
    }
}

// MARK: - Preview

struct EventDetailView_Previews: PreviewProvider {
    static var previews: some View {
        NavigationView {
            EventDetailView(eventId: "event_001")
        }
    }
}
