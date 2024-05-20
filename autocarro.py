import random
import heapq

# Constants
BUS_INTERVAL = 15  # Time interval between buses in minutes
TRAVEL_TIME = 20  # Travel time for a route in minutes
SIMULATION_TIME = 300  # Total simulation time in minutes
PASSENGER_ARRIVAL_MIN = 1
PASSENGER_ARRIVAL_MAX = 5

# Metrics
total_waiting_time = 0
total_passengers_served = 0
total_travel_time = 0  # Initialize total_travel_time here
queue_sizes = []

# Queue and server state
passenger_queue = []
passenger_times = []  # Track individual passenger times
bus_info = []  # Track bus information
current_time = 0
next_passenger_id = 1
next_passenger_arrival = random.randint(PASSENGER_ARRIVAL_MIN, PASSENGER_ARRIVAL_MAX)

# Event priority queue (min-heap)
events = []

def schedule_event(time, event_type, entity_id=None):
    heapq.heappush(events, (time, event_type, entity_id))

# Schedule the first bus and passenger arrivals
for i in range(0, SIMULATION_TIME, BUS_INTERVAL):
    schedule_event(i, 'bus_arrival', entity_id=i // BUS_INTERVAL + 1)
schedule_event(next_passenger_arrival, 'passenger_arrival')

while events:
    # Get the next event
    current_time, event_type, entity_id = heapq.heappop(events)

    if event_type == 'passenger_arrival':
        # Handle passenger arrival
        if current_time < SIMULATION_TIME:
            passenger_queue.append((current_time, next_passenger_id))
            queue_sizes.append(len(passenger_queue))
            next_passenger_id += 1
            next_passenger_arrival = current_time + random.randint(PASSENGER_ARRIVAL_MIN, PASSENGER_ARRIVAL_MAX)
            if next_passenger_arrival < SIMULATION_TIME:
                schedule_event(next_passenger_arrival, 'passenger_arrival')
        
    elif event_type == 'bus_arrival':
        # Handle bus arrival
        bus_arrival_time = current_time
        passengers_served_by_bus = 0
        bus_departure_time = current_time + TRAVEL_TIME
        
        bus_info.append({
            'bus_id': entity_id,
            'arrival_time': bus_arrival_time,
            'passengers': [],
        })

        while passenger_queue:
            arrival_time, passenger_id = passenger_queue.pop(0)
            waiting_time = current_time - arrival_time
            travel_end_time = current_time + TRAVEL_TIME
            
            total_waiting_time += waiting_time
            total_passengers_served += 1
            total_travel_time += TRAVEL_TIME
            passengers_served_by_bus += 1

            # Record individual passenger times
            passenger_times.append({
                'passenger_id': passenger_id,
                'waiting_time': waiting_time,
                'travel_time': TRAVEL_TIME,
                'total_time': waiting_time + TRAVEL_TIME,
                'bus_id': entity_id,
                'board_time': current_time
            })
            
            bus_info[-1]['passengers'].append({
                'passenger_id': passenger_id,
                'waiting_time': waiting_time,
                'travel_time': TRAVEL_TIME,
                'total_time': waiting_time + TRAVEL_TIME,
                'bus_id': entity_id,
                'board_time': current_time
            })

        # Schedule next bus arrival
        next_bus_arrival = current_time + BUS_INTERVAL
        if next_bus_arrival < SIMULATION_TIME:
            schedule_event(next_bus_arrival, 'bus_arrival', entity_id=entity_id + 1)

# Calculate metrics
average_waiting_time = total_waiting_time / total_passengers_served if total_passengers_served else 0
average_queue_size = sum(queue_sizes) / len(queue_sizes) if queue_sizes else 0
maximum_queue_size = max(queue_sizes) if queue_sizes else 0

# Print individual passenger times
print("Passenger times (waiting and travel):")
for pt in passenger_times:
    print(f"Passenger {pt['passenger_id']}: Waiting Time = {pt['waiting_time']:.2f} mins, Travel Time = {pt['travel_time']:.2f} mins, Total Time = {pt['total_time']:.2f} mins, Entered Bus {pt['bus_id']} at {pt['board_time']} mins")

# Print bus information
print("\nBus Information:")
for bus in bus_info:
    print(f"Bus {bus['bus_id']} arrived at {bus['arrival_time']} mins")
    for passenger in bus['passengers']:
        print(f"  Passenger {passenger['passenger_id']}: Waiting Time = {passenger['waiting_time']:.2f} mins, Travel Time = {passenger['travel_time']:.2f} mins, Total Time = {passenger['total_time']:.2f} mins, Entered Bus {passenger['bus_id']} at {passenger['board_time']} mins")

# Print overall results
print("\nSimulation run time:", current_time)
print("Total passengers served:", total_passengers_served)
print("Average waiting time in the queue:", average_waiting_time)
print("Average queue size:", average_queue_size)
print("Maximum queue size:", maximum_queue_size)
print("Total travel time:", total_travel_time)