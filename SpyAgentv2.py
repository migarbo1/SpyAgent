import usuario
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
import time
import random
import requests
import auxiliar_methods as am
import queue


class SpyAgent(Agent):
    def __init__(self, jid, password, guid, nam):
        super().__init__(jid, password)
        self.guid = guid
        self.agName = nam
        self.users_retrived = []
        self.count = 0
        self.require_pers_change = False
        self.max_changes = len(agent_guid_pool) - 1

    async def setup(self):
        beh = self.SpyUsers(period=45)  # has to be set to 15 minutes
        self.add_behaviour(beh)
        print('agent ready')

    class SpyUsers(PeriodicBehaviour):
        async def on_start(self):
            print('Hello i\'m ' + spy.agName)
            friends_guid = []
            for g in agent_guid_pool:
                friends_guid += am.get_friends(g)
            print('process finished')

            for g in friends_guid:
                usr = usuario.Usuario(g, True, True)
                spy.users_retrived += [usr]

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
                    content = res.json()
                    if content['status'] == 0:
                        print('users information status good')
                        content = content['result']
                        for k in content.keys():
                            if int(k) not in agent_guid_pool:
                                aux = am.get_user(spy.users_retrived, int(k))
                                if aux == -1:
                                    usr = usuario.Usuario(int(k), False, False)
                                    usr.information.append((i, content[k]))
                                    spy.users_retrived += [usr]
                                else:
                                    spy.users_retrived.remove(aux)
                                    aux.information.append((i, content[k]))
                                    spy.users_retrived += [aux]
                        print(
                            'users to be contacted and users indexed by theme correctly created with theme ' + str(
                                i))
            print('start behaviour finished')

        async def run(self):
            print('before starting sending messages')
            friends_guid = []
            friends_guid += am.get_friends(spy.guid)

            friends_guid = am.unique(friends_guid)
            for f in friends_guid:
                print(f)
                for i in range(len(spy.users_retrived)):
                    if f == spy.users_retrived[i].guid:
                        print('making an user my friend')
                        spy.users_retrived[i] = spy.users_retrived[i].now_is_friend()
            print('friendlist updated')

            print('preparing to send a lot of messages')
            for i in range(len(spy.users_retrived)):
                u = spy.users_retrived[i]
                print('user selected, about to send him a message')
                if not u.is_friend:
                    info = u.information[0]  # no ha hecho falta check_conversation
                    sub, con = am.head_body_selector(info, u.messages_received, spy.agName)
                    spy.users_retrived[i].themes_contacted += [info[0]]
                    spy.users_retrived[i].last_theme = info[0]

                    spy.users_retrived[i].contacted_by = spy.agName
                    print('this user is not my friend, so let\'s go')
                    sender = requests.post('http://localhost/services/api/rest/json/?',
                                           params={'method': 'users.send_message',
                                                   'agentGUID': spy.guid,
                                                   'receiverGUID': u.guid,
                                                   'subject': sub,
                                                   'content': con})
                    if sender:
                        print('message sent with exit with status: ' + str(sender.json()))
                        spy.users_retrived[i].messages_received += 1
                    else:
                        print('message sent failed')
                        print(sender.json())

                    print('after sending the message, i\'m going to send a friend request')
                    sender = requests.post('http://localhost/services/api/rest/json/?',
                                           params={'method': 'users.send_Friend_Request',
                                                   'agentGUID': spy.guid,
                                                   'receiverGUID': u.guid})
                    if sender:
                        print('message sent with exit with status: ' + str(sender.json()))
                        content = sender.json()
                        if content['status'] == -1:
                            print('I\'ve already sent him a friend request and he hasn\'t answered yet')
                else:
                    if not u.initially_friend:
                        print('user ' + str(u.guid) + ' already is my friend, so my job with him is done.' +
                              ' Removing him from the contact list. i\'ve sent him ' +
                              str(u.messages_received)
                              + ' messages about ' + u.last_theme)
                if spy.users_retrived[i].messages_received == 3:
                    spy.users_retrived[i].information.pop(0)
                    spy.require_pers_change = True

            if spy.require_pers_change:
                if spy.count < spy.max_changes:
                    spy.count += 1
                    spy.agName = agent_name_pool[spy.count]
                    spy.guid = agent_guid_pool[spy.count]
                    spy.require_pers_change = False
                    print("Now i\'m " + spy.agName)
                else:
                    self.kill()

        async def on_end(self):
            print('before finishing my behaviour, i\'m going to check my friends')
            friends_guid = []
            for g in agent_guid_pool:
                friends_guid += am.get_friends(g)

            for g in friends_guid:
                for i in range(len(spy.users_retrived)):
                    if spy.users_retrived[i].guid == g:
                        spy.users_retrived[i].is_friend = True
            print('process finished')
            print('Reporting stats...')
            am.plot_results(spy.users_retrived)


# main
if __name__ == "__main__":
    agent_guid_pool = [1421, 1595]
    agent_name_pool = ["Manolo", "Pedrito"]
    spy = SpyAgent("agente1@localhost", "agente1", agent_guid_pool[0], agent_name_pool[0])
    spy.start()
