import random
import utils


def get_random_user_agent():
    with open("agents/agents.txt", "r") as f:
        agents = f.readlines()

    return agents[utils.clamp(0, random.randint(0, 30), len(agents) - 1)]
