from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
import time
import random
import requests
import auxiliar_methods as am

mins = 20  # set it to 5 minutes


class SpyAgent(Agent):
    def __init__(self, jid, password, guid, nam):
        super().__init__(jid, password)
        self.guid = guid
        self.agName = nam
        self.users_information = {}  # dictionary k = guid, v = [(theme, selection, num messages sent), ...]
        self.friends = []  # array containing the guid of the agent friends
        self.initial_friends = []
        self.profile_changes = 0
        self.change = False
        self.users_by_profile = {}
        self.users_removed = {}

    async def setup(self):
        beh = self.SpyUsers(period=mins)  # every 15 minutes
        self.add_behaviour(beh)
        print('agent ready')

    class SpyUsers(PeriodicBehaviour):
        async def on_start(self):  # get_agent_friends(), select_users()
            print('Hello i\'m ' + spy.agName)
            for g in agent_guid_pool:
                spy.friends += am.get_friends(g)
            print('friends added')
            spy.initial_friends = spy.friends
            print('i\'m now getting users information')
            indexes = [0, 1, 2, 3, 4]
            random.shuffle(indexes)
            for i in indexes:
                res = requests.get('http://localhost/services/api/rest/json/?',
                                   params={'method': 'users.select_users',
                                           'theme': i,
                                           'agentGUID': spy.guid}
                                   )
                if res:
                    print('users information response received')
                    print(res.text)
                    content = res.json()

                    if content['status'] == 0:
                        print('users information status good')
                        content = content['result']

                        for k in content.keys():
                            if int(k) not in spy.friends:  # if it isn't a friend
                                tups = spy.users_information.get(int(k), [])
                                spy.users_information[int(k)] = tups + [(
                                    i, content[k], 0)]  # save the user to be contacted later
                        print('users to be contacted and users indexed by theme correctly created with theme ' + str(i))
                    else:
                        print('status ' + str(i) + ' incorrect')
                        print(content)
                else:
                    print('res ' + str(i) + ' failed')
                    print(res.json())
            print('start behaviour finished')

        async def run(self):  # get_friends -> send_message() -> send_friend_request()
            to_rm = []
            if not spy.users_by_profile.get(spy.agName, []):
                spy.users_by_profile[spy.agName] = []
            print('before starting sending messages')
            spy.friends += am.get_friends(spy.guid)
            spy.friends = am.unique(spy.friends)
            print('friendlist updated')

            print('preparing to send a lot of messages')
            users = spy.users_information.keys()
            for usr in users:
                spy.users_by_profile[spy.agName] += [usr]
                info = spy.users_information[usr]
                print(info)
                conver = am.check_conversation(info)
                sub, con, new_info = am.head_body_selector(conver, spy.agName)
                spy.users_information[usr] = am.update_dict_value(info, new_info)
                print('user selected, about to send him a message')
                if usr not in spy.friends:
                    print('this user is not my friend, so let\'s go')
                    sender = requests.post('http://localhost/services/api/rest/json/?',
                                           params={'method': 'users.send_message',
                                                   'agentGUID': spy.guid,
                                                   'receiverGUID': usr,
                                                   'subject': sub,
                                                   'content': con})
                    if sender:
                        print('message sent with exit with status: ' + str(sender.json()))
                    else:
                        print('message sent failed')
                        print(sender.json())

                    print('after sending the message, i\'m going to send a friend request')
                    sender = requests.post('http://localhost/services/api/rest/json/?',
                                           params={'method': 'users.send_Friend_Request',
                                                   'agentGUID': spy.guid,
                                                   'receiverGUID': usr})
                    if sender:
                        print('message sent with exit with status: ' + str(sender.json()))
                        content = sender.json()
                        if content['status'] == -1:
                            print('I\'ve already sent him a friend request and he hasn\'t answered yet')
                    else:
                        print('message sent failed')
                        print(sender.json())

                    if new_info[-1] > 2:
                        print('last contact with ' + str(usr) + ' about ' + new_info[1])
                        spy.change = True
                else:
                    print('user ' + str(usr) + ' already is my friend, so my job with him is done.' +
                          ' Removing him from the contact list. i\'ve sent him ' +
                          str(conver[-1])
                          + ' messages about ' + conver[1])
                    to_rm += [usr]
            for u in to_rm:
                spy.users_removed[u] = spy.users_information.pop(u, -1)

            if spy.change:
                spy.profile_changes += 1
                if spy.profile_changes <= 1:
                    agent_name_pool.remove(spy.agName)
                    agent_guid_pool.remove(spy.guid)
                    ind = random.randint(0, len(agent_guid_pool)-1)
                    spy.agName = agent_name_pool[ind]
                    spy.guid = agent_guid_pool[ind]
                    spy.change = False
                    print("Now i\'m " + spy.agName)
                else:
                    self.kill()

            if not spy.users_information:
                self.kill()

        async def on_end(self):  # report_info()
            #time.sleep(300)  # simulates the 5-minutes waiting time. Otherwise the last message hasn't wait time.
            print('before finishing my behaviour, i\'m going to check my friends')
            for g in agent_guid_pool:
                spy.friends += am.get_friends(g)
            spy.friends = am.unique(spy.friends)
            spy.initial_friends = am.unique(spy.initial_friends)
            print('friendlist updated')
            print('Reporting stats...')
            print('At the beginning of my duty, i had: ' + str(len(spy.initial_friends)) + ' friends')
            print('Now, at the end, i have: ' + str(len(spy.friends)) + ' friends')
            if len(spy.friends) > len(spy.initial_friends):
                new_friends = list(set(spy.friends) - set(spy.initial_friends))
                print('This means that users with guids: ' + str(new_friends) + 'have added me because of my messages')
                am.plot_results(users_removed, spy.users_information, new_friends, spy.users_by_profile)
            await self.agent.stop()


# main
if __name__ == "__main__":
    agent_guid_pool = [1421, 1595]
    agent_name_pool = ["Manolo", "Pedrito"]
    index = random.randint(0, len(agent_guid_pool)-1)
    change = False
    spy = SpyAgent("agente1@localhost", "agente1", agent_guid_pool[index], agent_name_pool[index])
    spy.start()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break
    spy.stop()
