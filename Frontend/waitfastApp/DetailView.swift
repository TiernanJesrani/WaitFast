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
                    
                    // Place Image IT WONT WORK
                    if let imageURL = placeImageURL, let url = URL(string: imageURL) {
                        AsyncImage(url: url) { image in
                            image
                                .resizable()
                                .scaledToFill()
                                .frame(height: 200)
                                .clipped()
                                .cornerRadius(12)
                                .shadow(radius: 4)
                        } placeholder: {
                            ProgressView() 
                        }
                    } else {
                        // Placeholder if no image found
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
        let apiKey = "AIzaSyAKhhq8I_ZmNmyhpwhqZcof2ExPLilyiWk"
        let placeID = place.id

        print("Fetching image for Place ID: \(placeID)")

        let detailsURL = "https://maps.googleapis.com/maps/api/place/details/json?place_id=\(placeID)&fields=photo&key=\(apiKey)"

        guard let url = URL(string: detailsURL) else { return }

        URLSession.shared.dataTask(with: url) { data, response, error in
            guard let data = data, error == nil else {
                print("Error fetching place details: \(error?.localizedDescription ?? "Unknown error")")
                return
            }

            do {
                // Print full JSON response
                if let jsonString = String(data: data, encoding: .utf8) {
                    print("API Response: \(jsonString)")
                }

                let json = try JSONSerialization.jsonObject(with: data, options: []) as? [String: Any]

                if let result = json?["result"] as? [String: Any],
                   let photos = result["photos"] as? [[String: Any]],
                   let firstPhoto = photos.first,
                   let photoReference = firstPhoto["photo_reference"] as? String {

                    let imageURL = "https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference=\(photoReference)&key=\(apiKey)"

                    DispatchQueue.main.async {
                        self.placeImageURL = imageURL
                        print("Successfully fetched image URL: \(imageURL)")
                    }

                } else {
                    print("No photos found for this place.")
                    DispatchQueue.main.async {
                        self.showImageError = true
                    }
                }

            } catch {
                print("Error parsing JSON: \(error.localizedDescription)")
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
