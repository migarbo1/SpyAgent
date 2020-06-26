

class Usuario:
    def __init__(self, guid, initially_friend, is_friend):
        self.guid = guid
        self.information = list()
        self.is_friend = is_friend
        self.initially_friend = initially_friend
        self.messages_received = 0
        self.guid_of_friend = -1
        self.themes_contacted = []
        self.last_theme = -1
        self.contacted_by = ''

    def now_is_friend(self):
        self.is_friend = True
        return self
