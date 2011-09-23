class Message(object):
    """
    This is a message to use for comunication between Collector server and
    clients. Has the following components:

    [XXX] head: Integer zero-filled to left, 3 digits.
    [XXXXXXXX...] body: String with length as indicated in 'length' field.

    Also the body is separated in 3 parts that will be verificated as a valid
    message:

        <server_id>:<method>:<params>

    Example:

    0201:show_status:Uptime
     | |      |         |______> 'Uptime': The variable to check.
     | |      |______> 'show_status': The method to execute.
     | |______> '1': The server Id to use.
     |______> '020': The length of entire body.

    """
    HEAD_LENGTH = 3  # chars

    def __init__(self, body):
        super(Message, self).__init__()
        self.body = body

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u"%s%s" % (str(len(self.body)).zfill(Message.HEAD_LENGTH),
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
