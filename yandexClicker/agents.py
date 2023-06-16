import random
import yandexClicker.utils as utils


def get_random_user_agent():
    with open("yandexClicker/agents/agents.txt", "r") as f:
        agents = f.readlines()

    return agents[utils.clamp(0, random.randint(0, 30), len(agents) - 1)]
