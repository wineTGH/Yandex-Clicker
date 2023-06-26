from yandexClicker.main import main

with open("proxys.txt", "r") as f:
    proxys = [proxy.split() for proxy in f.readlines() if "#" not in proxy]
    if len(proxys) > 0:
        for type, ip in proxys:
            main(type, ip)
    else:
        main()