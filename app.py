from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

API_URL = "https://www.microburbs.com.au/report_generator/api/suburb/properties"
HEADERS = {
    "Authorization": "Bearer test",
    "Content-Type": "application/json"
}

# Mock data as fallback when API fails
MOCK_DATA = {
    "results": [
        {
            "address": {"street": "25 Seacroft Close", "sal": "Belmont North", "state": "NSW"},
            "area_name": "25 Seacroft Close, Belmont North, NSW",
            "attributes": {"bathrooms": 2, "bedrooms": 4, "garage_spaces": 2, "land_size": "973 m²"},
            "listing_date": "2025-10-07",
            "price": 1250000,
            "property_type": "House"
        },
        {
            "address": {"street": "67 Old Belmont Road", "sal": "Belmont North", "state": "NSW"},
            "area_name": "67 Old Belmont Road, Belmont North, NSW",
            "attributes": {"bathrooms": 1, "bedrooms": 3, "garage_spaces": 2, "land_size": "556 m²"},
            "listing_date": "2025-10-08",
            "price": 890000,
            "property_type": "House"
        },
        {
            "address": {"street": "17 Dulungra Avenue", "sal": "Belmont North", "state": "NSW"},
            "area_name": "17 Dulungra Avenue, Belmont North, NSW",
            "attributes": {"bathrooms": 3, "bedrooms": 5, "garage_spaces": 2, "land_size": "605 m²"},
            "listing_date": "2025-10-08",
            "price": 1350000,
            "property_type": "House"
        },
        {
            "address": {"street": "5 Pinnaroo Close", "sal": "Belmont North", "state": "NSW"},
            "area_name": "5 Pinnaroo Close, Belmont North, NSW",
            "attributes": {"bathrooms": 3, "bedrooms": 4, "garage_spaces": 3, "land_size": "768 m²"},
            "listing_date": "2025-10-13",
            "price": 1200000,
            "property_type": "House"
        },
        {
            "address": {"street": "30 John Fisher Road", "sal": "Belmont North", "state": "NSW"},
            "area_name": "30 John Fisher Road, Belmont North, NSW",
            "attributes": {"bathrooms": 1, "bedrooms": 3, "garage_spaces": 3, "land_size": "556 m²"},
            "listing_date": "2025-10-20",
            "price": 900000,
            "property_type": "House"
        },
        {
            "address": {"street": "Unit 2, 1 Vincent Street", "sal": "Belmont North", "state": "NSW"},
            "area_name": "Unit 2, 1 Vincent Street, Belmont North, NSW",
            "attributes": {"bathrooms": 1, "bedrooms": 2, "garage_spaces": 1, "land_size": "N/A"},
            "listing_date": "2025-04-29",
            "price": 599000,
            "property_type": "Unit"
        },
        {
            "address": {"street": "46 Patrick Street", "sal": "Belmont North", "state": "NSW"},
            "area_name": "46 Patrick Street, Belmont North, NSW",
            "attributes": {"bathrooms": 1, "bedrooms": 4, "garage_spaces": 4, "land_size": "466 m²"},
            "listing_date": "2025-09-15",
            "price": 920000,
            "property_type": "House"
        },
        {
            "address": {"street": "380-384 Pacific Highway", "sal": "Belmont North", "state": "NSW"},
            "area_name": "380-384 Pacific Highway, Belmont North, NSW",
            "attributes": {"bathrooms": None, "bedrooms": None, "garage_spaces": None, "land_size": "1377 m²"},
            "listing_date": "2025-09-23",
            "price": 1800000,
            "property_type": "Unit"
        }
    ]
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/test")
def test():
    return render_template("test.html")

@app.route("/search")
def search():
    suburb = request.args.get("suburb", "Belmont North")
    params = {"suburb": suburb}
    use_mock = False
    
    try:
        # Try to fetch from real API first
        response = requests.get(API_URL, headers=HEADERS, params=params, timeout=5)
        print(f"API Response Status: {response.status_code}")
        
        # If API fails (401, 403, 500, etc.), use mock data
        if response.status_code == 401:
            print("⚠️ API authentication failed (401), using mock data")
            use_mock = True
        elif response.status_code != 200:
            print(f"⚠️ API error {response.status_code}, using mock data")
            use_mock = True
        else:
            data = response.json()
            print(f"✅ API Response keys: {list(data.keys())}")
            results = data.get("results", [])
            
            # If no results from API, use mock data
            if not results:
                print("⚠️ No results from API, using mock data")
                use_mock = True
        
    except requests.exceptions.RequestException as e:
        print(f"⚠️ API request failed: {e}, using mock data")
        use_mock = True
    except Exception as e:
        print(f"⚠️ Unexpected error: {e}, using mock data")
        use_mock = True
    
    # Use mock data if API failed
    if use_mock:
        print(f"📦 Using mock data for {suburb}")
        results = MOCK_DATA["results"]
    
    # Process results
    try:
        print(f"Found {len(results)} properties")
        clean = []
        for item in results:
            attributes = item.get("attributes", {})
            
            # Safe value extraction - replace None/NaN with appropriate defaults
            def safe_number(value):
                if value is None:
                    return None
                try:
                    num = float(value)
                    # Check for NaN
                    if num != num:  # NaN is the only value that != itself
                        return None
                    return num
                except (ValueError, TypeError):
                    return None
            
            clean.append({
                "address": item.get("area_name", "N/A"),
                "price": safe_number(item.get("price")),
                "bedrooms": safe_number(attributes.get("bedrooms")),
                "bathrooms": safe_number(attributes.get("bathrooms")),
                "garages": safe_number(attributes.get("garage_spaces")),
                "land_size": attributes.get("land_size"),
                "type": item.get("property_type", "N/A"),
                "listing_date": item.get("listing_date", "N/A")
            })
        
        print(f"Processed {len(clean)} properties")
        return jsonify(clean)
        
    except Exception as e:
        print(f"❌ Error processing data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/analytics")
def analytics():
    """Endpoint to provide statistical analysis of property data"""
    suburb = request.args.get("suburb", "Belmont North")
    params = {"suburb": suburb}
    use_mock = False
    
    try:
        # Try to fetch from real API first
        response = requests.get(API_URL, headers=HEADERS, params=params, timeout=5)
        
        if response.status_code == 401 or response.status_code != 200:
            print(f"⚠️ Analytics API failed ({response.status_code}), using mock data")
            use_mock = True
        else:
            results = response.json().get("results", [])
            if not results:
                use_mock = True
        
    except Exception as e:
        print(f"⚠️ Analytics API error: {e}, using mock data")
        use_mock = True
    
    # Use mock data if API failed
    if use_mock:
        results = MOCK_DATA["results"]
    
    try:
        # Safe number filter
        def is_valid_number(val):
            if val is None:
                return False
            try:
                num = float(val)
                return num == num  # False if NaN
            except:
                return False
        
        # Calculate statistics
        prices = [item.get("price") for item in results if is_valid_number(item.get("price"))]
        bedrooms = [item.get("attributes", {}).get("bedrooms") for item in results if is_valid_number(item.get("attributes", {}).get("bedrooms"))]
        property_types = [item.get("property_type") for item in results if item.get("property_type")]
        
        # Price statistics
        avg_price = sum(prices) / len(prices) if prices else 0
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0
        
        # Property type distribution
        type_counts = {}
        for ptype in property_types:
            type_counts[ptype] = type_counts.get(ptype, 0) + 1
        
        # Bedroom distribution
        bedroom_counts = {}
        for bed in bedrooms:
            bedroom_counts[bed] = bedroom_counts.get(bed, 0) + 1
        
        # Ensure no NaN values in response
        def safe_value(val):
            if val is None or (isinstance(val, float) and val != val):
                return 0
            return val
        
        analytics_data = {
            "total_properties": len(results),
            "price_stats": {
                "average": round(safe_value(avg_price), 2),
                "min": safe_value(min_price),
                "max": safe_value(max_price)
            },
            "property_types": type_counts,
            "bedroom_distribution": bedroom_counts
        }
        
        return jsonify(analytics_data)
        
    except Exception as e:
        print(f"❌ Analytics Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("🚀 Starting Flask application on port 8000...")
    print("📦 Mock data fallback enabled for API failures")
    app.run(debug=True, port=8000)