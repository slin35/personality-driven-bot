import sys
import socket
import time

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
        self.irc.send(bytes(f"PRIVMSG {self.channel} {msg}\n", "UTF-8"))

    def start(self):
        self.connect()

        while True:
            text = self.get_response()
            print(text)

            if "hello" in text:
                self.send("hello!")

            if "die" in text:
                self.send("Bye!")
                self.irc.shutdown(socket.SHUT_RDWR)
                self.irc.close()
                sys.exit()



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