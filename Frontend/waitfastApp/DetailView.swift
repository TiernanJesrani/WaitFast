//
//  DetailView.swift
//  waitfastApp
//
//  Created by Adam Simpson on 2/12/25.
//

import Foundation
import SwiftUI

struct DetailView: View {
    let place: Place

    var body: some View {
        VStack {
            Text(place.name).font(.largeTitle)
            Text("Category: \(place.category.capitalized)").font(.title3)
            Text("Live Wait Time: \(place.liveWaitTimes)").font(.headline).padding()
            Button("Submit Wait Time") {
                // Navigate to SubmitWaitView
            }
            .buttonStyle(.borderedProminent)
            Spacer()
        }
        .navigationTitle(place.name)

        #if os(iOS)  // Only applies the display mode on iOS
        .navigationBarTitleDisplayMode(.inline)
        #endif
    }
}

/*
NOTES:
    Views are reusable building blocks for creating our user-interface
    Place is a constant that holds the data for the place that will be displayed
    Should this be a constant considering this value is going to be changed
*/
