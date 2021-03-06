from flask import Flask, request
import pymysql
import memcache
import redis
import random
from time import sleep
app = Flask(__name__)

testsize = 10000

while True:
    try:
        connection = pymysql.connect(host='127.0.0.1',
                                     user='maybe',
                                     password='password',
                                     db='ite3068')
        cursor = connection.cursor()
        nbase = redis.StrictRedis(host='127.0.0.1', port=6000)
        nbase.get(None)
        arcus = memcache.Client(["127.0.0.1:11211", "127.0.0.1:11212"])
        break
    except redis.ConnectionError:
        print ('Redis Connection failed ... wait for 5s')
        sleep(5)
    except:
        print ('Connection failed ... wait for 5s')
        sleep(5)

@app.route('/')
def main():
    return 'Main page'

@app.route('/init', methods=['GET'])
def init():
    cursor.execute('drop table if exists testset');
    cursor.execute('create table testset ( id int, data int );')
    for i in range(testsize):
        v = random.randint(0, testsize)
        cursor.execute('insert into testset values(%s,%s)'%(i + 1, v))
        nbase.set(i + 1, v)
    connection.commit()
    return 'Initialization finished'

def select(record_id):
    query = 'select * from testset where id=%s' % record_id
    cursor.execute(query)
    res = cursor.fetchone()
    return res

@app.route('/mysql', methods=['GET'])
def mysql():
    record_id = request.args.get('id', random.randint(1, testsize))
    return str(select(record_id))

@app.route('/arcus', methods=['GET'])
def arcus_():
    record_id = request.args.get('id', random.randint(1, testsize))
    res = arcus.get(str(record_id))
    if res:
        return 'Cache Hit: ' + str(res)
    else:
        res = select(record_id)
        arcus.set(str(record_id), res[1])
        return 'Cache Miss: ' + str(res)

@app.route('/nbase', methods=['GET'])
def nbase_():
    record_id = request.args.get('id', random.randint(1, testsize))
    res = nbase.get(record_id)
    if res:
        return 'Cache Hit: ' + str(res)
    else:
        res = select(record_id)
        nbase.set(record_id, res[1])
        return 'Cache Miss: ' + str(res)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)

