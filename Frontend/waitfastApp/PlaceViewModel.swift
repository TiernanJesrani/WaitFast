//
//  PlaceViewModel.swift
//  waitfastApp
//
//  Created by Adam Simpson on 2/12/25.
//

import Foundation

class PlaceViewModel: ObservableObject {
    @Published var places: [Place] = [
        Place(name: "Joe's", category: "food", distance: 0.5, liveWaitTime: "5 min"),
        Place(name: "Skeeps", category: "bar", distance: 1.2, liveWaitTime: "10 min"),
        Place(name: "Panch", category: "food", distance: 2.0, liveWaitTime: "15 min"),
        Place(name: "Ricks", category: "bar", distance: 0.8, liveWaitTime: "20 min")
    ]
    
    @Published var searchText: String = ""
    @Published var selectedCategory: String = "All"
    @Published var maxDistance: Double = 5.0
    
    var filteredPlaces: [Place] {
        places.filter { place in
            let matchesName = searchText.isEmpty || place.name.lowercased().contains(searchText.lowercased())
            let matchesCategory = (selectedCategory == "All") || (place.category.lowercased() == selectedCategory.lowercased())
            let matchesDistance = place.distance <= maxDistance
            return matchesName && matchesCategory && matchesDistance
        }
    }
}

