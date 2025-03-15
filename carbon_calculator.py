import pandas as pd

def calculate_transport_emissions(transport_type: str, distance: float) -> tuple[float, float]:
    """Calculate carbon emissions and points from transportation."""
    emissions_factors = {
        'car': 0.25,      # kg CO2 per mile (gasoline car)
        'bus': 0.15,      # kg CO2 per mile
        'walk': 0,
        'bike': 0,
        'electric_vehicle': 0.05  # kg CO2 per mile
    }

    # Points system (negative for emissions, positive for eco-friendly choices)
    points_factors = {
        'car': -0.25,
        'bus': 0.15,      # Changed to positive to reward public transit
        'walk': 0.05,     # Bonus points for walking
        'bike': 0.05,     # Bonus points for biking
        'electric_vehicle': -0.05
    }

    emissions = distance * emissions_factors.get(transport_type, 0)
    points = distance * points_factors.get(transport_type, 0)

    return emissions, points

def calculate_food_emissions(food_type: str, portions: int) -> float:
    """Calculate carbon emissions from food consumption."""
    emissions_factors = {
        'meat': 3.0,      # kg CO2 per portion
        'fish': 1.34,     # kg CO2 per portion
        'vegetarian': 0.5, # kg CO2 per portion
        'vegan': 0.25     # kg CO2 per portion
    }
    return portions * emissions_factors.get(food_type, 0)

def calculate_energy_emissions(kwh: float) -> float:
    """Calculate carbon emissions from energy usage."""
    hawaii_energy_factor = 0.7  # kg CO2 per kWh (Hawaii-specific grid mix)
    return kwh * hawaii_energy_factor

def calculate_total_daily_emissions(activities: dict) -> tuple[float, float]:
    """Calculate total daily carbon emissions and points."""
    total_emissions = 0
    total_points = 0
    
    # Transport emissions and points
    if 'transport' in activities:
        emissions, points = calculate_transport_emissions(
            activities['transport']['type'],
            activities['transport']['distance']
        )
        total_emissions += emissions
        total_points += points
    
    # Food emissions
    if 'food' in activities:
        total_emissions += calculate_food_emissions(
            activities['food']['type'],
            activities['food']['portions']
        )
    
    # Energy emissions
    if 'energy' in activities:
        total_emissions += calculate_energy_emissions(activities['energy']['kwh'])
    
    return total_emissions, total_points