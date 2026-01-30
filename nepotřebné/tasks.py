import simpy

def student(env, duration):
    yield env.timeout(duration)
    result = 2 + 3
    return result

def teacher(env):
    result = yield env.process(student(env, 3))
    print(result)

env = simpy.Environment()
env.run(env.process(teacher(env)))