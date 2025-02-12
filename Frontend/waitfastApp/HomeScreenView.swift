//
//  HomeScreenView.swift
//  waitfastApp
//
//  Created by Adam Simpson on 2/12/25.
//

import Foundation
import SwiftUI

struct HomeScreenView: View {
    @StateObject var viewModel = PlaceViewModel()
    
    var body: some View {
        NavigationView {
            VStack {
                // App Logo at the Top
                Image("waitfast_logo")
                    .resizable()
                    .scaledToFit()
                    .frame(width: 180, height: 100)
                    .padding(.top, 20)

                // Search Bar
                TextField("Search by name...", text: $viewModel.searchText)
                    .padding()
                    .background(Color(.systemGray6))
                    .cornerRadius(10)
                    .shadow(color: .gray.opacity(0.2), radius: 5, x: 0, y: 2)
                    .padding([.horizontal, .top])

                // Category Picker
                Picker("Category", selection: $viewModel.selectedCategory) {
                    Text("All").tag("All")
                    Text("Food").tag("food")
                    Text("Bar").tag("bar")
                }
                .pickerStyle(SegmentedPickerStyle())
                .padding(.horizontal)

        
                List(viewModel.filteredPlaces) { place in
                    NavigationLink(destination: DetailView(place: place)) {
                        HStack {
                            VStack(alignment: .leading, spacing: 4) {
                                Text(place.name)
                                    .font(.headline)
                                    .foregroundColor(.white)
                                
                                Text(place.category.capitalized)
                                    .font(.subheadline)
                                    .foregroundColor(place.category == "food" ? .cyan : .blue)
                            }
                            Spacer()
                            VStack(alignment: .trailing) {
                                Text("\(String(format: "%.1f", place.distance)) km")
                                    .foregroundColor(.white)
                                Text("Wait: \(place.liveWaitTime)")
                                    .bold()
                                    .foregroundColor(.yellow)
                            }
                        }
                        .padding()
                        .background(LinearGradient(
                            gradient: Gradient(colors: [Color.blue.opacity(0.9), Color.black.opacity(0.8)]),
                            startPoint: .leading,
                            endPoint: .trailing))
                        .cornerRadius(10)
                        .shadow(color: .gray.opacity(0.3), radius: 4, x: 0, y: 2)
                    }
                    .listRowBackground(Color.clear)
                }
                .listStyle(PlainListStyle())
            }
            .background(Color(.systemGray6).edgesIgnoringSafeArea(.all))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .principal) {
                    HStack {
                        Image(systemName: "clock") // Small clock icon for styling
                            .foregroundColor(.blue)
                        Text("WaitFast")
                            .font(.title2)
                            .bold()
                            .foregroundColor(.blue)
                    }
                }
            }
        }
    }
}
