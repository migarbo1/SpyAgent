from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
import requests
import auxiliar_methods as am


class UserSimulation(Agent):
    def __init__(self, jid, password, pheromone, identities):
        super().__init__(jid, password)
        self.pheromone = pheromone
        self.guids = identities
        self.num_friends = []
        self.cont = 0

    def kill(self):
        super().stop()

    class UserBehaviour(PeriodicBehaviour, Agent):
        def __init__(self, agent):
            super().__init__(period=70)
            self.agent = agent

        async def on_start(self):
            for i in range(0, len(self.agent.guids)):
                ident = self.agent.guids[i]
                n_friends = len(am.get_friends(ident))
                self.agent.num_friends += [n_friends]

        async def run(self):
            for gu in self.agent.guids:
                res = requests.get('http://localhost/services/api/rest/json/?',
                                   params={'method': 'users.perform_user_simulator',
                                           'userGuid': gu,
                                           'pheromone': self.agent.pheromone}
                                   )
                if res:
                    print('perform response received')
                    content = res.json()
                    print(content)
                    if content['status'] == 0:
                        print('perform status good')
                        content = content['result']
                        print(content)
            self.agent.cont += 1
            if self.agent.cont == 5:
                self.agent.kill()

    async def setup(self):
        beh = self.UserBehaviour(self)
        self.add_behaviour(beh)
        print('agent ready')


if __name__ == "__main__":
    fu1 = UserSimulation("fakeuser1@localhost", "fakeUser1", 15, [2305, 2315]) # visente y andreu
    fu2 = UserSimulation("fakeuser2@localhost", "fakeUser2", 45, [2303, 2311]) # pako y miguel
    fu3 = UserSimulation("fakeuser3@localhost", "fakeUser3", 70, [2307, 2313]) # mario y aaron
    fu4 = UserSimulation("fakeuser4@localhost", "fakeUser4", 90, [2297, 2309]) # pepe y zura
    fu1.start()
    fu2.start()
    fu3.start()
    fu4.start()
