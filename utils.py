import json
import string
import random
import os

class ConfigManager:
    def __init__(self, path):
        self.path = path
        self.data = self.read_from_json()


    def write_to_json(self, index, new_param) -> str:
        try:
            if not (index and new_param):
                return ""
            
            self.data[index] = new_param

            with open(self.path, "w") as json_file:
                json.dump(self.data, json_file, indent=4)
        except Exception as e:
            print('Error: ' + str(e))
        

    def read_from_json(self) -> dict:
        try:
            with open(self.path, "r") as json_file:
                j_data = json.load(json_file)
            return j_data
        except Exception as e:
            print('Error: ' + str(e))
            return {}


    def print_data(self):
        print(self.data)


    def update_values(self):
        self.data = self.read_from_json()


    def generate_random_string(self, length) -> str:
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    

    def list_file_path(self, c_path: str) -> list:
        files = []

        try:
            for file in os.listdir(c_path):
                if file.endswith(".mp3"):
                    files.append(file)
        except PermissionError as perm_err:
            return [str(perm_err)]
        

        return files
    
    
    # da sistemare, non da nessun errore solamente blocca il codice successivo alla funzione
    def remove_file_path(self, c_path: str) -> str:
        file = os.path.isfile(c_path)

        try:
            if file:
                os.remove(c_path)
        except PermissionError as perm_err:
            return perm_err
        

    def write_to_txt(c_path: str, msg) -> list:
        status = []
        try:
            with open(f"{str(c_path)}.txt", "w") as fh:
                fh.write(str(msg))
            if not fh.closed:
                fh.close()

            status = [True, f"messaggio scritto con successo sul file {c_path}"]
        except FileNotFoundError:
            print('impossibile creare il file, controllare i permessi')
            status = [False, f"impossibile scrivere sul file {c_path} - controllare i permessi"]

        return status

    def read_from_txt(c_path: str, gTTS, lang: str, slow_mode: bool) -> list:
        status = []
        try:
            with open(f"{str(c_path)}.txt", "r") as fh:
                myText = fh.read().replace("\n", " ")
                language = lang
                output = gTTS(text=myText, lang=language, tld=lang, slow=slow_mode)
            if not fh.closed:
                fh.close()
            output.save(f"{str(c_path)}.mp3")

            status = [True, f"messaggio letto con successo sul file {c_path}"]
        except FileNotFoundError:
            print('impossibile trovare il file, controllare i permessi')
            status = [False, f"impossibile leggere il file {c_path} - controllare i permessi"]
        
        return status

# how to use
# Uso della classe
# json_manager = JsonManager("config.json")

# Scrivere nel file JSON
# json_manager.write_to_json("new_key", "new_value")

# Leggere dal file JSON (automaticamente avviene all'inizializzazione)
# data = json_manager.data
# json_manager.print_data()  # Stampa i dati caricati