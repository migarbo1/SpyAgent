import random
import message_content as mc
import requests
import matplotlib.pyplot as plt

diction = {1421: "Manolo", 1595: "Pedrito"}


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


def head_body_selector(info, nmes, spyname):
    sub = " "
    con = " "

    if nmes % 3 == 0:
        print('fist time contacting this dude')
        sub = "Hola, soy " + spyname
        t = mc.themes[info[0]]
        s = info[1]
        con = "He visto en tu perfil que a ti tambien te gusta " + mc.predef_msg[t, s]

    if nmes % 3 == 1:
        print('second time contacting this dude')
        sub = "Hola otra vez"
        s = info[1]
        con = "No has aceptado mi solicitud de amistad :(  Podemos ser muy buenos amigos y hablar sobre " + \
              s

    if nmes % 3 == 2:
        print('last time contacting this dude')
        sub = "¿No quieres ser mi amigo?"
        con = "¿Por qué no quieres ser mi amigo? " \
              " pensaba que teniamos cosas en común..."

    return sub, con


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

    print(friends)
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


def plot_results(users):
    pieLabels = 'Accepted', 'Denied'
    pos = 0
    neg = 0
    theme_histogram_labels = ["película", "deporte", "mascota", "música", "videojuego"]
    theme_data = [0, 0, 0, 0, 0]
    nmes_dict = {}
    nmes_data = []
    manolo = 0
    pedrito = 0
    for u in users:
        if u.is_friend:
            pos += 1
            theme_data[u.last_theme] += 1
            if nmes_dict.get(u.messages_received, -5) == -5:
                nmes_dict[u.messages_received] = 1
            else:
                nmes_dict[u.messages_received] += 1
            if u.contacted_by == "Manolo":
                manolo += 1
            else:
                pedrito += 1
        else:
            neg += 1

    for n in nmes_dict.keys():
        nmes_data += [nmes_dict[n]]

    data = [pos, neg]
    f1 = plt.figure(1)
    plt.pie(data,
            labels=pieLabels,
            autopct='%1.2f',
            startangle=90)
    plt.axis('equal')
    f1.savefig('piechart.png')

    f2 = plt.figure(2)
    plt.bar(theme_histogram_labels, theme_data, label='new friends per theme')
    plt.xlabel('Themes')
    plt.ylabel('Number of new friends')
    f2.savefig('theme_histogram.png')

    f3 = plt.figure(3)
    plt.bar(nmes_dict.keys(), nmes_data, label='new friends per message sent')
    plt.xlabel('Number of messages')
    plt.ylabel('Number of new friends')
    f3.savefig('message_number_histogram.png')

    f4 = plt.figure(4)
    plt.bar(["Manolo", "Pedrito"], [manolo, pedrito], label='friends added by each identity')
    plt.xlabel('Name of the spy user')
    plt.ylabel('Number of new friends')
    f4.savefig('identity_histogram.png')


def table_results(user_Array):
    with open("results_table.txt", 'a') as file:
        for u in user_Array:
            file.write(
                str(u.guid) + "\t" + u.contacted_by + "\t" + str(u.initially_friend) + "\t" + str(u.is_friend) + "\t" + str(u.messages_received) + "\t" + str(u.last_theme) + "\n")


def any_one_or_two(ar):
    for a in ar:
        n = a[-1]
        if 1 <= n <= 2:
            return True
    return False


def get_user(array, guid):
    for u in array:
        if guid == u.guid:
            return u

    return -1
