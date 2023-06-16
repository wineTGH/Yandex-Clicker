from yandexClicker.main import main

with open("proxys.txt", "r") as f:
    proxys = [proxy.split() for proxy in f.readlines() if "#" not in proxy]

    for type, ip in proxys:
        main(type, ip)