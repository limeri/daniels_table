import logging

log = logging.getLogger()


class DisplayData:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DisplayData, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.data = []

    def save(self, message):
        self.data.append(message)
        return message

    def error(self, message):
        self.data.append('Error: ' + message)
        return message

    def to_string(self):
        messages = '\n -'.join(self.data)
        msg = 'The messages are:\n{}'.format(messages)
        return msg
