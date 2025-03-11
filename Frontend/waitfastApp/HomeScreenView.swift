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

                List(viewModel.filteredPlaces.indices, id: \.self) { index in
                    let place = viewModel.filteredPlaces[index]
                    var distanceInMeters: Double {
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
                                    .foregroundColor(place.category == "food" ? .cyan : .blue)
                            }
                            Spacer()
                            VStack(alignment: .trailing) {
                                Text("\(String(format: "%.1f", distanceInMeters)) miles")
                                    .foregroundColor(.white)
                                if place.waitTimeNow == "Unknown" {
                                    Text("Wait: Unknown")
                                        .bold()
                                        .foregroundColor(.yellow)
                                } else {
                                    Text("Wait: \(place.waitTimeNow) min")
                                        .bold()
                                        .foregroundColor(.yellow)
                                }
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
            .onAppear {
                observeCoordinateUpdates()
                observeDeniedLocationAccess()
                deviceLocationService.requestLocationUpdates()
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

    func observeCoordinateUpdates() {
        deviceLocationService.coordinatesPublisher
            .receive(on: DispatchQueue.main)
            .sink { completion in
                print("Handle \(completion) for error and finished subscription.")
            } receiveValue: { coordinates in
                print(coordinates)
                self.coordinates = (coordinates.latitude, coordinates.longitude)
                Task {
                    await viewModel.fetchAttractions(lat: self.coordinates.lat, lon: self.coordinates.lon)
                }
                print(self.coordinates)
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
