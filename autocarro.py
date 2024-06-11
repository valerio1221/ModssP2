import heapq
import random

# Prompt user for constants
BUS_INTERVAL = int(input("Enter the time interval between buses in minutes: "))
NORMAL_TRAVEL_TIME = int(input("Enter the normal travel time for a route in minutes: "))
TRAFFIC_TRAVEL_TIME = int(input("Enter the travel time during traffic hours in minutes: "))
SIMULATION_TIME = int(input("Enter the total simulation time in minutes (1 day): "))
PASSENGER_ARRIVAL_MIN = int(input("Enter the minimum passenger arrival interval in minutes: "))
PASSENGER_ARRIVAL_MAX = int(input("Enter the maximum passenger arrival interval in minutes: "))
BUS_CAPACITY = int(input("Enter the bus capacity: "))

# Traffic hour constants
TRAFFIC_HOURS = [(7 * 60, 9 * 60), (17 * 60, 19 * 60)]  # Traffic hours in minutes

# Bus stop constants
NUM_BUS_STOPS = 5
MIN_STOP_INTERVAL = 5
MAX_STOP_INTERVAL = 15

# Metrics
total_waiting_time = 0
total_passengers_served = 0
total_travel_time = 0
queue_sizes = []

# Queue and server state
passenger_queue = [[] for _ in range(NUM_BUS_STOPS)]
passenger_times = []
buses = []
current_time = 0
next_passenger_id = 1
next_passenger_arrival = random.randint(PASSENGER_ARRIVAL_MIN, PASSENGER_ARRIVAL_MAX)

# Event priority queue (min-heap)
events = []

