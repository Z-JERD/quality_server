from cassandra.cluster import Cluster
from cassandra.auth import  PlainTextAuthProvider

from AI.settings import cassandre_data
#session = cluster.connect(keyspace=cassandre_data['keyspace'])

class CassandraSql(object):

    def __init__(self):
       self.ap = PlainTextAuthProvider(username=cassandre_data['username'], password=cassandre_data['password'])
       self.cluster = Cluster(contact_points=cassandre_data['ip'], port=cassandre_data['port'], auth_provider=self.ap)
       self.keyspace = cassandre_data['new_create_keyspace']
       self.data_keyspace = cassandre_data['query_keyspace']
       self.session =  self.cluster.connect(keyspace=self.keyspace)
       self.data_session = self.cluster.connect(keyspace=self.data_keyspace)

    def create_keyspace(self):
       #新建keyspace
       session = self.cluster.connect()
       query = "CREATE KEYSPACE %s WITH replication = {'class':'SimpleStrategy', 'replication_factor' : 3};" % self.keyspace
       session.execute(query)

    def create_quality_rule(self):
       #规则表
       query = "CREATE  TABLE qualityrule(rule_id text PRIMARY KEY," \
               "site_id text, " \
               "rule_name text," \
               "rule_type int," \
               "rule_description text," \
               "attribute int," \
               "mood_expression int, " \
               "condition text," \
               "grade int," \
               "is_template int);"
       self.session.execute(query)

    def create_condition(self):
       #条件表
       query = "CREATE  TABLE condition(condition_id text PRIMARY KEY," \
               "condition_name text, " \
               "description text," \
               "operator text," \
               "text_scope text," \
               "role_scope int, " \
               "reference_content text);"
       self.session.execute(query)

    def create_operator(self):
       #算子表
       query = "CREATE  TABLE operator(operation_id text PRIMARY KEY," \
               "operator_name text, " \
               "operator_type int);"
       self.session.execute(query)

    def create_task(self):
       #任务表
       query = "CREATE  TABLE task(task_id text PRIMARY KEY," \
               "site_id text, " \
               "task_name text, " \
               "start_time text," \
               "end_time text," \
               "monitor_type int, " \
               "transaction_id text);"
       self.session.execute(query)

    def create_qc_result(self):
       #质检结果表
       query = "CREATE  TABLE qcresult(transaction_id text PRIMARY KEY," \
               "siteid text," \
               "monitor_type int," \
               "starttime bigint," \
               "endtime bigint," \
               "customerid text," \
               "firstsupplierid text," \
               "ruleids text," \
               "grade int);"
       self.session.execute(query)

class  CassandraRule(CassandraSql):

    def deal_data(self, all_data):
        for data in all_data:
            dict_data = {
                'rule_id': data.rule_id,
                'site_id': data.site_id,
                'rule_name': data.rule_name,
                'rule_type': data.rule_type,
                'rule_description': data.rule_description,
                'attribute': data.attribute,
                'mood_expression': data.mood_expression,
                'condition': data.condition,
                'grade': data.grade,
                'is_template': data.is_template,
            }
            yield dict_data

    def list(self):
        result = []
        query = 'select * from qualityrule'
        rs = self.session.execute(query)
        all_data = rs.current_rows
        for data in self.deal_data(all_data):
            result.append(data)
        return result

    def search(self,data,attribute):
        result = []
        query = "select * from qualityrule WHERE site_id = %s AND attribute = %s  ALLOW FILTERING;"
        deal_data = (data,attribute,)
        rs = self.session.execute(query,deal_data)
        all_data = rs.current_rows
        for data in self.deal_data(all_data):
            result.append(data)
        return result


    def create_data(self,data):
        query = "INSERT INTO qualityrule (rule_id, site_id, rule_name,rule_type, " \
                "rule_description,attribute,mood_expression,condition,grade,is_template) " \
                "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"

        deal_data = (data['rule_id'],data['site_id'], data['rule_name'],
                data['rule_type'], data['rule_description'], data['attribute'],data['mood_expression'],
                data['condition'],data['grade'],data['is_template'])

        rs = self.session.execute(query, deal_data)

    def update_data(self, data,pk):
        query = "UPDATE qualityrule SET site_id = %s,rule_name = %s,rule_type = %s," \
                "rule_description = %s,attribute = %s,mood_expression = %s,condition = %s,grade = %s, " \
                "is_template = %s WHERE rule_id = %s;"

        deal_data = (data['site_id'], data['rule_name'],data['rule_type'],
                     data['rule_description'], data['attribute'],data['mood_expression'],
                     data['condition'],data['grade'],data['is_template'],pk,)

        rs = self.session.execute(query, deal_data)

    def delete_data(self, data):
        query = 'DELETE  FROM qualityrule WHERE rule_id= %s;'
        deal_data = (data,)
        rs = self.session.execute(query, deal_data)

