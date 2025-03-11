//
//  Stopwatch.swift
//  waitfastApp
//
//  Created by Tiernan Jesrani on 3/10/25.
//
import Combine
import Foundation

class Stopwatch: ObservableObject, Identifiable {
    private var startTime: Date?
    private var accumulatedTime:TimeInterval = 0
    private var timer: Cancellable?
    
    @Published var errorMessage: String? = nil
    
    
    @Published var isRunning = false {
        didSet {
            if self.isRunning {
                self.start()
            } else {
                self.stop()
            }
        }
    }
    @Published private(set) var elapsedTime: TimeInterval = 0
    
    let id = UUID()
    
    private func start() -> Void {
        self.timer?.cancel()
        self.timer = Timer.publish(every: 0.5, on: .main, in: .common).autoconnect().sink { _ in
            self.elapsedTime = self.getElapsedTime()
        }
        self.startTime = Date()
    }
    
    private func stop() -> Void {
        self.timer?.cancel()
        self.timer = nil
        self.accumulatedTime = self.getElapsedTime()
        self.startTime = nil
    }
    
    func reset() -> Void {
        self.accumulatedTime = 0
        self.elapsedTime = 0
        self.startTime = nil
        self.isRunning = false
    }
    
    private func getElapsedTime() -> TimeInterval {
        return -(self.startTime?.timeIntervalSinceNow ??     0)+self.accumulatedTime
    }
    
    func postTime(pid: String) async -> WaitTimeResponse {
        errorMessage = nil
        
        guard var urlComponents = URLComponents(string: "http://127.0.0.1:5000/addtime/") else {
                errorMessage = "Invalid URL"
            return WaitTimeResponse()
            }
        
        urlComponents.queryItems = [
            URLQueryItem(name: "time", value: String(self.accumulatedTime)),
            URLQueryItem(name: "pid", value: pid)
            ]
            
            // Ensure URL is valid after adding query parameters
            guard let url = urlComponents.url else {
                errorMessage = "Failed to build URL with parameters"
                return WaitTimeResponse()
            }
        
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        do {
            let (data, response) = try await URLSession.shared.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse, (200...299).contains(httpResponse.statusCode) else {
                errorMessage = "Server error, please try again later."
                return WaitTimeResponse()
            }
            
            let decoder = JSONDecoder()
            
            // MARK: - Retrieve and process api data
            let waitStuff = try decoder.decode(WaitTimeResponse.self, from: data)
            print("Average Wait Time: \(waitStuff.averageWaitTime)")
            print("Sample Count: \(waitStuff.sampleCount)")
            return waitStuff
            
        } catch {
            errorMessage = "Failed to send data: \(error.localizedDescription)"
            print("Error while sending data", error)
        }
        return WaitTimeResponse()
    }
}

struct WaitTimeResponse: Codable {
    let averageWaitTime: String
    let sampleCount: Int
    
    init() {
            self.averageWaitTime = "Unknown"
            self.sampleCount = 0
    }
}

