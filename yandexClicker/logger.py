from datetime import datetime
from os import mkdir
from os.path import exists

class Logger:
    def __init__(self):
        try:
            if not exists('log'):
                mkdir('log')
                
            self.file = open(f"log/{datetime.today().strftime('%Y-%m-%d')}-logs.txt", "a")
        
        except Exception as e:
            print("!!!Can't open log directory or file!!!")
            print(f'Reason: {e}')

    def log(self, *data, action: str):
        log_str = f"{datetime.today().strftime('%Y-%m-%d %H:%M:%S')} --- {' '.join(data)}  --- {action}\n"
        print(f"{datetime.today().strftime('%Y-%m-%d %H:%M:%S')} --- {action}")
        self.file.write(log_str)