from cassandra.cluster import Cluster
from cassandra.auth import  PlainTextAuthProvider

from AI.settings import cassandre_data

ap = PlainTextAuthProvider(username=cassandre_data['username'], password=cassandre_data['password'])
cluster = Cluster(contact_points=cassandre_data['ip'],port=cassandre_data['port'], auth_provider=ap)
session = cluster.connect(keyspace=cassandre_data['query_keyspace'])
#session = cluster.connect(keyspace=cassandre_data['new_create_keyspace'])

def get_cassandre_data(sql,data):

    rs = session.execute(sql,data)

    return rs.current_rows

# sql = 'select converid,starttime,endtime,customerid,firstsupplierid from dolphin_conversation where siteid = %s AND  converid = %s ALLOW FILTERING '
# data = ('kf_8006', 'kf_8006_template_10_1533295528749347484')
# #
# print(get_cassandre_data(sql,data))
#
# for  i in get_cassandre_data(sql,data):
#     print(i.customerid)


