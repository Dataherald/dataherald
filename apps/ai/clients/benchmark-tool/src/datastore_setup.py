import requests
import os
import pinecone
import urllib.parse
import json

URI = "http://localhost:80/api/v1/"
PINECONE_API_KEY = '9bda1698-0de4-4cbb-8335-1bd0aa9b65b4'


def load_db_connections():
    print('loading db connections')
    with open('apps/ai/clients/benchmark-tool/init-files/db_connections.jsonl', 'r') as file:
        db_connections = list(file)
        for db_connection in db_connections:
            db_connection = json.loads(db_connection)
            payload = {
                'connection_uri': db_connection['connection_uri'],
                'use_ssh': db_connection['use_ssh'],
                'alias': db_connection['db_alias']
                }
            end_point = URI + "database?" + urllib.parse.urlencode(payload)
            if payload['use_ssh']:
                response = requests.post(end_point, json=db_connection['ssh_settings'])
            else:
                response = requests.post(end_point)
            print(response.text)
            #requests.post(URI + 'database', json=db_connection) switch to this once JC implements change


def empty_pinecone():
    print('Emptying Pinecone')
    api_key = PINECONE_API_KEY#os.environ.get("PINECONE_API_KEY")
    pinecone.init(api_key=PINECONE_API_KEY,
              environment="us-east-1-aws")
    if api_key is None:
        raise ValueError("PINECONE_API_KEY environment variable not set")

    index = pinecone.Index("benchmark")
    index.delete(delete_all=True)

if __name__ == '__main__':
    empty_pinecone()
    load_db_connections()
    
    