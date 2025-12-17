import random
import simpy

position = {"Robot A": 0, "Robot B": 5}

def robot(env, name, event):
    while True:

        if position["Robot A"] == position["Robot B"]: 
            event.succeed()  
            break

        else:
            print(f"{env.now}: {name} je na pozici {position[name]} a začal se pohybovat")

        if name == "Robot A":
            position[name] += 1
        else:
            position[name] -= 1

        yield env.timeout(random.randint(1, 3))
        print(f"{env.now}: {name} se zastavil a rozhlíží se")
        yield env.timeout(1)

def meeting_callback(event):
    print(f"Roboti se potkali na pozici ", position)

env = simpy.Environment()
meeting_event = env.event()
meeting_event.callbacks.append(meeting_callback)

env.process(robot(env, "Robot A", meeting_event))
env.process(robot(env, "Robot B", meeting_event))

env.run(until=meeting_event)