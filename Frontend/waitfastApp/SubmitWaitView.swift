//
//  SubmitWaitView.swift
//  waitfastApp
//
//  Created by Adam Simpson on 2/12/25.
//

import Foundation
import SwiftUI

struct SubmitWaitView: View {
    @State private var waitTime = ""
    
    // State for showing alerts
    @State private var showErrorAlert = false
    @State private var showAlert = false
    @State private var showSuccessAlert = false
    @State private var errorMessage = ""
    
    // If SubmitWaitView is presented as a sheet or popoover, or some other kind of modal in SwiftUI, returns to normal state
    @Environment(\.dismiss) private var dismiss
    
    var pid: String
    @Binding var place: Place
    
    var body: some View {
        VStack(spacing: 16) {
            Text("Submit a Wait Time")
                .font(.title2)
                .padding(.top)
            TextField("Enter wait time in minutes", text: $waitTime)
                .textFieldStyle(RoundedBorderTextFieldStyle())
                .keyboardType(.decimalPad)
                .padding(.horizontal)
            Button("Submit") {
                // 1) Validate input and make sure that it's a positive number
                guard let timeInMinutes = Double(waitTime), timeInMinutes > 0 else {
                    errorMessage = "Please enter a valid positive number"
                    showErrorAlert = true
                    return
                }
                // 2) Convert minutes to seconds
                let timeInSeconds = timeInMinutes * 60
                
                // 3) Post this time to the same endpoint stopwatch uses
                Task {
                    let response = await postManualTime(pid: pid, time: timeInSeconds)
                    
                    // 4) Check if server gave valid response
                    if response.averageWaitTime == "Unknown" && response.sampleCount == 0 {
                        errorMessage = "Server error or invalid response"
                        showErrorAlert = true
                    } else {
                        
                        place = Place(
                            id: place.id,
                            name: place.name,
                            category: place.category,
                            lat: place.lat,
                            long: place.long,
                            sampleCount: response.sampleCount,
                            waitTimeNow: response.averageWaitTime
                        )
                        
                        
                        showSuccessAlert = true
                    }
                }
                
            }
            .buttonStyle(.borderedProminent)
            Spacer()
        }
        .padding()
        
        // Mark: - Error Alert
        .alert("Error", isPresented: $showErrorAlert) {
            Button("OK", role: .cancel) { }
        } message: {
            Text(errorMessage)
        }
        
        // Mark: - Success alert
        .alert("Success", isPresented: $showSuccessAlert) {
            Button("OK") {
                dismiss()
            }
        } message: {
            Text("Wait time submitted successfully!")
        }
    }
}

extension SubmitWaitView {

    private func postManualTime(pid: String, time: Double) async -> WaitTimeResponse {
        
        // Build the URL
        guard var urlComponents = URLComponents(string: "http://127.0.0.1:5000/addtime/") else {
            // If this fails, just return a default response
            // (which has averageWaitTime = "Unknown")
            return WaitTimeResponse()
        }
        
        // Add query parameters: ?time=<time>&pid=<pid>
        urlComponents.queryItems = [
            URLQueryItem(name: "time", value: String(time)),
            URLQueryItem(name: "pid", value: pid)
        ]
        
        // Ensure URL is valid
        guard let url = urlComponents.url else {
            return WaitTimeResponse()
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        do {
            // Perform the network call
            let (data, response) = try await URLSession.shared.data(for: request)
            
            // Check for successful (200-299) HTTP status
            guard let httpResponse = response as? HTTPURLResponse,
                  (200...299).contains(httpResponse.statusCode) else {
                return WaitTimeResponse()
            }
            
            // Decode the JSON into WaitTimeResponse
            let decoder = JSONDecoder()
            let waitStuff = try decoder.decode(WaitTimeResponse.self, from: data)
            return waitStuff
            
        } catch {
            // If there's an error, return a default "Unknown" response
            return WaitTimeResponse()
        }
    }
}
