import time
import random

from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
import requests

"""
fields:
$object->Fav_Sport_selection = get_input('Fav_Sport_selection');
$object->Fav_film_selection = get_input('Fav_film_selection');
$object->Fav_Pet_selection = get_input('Fav_Pet_selection');
$object->Fav_Music_selection = get_input('Fav_Music_selection');
$object->Fav_VG_selection = get_input('Fav_VG_selection');
theme = "Fav_VG_selection"
selection = "Fortnite"

response = rq.get('http://localhost/services/api/rest/json/?method=users.select_users&theme='+ theme +'&selection='+ selection)

with requests.Session() as session:
    session.headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"}
    session.get("http://www.allflicks.net/")
    response = session.get(url, headers={"Accept" : "application/json, text/javascript, */*; q=0.01",
                                         "X-Requested-With": "XMLHttpRequest",
                                         "Referer": "http://www.allflicks.net/",
                                         "Host": "www.allflicks.net"})
    print(response.json())
"""


themes = {0: "película", 1: "deporte", 2: "mascota", 3: "música", 4: "videojuego"}
line_composer = {
    ("deporte", "Fútbol"): " el fútbol. A mi me encanta jugar. ¿Te gusta más jugar o verlo? ¿Me envias una petición de amistad y quedamos para jugar un dia?",
    ("deporte", "Tenis"): " el tenis. ¿Te gusta más jugar o verlo? ¿Me envias una petición de amistad y quedamos para jugar un dia?",
    ("deporte", "Voleybol"): " jugar a voleybol. ¿Te gusta más jugar o verlo? ¿Me envias una petición de amistad y quedamos para jugar un dia?",
    ("deporte", "Natación"): " practicar natación. Yo suelo ir mucho a la piscina. ¿Qué tal si nos hacemos amigos y vamos un día juntos?",
    ("deporte", "Balonecsto"): " el baloncesto. ¿Te gusta más jugar o verlo? ¿Me envias una petición de amistad y quedamos para jugar un dia?",
    ("deporte", "Atletismo"): " el atletismo. ¿Te gusta más jugar o verlo? ¿Me envias una petición de amistad y quedamos para jugar un dia?",
    ("deporte", "Pádel"): " el pádel. ¿Te gusta más jugar o verlo? ¿Me envias una petición de amistad y quedamos para jugar un dia?",
    ("deporte", "Ballet"): " bailar ballet. Si fuesemos amigos podríamos bailar juntos. ¿Qué te parece? ¿Me envias una petición de amistad?",
    ("película", "Batman"): " las películas de Batman. ¿Cuál es tu favorita? La mia es La Leyenda Renace. ¿Me envias una petición de amistad y quedamos un dia para verla?",
    ("película", "Piratas del Caribe"): " las películas de Piratas del Caribe ¿Cuál es tu favorita? La mia es la primera. ¿Me envias una petición de amistad y quedamos un dia para verla?",
    ("película", "Harry Potter"): " las películas de Harry Potter. ¿Cuál es tu favorita? La mia es el prisionero de Azkaban. ¿Me envias una petición de amistad y quedamos un dia para verla?",
    ("película", "El Señor de los Anillos"): " las películas de El Señor de los Anillos. ¿Cuál es tu favorita? La mia es El retorno del rey. ¿Me envias una petición de amistad y quedamos un dia para verla?",
    ("película", "Los juegos del Hambre"): " las películas de Los juegos del Hambre. ¿Cuál es tu favorita? La mia es Sinsajo Parte 1. ¿Me envias una petición de amistad y quedamos un dia para verla?",
    ("película", "Star Wars"): " las películas de Star Wars. ¿Cuál es tu favorita? La mia es la última. ¿Me envias una petición de amistad y quedamos un dia para verla?",
    ("película", "Jurassic Park"): " las películas de Jurassic Park. ¿Cuál es tu favorita? La mia es la primera. ¿Me envias una petición de amistad y quedamos un dia para verla?",
    ("película", "Los Vengadores"): " las películas de Los Vengadores. ¿Cuál es tu favorita? La mia es Endgame. ¿Me envias una petición de amistad y quedamos un dia para verla?",
    ("película", "Disney"): " las películas de Disney. ¿Cuál es tu favorita? La mia es la sirenita. ¿Me envias una petición de amistad y quedamos un dia para verla?",
    ("mascota", "Perro"): " los perros. ¿Tienes uno como mascota? Yo tengo una, se llama Noa. Si fuesemos amigos podríamos quedar para sacarlos a pasear. ¿Me envías una petición de amistad?",
    ("mascota", "Gato"): " los gatos. ¿Tienes uno como mascota? Yo tengo uno se llama pelusa, es muy juguetón. ¿Nos hacemos amigos y hablamos más sobre gatos?",
    ("mascota", "Periquito"): " los periquitos. ¿Tienes uno como mascota? Yo tengo uno se llama robi, es muy hablador. ¿Nos hacemos amigos y hablamos más sobre periquitos?",
    ("mascota", "Pez"): " los peces. ¿Tienes uno como mascota? Yo tengo uno se llama burbuja como la supernena, porque también es azul. ¿Nos hacemos amigos y hablamos más sobre peces?",
    ("mascota", "Conejo"): " los conejos. ¿Tienes uno como mascota? Yo tengo uno se llama pompón, es muy juguetón. ¿Nos hacemos amigos y hablamos más sobre conejos?",
    ("mascota", "Tortuga"): " las Tortugas. ¿Tienes una como mascota?",
    ("música", "Pop"): " escuchar Pop. ¿Cuál es tu grupo favorito?"




}


