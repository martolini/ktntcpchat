'''
KTN-project 2013 / 2014
'''
import socket
import sys
import json
from MessageWorker import ReceiveMessageWorker
import select
from time import sleep

class Client(object):

    def __init__(self):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.messages = []
        self.running = True

    def handle_login(self):
        print "Enter username: "
        username = sys.stdin.readline().strip()
        self.connection.sendall(json.dumps({'request': 'login', 'username': username}))
        response = self.connection.recv(1024)
        response = json.loads(response)
        if 'error' in response:
            print response['error']
            self.handle_login()
            return
        print 'Logged in! Type a message to get started!!!!!!!!!!!!!'
        for message in response['messages']:
            message = json.loads(message)
            self.message_received(message)

    def start(self, host, port):
        self.connection.connect((host, port))
        self.handle_login()
        self.messages = []
        ReceiveMessageWorker(self, self.connection).start()
        while self.running:
            r, _, _ = select.select([sys.stdin,], [], [] , 0.0)
            if r:
                self.send(sys.stdin.readline())


    def message_received(self, message):
        if message['response'] == 'logout':
            self.running = False
            self.connection.close()
        if 'message' in message:
            print message['message']

    def connection_closed(self):
        print 'connection closed'
        self.connection.close()

    def send(self, data):
        if data.strip().lower() == 'logout':
            message = json.dumps({'request': 'logout'})
            self.connection.sendall(message)
            return
        message = json.dumps({'request': 'message', 'message': data.strip()})
        self.connection.sendall(message)

    def force_disconnect(self):
        self.connection.close()


if __name__ == "__main__":
    client = Client()
    client.start('localhost', 9999)
