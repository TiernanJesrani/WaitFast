//
//  DetailView.swift
//  waitfastApp
//
//  Created by Adam Simpson on 2/12/25.
//

import SwiftUI
import Combine
import Charts

struct DetailView: View {
    @Binding var place: Place
    @StateObject var stopwatch = Stopwatch()
    @State private var showSubmitSheet = false
    @State private var placeImageURL: String? = nil
    @State private var showImageError = false

    
    var body: some View {
        ZStack {
            //  gradient
            LinearGradient(
                gradient: Gradient(colors: [Color.blue.opacity(0.6), Color.black.opacity(0.8)]),
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .edgesIgnoringSafeArea(.all)
            
            ScrollView {
                VStack(spacing: 20) {
                    
                    // Place Image - Using the imageURL from your model
                    if let imageURL = place.imageURL, let url = URL(string: imageURL) {
                        AsyncImage(url: url) { phase in
                            switch phase {
                            case .success(let image):
                                image
                                    .resizable()
                                    .scaledToFill()
                                    .frame(height: 200)
                                    .clipped()
                                    .cornerRadius(12)
                                    .shadow(radius: 4)
                            case .failure(let error):
                                VStack {
                                    Image(systemName: "photo.fill")
                                        .resizable()
                                        .scaledToFit()
                                        .frame(height: 150)
                                        .foregroundColor(.gray)
                                    Text("Failed to load image")
                                        .font(.caption)
                                        .foregroundColor(.gray)
                                }
                                .frame(height: 200)
                                .onAppear {
                                    print("Image loading error: \(error.localizedDescription)")
                                }
                            case .empty:
                                ProgressView()
                                    .frame(height: 200)
                            @unknown default:
                                EmptyView()
                            }
                        }
                    } else {
                        // Placeholder if no image URL
                        Image(systemName: "photo")
                            .resizable()
                            .scaledToFit()
                            .frame(height: 200)
                            .foregroundColor(.gray)
                            .opacity(0.5)
                            .cornerRadius(12)
                    }
                    
                    Chart {
                        ForEach(place.dailyWaits) { stat in
                            BarMark(
                                x: .value("Time", stat.time),
                                y: .value("Wait", stat.min_delay)
                            )
                            .foregroundStyle(.blue) // Customize color if needed
                            .clipShape(RoundedRectangle(cornerRadius: 16)) // Optional rounded corners
                        }
                    }
                    .padding()
                    .frame(height: 300)
                    
                    VStack(spacing: 10) {
                        Text(place.name)
                            .font(.largeTitle)
                            .bold()
                            .foregroundColor(.white)
                        
                        Text(place.category.capitalized)
                            .font(.title3)
                            .foregroundColor(.yellow)
                        
                        Text("Current Wait: \(place.waitTimeNow == "Unknown" ? "\(place.getWaitByHour()) min" : "\(place.waitTimeNow) min")")
                            .font(.headline)
                            .foregroundColor(.green)
                    }
                    .padding()
                    .background(Color.white.opacity(0.2))
                    .cornerRadius(12)

                    VStack(spacing: 12) {
                        HStack {
                            Button(stopwatch.isRunning ? "Stop" : "Start") {
                                stopwatch.isRunning.toggle()
                            }
                            .frame(maxWidth: .infinity)
                            .buttonStyle(.borderedProminent)
                            
                            Button("Reset") {
                                stopwatch.reset()
                            }
                            .frame(maxWidth: .infinity)
                            .buttonStyle(.bordered)
                        }
                        
                        Text(elapsedTimeStr(timeInterval: stopwatch.elapsedTime))
                            .font(.system(.title, design: .monospaced))
                            .foregroundColor(.white)
                            .padding()
                    }
                    .padding()
                    .background(Color.white.opacity(0.2))
                    .cornerRadius(12)

                    // Submit Wait Time Button
                    Button("Submit Wait Time") {
                        showSubmitSheet.toggle()
                    }
                    .frame(maxWidth: .infinity)
                    .buttonStyle(.borderedProminent)
                    .sheet(isPresented: $showSubmitSheet) {
                        SubmitWaitView(pid: place.id, place: $place)
                    }
                }
                .padding()
            }
        }
        .navigationTitle(place.name)
        .navigationBarTitleDisplayMode(.inline)
        .onAppear {
            fetchPlaceImage()
        }
    }

    private func fetchPlaceImage() {
        // If we already have the image URL in the Place model, use it
        if let imageURL = place.imageURL {
            self.placeImageURL = imageURL
            print("Using image URL from model: \(imageURL)")
            return
        }
        
        // Construct the URL to your backend to fetch the image
        let baseURL = "http://127.0.0.1:5000" // Use your actual backend base URL
        let imageEndpoint = "/place/\(place.id)/image" // Adjust this endpoint to match your backend
        
        guard let url = URL(string: baseURL + imageEndpoint) else {
            print("Invalid image URL")
            return
        }
        
        print("Fetching image for Place ID: \(place.id) from backend")
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            guard let data = data, error == nil else {
                print("Error fetching image: \(error?.localizedDescription ?? "Unknown error")")
                return
            }
            
            do {
                if let jsonResponse = try JSONSerialization.jsonObject(with: data) as? [String: Any],
                   let imageURL = jsonResponse["imageURL"] as? String {
                    
                    DispatchQueue.main.async {
                        self.placeImageURL = imageURL
                        print("Successfully fetched image URL from backend: \(imageURL)")
                    }
                } else {
                    print("No image URL found in response")
                    DispatchQueue.main.async {
                        self.showImageError = true
                    }
                }
            } catch {
                print("Error parsing image response: \(error.localizedDescription)")
            }
        }.resume()
    }
    /// Formats elapsed time in hh:mm:ss
    private func elapsedTimeStr(timeInterval: TimeInterval) -> String {
        let formatter = DateComponentsFormatter()
        formatter.unitsStyle = .positional
        formatter.allowedUnits = [.hour, .minute, .second]
        formatter.zeroFormattingBehavior = [.pad]
        return formatter.string(from: timeInterval) ?? "00:00:00"
    }
}