class StalkerAgent(Agent):
    def __init__(self, guid, jid, password, name):
        super().__init__(jid, password)
        self.guid = guid
        self.agName = name

    class StalkBehaviour(PeriodicBehaviour):
        async def on_start(self):
            for i in range(5):
                response = requests.get('http://localhost/services/api/rest/json/?',
                                        params={'method': 'users.select_users',
                                                'theme': i,
                                                'agentGUID': stalker.guid})
                if response:
                    content = response.json()
                    if content['status'] != -1:
                        content = content['result']
                        if user_by_theme.get(i, 0) == 0:
                            user_by_theme[i] = []

                        user_by_theme[i] += content.keys()
                        user_by_theme[i] = unique((user_by_theme[i]))

                        print(user_by_theme)
                        for guid in user_by_theme[i]:
                            if user_com.get(guid, 0) == 0:
                                user_com[guid] = 0
                else:
                    print('failed')

        async def run(self):
            theme = random.randint(0, 4)
            if user_by_theme.get(theme, 0) != 0:
                for user in user_by_theme[theme]:
                    n_mes = user_com.get(user)
                    subject, content = message_creator(n_mes, user)
                    sender = requests.post('http://localhost/services/api/rest/json/?',
                                           params={'method': 'users.send_message',
                                                   'agentGUID': stalker.guid,
                                                   'receiverGUID': user,
                                                   'subject': subject,
                                                   'content': content})
                    if sender:
                        print("éxito")
                        print(sender.json())
                    else:
                        print("failed")

            print("fin iteración")

    async def setup(self):
        b = self.StalkBehaviour(period=15)
        self.add_behaviour(b)


def unique(list1):
    # intilize a null list
    unique_list = []
    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    return unique_list


def message_creator(num_mes, user_guid):
    if num_mes == 0:
        # first message
        print("about to send a message")
        user_com[user_guid] += 1
        sub = "Hola, soy " + stalker.agName
        con = "He visto en tu perfil que a ti tambien te gusta " + "TO DO " + \
                  "¿Qué te parece si quedamos y hacemos " + "TO DO ?"



    if num_mes == 1:
        # second message
        user_com[user_guid] += 1
        # TO DO

    if num_mes == 2:
        # last message
        user_com[user_guid] += 1
        # TO DO
    return sub, con


if __name__ == "__main__":
    user_com = {}
    user_by_theme = {}
    stalker = StalkerAgent('1421', "agente1@localhost", "agente1", "Manolo")
    stalker.start()

    print("Wait until user interrupts with ctrl+C")
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break
    stalker.stop()
