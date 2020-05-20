from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
import time
import random
import requests
import auxiliar_methods as am


# agent code
class SpyAgent(Agent):
    def __init__(self, jid, password, guid, name):
        super().__init__(jid, password)
        self.guid = guid
        self.agName = name
        self.users_information = {}  # dictionary k = guid, v = (theme, selection, num messages sent)
        self.friends = []  # array containing the guid of the agent friends

    async def setup(self):
        beh = self.SpyUsers(period=900)  # every 15 minutes
        self.add_behaviour(beh)
        print('agent ready')

    class SpyUsers(PeriodicBehaviour):
        async def on_start(self):  # get_agent_friends(), select_users()
            print('first i\'m going to get my friends')
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

            print('i\'m now getting users information')
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

                        for k in content.keys():
                            if int(k) not in spy.friends:  # if it isn't a friend
                                spy.users_information[int(k)] = (
                                    i, content[k], 0)  # save the user to be contacted later
                        print('users to be contacted and users indexed by theme correctly created')
                    else:
                        print('status ' + str(i) + ' incorrect')
                        print(content)
                else:
                    print('res ' + str(i) + ' failed')
                    print(res.json())
            print('start behaviour finished')

        async def run(self):  # send_message()
            print('before starting sending messages, i\'m going to update my friendlist')
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
                        spy.friends = am.unique(spy.friends)
                    print('friendlist updated')

            print('preparing to send a lot of messages')
            for usr in spy.users_information.keys():
                info = spy.users_information[usr]
                conver = am.check_conversation(info)
                sub, con, info = am.head_body_selector(conver, spy.agName)
                print('user selected, about to send him a message')
                if usr not in spy.friends:
                    print('this user is not my friend, so let\'s go')
                    sender = requests.post('http://localhost/services/api/rest/json/?',
                                           params={'method': 'users.send_message',
                                                   'agentGUID': spy.agName,
                                                   'receiverGUID': usr,
                                                   'subject': sub,
                                                   'content': con})
                    if sender:
                        print('message sent with exit')
                    else:
                        print('message sent failed')
                        print(sender.json())

                    if info[-1] == 3:
                        print('last contact with ' + str(usr) + ' removing him from the contact list')
                        spy.users_information.pop(usr)
                else:
                    print('user ' + str(usr) + ' already is my friend, so my job with him is done.' +
                          ' Removing him from the contact list')
                    spy.users_information.pop(usr)

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
