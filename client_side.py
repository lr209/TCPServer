import socket
import threading

usernames = input("Please enter your username: ")
if usernames == 'admin':
    password = input("Enter password for admin: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect(('127.0.0.1', 5050))

stop_thread = False


def receive():
    while True:
        global stop_thread
        if stop_thread:
            break
        try:
            message = client.recv(1024).decode('ascii')
            if message == 'USERNAME':
                client.send(usernames.encode('ascii'))
                new_message = client.recv(1024).decode('ascii')
                if new_message == 'PASS':
                    client.send(password.encode('ascii'))
                    if client.recv(1024).decode('ascii') == 'REFUSE':
                        print("Incorrect password: connection refused")
                        stop_thread = True
                elif new_message == 'BAN':
                    print('Connection refused. User not allowed.')
                    client.close()
                    stop_thread =True

            else:
                print(message)
        except:
            print("Error occured")
            client.close()
            break


def write():
    while True:
        if stop_thread:
            break
        message = f'{usernames}: {input("")}'
        if message[len(usernames) + 2:].startswith('/'):
            if usernames == 'admin':
                if message[len(usernames)+2:].startswith('/kick'):
                    client.send(f'KICK {message[len(usernames)+2+6:]}'.encode('ascii'))
                elif message[len(usernames)+2:].startswith('/ban'):
                    client.send(f'BAN {message[len(usernames)+2+6:]}'.encode('ascii'))
            else:
                print("Commands can only be executed by the admin.")
        else:
            client.send(message.encode('ascii'))


receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
