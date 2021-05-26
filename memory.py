
class Memory:
    def __init__(self):
        self.mem = {}

    def update_mem(self, user, data):
        if user in self.mem:
            self.mem[user] = self.mem[user].update(data)
        else:
            self.mem[user] = User(user)

    def reset(self):
        self.mem = {}


class User:

    def __init__(self, name):
        self.name = name
        self.chatbot_interest = False
        self.fav_chatbot = ''
        self.snide = False
        self.chatbot_dislike = False

    def update(self, data):
        words = ['chatbot', 'chatbots', 'bot', 'bots']
        words_in_msg = any(x in data for x in words)

        if "don't like" in data and words_in_msg:
            self.chatbot_dislike = True
        elif 'like' in data and words_in_msg:
            self.chatbot_interest = True
        elif 'favorite' in data and words_in_msg:
            self.fav_chatbot = data.strip().split()[-1]
        elif words_in_msg:
            self.snide = True
        

        return self