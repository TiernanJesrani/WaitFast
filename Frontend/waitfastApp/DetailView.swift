import SwiftUI

struct DetailView: View {
    @Binding var place: Place
    
    // Create a single stopwatch for this view to observe
    @StateObject var stopwatch = Stopwatch()
    
    // State to control showing the sheet for SubmitWaitView
    @State private var showSubmitSheet = false
    
    // A formatter to convert raw seconds into hh:mm:ss
    private static var formatter: DateComponentsFormatter = {
        let formatter = DateComponentsFormatter()
        formatter.unitsStyle = .positional
        formatter.allowedUnits = [.hour, .minute, .second]
        formatter.zeroFormattingBehavior = [.pad]
        return formatter
    }()
    
    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                
                // MARK: - Place Info Section
                VStack(spacing: 8) {
                    Text(place.name)
                        .font(.largeTitle)
                        .fontWeight(.bold)
                    
                    Text("Category: \(place.category.capitalized)")
                        .font(.title3)
                    
                    if place.waitTimeNow == "Unknown" {
                        Text("Wait: Unknown")
                            .font(.headline)
                    } else {
                        Text("Wait: \(place.waitTimeNow) min")
                            .font(.headline)
                    }
                }
                .padding()
                .background(Color(.systemGray6))
                .cornerRadius(12)
                
                // MARK: - Submit Wait Time Button
                Button(action: {
                    showSubmitSheet.toggle()
                }) {
                    Text("Submit Wait Time")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .sheet(isPresented: $showSubmitSheet) {
                    // Present your SubmitWaitView in a sheet
                    SubmitWaitView(pid: place.id, place: $place)
                }
                
                // MARK: - Stopwatch Controls
                VStack(spacing: 12) {
                    HStack {
                        Button("Start Wait Timer") {
                            stopwatch.isRunning.toggle()
                        }
                        .buttonStyle(.borderedProminent)
                        
                        Button("Stop Wait Timer") {
                            stopwatch.isRunning.toggle()
                            Task {
                                let waitStuff = await stopwatch.postTime(pid: place.id)
                                // Update place with the new average wait time and sample count
                                place = Place(
                                    id: place.id,
                                    name: place.name,
                                    category: place.category,
                                    lat: place.lat,
                                    long: place.long,
                                    sampleCount: waitStuff.sampleCount,
                                    waitTimeNow: waitStuff.averageWaitTime
                                )
                            }
                        }
                        .buttonStyle(.borderedProminent)
                        
                        Button("Reset") {
                            stopwatch.reset()
                        }
                        .buttonStyle(.borderedProminent)
                    }
                    
                    // Elapsed Time Display
                    Text(elapsedTimeStr(timeInterval: stopwatch.elapsedTime))
                        .font(.system(.body, design: .monospaced))
                }
                .padding()
                .background(Color(.systemGray6))
                .cornerRadius(12)
            }
            .padding()
        }
        .navigationTitle(place.name)
        .navigationBarTitleDisplayMode(.inline)
    }
    
    /// Helper to format a TimeInterval into hh:mm:ss
    private func elapsedTimeStr(timeInterval: TimeInterval) -> String {
        DetailView.formatter.string(from: timeInterval) ?? "00:00:00"
    }
}
