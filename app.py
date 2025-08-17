from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

# --- Initialize Flask App ---
app = Flask(__name__)
# Enable Cross-Origin Resource Sharing (CORS) to allow your UI to call this server
CORS(app)

# --- Scraper Functions (from our previous script) ---

def scrape_booking(city):
    """ Scrapes hotel data for a given city from Booking.com. """
    print(f"Scraping Booking.com for {city}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    city_formatted = city.replace(' ', '+')
    url = f'https://www.booking.com/searchresults.html?ss={city_formatted}'
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error making request to Booking.com: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    hotels = []
    for hotel_card in soup.find_all('div', {'data-testid': 'property-card'}):
        try:
            name = hotel_card.find('div', {'data-testid': 'title'}).text.strip()
            price = hotel_card.find('span', {'data-testid': 'price-and-discounted-price'}).text.strip()
            rating_element = hotel_card.find('div', {'data-testid': 'review-score'})
            rating = rating_element.find('div').text.strip() if rating_element else 'N/A'
            hotels.append({'name': name, 'price': price, 'rating': rating, 'source': 'Booking.com'})
        except Exception:
            continue # Skip if a card is missing info
    return hotels

def scrape_airbnb(city):
    """ Scrapes listing data for a given city from Airbnb. """
    print(f"Scraping Airbnb for {city}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    city_formatted = city.replace(' ', '-')
    url = f'https://www.airbnb.com/s/{city_formatted}/homes'
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error making request to Airbnb: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    listings = []
    # Note: Airbnb class names can change. This is a potential point of failure.
    for listing_card in soup.find_all('div', class_='c4mnd7m'):
        try:
            name = listing_card.find('div', {'data-testid': 'listing-card-title'}).text.strip()
            price = listing_card.find('span', class_='_14y1gc').text.strip()
            rating = listing_card.find('span', class_='r1v211wb').text.strip().split(' ')[0]
            listings.append({'name': name, 'price': price, 'rating': rating, 'source': 'Airbnb'})
        except Exception:
            continue # Skip if a card is missing info
    return listings


# --- API Endpoint ---
@app.route('/scrape')
def scrape():
    # Get the city from a URL parameter (e.g., /scrape?city=Paris)
    city = request.args.get('city')
    if not city:
        return jsonify({"error": "A 'city' parameter is required."}), 400

    # Run the scrapers and combine the data
    booking_data = scrape_booking(city)
    airbnb_data = scrape_airbnb(city)
    combined_data = booking_data + airbnb_data

    # Return the data as JSON
    return jsonify(combined_data)

if __name__ == '__main__':
    # This allows you to run the server locally for testing
    app.run(debug=True, port=5001)
