//
//  Place.swift .swift
//  waitfastApp
//
//  Created by Adam Simpson on 2/12/25.
//

import Foundation

struct Place: Identifiable, Decodable {
    let id = UUID()
    let name: String
    let category: String // "food" or "bar"
    let distance: Double  // in kilometers
    let liveWaitTime: String
}
