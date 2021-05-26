import sys
import socket
import time
import aiml
import os
import memory

class IRCBot:
    def __init__(self, server, port, channel, nickname):
        self.irc = socket.socket()
        self.server = server
        self.port = port
        self.channel = channel
        self.nickname = nickname
        self.memory = memory.Memory()

    def connect(self):
        self.irc.connect((self.server, self.port))
        self.irc.send(bytes(f"USER {self.nickname} {self.nickname} {self.server} :{self.nickname}\n", "UTF-8"))
        self.irc.send(bytes(f"NICK {self.nickname}\n", "UTF-8"))
        self.irc.send(bytes(f"JOIN {self.channel}\n", "UTF-8"))

    def get_response(self):
        time.sleep(1)
        resp = self.irc.recv(2040).decode("UTF-8")
        return resp

    def send(self, msg):
        self.irc.send(bytes(f"PRIVMSG {self.channel} :{msg}\n", "UTF-8"))

    def start(self):
        self.connect()

        self.setup_kernel()

        while True:
            msg = self.get_response()
            self.process_utterance(msg)
            
    def setup_kernel(self):
        self.kernel = aiml.Kernel()

        if os.path.isfile("bot_brain.brn"):
            self.kernel.bootstrap(brainFile = "bot_brain.brn")
        else:
            self.kernel.bootstrap(learnFiles="std-startup.xml", commands="load aiml b")
            self.kernel.saveBrain("bot_brain.brn")

    def process_utterance(self, msg):
        # message format <nickname_of_sender>!<hostname> PRIVMSG <channel> :<message>
        print(msg)
        if msg.find("PRIVMSG") != -1:
            user = msg.split('!', 1)[0][1:]
            channel = msg.split('PRIVMSG', 1)[1].split(':', 1)[0] or ''
            userMsg = msg.split('PRIVMSG', 1)[1].split(':', 1)[1] or ''

            if f"{self.nickname}:die" in userMsg:
                self.send("Bye!")
                self.irc.send(bytes(f"QUIT\n", "UTF-8"))
                self.irc.shutdown(socket.SHUT_RDWR)
                self.irc.close()
                sys.exit()
            elif f"{self.nickname}:*forget" in userMsg:
                self.memory.reset()
            elif "list" in userMsg:
                self.irc.send(bytes(f"NAMES {self.channel}\n", "UTF-8"))
                names = self.get_response().split(":")[2].strip('\r\n')
                self.send(names)
            elif 'Hi' in userMsg or "Hello" in userMsg or 'hi' in userMsg or 'hello' in userMsg:
                response = f"{self.kernel.respond('hello')} {user}"
                self.send(response)
            elif f"{self.nickname}:" in userMsg:
                userMsg = userMsg.split(':', 1)[1]
                response = self.kernel.respond(userMsg)

                words = ['chatbot', 'chatbots', 'bot', 'bots']
                words_in_msg = any(x in userMsg for x in words)
                
                if "don't like" in userMsg and words_in_msg:
                    response = "That's unfortunate. What do you like then?"
                elif 'like' in userMsg and words_in_msg:
                    response = self.kernel.respond("chatbot")
                    response = response[0].lower() + response[1:]
                    response = f"I like chatbots too! Do you know that {response}"
                elif 'favorite' in userMsg and words_in_msg:
                    chatbot = userMsg.split()[-1]
                    response = self.kernel.respond(chatbot)
                    response = response[0].lower() + response[1:]
                    response = f"Speaking of {chatbot}, {response}"
                elif words_in_msg:
                    response = self.kernel.respond("snide")

                self.send(response)

                if user in self.memory.mem:
                    response = ''
                    if self.memory.mem[user].snide:
                        response = f'You mentioned chatbots last time, what else do you know?'
                        self.send(response)
                        response = self.kernel.respond("snide")
                    elif self.memory.mem[user].fav_chatbot:
                        response = f'You mentioned your favorite chatbot is {self.memory.mem[user.fav_chatbot]} last time, I also happened to know a few more things about it.'
                        self.send(response)
                        response = self.kernel.respond(self.memory.mem[user.fav_chatbot])
                    elif self.memory.mem[user].chatbot_interest == False:
                        response = 'You never mention it. Do you like chatbots?'
                    elif self.memory.mem[user].chatbot_interest:
                        response = self.kernel.respond("snide")
                        response = f'You expressed interest about chatbots. {response}'
                    elif self.memory.mem[user].chatbot_dislike:
                        response = "It's a shame that you're not interested in chatbots."

                    if response:
                        self.send(response)

                self.memory.update_mem(user, userMsg)
            else:               
                pass


def main():
    '''    
    if len(sys.argv) != 4:
        print("Usage: testbot <server[:port]> <channel> <nickname>")
        sys.exit(1)

    _idx = sys.argv[1].find(":")

    server = sys.argv[1][:_idx] if _idx != -1 else sys.argv[1]
    port = sys.argv[1][_idx:] if sys.argv[1][_idx:].isnumeric() else 6667
    channel = sys.argv[2]
    nickname = sys.argv[3]
    '''

    server = "irc.freenode.net"
    port = 6667
    channel = "#CSC582"
    nickname = "sheldon-bot"
    if "-bot" not in nickname:
        print("chatbot's nickname must end with string '-bot'")
        sys.exit(1)

    bot = IRCBot(server, port, channel, nickname)
    bot.start()


if __name__ == "__main__":
    main()