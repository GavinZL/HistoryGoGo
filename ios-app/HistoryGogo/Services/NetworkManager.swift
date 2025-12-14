//
//  NetworkManager.swift
//  HistoryGogo
//
//  网络管理器 - 处理所有HTTP请求
//

import Foundation

/// 网络管理器（单例模式）
class NetworkManager {
    
    // MARK: - Properties
    
    static let shared = NetworkManager()
    
    private let session: URLSession
    private let decoder: JSONDecoder
    
    /// API基础URL
    private let baseURL = "http://localhost:8000/api/v1"
    
    // MARK: - Initialization
    
    private init() {
        let configuration = URLSessionConfiguration.default
        configuration.timeoutIntervalForRequest = 30
        configuration.timeoutIntervalForResource = 60
        self.session = URLSession(configuration: configuration)
        
        self.decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .custom { decoder in
            let container = try decoder.singleValueContainer()
            let dateString = try container.decode(String.self)
            
            // 尝试多种日期格式
            let formatters = [
                "yyyy-MM-dd'T'HH:mm:ss.SSSZ",
                "yyyy-MM-dd'T'HH:mm:ss",
                "yyyy-MM-dd HH:mm:ss",
                "yyyy-MM-dd"
            ]
            
            for format in formatters {
                let formatter = DateFormatter()
                formatter.dateFormat = format
                formatter.locale = Locale(identifier: "en_US_POSIX")
                formatter.timeZone = TimeZone(secondsFromGMT: 0)
                
                if let date = formatter.date(from: dateString) {
                    return date
                }
            }
            
            throw DecodingError.dataCorruptedError(
                in: container,
                debugDescription: "无法解析日期: \(dateString)"
            )
        }
    }
    
    // MARK: - Public Methods
    
    /// 通用GET请求
    func get<T: Decodable>(
        _ endpoint: String,
        parameters: [String: String]? = nil
    ) async throws -> T {
        let url = try buildURL(endpoint: endpoint, parameters: parameters)
        let request = URLRequest(url: url)
        
        return try await performRequest(request)
    }
    
    /// 通用POST请求
    func post<T: Decodable, Body: Encodable>(
        _ endpoint: String,
        body: Body
    ) async throws -> T {
        let url = try buildURL(endpoint: endpoint)
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let encoder = JSONEncoder()
        request.httpBody = try encoder.encode(body)
        
        return try await performRequest(request)
    }
    
    // MARK: - Private Methods
    
    /// 构建URL
    private func buildURL(
        endpoint: String,
        parameters: [String: String]? = nil
    ) throws -> URL {
        guard var components = URLComponents(string: baseURL + endpoint) else {
            throw APIError.invalidURL
        }
        
        if let parameters = parameters, !parameters.isEmpty {
            components.queryItems = parameters.map {
                URLQueryItem(name: $0.key, value: $0.value)
            }
        }
        
        guard let url = components.url else {
            throw APIError.invalidURL
        }
        
        return url
    }
    
    /// 执行请求
    private func performRequest<T: Decodable>(_ request: URLRequest) async throws -> T {
        do {
            let (data, response) = try await session.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                throw APIError.unknown
            }
            
            // 检查HTTP状态码
            guard (200...299).contains(httpResponse.statusCode) else {
                // 尝试解析错误信息
                if let errorResponse = try? decoder.decode(APIResponse<String>.self, from: data) {
                    throw APIError.serverError(httpResponse.statusCode, errorResponse.message ?? "未知错误")
                }
                throw APIError.serverError(httpResponse.statusCode, "服务器错误")
            }
            
            // 解码数据
            do {
                let decoded = try decoder.decode(T.self, from: data)
                return decoded
            } catch {
                throw APIError.decodingError(error)
            }
            
        } catch let error as APIError {
            throw error
        } catch {
            throw APIError.networkError(error)
        }
    }
}

// MARK: - URL Configuration

extension NetworkManager {
    /// 更新API基础URL（用于配置不同环境）
    func updateBaseURL(_ newBaseURL: String) {
        // 注意：这里简化实现，实际应该使用配置文件
        // baseURL = newBaseURL
    }
}
