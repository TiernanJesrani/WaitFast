//
//  PlaceViewModel.swift
//  waitfastApp
//
//  Created by Adam Simpson on 2/12/25.
//

import Foundation

class PlaceViewModel: ObservableObject {
    @Published var places: [Place] = []
    @Published var isLoading: Bool = false
    @Published var errorMessage: String? = nil
    
    @Published var searchText: String = ""
    @Published var selectedCategory: String = "All"
    @Published var maxDistance: Double = 5.0

    
    func fetchAttractions(lat: Double, lon: Double) async {
        isLoading = true
        errorMessage = nil
        
        guard var urlComponents = URLComponents(string: "http://127.0.0.1:5000/attractions/") else {
                errorMessage = "Invalid URL"
                isLoading = false
                return
            }
        
        urlComponents.queryItems = [
            URLQueryItem(name: "lat", value: String(lat)),
                URLQueryItem(name: "lon", value: String(lon)),
            URLQueryItem(name: "query", value: "eat")
            ]
            
            // Ensure URL is valid after adding query parameters
            guard let url = urlComponents.url else {
                errorMessage = "Failed to build URL with parameters"
                isLoading = false
                return
            }
        
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        do {
            let (data, response) = try await URLSession.shared.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse, (200...299).contains(httpResponse.statusCode) else {
                errorMessage = "Server error, please try again later."
                isLoading = false
                return
            }

            let decoder = JSONDecoder()
            
            // MARK: - Retrieve and process api data
            self.places = try decoder.decode([Place].self, from: data)
            
        } catch {
            errorMessage = "Failed to fetch data: \(error.localizedDescription)"
            print("Error while fetching data", error)
        }
        
        isLoading = false
    }
    
    var filteredPlaces: [Place] {
        places.filter { place in
            let matchesName = searchText.isEmpty || place.name.lowercased().contains(searchText.lowercased())
            let matchesCategory = (selectedCategory == "All") || (place.category.lowercased() == selectedCategory.lowercased())
            //let matchesDistance = place.distance <= maxDistance
            return matchesName && matchesCategory //&& matchesDistance
        }
    }
}

