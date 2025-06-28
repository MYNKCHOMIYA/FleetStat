from db_handler import insert_vehicle, insert_trip, view_vehicles, view_trips
from datetime import date

# Insert a sample vehicle
insert_vehicle("Maruti Swift", "RJ14AB1234", "Mayank", "Car", date.today())

# Insert a sample trip
insert_trip("RJ14AB1234", 5.5, date.today(), "Jaipur", "Ajmer",
            26.9124, 75.7873, 26.4499, 74.6399, 130.0)

# View all data
print("Vehicles:", view_vehicles())
print("Trips:", view_trips())
