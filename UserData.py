import pickle
import getpass


class User:
    def __init__(self):
        self.default_data = {"out_directory": f"C:/Users/{getpass.getuser()}/Videos",
                             "audio_input": 0}
        self.all_data = self.load_data()

    def load_data(self):
        try:
            with open("userData.pickle", "rb") as file:
                return pickle.load(file)
        except FileNotFoundError:
            return self.default_data

    def save_data(self):
        with open("userData.pickle", "wb") as file:
            pickle.dump(self.all_data, file)

    def update_data(self, name, value):
        self.all_data[name] = value
        self.save_data()

    def get_data(self, name):
        d = self.all_data.get(name)
        if d:
            return d
        return None
