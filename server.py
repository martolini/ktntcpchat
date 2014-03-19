'''
KTN-project 2013 / 2014
Very simple server implementation that should serve as a basis
for implementing the chat server
'''
import SocketServer, json
import re
from threading import Lock
from datetime import datetime
'''
The RequestHandler class for our server.

It is instantiated once per connection to the server, and must
override the handle() method to implement communication to the
client.
'''


class ClientHandler(SocketServer.BaseRequestHandler):

    def __init__(self, *args, **kwargs):
        SocketServer.BaseRequestHandler.__init__(self, *args, **kwargs)
        self.username = None
        self.loggedin = False

    def username_is_valid(self):
        return re.match('^[0-9a-zA-Z_]+$', self.username)

    def username_is_taken(self):
        return self.username in self.server.connections.keys()

    def handle_login(self, data):
        self.username = data['username']
        if self.username_is_valid() and not self.username_is_taken():
            self.server.connections[self.username] = self.connection
            self.connection.sendall(json.dumps({'response': 'login', 'username': self.username, 'messages': self.server.messages}))
            self.loggedin = True
            return
        if not self.username_is_valid():
            error = 'Invalid username!'
        elif self.username_is_taken():
            error = 'Name already taken!'
        self.connection.sendall(json.dumps({'response': 'login', 'username': self.username, 'error': error}))


    def handle(self):
        # Get a reference to the socket object
        self.connection = self.request
        # Get the remote ip adress of the socket
        self.ip = self.client_address[0]
        # Get the remote port number of the socket
        self.port = self.client_address[1]
        print 'Client connected @' + self.ip + ':' + str(self.port)
        while True:
            data = self.connection.recv(1024).strip()
            if data:
                data = json.loads(data)
                if data['request'] == 'login':
                    self.handle_login(data)
                elif data['request'] == 'logout':
                    message = {'response': 'logout', 'username': self.username}
                    if not self.loggedin:
                        message['error'] = "Not logged in!"
                    self.connection.sendall(json.dumps(message))
                    del self.server.connections[self.username]
                    break
                elif data['request'] == 'message':
                    if not self.loggedin:
                        message = json.dumps({'response': 'message', 'error': 'You are not logged in!'})
                        self.connection.sendall(message)
                    else:
                        message = json.dumps({'response': 'message', 'message': "<%s> said @ %s: %s" % (self.username, datetime.now().strftime("%H:%M"), data['message'])})
                        self.server.messages.append(message)
                        for conn in self.server.connections.values():
                            conn.sendall(message)
                else:
                    print 'WHAAAAAT'
            else:
                print 'Connection with %s lost' % self.ip
                del self.server.connections[self.username]
                break

        # Check if the data exists
        # (recv could have returned due to a disconnect)

'''
This will make all Request handlers being called in its own thread.
Very important, otherwise only one client will be served at a time
'''


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    def __init__(self, *args, **kwargs):
        SocketServer.TCPServer.__init__(self, *args, **kwargs)
        self.connections = {}
        self.messages = []

if __name__ == "__main__":
    HOST = 'localhost'
    PORT = 9999

    # Create the server, binding to localhost on port 9999
    server = ThreadedTCPServer((HOST, PORT), ClientHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
