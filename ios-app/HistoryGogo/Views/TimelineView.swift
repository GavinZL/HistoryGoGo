//
//  TimelineView.swift
//  HistoryGogo
//
//  时间轴主视图 - SwiftUI
//

import SwiftUI

struct TimelineView: View {
    
    @StateObject private var viewModel = TimelineViewModel()
    @State private var selectedYear: Int?
    
    let dynastyId: String = "ming" // 默认明朝
    
    var body: some View {
        NavigationView {
            ZStack {
                if viewModel.isLoading {
                    loadingView
                } else if let timeline = viewModel.timelineData {
                    timelineContent(timeline)
                } else {
                    emptyView
                }
            }
            .navigationTitle("历史时间轴")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    refreshButton
                }
            }
            .alert("错误", isPresented: $viewModel.showError) {
                Button("确定", role: .cancel) {}
            } message: {
                Text(viewModel.errorMessage ?? "未知错误")
            }
            .task {
                await viewModel.loadTimeline(dynastyId: dynastyId)
            }
        }
    }
    
    // MARK: - View Components
    
    private func timelineContent(_ timeline: TimelineResponse) -> some View {
        ScrollView {
            LazyVStack(spacing: 0) {
                // 朝代信息头部
                dynastyHeader
                
                // 时间轴列表
                ForEach(timeline.timeline) { item in
                    TimelineItemRow(item: item)
                        .onTapGesture {
                            selectedYear = item.year
                        }
                }
            }
        }
        .refreshable {
            await viewModel.refresh(dynastyId: dynastyId)
        }
    }
    
    private var dynastyHeader: some View {
        VStack(alignment: .leading, spacing: 8) {
            if let dynasty = viewModel.dynasty {
                Text(dynasty.name)
                    .font(.largeTitle)
                    .fontWeight(.bold)
                
                Text(dynasty.timeSpan)
                    .font(.headline)
                    .foregroundColor(.secondary)
                
                HStack(spacing: 20) {
                    InfoLabel(title: "皇帝", value: "\(viewModel.totalEmperors)")
                    InfoLabel(title: "事件", value: "\(viewModel.totalEvents)")
                }
                .padding(.top, 4)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color(.systemBackground))
    }
    
    private var loadingView: some View {
        VStack {
            ProgressView()
            Text("加载中...")
                .foregroundColor(.secondary)
                .padding(.top)
        }
    }
    
    private var emptyView: some View {
        VStack {
            Image(systemName: "calendar.badge.exclamationmark")
                .font(.system(size: 60))
                .foregroundColor(.gray)
            Text("暂无数据")
                .font(.headline)
                .foregroundColor(.secondary)
                .padding(.top)
        }
    }
    
    private var refreshButton: some View {
        Button {
            Task {
                await viewModel.refresh(dynastyId: dynastyId)
            }
        } label: {
            Image(systemName: "arrow.clockwise")
        }
    }
}

// MARK: - Supporting Views

struct TimelineItemRow: View {
    let item: TimelineItem
    
    var body: some View {
        HStack(alignment: .top, spacing: 16) {
            // 年份指示器
            VStack {
                Text("\(item.year)")
                    .font(.headline)
                    .foregroundColor(.white)
                    .frame(width: 60, height: 60)
                    .background(
                        Circle()
                            .fill(item.hasEvents ? Color.red : Color.gray.opacity(0.5))
                    )
                
                if item.hasEvents {
                    Rectangle()
                        .fill(Color.red.opacity(0.3))
                        .frame(width: 2)
                }
            }
            
            // 内容区域
            VStack(alignment: .leading, spacing: 8) {
                // 皇帝信息
                if let emperor = item.emperor {
                    EmperorBadge(emperor: emperor)
                }
                
                // 事件列表
                if !item.events.isEmpty {
                    VStack(alignment: .leading, spacing: 4) {
                        ForEach(item.events) { event in
                            EventBadge(event: event)
                        }
                    }
                }
            }
            .padding(.vertical, 8)
            
            Spacer()
        }
        .padding(.horizontal)
        .background(Color(.systemBackground))
    }
}

struct EmperorBadge: View {
    let emperor: TimelineEmperor
    
    var body: some View {
        HStack {
            Image(systemName: "crown.fill")
                .foregroundColor(.yellow)
            Text(emperor.displayName)
                .font(.subheadline)
                .fontWeight(.medium)
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 6)
        .background(Color.blue.opacity(0.1))
        .cornerRadius(8)
    }
}

struct EventBadge: View {
    let event: TimelineEvent
    
    var body: some View {
        HStack {
            Circle()
                .fill(eventColor)
                .frame(width: 8, height: 8)
            
            Text(event.title)
                .font(.footnote)
            
            if let location = event.location {
                Text("· \(location)")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 4)
        .background(Color(.secondarySystemBackground))
        .cornerRadius(6)
    }
    
    private var eventColor: Color {
        switch event.eventType {
        case "政治": return .blue
        case "军事": return .red
        case "文化": return .purple
        case "经济": return .green
        case "外交": return .orange
        default: return .gray
        }
    }
}

struct InfoLabel: View {
    let title: String
    let value: String
    
    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
            Text(value)
                .font(.title3)
                .fontWeight(.semibold)
        }
    }
}

// MARK: - Preview

struct TimelineView_Previews: PreviewProvider {
    static var previews: some View {
        TimelineView()
    }
}
