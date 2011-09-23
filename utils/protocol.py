class Message(object):
    """
    This is a message to use for comunication between Collector server and
    clients. Has the following components:

    [XXX] head: Integer zero-filled to left, 3 digits.
    [XXXXXXXX...] body: String with length as indicated in 'length' field.
    """
    HEAD_LENGTH = 3  # chars

    def __init__(self, body):
        super(Message, self).__init__()
        self.body = body

    def __unicode__(self):
        return u"%s%s%" % (str(len(self.body)).zfill(self.HEAD_LENGTH),
                self.body)

    def to_parts(self):
        return self.body.split(':')

    @classmethod
    def decode(cls, raw):
        if len(raw) < Message.HEAD_LENGTH:
            return None
        try:
            l = int(raw[:Message.HEAD_LENGTH])
        except:
            return None
        return cls(raw[Message.HEAD_LENGTH:])
