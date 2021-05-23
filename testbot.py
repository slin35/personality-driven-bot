import sys
import socket
import time
import aiml
import os

class TestBot:
    def __init__(self, server, port, channel, nickname):
        self.irc = socket.socket()
        self.server = server
        self.port = port
        self.channel = channel
        self.nickname = nickname

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
            self.kernel.bootstrap(learnFiles="std-startup.xml", commands="load aiml all")
            self.kernel.saveBrain("bot_brain.brn")

    def process_utterance(self, msg):
        # message format <nickname_of_sender>!<hostname> PRIVMSG <channel> :<message>
        print(msg)
        if msg.find("PRIVMSG") != -1:
            user = msg.split('!', 1)[0][1:]
            channel = msg.split('PRIVMSG', 1)[1].split(':', 1)[0] or ''
            userMsg = msg.split('PRIVMSG', 1)[1].split(':', 1)[1] or ''

            if f"{self.nickname}: die" in userMsg:
                self.send("Bye!")
                self.irc.send(bytes(f"QUIT\n", "UTF-8"))
                self.irc.shutdown(socket.SHUT_RDWR)
                self.irc.close()
                sys.exit()
            elif "list" in userMsg:
                self.irc.send(bytes(f"NAMES {self.channel}\n", "UTF-8"))
                names = self.get_response().split(":")[2].strip('\r\n')
                self.send(names)
            else:               
                response = self.kernel.respond(userMsg)
                self.send(response)


def main():
    if len(sys.argv) != 4:
        print("Usage: testbot <server[:port]> <channel> <nickname>")
        sys.exit(1)

    _idx = sys.argv[1].find(":")

    server = sys.argv[1][:_idx] if _idx != -1 else sys.argv[1]
    port = sys.argv[1][_idx:] if sys.argv[1][_idx:].isnumeric() else 6667
    channel = sys.argv[2]
    nickname = sys.argv[3]

    if "-bot" not in nickname:
        print("chatbot's nickname must end with string '-bot'")
        sys.exit(1)

    bot = TestBot(server, port, channel, nickname)
    bot.start()


if __name__ == "__main__":
    main()