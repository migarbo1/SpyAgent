from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from usuario import Usuario
import requests
import random

agent_guid_pool = [1421, 1595]


class FakeUser(Usuario):
    def __init__(self, guid, initially_friend, is_friend, ph):
        Usuario.__init__(self, guid, initially_friend, is_friend)
        self.pheromone = ph + random.randint(-5, 5)


class UserSimulation(Agent):
    def __init__(self, jid, password, identities):
        super().__init__(jid, password)
        self.users = identities

    def kill(self):
        super().stop()

    class UserBehaviour(PeriodicBehaviour, Agent):
        def __init__(self, agent):
            super().__init__(period=60)
            self.agent = agent

        async def on_start(self):
            for i in range(0, len(self.agent.users)):
                user = self.agent.users[i]
                for j in agent_guid_pool:
                    print('deleting friends')
                    res = requests.get('http://localhost/services/api/rest/json/?',
                                       params={'method': 'users.remove_friendship',
                                               'friend1': user.guid,
                                               'friend2': j}
                                       )
                    print(res.json())

        async def run(self):
            for gu in self.agent.users:
                print('performing user simulation')
                res = requests.get('http://localhost/services/api/rest/json/?',
                                   params={'method': 'users.perform_user_simulator',
                                           'userGuid': gu.guid,
                                           'pheromone': gu.pheromone}
                                   )
                if res:
                    print('perform response received')
                    content = res.json()
                    print(content)
                    if content['status'] == 0:
                        print('perform status good')
                        content = content['result']
                        print(content)

    async def setup(self):
        beh = self.UserBehaviour(self)
        self.add_behaviour(beh)
        print('agent ready')


if __name__ == "__main__":
    # 3 tipos parametrizables en %.
    guids = [2831, 2827, 2829, 2825, 2823, 2819, 2821, 2817]
    t1 = 2
    t2 = 2
    t3 = len(guids) - (t1 + t2)
    ts = [t1, t1 + t2, t3]
    users = []

    for i in range(len(guids)):
        if i < ts[0]:
            p = 25
        elif i < ts[1]:
            p = 50
        else:
            p = 75
        u = FakeUser(guids[i], False, False, p)
        users.append(u)

    base = 0
    for i in range(3):
        aux = ts[i]
        fu = UserSimulation("fakeuser" + str(i) + "@localhost", "fakeUser" + str(i), users[base:aux])
        fu.start()
        base = aux

    '''fu1 = UserSimulation("fakeuser1@localhost", "fakeUser1", 15, [2831, 2827])  # ivan y marta
    fu2 = UserSimulation("fakeuser2@localhost", "fakeUser2", 45, [2829, 2825])  # yusuf y clara
    fu3 = UserSimulation("fakeuser3@localhost", "fakeUser3", 70, [2823, 2819])  # yessi y antonio
    fu4 = UserSimulation("fakeuser4@localhost", "fakeUser4", 90, [2821, 2817])  # vane y benja
    fu1.start()
    fu2.start()
    fu3.start()
    fu4.start()'''