def schedule_event(time, event_type, entity_id=None, stop_id=None):
    heapq.heappush(events, (time, event_type, entity_id, stop_id))

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
    schedule_event(i, 'bus_arrival', entity_id=(i - start_time) // BUS_INTERVAL + 1, stop_id=0)
schedule_event(next_passenger_arrival, 'passenger_arrival')

while events:
    # Get the next event
    current_time, event_type, entity_id, stop_id = heapq.heappop(events)
    
    if current_time >= SIMULATION_TIME:
        break

    if event_type == 'passenger_arrival':
        # Handle passenger arrival
        stop_id = random.randint(0, NUM_BUS_STOPS - 2)  # Random stop where the passenger arrives (not the last stop)
        passenger_queue[stop_id].append((current_time, next_passenger_id))
        queue_sizes.append(len(passenger_queue[stop_id]))
        next_passenger_id += 1
        next_passenger_arrival = current_time + random.randint(PASSENGER_ARRIVAL_MIN, PASSENGER_ARRIVAL_MAX)
        if next_passenger_arrival < SIMULATION_TIME:
            schedule_event(next_passenger_arrival, 'passenger_arrival')
        
    elif event_type == 'bus_arrival':
        # Handle bus arrival
        bus_arrival_time = current_time
        travel_time = get_travel_time(current_time)
        bus_capacity_remaining = BUS_CAPACITY

        # Initialize bus information for each bus separately
        if entity_id > len(buses):
            buses.append({
                'bus_id': entity_id,
                'arrival_time': bus_arrival_time,
                'passengers': [],
                'stops': []
            })

        bus_info = buses[entity_id - 1]

        if stop_id == 0:
            bus_info['arrival_time'] = bus_arrival_time

        bus_stop_info = {
            'stop_id': stop_id,
            'arrival_time': bus_arrival_time,
            'passengers_boarded': [],
            'passengers_left': []  # Changed to 'left'
        }

        # Passengers leaving at this stop
        for passenger in list(bus_info['passengers']):
            if passenger['alight_stop'] == stop_id:
                passenger_left_time = current_time
                passenger['travel_time'] = passenger_left_time - passenger['board_time']
                passenger['total_time'] = passenger_left_time - passenger['arrival_time']
                bus_stop_info['passengers_left'].append(passenger)
                total_passengers_served += 1
                bus_info['passengers'].remove(passenger)

        # Passengers boarding at this stop
        while passenger_queue[stop_id] and bus_capacity_remaining > 0:
            arrival_time, passenger_id = passenger_queue[stop_id].pop(0)
            waiting_time = current_time - arrival_time
            alight_stop = random.randint(stop_id + 1, NUM_BUS_STOPS - 1)  # Random stop where the passenger will leave
            travel_time_for_passenger = travel_time if alight_stop == NUM_BUS_STOPS - 1 else current_time + travel_time - bus_arrival_time
            
            bus_capacity_remaining -= 1

            passenger_record = {
                'passenger_id': passenger_id,
                'arrival_time': arrival_time,
                'waiting_time': waiting_time,
                'travel_time': travel_time_for_passenger,  # Updated travel time for each passenger
                'total_time': waiting_time + travel_time_for_passenger,
                'bus_id': entity_id,
                'board_time': current_time,
                'board_stop': stop_id,
                'alight_stop': alight_stop
            }

            total_waiting_time += waiting_time
            bus_stop_info['passengers_boarded'].append(passenger_record)
            bus_info['passengers'].append(passenger_record)
            passenger_times.append(passenger_record)

        bus_info['stops'].append(bus_stop_info)
        
        if stop_id < NUM_BUS_STOPS - 1:
            next_stop_time = current_time + random.randint(MIN_STOP_INTERVAL, MAX_STOP_INTERVAL)
            schedule_event(next_stop_time, 'bus_arrival', entity_id=entity_id, stop_id=stop_id + 1)

# Calculate metrics
average_waiting_time = total_waiting_time / total_passengers_served if total_passengers_served else 0
average_queue_size = sum(queue_sizes) / len(queue_sizes) if queue_sizes else 0
maximum_queue_size = max(queue_sizes) if queue_sizes else 0

# Print individual passenger times
print("Passenger times (waiting and travel):")
for pt in passenger_times:
    arrival_time_hhmm = minutes_to_hhmm(pt['arrival_time'])
    waiting_time_hhmm = minutes_to_hhmm(pt['waiting_time'])
    board_time_hhmm = minutes_to_hhmm(pt['board_time'])
    if 'left_time' in pt:
        travel_time_hhmm = minutes_to_hhmm(pt['travel_time'])
        total_time_hhmm = minutes_to_hhmm(pt['total_time'])
        print(f"Passenger {pt['passenger_id']} boarded at Stop {pt['board_stop']} on Bus {pt['bus_id']}: Arrival Time = {arrival_time_hhmm}, Waiting Time = {waiting_time_hhmm}, Board Time = {board_time_hhmm}. Left at Stop {pt['alight_stop']}: Travel Time = {travel_time_hhmm}, Total Time = {total_time_hhmm}")
    else:
        print(f"Passenger {pt['passenger_id']} boarded at Stop {pt['board_stop']} on Bus {pt['bus_id']}: Arrival Time = {arrival_time_hhmm}, Waiting Time = {waiting_time_hhmm}, Board Time = {board_time_hhmm}")

# Print bus information
print("\nBus Information:")
for bus in buses:
    bus_arrival_hhmm = minutes_to_hhmm(bus['arrival_time'])
    print(f"Bus {bus['bus_id']} arrived at {bus_arrival_hhmm}")
    for stop in bus['stops']:
        stop_arrival_hhmm = minutes_to_hhmm(stop['arrival_time'])
        print(f"  Stop {stop['stop_id']} arrival time: {stop_arrival_hhmm}")
        for passenger in stop['passengers_boarded']:
            arrival_time_hhmm = minutes_to_hhmm(passenger['arrival_time'])
            waiting_time_hhmm = minutes_to_hhmm(passenger['waiting_time'])
            board_time_hhmm = minutes_to_hhmm(passenger['board_time'])
            print(f"    Passenger {passenger['passenger_id']} boarded at Stop {passenger['board_stop']}: Arrival Time = {arrival_time_hhmm}, Waiting Time = {waiting_time_hhmm}, Board Time = {board_time_hhmm}")
        for passenger in stop['passengers_left']:
            arrival_time_hhmm = minutes_to_hhmm(passenger['arrival_time'])
            waiting_time_hhmm = minutes_to_hhmm(passenger['waiting_time'])
            board_time_hhmm = minutes_to_hhmm(passenger['board_time'])
            travel_time_hhmm = minutes_to_hhmm(passenger['travel_time'])
            total_time_hhmm = minutes_to_hhmm(passenger['total_time'])
            print(f"    Passenger {passenger['passenger_id']} left at Stop {passenger['alight_stop']}: Arrival Time = {arrival_time_hhmm}, Waiting Time = {waiting_time_hhmm}, Travel Time = {travel_time_hhmm}, Total Time = {total_time_hhmm}, Board Time = {board_time_hhmm}")


print("\nSimulation run time:", minutes_to_hhmm(current_time))
print("Total passengers served:", total_passengers_served)
print("Average waiting time in the queue:", minutes_to_hhmm(int(average_waiting_time)))
print("Average queue size:", average_queue_size)
print("Maximum queue size:", maximum_queue_size)
