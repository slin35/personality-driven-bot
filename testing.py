import aiml

kernel = aiml.Kernel()
kernel.bootstrap(learnFiles="std-startup.xml", commands="load aiml b")
kernel.saveBrain("bot_brain.brn")

while True:
    user = input("user>>>")
    bot = kernel.respond(user)
    print("bot>>>", bot)