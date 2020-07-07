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
                with open('users_index.txt', 'a') as file:
                    file.write('id: ' + str(user.guid) + ' phe: ' + str(user.pheromone) + "\n")

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
    guIds = [2831, 2827, 2829, 2825, 2823, 2819, 2821, 2817]

    correct_param = False
    while not correct_param:
        print('¿cuántos usuarios quieres tener en activo? Como máximo pueden ser ' + str(len(guIds)))
        max = int(input())
        guids = guIds[0:max]
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
