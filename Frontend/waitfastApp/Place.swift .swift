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
    //let operatingTimes: [String: String]
    let liveWaitTimes: String // this isn't correct
    
    enum CodingKeys: String, CodingKey {
        case id
        case name
        case category
        case lat
        case long
        case liveWaitTimes
    }
    
    //init(id: String, name: String, category: String, lat: String, long: String, liveWaitTimes: String) {
     //   self.id = id
      //  self.name = name
    //    self.category = category
   //     self.lat = Double(lat) ?? 0.00
        //self.long = Double(long) ?? 0.00
      //  self.liveWaitTimes = liveWaitTimes
    //}
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(String.self, forKey: .id)
        name = try container.decode(String.self, forKey: .name)
        category = try container.decode(String.self, forKey: .category)
        let latString = try container.decode(String.self, forKey: .lat)
        let longString = try container.decode(String.self, forKey: .long)
        lat = Double(latString) ?? 0.00
        long = Double(longString) ?? 0.00
        liveWaitTimes = try container.decodeIfPresent(String.self, forKey: .liveWaitTimes) ?? "Unknown"
        coordinate = CLLocationCoordinate2D(latitude: lat, longitude: long)
    }
}
                                                                            
                
