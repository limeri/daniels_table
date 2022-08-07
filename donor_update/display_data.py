# This class is a singleton that will store log messages that can be displayed to the user later.  It was
# possible to accomplish this by extending the log functions, but that would probably mess up the line and
# method names in the messages.  Instead, the calls in this class can be wrapped inside of a log call and
# the will save the message internally and then return the message so the log call can display it as well.
# This also allows the developer to choose exactly what messages are saved to be displayed to the user.
#
# dd = display_data.DisplayData()
# log.info(dd.save('This is my standard message.'))
# log.error(dd.save('This is my error message.'))
#
# This class must be a Singleton so that the messages are always saved in one place.
#
class DisplayData:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DisplayData, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.messages = []

    # This method will save a standard message in the data list.
    #
    # Args -
    #   message - the message to save
    #
    # Returns - the message
    def save(self, message):
        self.messages.append(message)
        return message

    # This method will save an error message in the data list.  It will prepend "Error: " to the message.
    #
    # Args -
    #   message - the message to save
    #
    # Returns - the message (with no changes)
    def error(self, message):
        self.messages.append('Error: ' + message)
        return message

    # This method will create a single string of the message list separated by new lines.  Each message but the
    # first will have a dash before it as a bullet.
    def to_string(self):
        return '\n- '.join(self.messages)
