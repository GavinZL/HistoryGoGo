//
//  HistoryGogoApp.swift
//  HistoryGogo
//
//  App入口
//

import SwiftUI

@main
struct HistoryGogoApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}

struct ContentView: View {
    var body: some View {
        TabView {
            TimelineView()
                .tabItem {
                    Label("时间轴", systemImage: "timeline.selection")
                }
            
            EmperorListView()
                .tabItem {
                    Label("皇帝", systemImage: "crown")
                }
            
            EventListView()
                .tabItem {
                    Label("事件", systemImage: "calendar")
                }
            
            PersonListView()
                .tabItem {
                    Label("人物", systemImage: "person.3")
                }
        }
    }
}

// MARK: - Event List View (Simplified)

struct EventListView: View {
    @StateObject private var viewModel = EventListViewModel()
    let dynastyId: String = "ming"
    
    var body: some View {
        NavigationView {
            List {
                ForEach(viewModel.events) { event in
                    EventRow(event: event)
                }
            }
            .navigationTitle("历史事件")
            .task {
                await viewModel.loadEvents(dynastyId: dynastyId)
            }
        }
    }
}

struct EventRow: View {
    let event: EventSummary
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(event.title)
                .font(.headline)
            
            HStack {
                Text(event.eventType)
                    .font(.caption)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.blue.opacity(0.2))
                    .cornerRadius(4)
                
                if let location = event.location {
                    Text(location)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding(.vertical, 4)
    }
}

// MARK: - Person List View (Simplified)

struct PersonListView: View {
    @StateObject private var viewModel = PersonListViewModel()
    let dynastyId: String = "ming"
    
    var body: some View {
        NavigationView {
            List {
                ForEach(viewModel.persons) { person in
                    PersonRow(person: person)
                }
            }
            .navigationTitle("历史人物")
            .task {
                await viewModel.loadPersons(dynastyId: dynastyId)
            }
        }
    }
}

struct PersonRow: View {
    let person: PersonSummary
    
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(person.name)
                    .font(.headline)
                
                Text(person.personType)
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                
                if let alias = person.alias {
                    Text("字号：\(alias)")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            
            Spacer()
        }
        .padding(.vertical, 4)
    }
}

// MARK: - Preview

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
