//
//  Place.swift .swift
//  waitfastApp
//
//  Created by Adam Simpson on 2/12/25.
//
import CoreLocation
import Foundation

struct Place: Identifiable, Decodable {
    let id: String
    let name: String
    let category: String // "food" or "bar"
    let lat: Double
    let long: Double
    let coordinate: CLLocationCoordinate2D
    let dailyWaitTimes: [String: Int]
    let sampleCount: Int
    let waitTimeNow: String
    let imageURL: String
    
    enum CodingKeys: String, CodingKey {
        case id
        case name
        case category
        case lat
        case long
        case sampleCount
        case waitTimeNow
        case dailyWaitTimes
        case imageURL
    }
    
    var dailyWaits: [Waits] {
        return dailyWaitTimes
            .sorted { compareTimeStrings($0.key, $1.key) }
            .map { Waits(time: $0.key, min_delay: $0.value) }
    }
    
    init(id: String, name: String, category: String, lat: Double, long: Double, sampleCount: Int, waitTimeNow: String, dailyWaitTimes: [String: Int], imageURL: String) {
        self.id = id
        self.name = name
        self.category = category
        self.lat = lat
        self.long = long
        self.coordinate = CLLocationCoordinate2D(latitude: lat, longitude: long)
        self.sampleCount = sampleCount
        self.waitTimeNow = waitTimeNow
        self.imageURL = imageURL
        self.dailyWaitTimes = dailyWaitTimes
    }
    
    // Decoding
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(String.self, forKey: .id)
        name = try container.decode(String.self, forKey: .name)
        category = try container.decode(String.self, forKey: .category)
        
        let latString = try container.decode(String.self, forKey: .lat)
        let longString = try container.decode(String.self, forKey: .long)
        lat = Double(latString) ?? 0.00
        long = Double(longString) ?? 0.00
        coordinate = CLLocationCoordinate2D(latitude: lat, longitude: long)
        
        sampleCount = try container.decode(Int.self, forKey: .sampleCount)
        waitTimeNow = try container.decode(String.self, forKey: .waitTimeNow)
        imageURL = try container.decode(String.self, forKey: .imageURL)
        dailyWaitTimes = try container.decode([String: Int].self, forKey: .dailyWaitTimes)
    }
    
    func compareTimeStrings(_ time1: String, _ time2: String) -> Bool {
        let formatter = DateFormatter()
        formatter.dateFormat = "hh:mma"
        formatter.amSymbol = "AM"
        formatter.pmSymbol = "PM"
        
        if let date1 = formatter.date(from: time1), let date2 = formatter.date(from: time2) {
            return date1 < date2
        }
        return false
    }
    
    func getWaitByHour() -> Int {
        let formatter = DateFormatter()
        formatter.dateFormat = "hh:00a"
        formatter.amSymbol = "AM"
        formatter.pmSymbol = "PM"
        let currentHour = formatter.string(from: Date())
        return self.dailyWaitTimes[currentHour] ?? 0
    }
}

struct Waits: Identifiable {
    var id = UUID()
    var time: String
    var min_delay: Int
}
