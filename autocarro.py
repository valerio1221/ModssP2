import random
import heapq

# Prompt user for constants
BUS_INTERVAL = int(input("Enter the time interval between buses in minutes: "))
NORMAL_TRAVEL_TIME = int(input("Enter the normal travel time for a route in minutes: "))
TRAFFIC_TRAVEL_TIME = int(input("Enter the travel time during traffic hours in minutes: "))
SIMULATION_TIME = int(input("Enter the total simulation time in minutes (1 day): "))
PASSENGER_ARRIVAL_MIN = int(input("Enter the minimum passenger arrival interval in minutes: "))
PASSENGER_ARRIVAL_MAX = int(input("Enter the maximum passenger arrival interval in minutes: "))

# Traffic hour constants
TRAFFIC_HOURS = [(7 * 60, 9 * 60), (17 * 60, 19 * 60)]  # Traffic hours in minutes

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

def minutes_to_hhmm(minutes):
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02}:{mins:02}"

def is_traffic_hour(current_time):
    for start, end in TRAFFIC_HOURS:
        if start <= current_time % 1440 < end:
            return True
    return False

def get_travel_time(current_time):
    return TRAFFIC_TRAVEL_TIME if is_traffic_hour(current_time) else NORMAL_TRAVEL_TIME

# Schedule the first bus and passenger arrivals
start_time = 6 * 60  # 6:00 AM in minutes
end_time = 21 * 60  # 9:00 PM in minutes

for i in range(start_time, end_time, BUS_INTERVAL):
    schedule_event(i, 'bus_arrival', entity_id=(i - start_time) // BUS_INTERVAL + 1)
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
        travel_time = get_travel_time(current_time)
        bus_departure_time = current_time + travel_time
        
        bus_info.append({
            'bus_id': entity_id,
            'arrival_time': bus_arrival_time,
            'passengers': [],
        })

        while passenger_queue:
            arrival_time, passenger_id = passenger_queue.pop(0)
            waiting_time = current_time - arrival_time
            travel_end_time = current_time + travel_time
            
            total_waiting_time += waiting_time
            total_passengers_served += 1
            total_travel_time += travel_time
            passengers_served_by_bus += 1

            # Record individual passenger times
            passenger_times.append({
                'passenger_id': passenger_id,
                'arrival_time': arrival_time,
                'waiting_time': waiting_time,
                'travel_time': travel_time,
                'total_time': waiting_time + travel_time,
                'bus_id': entity_id,
                'board_time': current_time
            })
            
            bus_info[-1]['passengers'].append({
                'passenger_id': passenger_id,
                'arrival_time': arrival_time,
                'waiting_time': waiting_time,
                'travel_time': travel_time,
                'total_time': waiting_time + travel_time,
                'bus_id': entity_id,
                'board_time': current_time
            })

# Calculate metrics
average_waiting_time = total_waiting_time / total_passengers_served if total_passengers_served else 0
average_queue_size = sum(queue_sizes) / len(queue_sizes) if queue_sizes else 0
maximum_queue_size = max(queue_sizes) if queue_sizes else 0

# Print individual passenger times
print("Passenger times (waiting and travel):")
for pt in passenger_times:
    arrival_time_hhmm = minutes_to_hhmm(pt['arrival_time'])
    waiting_time_hhmm = minutes_to_hhmm(pt['waiting_time'])
    travel_time_hhmm = minutes_to_hhmm(pt['travel_time'])
    total_time_hhmm = minutes_to_hhmm(pt['total_time'])
    board_time_hhmm = minutes_to_hhmm(pt['board_time'])
    print(f"Passenger {pt['passenger_id']}: Arrival Time = {arrival_time_hhmm}, Waiting Time = {waiting_time_hhmm}, Travel Time = {travel_time_hhmm}, Total Time = {total_time_hhmm}, Entered Bus {pt['bus_id']} at {board_time_hhmm}")

# Print bus information
print("\nBus Information:")
for bus in bus_info:
    bus_arrival_hhmm = minutes_to_hhmm(bus['arrival_time'])
    print(f"Bus {bus['bus_id']} arrived at {bus_arrival_hhmm}")
    for passenger in bus['passengers']:
        arrival_time_hhmm = minutes_to_hhmm(passenger['arrival_time'])
        waiting_time_hhmm = minutes_to_hhmm(passenger['waiting_time'])
        travel_time_hhmm = minutes_to_hhmm(passenger['travel_time'])
        total_time_hhmm = minutes_to_hhmm(passenger['total_time'])
        board_time_hhmm = minutes_to_hhmm(passenger['board_time'])
        print(f"  Passenger {passenger['passenger_id']}: Arrival Time = {arrival_time_hhmm}, Waiting Time = {waiting_time_hhmm}, Travel Time = {travel_time_hhmm}, Total Time = {total_time_hhmm}, Entered Bus {passenger['bus_id']} at {board_time_hhmm}")

# Print overall results
print("\nSimulation run time:", minutes_to_hhmm(current_time))
print("Total passengers served:", total_passengers_served)
print("Average waiting time in the queue:", minutes_to_hhmm(int(average_waiting_time)))
print("Average queue size:", average_queue_size)
print("Maximum queue size:", maximum_queue_size)
print("Total travel time:", minutes_to_hhmm(total_travel_time))
