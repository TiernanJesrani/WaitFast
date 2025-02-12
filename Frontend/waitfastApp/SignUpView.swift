//
//  SignUpView.swift
//  waitfastApp
//
//  Created by Adam Simpson on 2/12/25.
//

import Foundation
import SwiftUI

struct SignUpView: View {
    @State private var email = ""
    @State private var password = ""

    var body: some View {
        VStack {
            TextField("Email", text: $email).textFieldStyle(RoundedBorderTextFieldStyle()).padding()
            SecureField("Password", text: $password).textFieldStyle(RoundedBorderTextFieldStyle()).padding()
            Button("Sign Up") {
                // Handle sign up logic
            }
            .buttonStyle(.borderedProminent)
            Spacer()
        }
        .padding()
    }
}
