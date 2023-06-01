from datetime import datetime
from os import mkdir
from os.path import exists

class Logger:
    def __init__(self):
        try:
            if not exists('../log'):
                mkdir('../log')
                
            self.file = open(f"../log/{datetime.today().strftime('%Y-%m-%d')}-logs.txt", "a")
            print("Opened log file...")
        
        except Exception as e:
            print("!!!Can't open log directory or file!!!")
            print(f'Reason: {e}')

    def log(self, *data, action: str):
        self.file.write(f"{datetime.today().strftime('%Y-%m-%d %H:%M:%S')} --- {' '.join(data)}  --- {action}\n")