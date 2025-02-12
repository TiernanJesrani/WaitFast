//
//  SettingsView.swift
//  waitfastApp
//
//  Created by Adam Simpson on 2/12/25.
//

import Foundation
import SwiftUI

struct SettingsView: View {
    var body: some View {
        VStack {
            Toggle("Enable Notifications", isOn: .constant(true))
                .padding()
            Button("Log Out") {
                // Handle logout
            }
            .buttonStyle(.borderedProminent)
            Spacer()
        }
        .navigationTitle("Settings")
    }
}
