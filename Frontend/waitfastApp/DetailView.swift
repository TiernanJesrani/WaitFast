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
                gradient: Gradient(colors: [Color.black.opacity(0.8), Color.blue.opacity(0.6)]),
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .edgesIgnoringSafeArea(.all)
            
            ScrollView {
                VStack(spacing: 20) {
                    
                    // Place Image - Using the imageURL from your model
                    if place.imageURL != "NA", let url = URL(string: place.imageURL) {
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
                            case .failure:
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
                            case .empty:
                                ProgressView()
                                    .frame(height: 200)
                            @unknown default:
                                EmptyView()
                            }
                        }
                    } else {
                        // Placeholder if no valid image URL
                        Image(systemName: "photo")
                            .resizable()
                            .scaledToFit()
                            .frame(height: 200)
                            .foregroundColor(.gray)
                            .opacity(0.5)
                            .cornerRadius(12)
                    }

                    
                    WaitTimeChart(dailyWaits: place.dailyWaits)
                    
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
                            Button(stopwatch.isRunning ? "Submit" : "Start") {
                                Task {
                                        if stopwatch.isRunning {
                                            let result = await stopwatch.postTime(pid: place.id)
                                            place = Place(
                                                id: place.id,
                                                name: place.name,
                                                category: place.category,
                                                lat: place.lat,
                                                long: place.long,
                                                sampleCount: result.sampleCount,
                                                waitTimeNow: result.averageWaitTime,
                                                dailyWaitTimes: place.dailyWaitTimes,
                                                imageURL: place.imageURL
                                            )
        
                                            print(place.waitTimeNow)
                                        }
                                        stopwatch.isRunning.toggle()
                                    }
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

struct WaitTimeChart: View {
    let dailyWaits: [Waits]

    var body: some View {
        Chart {
            ForEach(dailyWaits) { stat in
                BarMark(
                    x: .value("Time", stat.time),
                    y: .value("Wait", stat.min_delay)
                )
                .foregroundStyle(.blue)
                .clipShape(RoundedRectangle(cornerRadius: 6))
            }
        }
        .frame(height: 300)

        
        .chartYAxis {
            AxisMarks { _ in
                AxisValueLabel()
                    .foregroundStyle(.white)
                    .offset(x: 10)
                AxisGridLine()
                    .foregroundStyle(.white.opacity(0.7))
            }
        }

        .chartXAxis {
            AxisMarks(values: dailyWaits.map { $0.time }) { value in
                if let timeString = value.as(String.self), timeString.count >= 2 {
                    AxisValueLabel {
                        Text(String(timeString.prefix(2)))
                            .foregroundStyle(.white)
                    }
                }
                AxisTick()
                    .foregroundStyle(.white)
            }
        }
        .padding()
        .frame(height: 300)
    }
}
