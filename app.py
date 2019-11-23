# app.py
import os
import psycopg2
import logging
from flask import Flask, request, jsonify
app = Flask(__name__)

#logging.basicConfig(filename='example.log')
logging.basicConfig(level=logging.INFO)

def is_request_valid(request):
    is_token_valid = request.form.get('token', None) == '6mPhVZmqSZ57QFfMioqhl1Ra'
    is_team_valid = request.form.get('team_id', None) == 'T70DXRVH6'
    return is_token_valid and is_team_valid

@app.route('/', methods=['POST'])
def ndap_thanks():
    if not is_request_valid(request):
        abort(400)
    else: #Response to Slack
        # Parse the parameters you need
        command = request.form.get('command', None)
        thx_who = request.form.get('user_name', None)
        req_text = request.form.get('text', None)
        logging.info(thx_who)
        logging.info(req_text)

        #Split and convert to get the needed data
        data = req_text.split(" ",2)
        try:
            thx_amount = int(data[0])
            print(thx_amount)
        except ValueError:
            print(data[0],"is not an int!")

        if data[1][0] == '@':
            thx_to_whom = data[1][1:]
            print(thx_to_whom)
        else:
            print(data[1],"is not a valid '@mention' !")

        thx_for_what = data[2]
        print(thx_for_what)

        conn = None
        try:
            #set windows env variable
            #set DATABASE_URL=postgres://vxkhlsqjazuwxi:9acac04cf61d6527f61d74c2036263653c7154934a04a7c24fa55d54f694d14c@ec2-54-228-207-163.eu-west-1.compute.amazonaws.com:5432/d6fhd2k9uscss7
            DATABASE_URL = os.environ['DATABASE_URL']
            # connect to the PostgreSQL server
            print('Connecting to the PostgreSQL database...')
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            # create a cursor
            cur = conn.cursor()

            # execute a statement
            postgres_insert_query = """INSERT INTO thanks_data (c_who, c_amount, c_to_whom, c_for_what) VALUES (%s, %s, %s, %s) RETURNING id;"""
            record_to_insert = (thx_who,thx_amount, thx_to_whom,thx_for_what)
            cur.execute(postgres_insert_query, record_to_insert)

            # display the PostgreSQL database SQL result
            db_sql_result = cur.fetchone()[0]
            print('SQL Result:', db_sql_result)

            # commit the changes to the database
            conn.commit()

            # close the communication with the PostgreSQL
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
                print('Database connection closed.')

        return jsonify(
            response_type='in_channel',
            text='<https://youtu.be/frszEJb0aOo|General Kenobi!>',
            )

# A welcome message to our server
@app.route('/', methods=['GET'])
def index():
    return "<h1>Welcome to NDAP Thanks!!</h1>"

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
