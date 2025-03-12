//
//  HomeScreenView.swift
//  waitfastApp
//
//  Created by Adam Simpson on 2/12/25.
//

import Foundation
import SwiftUI
import Combine
import CoreLocation

struct HomeScreenView: View {
    @StateObject var viewModel = PlaceViewModel()
    @StateObject var deviceLocationService = DeviceLocationService.shared
    @State var tokens: Set<AnyCancellable> = []
    @State var coordinates: (lat: Double, lon: Double) = (0, 0)

    var body: some View {
        NavigationView {
            ZStack {
                //  bakcground
                LinearGradient(
                    gradient: Gradient(colors: [Color.blue.opacity(0.6), Color.black.opacity(0.8)]),
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
                .edgesIgnoringSafeArea(.all)

                VStack(spacing: 16) {
                    
                    // Search Bar
                    HStack {
                        Image(systemName: "magnifyingglass")
                            .foregroundColor(.gray)
                        TextField("Search for a place...", text: $viewModel.searchText)
                            .padding(8)
                            .background(Color(.systemGray6))
                            .cornerRadius(10)
                    }
                    .padding(.horizontal)
                    .background(Color.white.opacity(0.2))
                    .cornerRadius(12)
                    .shadow(color: .gray.opacity(0.3), radius: 4, x: 0, y: 2)

                    // Category
                    Picker("Category", selection: $viewModel.selectedCategory) {
                        Text("All").tag("All")
                        Text("Food").tag("food")
                        Text("Bar").tag("bar")
                    }
                    .pickerStyle(SegmentedPickerStyle())
                    .padding(.horizontal)
                    .background(Color.white.opacity(0.2))
                    .cornerRadius(12)

                    // Places list inf scroll
                    ScrollView {
                        VStack(spacing: 12) {
                            ForEach(viewModel.filteredPlaces.indices, id: \.self) { index in
                                let place = viewModel.filteredPlaces[index]
                                var distanceInMiles: Double {
                                    let placeLocation = CLLocation(latitude: place.coordinate.latitude, longitude: place.coordinate.longitude)
                                    let userLocation = CLLocation(latitude: coordinates.lat, longitude: coordinates.lon)
                                    return placeLocation.distance(from: userLocation) / 1609.34
                                }

                                NavigationLink(destination: DetailView(place: $viewModel.places[index])) {
                                    HStack {
                                        VStack(alignment: .leading, spacing: 4) {
                                            Text(place.name)
                                                .font(.headline)
                                                .foregroundColor(.white)
                                            Text(place.category.capitalized)
                                                .font(.subheadline)
                                                .foregroundColor(.yellow)
                                        }
                                        Spacer()
                                        VStack(alignment: .trailing) {
                                            Text("\(String(format: "%.1f", distanceInMiles)) miles")
                                                .foregroundColor(.white.opacity(0.8))
                                            Text("Wait: \(place.waitTimeNow == "Unknown" ? "Unknown" : "\(place.waitTimeNow) min")")
                                                .bold()
                                                .foregroundColor(place.waitTimeNow == "Unknown" ? .yellow : .green)
                                        }
                                    }
                                    .padding()
                                    .background(RoundedRectangle(cornerRadius: 12)
                                        .fill(Color.white.opacity(0.2))
                                        .shadow(radius: 2))
                                }
                                .buttonStyle(PlainButtonStyle())
                            }
                        }
                        .padding(.horizontal)
                    }
                }
                .padding(.top, 20)
            }
            .onAppear {
                print("HomeScreenView appeared, starting location updates...")
                observeCoordinateUpdates()
                observeDeniedLocationAccess()
                deviceLocationService.requestLocationUpdates()
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .principal) {
                    HStack {
                        Image(systemName: "clock.fill")
                            .foregroundColor(.white)
                        Text("WaitFast")
                            .font(.title2)
                            .bold()
                            .foregroundColor(.white)
                    }
                }
            }
        }
    }

    func observeCoordinateUpdates() {
        deviceLocationService.coordinatesPublisher
            .receive(on: DispatchQueue.main)
            .sink { completion in
                print("Handle \(completion) for error and finished subscription.")
            } receiveValue: { coordinates in
                print("Received coordinates: \(coordinates.latitude), \(coordinates.longitude)")
                self.coordinates = (coordinates.latitude, coordinates.longitude)
                Task {
                    await viewModel.fetchAttractions(lat: self.coordinates.lat, lon: self.coordinates.lon)
                }
            }
            .store(in: &tokens)
    }

    func observeDeniedLocationAccess() {
        deviceLocationService.deniedLocationAccessPublisher
            .receive(on: DispatchQueue.main)
            .sink {
                print("Handle access denied event, possibly with an alert.")
            }
            .store(in: &tokens)
    }
}
