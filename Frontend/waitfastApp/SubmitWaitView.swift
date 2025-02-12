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
    
    var body: some View {
        VStack {
            Text("Submit a Wait Time").font(.title2)
            TextField("Enter wait time in minutes", text: $waitTime)
                .textFieldStyle(RoundedBorderTextFieldStyle())
                .padding()
            Button("Submit") {
                // Logic to save wait time
            }
            .buttonStyle(.borderedProminent)
            Spacer()
        }
        .padding()
    }
}
