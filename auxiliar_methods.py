import random
import message_content as mc
import requests
import matplotlib.pyplot as plt


def check_conversation(tup_list):
    """
        returns the conversation, if has been contacted. A random conversation otherwise
        cases:
        - the user has been contacted and the conversation is finished
        - the user has been contacted and the conversation is NOT finished
        - the user hasn't been contacted
        in this method we are looking for the two lasts cases
    """
    nc = []  # themes no contacted, created to avoid selecting a theme with 3 messages
    for tup in tup_list:
        if 0 < tup[-1] < 3:
            return tup
        if tup[-1] == 0:
            nc += [tup]

    tup_index = random.randint(0, len(nc) - 1)
    return nc[tup_index]


def head_body_selector(info, spyname):
    sub = " "
    con = " "

    if info[-1] == 0:
        print('fist time contacting this dude')
        sub = "Hola, soy " + spyname
        t = mc.themes[info[0]]
        s = info[1]
        con = "He visto en tu perfil que a ti tambien te gusta " + mc.predef_msg[t, s]

    if info[-1] == 1:
        print('second time contacting this dude')
        sub = "Hola otra vez"
        s = info[1]
        con = "No has aceptado mi solicitud de amistad :(  Podemos ser muy buenos amigos y hablar sobre " + \
              s

    if info[-1] == 2:
        print('last time contacting this dude')
        sub = "¿No quieres ser mi amigo?"
        con = "¿Por qué no quieres ser mi amigo? " \
              " pensaba que teniamos cosas en común..."

    info = (info[0], info[1], info[-1] + 1)

    return sub, con, info


def unique(list1):
    # initialise a null list
    unique_list = []
    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    return unique_list


def get_friends(spy_id):
    print('i\'m going to update my friendlist')
    friends = []
    res = requests.get('http://localhost/services/api/rest/json/?',
                       params={'method': 'users.get_agent_friends',
                               'agentGUID': spy_id}
                       )
    if res:
        print('friends response received')
        content = res.json()
        if content['status'] == 0:
            print('friends status good')
            content = content['result']
            for k in content.keys():
                friends += [int(content[k])]
        else:
            print('status incorrect')
            friends = []
            print(content)
    else:
        print('res failed')
        print(res.json())

    return friends


def update_dict_value(array, to_add):
    to_remove = (to_add[0], to_add[1], to_add[-1] - 1)
    aux = []
    for item in array:
        if item != to_remove:
            aux += [item]
        else:
            aux += [to_add]
    return aux


def plot_results(user_dict, users_added):
    # porcentaje total de éxito
    pieLabels = 'Accepted', 'Denied'
    pos = len(users_added)
    neg = len(user_dict.keys()) - pos
    print(str(pos) + "   " + str(neg))
    data = [pos, neg]
    fObject, aObject = plt.subplots()
    aObject.pie(data,
                labels=pieLabels,
                autopct='%1.2f',
                startangle=90)
    aObject.axis('equal')
    plt.show()

    # gráfico de éxito por temas
    theme_histogram_labels = ["película", "deporte", "mascota", "música", "videojuego"]
    theme_dict = {0: [], 1: [], 2: [], 3: [], 4: []}
    for user in users_added:
        info = user_dict[user]
        # if 0 -> nothing. if 1 or 2 -> save it. if 3 -> save it only if there aren't any 1 or 2
        for i in info:
            nmes = i[-1]
            if nmes != 0:
                if 1 <= nmes <= 2:
                    theme_dict[i[0]] += [user]
                    break
                elif not any_one_or_two(info):
                    theme_dict[i[0]] += [user]
                    break
    theme_data = []
    for t in theme_dict.keys():
        theme_data += [len(theme_dict[t])]

    plt.bar(theme_histogram_labels,theme_data, label='new friends per theme')
    plt.xlabel('Themes')
    plt.ylabel('Number of new friends')
    plt.show()

    # gráfico de éxito por número de mensajes recibidos
    nmes_dict = {}
    for user in users_added:
        info = user_dict[user]
        acum = 0
        for i in info:
            nmes = i[-1]
            acum += nmes
        aux = nmes_dict.get(acum,0)
        if aux == 0:
            nmes_dict[acum] = []
        nmes_dict[acum] += [user]
    nmes_data = []
    for n in nmes_dict.keys():
        nmes_data += [len(nmes_dict[n])]

    plt.bar(nmes_dict.keys(), nmes_data, label='new friends per message sent')
    plt.xlabel('Number of messages')
    plt.ylabel('Number of new friends')
    plt.show()

    # gráfico de éxito por perfil de agente

    # gráfico de éxito por sexo del usuario (pateo xD)


def any_one_or_two(ar):
    for a in ar:
        n = a[-1]
        if 1 <= n <= 2:
            return True
    return False