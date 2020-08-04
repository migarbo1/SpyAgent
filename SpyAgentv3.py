import usuario
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
import random
import requests
import auxiliar_methods as am


class SpyAgent(Agent):
    def __init__(self, jid, password, guid, nam):
        super().__init__(jid, password)
        self.guid = guid
        self.agName = nam
        self.users_retrived = []
        self.is_done = False

    async def setup(self):
        beh = self.SpyUsers(self)  # has to be set to 15 minutes
        self.add_behaviour(beh)
        print('agent ready')

    class SpyUsers(PeriodicBehaviour, Agent):

        def __init__(self, agent):
            super().__init__(period=120)
            self.agent = agent

        async def on_start(self):
            print('Hello i\'m ' + self.agent.agName)
            friends_guid = []
            friends_guid += am.get_friends(self.agent.guid)
            print('process finished')

            for g in friends_guid:
                usr = usuario.Usuario(g, True, True)
                self.agent.users_retrived += [usr]

            indexes = [0, 1, 2, 3, 4]
            random.shuffle(indexes)
            for i in indexes:
                res = requests.get('http://localhost/services/api/rest/json/?',
                                   params={'method': 'users.select_users',
                                           'theme': i,
                                           'agentGUID': self.agent.guid}
                                   )
                if res:
                    print('users information response received')
                    content = res.json()
                    if content['status'] == 0:
                        print('users information status good')
                        content = content['result']
                        for k in content.keys():
                            if int(k) not in agent_guid_pool:
                                aux = am.get_user(self.agent.users_retrived, int(k))
                                if aux == -1:
                                    usr = usuario.Usuario(int(k), False, False)
                                    usr.information.append((i, content[k]))
                                    self.agent.users_retrived += [usr]
                                else:
                                    self.agent.users_retrived.remove(aux)
                                    aux.information.append((i, content[k]))
                                    self.agent.users_retrived += [aux]
                        print(
                            'users to be contacted and users indexed by theme correctly created with theme ' + str(
                                i))
            print('start behaviour finished')

        async def run(self):
            print('before starting sending messages')
            friends_guid = []
            friends_guid += am.get_friends(self.agent.guid)

            friends_guid = am.unique(friends_guid)
            for f in friends_guid:
                print(f)
                for i in range(len(self.agent.users_retrived)):
                    if f == self.agent.users_retrived[i].guid:
                        print('making an user my friend')
                        self.agent.users_retrived[i].is_friend = True
            print('friendlist updated')

            print('preparing to send a lot of messages')
            for i in range(len(self.agent.users_retrived)):
                u = self.agent.users_retrived[i]
                print(u.to_String())
                print('user selected, about to send him a message')
                if not u.is_friend:
                    if u.current_info is None:
                        index = random.randint(0, len(u.information) -1)
                        u.current_info = u.information[index]
                    info = u.current_info  # no ha hecho falta check_conversation
                    sub, con = am.head_body_selector(info, u.messages_received, self.agent.agName)
                    self.agent.users_retrived[i].themes_contacted += [info[0]]
                    self.agent.users_retrived[i].last_theme = info[0]

                    self.agent.users_retrived[i].contacted_by = self.agent.agName
                    print('this user is not my friend, so let\'s go')
                    sender = requests.post('http://localhost/services/api/rest/json/?',
                                           params={'method': 'users.send_message',
                                                   'agentGUID': self.agent.guid,
                                                   'receiverGUID': u.guid,
                                                   'subject': sub,
                                                   'content': con})
                    if sender:
                        print('message sent with exit with status: ' + str(sender.json()))
                        self.agent.users_retrived[i].messages_received += 1
                    else:
                        print('message sent failed')
                        print(sender.json())

                    print('after sending the message, i\'m going to send a friend request')
                    sender = requests.post('http://localhost/services/api/rest/json/?',
                                           params={'method': 'users.send_Friend_Request',
                                                   'agentGUID': self.agent.guid,
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
                              + ' messages about ' + str(u.last_theme))
                if self.agent.users_retrived[i].messages_received > 0 and self.agent.users_retrived[i].messages_received % 3 == 0:
                    # self.agent.users_retrived[i].information.pop(0)
                    self.agent.is_done = True

            if self.agent.is_done:
                self.kill()

        async def on_end(self):
            print('before finishing my behaviour, i\'m going to check my friends')
            friends_guid = []
            friends_guid += am.get_friends(self.agent.guid)

            for g in friends_guid:
                for i in range(len(self.agent.users_retrived)):
                    if self.agent.users_retrived[i].guid == g:
                        self.agent.users_retrived[i].is_friend = True
            print('process finished')
            print('Reporting stats...')
            print(len(self.agent.users_retrived))
            am.table_results(self.agent.users_retrived)


# main
if __name__ == "__main__":

    agent_guid_pool = [1421, 1595]
    agent_name_pool = ["Manolo", "Pedrito"]
    for i in range(len(agent_name_pool)):
        spy = SpyAgent("agente" + str(i) + "@localhost", "agente" + str(i), agent_guid_pool[i], agent_name_pool[i])
        spy.start()
