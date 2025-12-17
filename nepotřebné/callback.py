import simpy

def my_callback(event):
    print(f"Událost dokončena v čase {event.env.now}")

env = simpy.Environment()
event = env.timeout(3)
event.callbacks.append(my_callback)

env.run()