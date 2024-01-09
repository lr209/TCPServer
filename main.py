import socket
import threading

host = '127.0.0.1'
port = 5050

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

client_Names = []
client_Usernames = []


def broadcast(message):
    for client in client_Names:
        client.send(message)


def handle(client):
    while True:
        try:
            msg = message = client.recv(1024)
            if msg.decode('ascii').startswith('KICK'):
                if client_Usernames[client_Names.index(client)] == 'admin':
                    username_to_kick = msg.decode('ascii')[5:]
                    kick_user(username_to_kick)
                else:
                    client.send('Command refused.'.encode('ascii'))
            elif msg.decode('ascii').startswith('BAN'):
                if client_Usernames[client_Names.index(client)] == 'admin':
                    name_to_ban = msg.decode('ascii')[4:]
                    kick_user(name_to_ban)
                    with open('banlist.txt', 'a') as f:
                        f.write(f'{name_to_ban}\n')
                    print(f'{name_to_ban} is banned.')
                else:
                    client.send('Command refusesd.'.encode('ascii'))
            else:
                broadcast(message)
        except:
            index = client_Names.index(client)
            client_Names.remove(client)
            client.close()
            usernames = client_Usernames[index]
            broadcast(f'{usernames} left the chat.'.encode('ascii'))
            client_Usernames.remove(usernames)
            break


def receive():
    while True:
        client, address = server.accept()
        print(f'Connected with {str(address)}')

        client.send('USERNAME'.encode('ascii'))

        usernames = client.recv(1024).decode('ascii')

        with open('banlist.txt', 'r') as f:
            bans = f.readlines()
        if usernames + '\n' in bans:
            client.send('BAN'.encode('ascii'))

        if usernames == 'admin':
            client.send('PASS'.encode('ascii'))
            password = client.recv(1024).decode('ascii')

            if password != 'adminpass':
                client.send('REFUSE'.encode('ascii'))
                client.close()
                continue

        client_Usernames.append(usernames)
        client_Names.append(client)

        print(f'Username of client is {usernames}.')
        broadcast(f'{usernames} joined the chat.\n'.encode('ascii'))
        client.send('Connected to the server.'.encode('ascii'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


def kick_user(name):
    if name in client_Usernames:
        name_index = client_Usernames.index(name)
        client_to_kick = client_Names[name_index]
        client_Names.remove(client_to_kick)
        client_to_kick.send('You are kick off the server.'.encode('ascii'))
        client_to_kick.close()
        client_Usernames.remove(name)
        broadcast(f'{name} was removed from the server.'.encode('ascii'))


print("Server is listening....")
receive()
