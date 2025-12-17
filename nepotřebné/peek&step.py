import simpy

def procesni_funkce1(env):
    print(f"t = {env.now}: start aktivity_1")
    yield env.timeout(3)
    print(f"t = {env.now}: konec aktivity_1")

def procesni_funkce2(env):
    print(f"t = {env.now}: start aktivity_2")
    yield env.timeout(5)
    print(f"t = {env.now}: konec aktivity_2")

env = simpy.Environment()
env.process(procesni_funkce1(env))
env.process(procesni_funkce2(env))

print(env.peek())
env.step()
print(env.peek())
env.step()
print(env.peek())
env.step()
print(env.peek())
env.step()
print(env.peek())
env.step()
print(env.peek())
env.step()

