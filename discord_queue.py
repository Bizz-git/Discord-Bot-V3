class MusicQueue:
    def __init__(self):
        self.queue = []
        self.is_playing = False

    def add(self, c_file_path, info):
        self.queue.append((c_file_path, info))

    def pop(self):
        if self.queue:
            return self.queue.pop(0)
        return None

    def clear(self):
        self.queue = []

    def is_empty(self):
        return len(self.queue) == 0

    def set_playing(self, state):
        self.is_playing = state

    def get_playing(self):
        return self.is_playing

    def get_queue(self):
        return self.queue
