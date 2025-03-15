import folium
from datetime import datetime, timedelta

def get_bus_routes():
    """Get TheBus routes in Oahu."""
    return [
        {
            'name': 'Route 2 - Waikiki-School-Middle St.',
            'path': [[21.2792, -157.8297], [21.2931, -157.8374], [21.2792, -157.8297]],
            'distance': 3.5,
            'points_per_ride': 50
        },
        {
            'name': 'Route 13 - Liliha',
            'path': [[21.3069, -157.8583], [21.3169, -157.8633], [21.3199, -157.8683]],
            'distance': 2.8,
            'points_per_ride': 40
        },
        
    ]

def get_store_locations():
    """Get store locations and their rewards."""
    return [
        {
            'name': 'Eco-Friendly Market',
            'location': [21.3069, -157.8583],  # Honolulu coordinates
            'points_required': 500,
            'discount': '15% off all products',
            'description': 'Sustainable products and local goods'
        },
        {
            'name': 'Green Energy Store',
            'location': [21.3799, -157.9478],  # Pearl City coordinates
            'points_required': 750,
            'discount': '20% off solar products',
            'description': 'Solar and renewable energy products'
        },
        {
            'name': 'Sustainable Fashion Boutique',
            'location': [21.2749, -157.8240],  # Hawaii Kai coordinates
            'points_required': 1000,
            'discount': '25% off eco-friendly clothing',
            'description': 'Sustainable and locally made fashion'
        }
    ]

def get_activity_locations():
    """Get local activity locations."""
    return [
        {
            'name': 'Beach Cleanup',
            'location': [21.2770, -157.8275],  # Hanauma Bay coordinates
            'date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
            'points': 100,
            'description': 'Join our weekly beach cleanup effort'
        },
        {
            'name': 'Tree Planting',
            'location': [21.3469, -157.8375],  # Manoa Valley coordinates
            'date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
            'points': 150,
            'description': 'Help restore native Hawaiian forests'
        },
        {
            'name': 'Farmers Market',
            'location': [21.2937, -157.8466],  # KCC coordinates
            'date': 'Every Saturday',
            'points': 75,
            'description': 'Support local organic farmers'
        }
    ]

def create_oahu_map(user_points: int):
    """Create an interactive map of Oahu with markers for activities, stores, and bus routes."""
    # Center the map on Oahu
    m = folium.Map(
        location=[21.4389, -157.9243],
        zoom_start=11,
        tiles="cartodb positron"
    )

    # Add bus routes
    for route in get_bus_routes():
        folium.PolyLine(
            locations=route['path'],
            color='blue',
            weight=2,
            popup=f"""
                <b>{route['name']}</b><br>
                Distance: {route['distance']} miles<br>
                Points per ride: {route['points_per_ride']}
            """
        ).add_to(m)

    # Add activity locations
    for activity in get_activity_locations():
        folium.Marker(
            activity['location'],
            popup=folium.Popup(
                f"""<b>{activity['name']}</b><br>
                Date: {activity['date']}<br>
                Points: {activity['points']}<br>
                {activity['description']}""",
                max_width=300
            ),
            icon=folium.Icon(color='green', icon='info-sign')
        ).add_to(m)

    # Add store locations with rewards
    for store in get_store_locations():
        color = 'red' if user_points < store['points_required'] else 'green'
        status = "🔒 Locked" if user_points < store['points_required'] else "🔓 Unlocked"

        folium.Marker(
            store['location'],
            popup=folium.Popup(
                f"""<b>{store['name']}</b><br>
                {store['description']}<br>
                Points Required: {store['points_required']}<br>
                Reward: {store['discount']}<br>
                Status: {status}""",
                max_width=300
            ),
            icon=folium.Icon(color=color, icon='shopping-cart')
        ).add_to(m)

    return m