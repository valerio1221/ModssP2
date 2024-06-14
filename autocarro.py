import heapq
import random
import numpy as np
import matplotlib.pyplot as plt

# Prompt user for constants
BUS_INTERVAL = int(input("Enter the time interval between buses in minutes: "))
NORMAL_TRAVEL_TIME = int(input("Enter the normal travel time for a route in minutes: "))
TRAFFIC_TRAVEL_TIME = int(input("Enter the travel time during traffic hours in minutes: "))
SIMULATION_TIME = int(input("Enter the total simulation time in minutes (1 day): "))
MEAN_PASSENGER_ARRIVAL = float(input("Enter the mean passenger arrival interval in minutes: "))
STD_PASSENGER_ARRIVAL = float(input("Enter the standard deviation for passenger arrival interval in minutes: "))
BUS_CAPACITY = int(input("Enter the bus capacity: "))
MEAN_LATE_EARLY = float(input("Enter the mean deviation for bus arrival in minutes: "))
STD_LATE_EARLY = float(input("Enter the standard deviation for bus arrival deviation in minutes: "))

# Traffic hour constants
TRAFFIC_HOURS = [(7 * 60, 9 * 60), (17 * 60, 19 * 60)]  # Traffic hours in minutes

# Bus stop constants
NUM_BUS_STOPS = 5
MEAN_STOP_INTERVAL = 10
STD_STOP_INTERVAL = 3

# Metrics
total_waiting_time = 0
total_passengers_served = 0
total_travel_time = 0
queue_sizes = []
waiting_times = []
bus_arrival_deviations = []

# Queue and server state
passenger_queue = [[] for _ in range(NUM_BUS_STOPS)]
passenger_times = []
buses = []
current_time = 0
next_passenger_id = 1
next_passenger_arrival = int(np.random.exponential(MEAN_PASSENGER_ARRIVAL))

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
end_time = 23 * 60  # 23:00 PM in minutes

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
        queue_sizes.append((current_time, len(passenger_queue[stop_id])))
        next_passenger_id += 1
        next_passenger_arrival = current_time + int(np.random.exponential(MEAN_PASSENGER_ARRIVAL))
        if next_passenger_arrival < SIMULATION_TIME:
            schedule_event(next_passenger_arrival, 'passenger_arrival')
        
    elif event_type == 'bus_arrival':
        # Handle bus arrival
        bus_arrival_time = current_time + int(np.random.normal(MEAN_LATE_EARLY, STD_LATE_EARLY))
        bus_arrival_deviations.append(bus_arrival_time - current_time)
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
            'passengers_left': []
        }

        # Passengers leaving at this stop
        for passenger in list(bus_info['passengers']):
            if passenger['alight_stop'] == stop_id:
                passenger_left_time = bus_arrival_time
                passenger['travel_time'] = passenger_left_time - passenger['board_time']
                passenger['total_time'] = max(0, passenger_left_time - passenger['arrival_time'])  # Ensure total_time >= 0
                bus_stop_info['passengers_left'].append(passenger)
                total_passengers_served += 1
                bus_info['passengers'].remove(passenger)

        # Passengers boarding at this stop
        while passenger_queue[stop_id] and bus_capacity_remaining > 0:
            arrival_time, passenger_id = passenger_queue[stop_id].pop(0)
            waiting_time = max(0, bus_arrival_time - arrival_time)  # Ensure waiting time is not negative
            alight_stop = random.randint(stop_id + 1, NUM_BUS_STOPS - 1)
            travel_time_for_passenger = travel_time if alight_stop == NUM_BUS_STOPS - 1 else bus_arrival_time + travel_time - bus_arrival_time
            
            bus_capacity_remaining -= 1

            passenger_record = {
                'passenger_id': passenger_id,
                'arrival_time': arrival_time,
                'waiting_time': waiting_time,
                'travel_time': travel_time_for_passenger,
                'total_time': max(0, waiting_time + travel_time_for_passenger),  # Ensure total_time >= 0
                'bus_id': entity_id,
                'board_time': bus_arrival_time,
                'board_stop': stop_id,
                'alight_stop': alight_stop
            }

            total_waiting_time += waiting_time
            waiting_times.append(waiting_time)
            bus_stop_info['passengers_boarded'].append(passenger_record)
            bus_info['passengers'].append(passenger_record)
            passenger_times.append(passenger_record)

        bus_info['stops'].append(bus_stop_info)
        
        if stop_id < NUM_BUS_STOPS - 1:
            next_stop_time = bus_arrival_time + travel_time + max(1, int(np.random.normal(MEAN_STOP_INTERVAL, STD_STOP_INTERVAL)))
            schedule_event(next_stop_time, 'bus_arrival', entity_id=entity_id, stop_id=stop_id + 1)

# Calculate metrics
average_waiting_time = total_waiting_time / total_passengers_served if total_passengers_served else 0
average_queue_size = sum(size for _, size in queue_sizes) / len(queue_sizes) if queue_sizes else 0
maximum_queue_size = max(size for _, size in queue_sizes) if queue_sizes else 0

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

# Plot statistics
times, sizes = zip(*queue_sizes)

plt.figure(figsize=(12, 8))

plt.subplot(3, 1, 1)
plt.plot(times, sizes, label='Queue size over time')
plt.xlabel('Time (minutes)')
plt.ylabel('Queue size')
plt.title('Queue Size Over Time')
plt.legend()

plt.subplot(3, 1, 2)
plt.hist(waiting_times, bins=30, edgecolor='black')
plt.xlabel('Waiting time (minutes)')
plt.ylabel('Frequency')
plt.title('Distribution of Passenger Waiting Times')

plt.subplot(3, 1, 3)
plt.hist(bus_arrival_deviations, bins=30, edgecolor='black')
plt.xlabel('Deviation from scheduled time (minutes)')
plt.ylabel('Frequency')
plt.title('Distribution of Bus Arrival Deviations')

plt.tight_layout()
plt.show()
