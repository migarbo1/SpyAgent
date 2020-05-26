import random
import message_content as mc
import requests


def check_conversation(tup_list):
    """
        returns true and the conversation, if has been contacted. False and a random conversation otherwise
        cases:
        - the user has been contacted and the conversation is finished
        - the user has been contacted and the conversation is NOT finished
        - the user hasn't been contacted
        in this method we are looking for the two lasts cases
    """

    for tup in tup_list:
        if 0 < tup[-1] < 3:
            return tup

    tup_index = random.randint(0, len(tup_list) - 1)
    return tup_list[tup_index]


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
    to_remove = (to_add[0], to_add[1], to_add[-1]-1)
    aux = []
    for item in array:
        if item != to_remove:
            aux += [item]
        else:
            aux += [to_add]
    return aux
