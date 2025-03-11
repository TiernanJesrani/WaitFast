//
//  DetailView.swift
//  waitfastApp
//
//  Created by Adam Simpson on 2/12/25.
//

import Foundation
import SwiftUI

struct DetailView: View {
    @Binding var place: Place
    
    @StateObject var stopwatch = Stopwatch()
        
    private static var formatter: DateComponentsFormatter = {
        let formatter = DateComponentsFormatter()
        formatter.unitsStyle = .positional // Use the appropriate positioning for the current locale
        formatter.allowedUnits = [ .hour, .minute, .second ] // Units to display in the formatted string
        formatter.zeroFormattingBehavior = [ .pad ] // Pad with zeroes where appropriate for the locale
        formatter.allowsFractionalUnits = true
        return formatter
    }()

    var body: some View {
        VStack {
            Text(place.name).font(.largeTitle)
            Text("Category: \(place.category.capitalized)").font(.title3)
            Text("Live Wait Time: \(place.waitTimeNow)").font(.headline).padding()
            Button("Submit Wait Time") {
                // Navigate to SubmitWaitView
            }
            .buttonStyle(.borderedProminent)
            HStack {
                Button("Start Wait Timer") {
                    self.stopwatch.isRunning.toggle()
                }.buttonStyle(.borderedProminent)
                Button("Stop Wait Timer") {
                    self.stopwatch.isRunning.toggle()
                    Task {
                        let waitStuff = await self.stopwatch.postTime(pid:place.id)
                        place = Place(id: place.id, name: place.name, category: place.category, lat: place.lat, long: place.long, sampleCount: waitStuff.sampleCount, waitTimeNow: waitStuff.averageWaitTime)

                    }
                }.buttonStyle(.borderedProminent)
                Button("Reset") {
                    self.stopwatch.reset()
                }.buttonStyle(.borderedProminent)
                Spacer()
                Text(self.elapsedTimeStr(timeInterval: self.stopwatch.elapsedTime)).font(.system(.body, design: .monospaced))
                Spacer()
            }
            
        }
        .navigationTitle(place.name)

        #if os(iOS)  // Only applies the display mode on iOS
        .navigationBarTitleDisplayMode(.inline)
        #endif
    }
    
    private var playPauseImage: Image {
        return Image(systemName: self.stopwatch.isRunning ? "pause":"play")
    }
        
    private func elapsedTimeStr(timeInterval: TimeInterval) -> String {
        return DetailView.formatter.string(from: timeInterval) ?? ""
    }
}


/*
NOTES:
    Views are reusable building blocks for creating our user-interface
    Place is a constant that holds the data for the place that will be displayed
    Should this be a constant considering this value is going to be changed
*/
