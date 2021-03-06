from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from usuario import Usuario
import requests
import random


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
            super().__init__(period=45)
            self.agent = agent

        async def on_start(self):
            for i in range(0, len(self.agent.users)):
                user = self.agent.users[i]
                print(str(i) + ' de ' + str(len(self.agent.users)) + ' usuarios listos')
                with open('users_index.txt', 'a') as file:
                    file.write('id: ' + str(user.guid) + ' phe: ' + str(user.pheromone) + "\n")

        async def run(self):
            g = ""
            p = ""
            for gu in self.agent.users:
                if(g ==""):
                    g += str(gu.guid)
                    p += str(gu.pheromone)
                else:
                    g += "," + str(gu.guid)
                    p += "," + str(gu.pheromone)

            res = requests.get('http://localhost/services/api/rest/json/?',
                               params={'method': 'users.perform_user_simulator',
                                       'userGuids': g,
                                       'pheromones': p}
                               )
            if res:
                print('perform response received')
                content = res.text
                print(content)

    async def setup(self):
        beh = self.UserBehaviour(self)
        self.add_behaviour(beh)
        print('agent ready')


if __name__ == "__main__":
    # 3 tipos parametrizables en %.
    # guIds = [2831, 2827, 2829, 2825, 2823, 2819, 2821, 2817]

    agent_guid_pool = [1421, 1595]
    nag = 0
    res = requests.get('http://localhost/services/api/rest/json/?',
                       params={'method': 'users.return_users'}
                       )
    if res:
        content = res.json()
        if content['status'] == 0:
            content = content['result']
            guIds = list(content.keys())

    guIds.sort()

    res = requests.get('http://localhost/services/api/rest/json/?',
                       params={'method': 'users.remove_friendship'}
                       )
    correct_param = False
    while not correct_param:
        guids = guIds
        print('Introduce el número de agentes introvertidos (número entero desde 0 hasta ' + str(len(guids)) + ')')
        t1 = int(input())
        print('Introduce el número de agentes extrovertidos (número entero desde 0 hasta ' + str(len(guids) - t1) + ')')
        t3 = int(input())
        t2 = len(guids) - (t1 + t3)
        ts = [t1, t2, t3]
        if t1 >= 0 and t2 >= 0 and t3 >= 0:
            correct_param = True
        else:
            print('parámetros incorrectos, vuelvelo a intentar')
    users = []

    dict = {t1: [], t2: [], t3: []}

    cont = 0
    n = 1
    for t in ts:
        for i in range(t):
            u = FakeUser(guids[cont], False, False, 25 * n)
            dict[t].append(u)
            cont += 1
        n+=1

    with open('users_index.txt', 'w') as f:
        f.write('')

    for i in range(len(dict.keys())):
        fu = UserSimulation("fakeuser" + str(i) + "@localhost", "fakeUser" + str(i), dict[ts[i]])
        fu.start()

    '''fu1 = UserSimulation("fakeuser1@localhost", "fakeUser1", 15, [2831, 2827])  # ivan y marta
    fu2 = UserSimulation("fakeuser2@localhost", "fakeUser2", 45, [2829, 2825])  # yusuf y clara
    fu3 = UserSimulation("fakeuser3@localhost", "fakeUser3", 70, [2823, 2819])  # yessi y antonio
    fu4 = UserSimulation("fakeuser4@localhost", "fakeUser4", 90, [2821, 2817])  # vane y benja
    fu1.start()
    fu2.start()
    fu3.start()
    fu4.start()'''
