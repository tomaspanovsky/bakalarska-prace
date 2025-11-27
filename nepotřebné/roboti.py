import random
import simpy

position = {"Robot A": 0, "Robot B": 5}
direction = {"Robot A": "vpravo", "Robot B": "vlevo"}

def robot(env, name, event):
    while True:

        if position["Robot A"] == position["Robot B"]: 
            event.succeed()  
            break

        else:
            print(f"{env.now}: {name} je na pozici {position[name]} se začal pohybovat směrem {direction[name]}")

        if direction[name] == "vpravo":
            position[name] += 1
        else:
            position[name] -= 1

        yield env.timeout(random.randint(1, 3))
        print(f"{env.now}: {name} se zastavil a rozhlíží se")

def meeting_callback(event):
    print(f"Roboti se potkali!" , position, direction)
   
    for robot in direction:
        direction[robot] = "vlevo" if direction[robot] == "vpravo" else "vpravo"
        print(f"{robot} se otočil a odteď bude chodit {direction[robot]}")

env = simpy.Environment()
meeting_event = env.event()
meeting_event.callbacks.append(meeting_callback)

env.process(robot(env, "Robot A", meeting_event))
env.process(robot(env, "Robot B", meeting_event))

env.run(until=meeting_event)