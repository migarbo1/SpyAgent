from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
import time
import random
import requests


# auxiliary methods

def unique(list1):
    # intialize a null list
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
        self.users_contacted = {}  # dictionary k = guid, v = (theme, num messages sent)
        self.friends = []  # array containing the guid of the agent friends
        self.user_by_theme = {}  # dictionary k = theme, v = (user guid, selection)

    async def setup(self):
        beh = self.SpyUsers(period=900)  # every 15 minutes
        self.add_behaviour(beh)
        print('agent ready')

    class SpyUsers(PeriodicBehaviour):
        async def on_start(self):  # get_agent_friends(), select_users()
            print('first, getting friends')
            res = requests.get('http://localhost/services/api/rest/json/?',
                               params={'method': 'users.get_agent_friends',
                                       'agentGUID': spy.guid}
                               )
            if res:
                print('friends response received')
                content = res.json()
                if content['status'] == 0:
                    print('friends status good')
                    content = content['result']
                    for k in content.keys():
                        spy.friends += [int(content[k])]
                    print('friends added')
                    initial_friends = spy.friends
                else:
                    print('status incorrect')
                    print(content)
            else:
                print('res failed')
                print(res.json())

            print('now getting users information')
            for i in random.shuffle([0, 1, 2, 3, 4, 5]):
                res = requests.get('http://localhost/services/api/rest/json/?',
                                   params={'method': 'users.select_users',
                                           'theme': i,
                                           'agentGUID': spy.guid}
                                   )
                if res:
                    print('users information response received')
                    content = res.json()
                    if content['status'] == 0:
                        print('users information status good')
                        content = content['result']
                        if user_by_theme.get(i, 0) == 0:
                            spy.user_by_theme[i] = []

                        for k in content.keys():                    # for each user returned
                            tup = (int(k), content[k])
                            spy.user_by_theme[i] += [tup]           # inserts to the theme, (guid, selection)
                            if spy.users_contacted.get(int(k),0) == 0 and int(k) not in spy.friends:        # if the user hasn't been processed yet and it isn't a friend
                                spy.users_contacted[int(k)] = (i, 0)    # save the user to be contacted later
                        print('users to be contacted and users indexed by theme correctly created')
                    else:
                        print('status ' + str(i) + ' incorrect')
                        print(content)
                else:
                    print('res ' + str(i) + ' failed')
                    print(res.json())
            print('start behaviour finished')

        async def run(self):  # send_message()
            return

        async def at_end(self):  # report_info()
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
