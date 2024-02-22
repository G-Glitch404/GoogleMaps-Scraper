from main import GoogleMapsScraper


def test_get_webpage():
    googlemaps_keyword = "stores nearby me"
    google_maps_scraper = GoogleMapsScraper()
    results = google_maps_scraper.get_webpage(googlemaps_keyword)
    google_maps_data = google_maps_scraper.get_data(results)
    google_maps_scraper.export(google_maps_data, googlemaps_keyword)