class  CassandraCondition(CassandraSql):

    def deal_data(self, data):
            dict_data = {
                'condition_id': data.condition_id,
                'condition_name': data.condition_name,
                'description': data.description,
                'operator': data.operator,
                'text_scope': data.text_scope,
                'role_scope': data.role_scope,
                'reference_content': data.reference_content
            }
            return  dict_data

    def list(self):
        result = []
        query = 'select * from condition'
        rs = self.session.execute(query)
        all_data = rs.current_rows
        for data in self.deal_data(all_data):
            result.append(data)
        return result

    def search(self,data):
        result = {}
        query = "select * from condition WHERE condition_id = %s ALLOW FILTERING;"
        deal_data = (data,)
        rs = self.session.execute(query,deal_data)
        all_data = rs.current_rows
        result = self.deal_data(all_data[0])
        return result

    def create_data(self,data):
        query = "INSERT INTO condition(condition_id, condition_name, description,operator, " \
                "text_scope,role_scope,reference_content) " \
                "VALUES(%s,%s,%s,%s,%s,%s,%s);"

        deal_data = (data['condition_id'], data['condition_name'], data['condition_description'],
                data['operator'], data['text_scope'], data['role_scope'],
                data['reference_content'],)

        rs = self.session.execute(query, deal_data)

    def update_data(self, data,pk):
        query ="UPDATE condition SET condition_name = %s,description = %s,operator = %s," \
               "text_scope = %s,role_scope = %s,reference_content = %s WHERE condition_id = %s;"

        deal_data = (data['condition_name'], data['condition_description'],
                     data['operator'], data['text_scope'], data['role_scope'],
                     data['reference_content'],pk,)

        rs = self.session.execute(query, deal_data)

    def delete_data(self, data):
        query = 'DELETE  FROM condition WHERE condition_id = %s;'
        deal_data = (data,)
        rs = self.session.execute(query, deal_data)

class  CassandraOperator(CassandraSql):

    def search(self,data):
        query = "select operator_type from operator WHERE operation_id = %s ALLOW FILTERING;"
        deal_data = (data,)
        rs = self.session.execute(query,deal_data)
        data = rs.current_rows
        value = data[0].operator_type
        result = {'operator_type': value}
        return result

    def create_data(self, data):
        query = "INSERT INTO operator(operation_id,operator_name,operator_type) VALUES('op009','测试算子',9);"
        rs = self.session.execute(query)

    def delete_data(self, data):
        query = 'DELETE  FROM operator WHERE operation_id = %s;'
        deal_data = (data,)
        rs = self.session.execute(query, deal_data)

class  Cassandratask(CassandraSql):

    def deal_data(self,all_data):
        for data in all_data:
            dict_data = {
                'task_id': data.task_id,
                'site_id': data.site_id,
                'task_name': data.task_name,
                'start_time': data.start_time,
                'end_time': data.end_time,
                'monitor_type': data.monitor_type,
                'transaction_id': data.transaction_id
            }
            yield  dict_data

    def list(self):
        result = []
        query = 'select * from task'
        rs = self.session.execute(query)
        all_data = rs.current_rows
        for data in self.deal_data(all_data):
            result.append(data)
        return result

    def create_data(self,data):

        query = "INSERT INTO task (task_id,site_id,task_name,start_time, " \
                "end_time,monitor_type,transaction_id) " \
                "VALUES(%s,%s,%s,%s,%s,%s,%s);"

        deal_data = (data['task_id'], data['site_id'], data['task_name'],
                     data['start_time'], data['end_time'], data['monitor_type'], data['transaction_id'],)

        rs = self.session.execute(query, deal_data)

    def update_data(self, data,pk):
        query = "UPDATE task SET site_id = %s,task_name = %s,start_time = %s," \
                "end_time = %s,monitor_type = %s,transaction_id = %s WHERE task_id = %s;"

        deal_data = (data['site_id'], data['task_name'], data['start_time'],
                     data['end_time'], data['monitor_type'], data['transaction_id'],pk,)
        print(deal_data)
        rs = self.session.execute(query, deal_data)

    def delete_data(self, data):
        query = 'DELETE  FROM task WHERE task_id = %s;'
        deal_data = (data,)
        rs = self.session.execute(query, deal_data)

class  CassandraQcResult(CassandraSql):

    def deal_data(self,all_data):
        for data in all_data:
            dict_data = {
                'siteid': data.siteid,
                'monitor_type': data.monitor_type,
                'transaction_id': data.transaction_id,
                'starttime': data.starttime,
                'endtime': data.endtime,
                'customerid': data.customerid,
                'firstsupplierid': data.firstsupplierid,
                'ruleids': data.ruleids,
                'grade': data.grade,
            }
            yield  dict_data

    def list(self):
        query = 'select * from qcresult'
        rs = self.session.execute(query)
        all_data = rs.current_rows
        for data in self.deal_data(all_data):
            result.append(data)
        return result

    def create_data(self,data):
        query = "INSERT INTO qcresult (siteid,monitor_type,transaction_id,starttime, " \
                "endtime,customerid,firstsupplierid,ruleids,grade) " \
                "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s);"

        deal_data = (data['siteid'], data['monitor_type'], data['transaction_id'],
                     data['starttime'], data['endtime'], data['customerid'], data['firstsupplierid'],
                     data['ruleids'],data['grade'],
                     )
        rs = self.session.execute(query, deal_data)

    def get_data(self, sql, data):
        rs = self.session.execute(sql, data)
        return rs.current_rows

class CassandraGetData(CassandraSql):
    #获取会话/工单/呼叫中心的数据
    def get_data(self,sql, data):
        rs = self.data_session.execute(sql, data)
        return rs.current_rows

if __name__ == '__main__':
    cassandra_obj =  CassandraSql()
    #cassandra_obj.create_keyspace()
    #cassandra_obj.create_quality_rule()
    #cassandra_obj.create_condition()
    #cassandra_obj.create_operator()
    #cassandra_obj.create_task()
    #cassandra_obj.create_qc_result()
    #cassandra_condition =CassandraRule()
    #cassandra_condition.create_data(data )
    #operator_obj = CassandraOperator()
    #operator_obj.delete_data('op009')
