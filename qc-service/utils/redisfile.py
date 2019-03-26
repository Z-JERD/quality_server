import json
from django_redis import get_redis_connection

class DealRedis(object):

    def __init__(self):
        self.conn = get_redis_connection('default')

    def get_redis(self, key):
        if self.conn.exists(key) and self.conn.ttl(key) != 0:
            conn_data = self.conn.get(key)
            data = json.loads(conn_data.decode('utf8'))
            return data
        else:
            return key

    def join_redis(self, key, value):
        value = json.dumps(value)
        self.conn.set(key, value, ex=1209600)

    def delete_redis(self, key):
        self.conn.delete(key)

    def find_delete_key(self,key):
        keys = self.conn.scan_iter(key)
        if keys:
            for key in keys:
                self.conn.delete(key)

    def find_get_key(self,key):
        keys = self.conn.scan_iter(key)
        data_list = []
        key_not_redis = []
        if keys:
            for key in keys:
                data = self.get_redis(key)
                if data != key:
                    data_list.append(data)
                else:
                    key_not_redis.append(data)
        return data_list, key_not_redis