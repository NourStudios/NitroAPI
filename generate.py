import random
import string
import requests
import time

amount = 100000

filename = "links"

def generate():
    code = ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=16))
    with open(filename + ".txt", "a") as file:
        file.write("https://discord.gift/" + code)
        file.write("\n")
        file.close()

for i in range(int(amount)):
    print("\033c")
    start = time.time()
    generate()
    end = time.time()
    print("Generated " + str(i) + " out of " + str(amount) + " links")
    if round((end - start) * int(amount) - (end - start) * i) > 60:
     print("Done! " + str(amount) + " links generated and put into " + filename + ".txt")