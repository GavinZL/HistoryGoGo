//
//  APIResponse.swift
//  HistoryGogo
//
//  API响应模型
//

import Foundation

/// 通用API响应包装
struct APIResponse<T: Codable>: Codable {
    let code: Int
    let message: String?
    let data: T?
    
    /// 是否成功
    var isSuccess: Bool {
        return code == 200
    }
}

/// 分页响应
struct PaginatedResponse<T: Codable>: Codable {
    let total: Int
    let page: Int
    let pageSize: Int
    let totalPages: Int
    let items: [T]
    
    enum CodingKeys: String, CodingKey {
        case total
        case page
        case pageSize = "page_size"
        case totalPages = "total_pages"
        case items
    }
    
    /// 是否有下一页
    var hasNextPage: Bool {
        return page < totalPages
    }
    
    /// 是否有上一页
    var hasPreviousPage: Bool {
        return page > 1
    }
}

/// API错误
enum APIError: Error, LocalizedError {
    case invalidURL
    case networkError(Error)
    case decodingError(Error)
    case serverError(Int, String)
    case noData
    case unknown
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "无效的URL"
        case .networkError(let error):
            return "网络错误: \(error.localizedDescription)"
        case .decodingError(let error):
            return "数据解析错误: \(error.localizedDescription)"
        case .serverError(let code, let message):
            return "服务器错误 (\(code)): \(message)"
        case .noData:
            return "没有数据"
        case .unknown:
            return "未知错误"
        }
    }
}
