import socket
import threading
from Crypto.Util import number
import sys
import time
import os


def generate_large_prime():
    while True:
        candidate = number.getPrime(15)
        return candidate
def encrypt(message, key):
    encrypted_list = []
    for char in message:
        encrypted_list.append(ord(char) ^ key)

    encrypted_message = '#'.join(map(str, encrypted_list))
    return encrypted_message

def decrypt(message, key):
    encrypted_list = [int(x) for x in message.split('#')]
    decrypted_message = ''.join(chr(char ^ key) for char in encrypted_list)
    return decrypted_message

# Function to send messages
def check_phone(phone_no):
    check = False
    while check==False:
        check = True
        if len(phone_no) != 10:
            check = False
        elif phone_no[0] == "0":
            check = False
        else: 
            for digit in phone_no:
                if not digit.isdigit():
                    check = False
        if check == False:
            print("INVALID PHONE NUMBER.")
            phone_no = input("RE-ENTER YOUR PHONE NUMBER : ")
    return phone_no

def authentication(client_socket):
    #sd credential
    phone_no = input("ENTER YOUR PHONE NUMBER : ")
    phone_no = check_phone(phone_no)
    password = input("ENTER YOUR PASSWORD : ")
    # p_e = encrypt(phone_no,key)
    # password = encrypt(password,key)
    client_socket.send(phone_no.encode())
    client_socket.send(password.encode())

    cm_1 = client.recv(1024).decode()
    print(f"Received message: {cm_1}")
    if(cm_1=="ALREADY LOGGED IN...."):
        print("CLIENT ALREADY LOGGED IN...")
        return "diconnected"
    
    if(cm_1=="Client does not exist."):
        ans = input("want to create a new account(y/n)?")
        if(ans=='y' or ans=='Y'):
            rm_1 = "new"
            # rm_1 = encrypt(rm_1,key)
            client.send(rm_1.encode())
        else:
            print("THANK YOU")
            return
    elif (cm_1=="Invalid password"):
        print("LAST CHANCE TO CONNECT")
        password = input("RE-ENTER YOUR PASSWORD : ")
        rm_1="rp"
        # rm_1=encrypt(rm_1,key)
        # password = encrypt(password,key)
        client.send(rm_1.encode())
        client.send(password.encode())
    else :
        rm_1="connected"
        # rm_1 = encrypt(rm_1,key)
        client.send(rm_1.encode())

    cm_2 =client.recv(1024).decode()
    if(cm_2=="Invalid password"):
        print("UNABLE TO CONNECT!")
    else:
        print("connected")
        return "connected"
    return cm_2
    
    
def generate_key():
    cr  = generate_large_prime()
    # print(cr)
    time.sleep(0.3)
    g = int(client.recv(1024).decode())
    sys.stdout.flush()
    # print(g)
    time.sleep(0.3)
    p = int(client.recv(1024).decode())
    # print(p)
    time.sleep(0.3)
    R2 = (g**cr)%p
    R1 = int(client.recv(1024).decode())
    client.send(str(R2).encode())
    key = (R1**cr)%p
    print("END-TO-END ENCRYPTED")
    return key


BUFFER_SIZE = 1024  # Adjust the buffer size as needed

def send_file(client_socket, key):
    global BUFFER_SIZE
    file_path = input("Enter the path of the file to send: ")

    # Check if the file exists
    
    if not os.path.exists(file_path):
        print("File not found. Please enter a valid file path.")
        return
    encrypt_file_name = encrypt(file_path,key)
    client_socket.send(encrypt_file_name.encode())
    time.sleep(0.1)
    # Encrypt and send the file data in chunks
    with open(file_path, "r") as file:
        while True:
            chunk = str(file.read(BUFFER_SIZE))
            if not chunk:
                time.sleep(0.1)
                break  # End of file
            encrypted_chunk = encrypt(chunk, key)
            client_socket.send(encrypted_chunk.encode())
    m1 = "end-of-file"
    client_socket.send(m1.encode())
    print("File sent successfully.")

def send_to_phoneno(client_socket, key):
    receiver_id = input("Enter the client Phone Number you want to send a message to: ")
    client_socket.send(encrypt(receiver_id,key).encode())
    m1 = decrypt(client_socket.recv(1024).decode(),key)
    return m1

def send_message_to_client(option,client_socket, key):
    option = encrypt(option,key)
    client.send(option.encode())
    m1 = send_to_phoneno(client_socket, key)
    if(m1 == "CLIENT NOT FOUND"):
        print(m1)
        return
    message = input("Enter your message: ")
    encrypted_message = encrypt(message, key)
    client_socket.send(encrypted_message.encode())

def send_file_to_client(option,client_socket, key):
    option = encrypt(option,key)
    client.send(option.encode())
    m1 = send_to_phoneno(client_socket, key)
    if(m1 == "CLIENT NOT FOUND"):
        print(m1)
        return
    send_file(client_socket, key)

def getting_file(client_socket,key):
    count = int(decrypt(client_socket.recv(1024).decode(),key))
    if(count==0):
        print("NO FILES...")
        return
    sender=[]
    file_name=[]
    time=[]
    data=[]

    print("FILES .... ")
    for i in range(count):
        sender.append(client_socket.recv(1024).decode())
        file_name.append(client_socket.recv(1024).decode())
        time.append(client_socket.recv(1024).decode())
        data.append(client_socket.recv(1024).decode())
    
    for i in range(count -1,-1,-1):
        s = decrypt(sender[i],key)
        f = decrypt(file_name[i],key)
        t = decrypt(time[i],key)
        d = decrypt(data[i],key)
        with open(f,"w") as file:
            file.write(d)
        print(f"SENDER : {s}")
        print(f"FILE-NAME : {f} , TIME :{t}")
        o = input("DO YOU WANT TO READ THE FILE (Y/N) : ")
        if(o=='y' or o=='Y'):
            os.system('cls' if os.name == 'nt' else 'clear')
            print("CONTENT OF FILE ......")
            with open(f,"r") as file:
                dt = file.read()
                print(dt)
            print("END OF FILE ............")
    

def message_transfer(client_socket, key):
    while True:
        print("OPTIONS: ")
        print("1. Send a text message to a connection ")
        print("2. Send a text file ")
        print("3. Receive all your text messages ")
        print("4. Receive all your file messages ")
        print("5. Exit ")
        option = input("Choose an option: ")

        if option == "1":
            send_message_to_client(option,client_socket,key)
        elif option == "2":
            send_file_to_client(option,client_socket,key)
        elif option == "3":
            option = encrypt(option,key)
            client.send(option.encode())
            received_message =[]
            count = int(decrypt(client_socket.recv(1024).decode(), key))
            for i in range(count):
                received_message.append(client_socket.recv(1024).decode())
            os.system('cls' if os.name == 'nt' else 'clear')
            for i in range(count - 1, -1, -1):
                print("Received message:", decrypt(received_message[i],key))
        elif option == "4":
            option = encrypt(option,key)
            client.send(option.encode())
            getting_file(client_socket,key)
        elif option == "5":
            option = encrypt(option,key)
            client.send(option.encode())
            print("Exiting message transfer.")
            break
        else:
            print("Invalid option. Please try again.")
        time.sleep(1)


def start(client_socket):
    m = authentication(client_socket)
    if(m!="connected"):
        return
    key = generate_key()
    message_transfer(client_socket,key)
   
    
    

# Client setup2
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 12345))

# Start a separate thread for sending messages
send_thread = threading.Thread(target=start, args=(client,))
send_thread.start()

