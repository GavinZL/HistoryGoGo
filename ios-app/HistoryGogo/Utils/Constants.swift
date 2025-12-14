//
//  Constants.swift
//  HistoryGogo
//
//  常量定义
//

import Foundation

/// 应用常量
enum Constants {
    
    // MARK: - API
    
    enum API {
        /// 生产环境API地址
        static let productionBaseURL = "http://localhost:8000/api/v1"
        
        /// 开发环境API地址
        static let developmentBaseURL = "http://localhost:8000/api/v1"
        
        /// 当前环境
        static var current: String {
            #if DEBUG
            return developmentBaseURL
            #else
            return productionBaseURL
            #endif
        }
        
        /// 请求超时时间
        static let timeout: TimeInterval = 30
    }
    
    // MARK: - UI
    
    enum UI {
        /// 默认分页大小
        static let defaultPageSize = 20
        
        /// 最大分页大小
        static let maxPageSize = 100
        
        /// 默认圆角半径
        static let cornerRadius: CGFloat = 12
        
        /// 默认间距
        static let spacing: CGFloat = 16
        
        /// 卡片阴影半径
        static let shadowRadius: CGFloat = 4
    }
    
    // MARK: - Cache
    
    enum Cache {
        /// 朝代列表缓存时间（秒）
        static let dynastyTTL: TimeInterval = 60 * 60 * 24 * 7 // 7天
        
        /// 皇帝列表缓存时间
        static let emperorTTL: TimeInterval = 60 * 60 * 24 // 1天
        
        /// 事件列表缓存时间
        static let eventTTL: TimeInterval = 60 * 60 * 24 // 1天
        
        /// 人物列表缓存时间
        static let personTTL: TimeInterval = 60 * 60 * 24 // 1天
        
        /// 图片缓存时间
        static let imageTTL: TimeInterval = 60 * 60 * 24 * 30 // 30天
    }
    
    // MARK: - Dynasty
    
    enum Dynasty {
        /// 默认朝代ID（明朝）
        static let defaultId = "ming"
        
        /// 默认朝代名称
        static let defaultName = "明朝"
    }
    
    // MARK: - Error Messages
    
    enum ErrorMessage {
        static let networkError = "网络连接失败，请检查网络设置"
        static let serverError = "服务器错误，请稍后重试"
        static let dataError = "数据加载失败"
        static let noData = "暂无数据"
        static let unknown = "未知错误"
    }
}
