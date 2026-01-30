import simpy

def worker(env, done_event):
    yield env.timeout(3)
    done_event.fail(RuntimeError("Worker: Úkol se nepodařilo splnit"))

def manager(env):
    print("Manager: Zadávám úkol na 3 hodiny")
    done_event = simpy.Event(env)
    env.process(worker(env, done_event))

    try:
        yield done_event

    except RuntimeError as e:
        print(e)

env = simpy.Environment()
env.process(manager(env))
env.run()