'''
自定义回复内容
'''

class  BaseResponse(object):
    def __init__(self):
        self.data = None
        self.msg = ""
        self.code = 1000
    @property
    def dict(self):
        return self.__dict__

class  OperatorResponse(object):
    def __init__(self):
        self.data = None
        self.msg = ""
        self.result = True
    @property
    def dict(self):
        return self.__dict__

class FieldNullException(Exception):
    def __init__(self, msg):
        self.msg = msg

class AIPException(Exception):
    def __init__(self, msg):
        self.msg = msg




