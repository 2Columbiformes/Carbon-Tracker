import random
from datetime import datetime, timedelta

def get_real_time_energy_data():
    """
    Simulate real-time energy data for Hawaii's power grid.
    In a production environment, this would fetch real data from an API.
    """
    total_demand = random.uniform(900, 1200)  # MW
    solar_contribution = random.uniform(200, 400) * (1 + 0.3 * random.random())  # Higher during daylight
    wind_contribution = random.uniform(50, 150)
    
    # Calculate percentages
    renewable_percentage = ((solar_contribution + wind_contribution) / total_demand) * 100
    
    return {
        'total_demand': round(total_demand, 2),
        'solar_contribution': round(solar_contribution, 2),
        'wind_contribution': round(wind_contribution, 2),
        'renewable_percentage': round(renewable_percentage, 2),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def get_local_activities():
    """Return current local sustainability activities in Hawaii."""
    return [
        {
            'type': 'Beach Cleanup',
            'location': 'Waikiki Beach',
            'date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
            'impact': 'Help remove plastics and debris from our beaches',
            'points': 100
        },
        {
            'type': 'Public Transport Workshop',
            'location': 'Honolulu Transit Center',
            'date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
            'impact': 'Learn about TheBus routes and sustainable transportation',
            'points': 50
        },
        {
            'type': 'Farmers Market',
            'location': 'Kapiolani Community College',
            'date': 'Every Saturday',
            'impact': 'Support local farmers and reduce food miles',
            'points': 75
        }
    ]
