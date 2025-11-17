import simpy
import random

class Car:
    def __init__(self, env, name, gas_station, arrival_time, refuel_time):
        self.env = env
        self.name = name
        self.gas_station = gas_station
        self.arrival_time = arrival_time
        self.refuel_time = refuel_time
        self.wait_time = 0 

        self.process = env.process(self.refuel())

    def refuel(self):
        
        yield self.env.timeout(self.arrival_time)
        print(f'{self.name} arrives at time {self.env.now}')

        start_wait = self.env.now
        
        with self.gas_station.request() as request:

            yield request
            self.wait_time = self.env.now - start_wait
            if self.wait_time > 0:
                print(f'{self.name} waited {self.wait_time} time units for a free fuel nozzle')

            print(f'{self.name} starts refueling at time {self.env.now}')
            yield self.env.timeout(self.refuel_time)
            print(f'{self.name} leaves at time {self.env.now}')


env = simpy.Environment()
gas_station = simpy.Resource(env, capacity=2)

cars = [
    Car(env, 'Car 1', gas_station, random.randint(1,5), random.randint(1,5)),
    Car(env, 'Car 2', gas_station, random.randint(1,5), random.randint(1,5)),
    Car(env, 'Car 3', gas_station, random.randint(1,5), random.randint(1,5)),
    Car(env, 'Car 4', gas_station, random.randint(1,5), random.randint(1,5)),
    Car(env, 'Car 5', gas_station, random.randint(1,5), random.randint(1,5)),
    Car(env, 'Car 6', gas_station, random.randint(6,10), random.randint(1,5)),
    Car(env, 'Car 7', gas_station, random.randint(6,10), random.randint(1,5)),
    Car(env, 'Car 8', gas_station, random.randint(6,10), random.randint(1,5)),
    Car(env, 'Car 9', gas_station, random.randint(6,10), random.randint(1,5)),
    Car(env, 'Car 10', gas_station, random.randint(6,10), random.randint(1,5)),
]

env.run()