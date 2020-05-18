from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
import time
import random
import requests


# auxiliar methods

def unique(list1):
    # intilize a null list
    unique_list = []
    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    return unique_list


# agent code

class SpyAgent(Agent):
    def __init__(self, jid, password, guid, name):
        super().__init__(jid, password)
        self.guid = guid
        self.agName = name
        self.users_contacted = {}                   # dictionary k = guid, v = num messages sent
        self.friends = {}                           # array containing the guid of the agent friends
        self.user_by_theme = {}                     # dictionary k = theme, v = (user guid, selection)

    async def setup(self):
        beh = self.SpyUsers(period=900)             # every 15 minutes
        self.add_behaviour(beh)

    class SpyUsers(PeriodicBehaviour):
        async def on_start(self):                   # get_agent_friends(), select_users()
            return

        async def run(self):                        # send_message()
            return

        async def at_end(self):                     # report_info()
            return



# main

if __name__ == "__main__":
    user_com = {}
    user_by_theme = {}
    spy = SpyAgent("agente1@localhost", "agente1", 1421, "Manolo")
    spy.start()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break
    spy.stop()