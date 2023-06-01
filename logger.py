from datetime import datetime
from os import mkdir

class Logger:
    def __init__(self):
        try:
            mkdir('log')
            self.file = open(f"log/{datetime.today().strftime('%Y-%m-%d')}-logs.txt", "a")
            print("Opened log file...")
        
        except Exception as e:
            print("!!!Can't open log directory or file!!!")
            print(f'Reason: {e}')

    def log(self, data, action: str):
        self.file.write(f"{datetime.today().strftime('%Y-%m-%d %H:%M:%S')} --- {str(data)}  --- {action}\n")