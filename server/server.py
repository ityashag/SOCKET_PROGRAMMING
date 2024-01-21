import socket
import threading
import time
import pymongo
import sys

from Crypto.Util import number

def get_server_key():
    with open("server_key.txt","r") as f:
        d = f.readline()
        return int(d)
    
server_key = get_server_key()
current_log_in =[]

def generate_large_prime():
    while True:
        candidate = number.getPrime(15)  # Adjust the bit length as needed
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
        


def connect_db(phone, password):
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client["users"]
    users = db["user_authentication"]
    phone = encrypt(phone,server_key)
    password = encrypt(password,server_key)
    user_data = users.find_one({"phone": phone})
    if user_data is None:
        return "Client does not exist."
    if user_data["password"] != password:
        return "Invalid password"

    return "Verified."

def add_new_client(phone, password):
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client["users"]
    users = db["user_authentication"]
    phone = encrypt(phone,server_key)
    password = encrypt(password,server_key)
    users.insert_one({"phone": phone,"password":password})

def generate_key():
    sr  = generate_large_prime()
    time.sleep(0.3)
    g = generate_large_prime()
    send_g = str(g)
    time.sleep(0.3)
    sys.stdout.flush()
    client_socket.send(send_g.encode())
    p = generate_large_prime()
    send_p = str(p)
    time.sleep(0.3)
    client_socket.send(send_p.encode())
    R1 = (g**sr)%p
    send_r1 = str(R1)
    time.sleep(0.3)
    client_socket.send(send_r1.encode())
    R2 = int(client_socket.recv(1024).decode())
    time.sleep(0.3)
    key = (R2**sr)%p
    time.sleep(1)
    return key

def user_authentication():
    phone_no =  client_socket.recv(1024).decode()
    password = client_socket.recv(1024).decode()
    m1 =connect_db(phone_no,password)
    if(phone_no in current_log_in):
        m1 = "ALREADY LOGGED IN...."
        client_socket.send(m1.encode())
        return "diconnected"
    current_log_in.append(phone_no)
    client_socket.send(m1.encode())
    m2 =  client_socket.recv(1024).decode()
    m3=""
    if(m2 == "new"):
        add_new_client(phone_no,password)
        m3="connected"
    elif(m2=="rp"):
        password = client_socket.recv(1024).decode()
        m3= connect_db(phone_no,password)
    else:
        m3 ="connected"
            # m3 = encrypt(m3,key)
    client_socket.send(m3.encode())
    if(m3=="Verified."):
        return ["connected",phone_no]
    return ["connected",phone_no]


from datetime import datetime

def store_sender_info(sphone, rphone, enc_file_path):
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client["users"]
    users = db["data"]
    
    # Encrypt phone numbers with the server key
    sphone = encrypt(sphone, server_key)
    rphone = encrypt(rphone, server_key)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    existing_relation = users.find_one({"send_phone": sphone, "reciever_phone": rphone})

    if existing_relation:
        users.update_one(
            {"send_phone": sphone, "reciever_phone": rphone},
            {"$push": {"file_info": {"file_name": enc_file_path, "timestamp": current_time}}}
        )
    else:
        users.insert_one({
            "send_phone": sphone,
            "reciever_phone": rphone,
            "file_info": [{"file_name": enc_file_path, "timestamp": current_time}]
        })

def recieve_message(sphone,rphone,client_socket, key):
    global server_key
    message = client_socket.recv(1024).decode()
    message= decrypt(message,key)
    message = encrypt(message,server_key)
    print("MESSAGE RECIEVED TO SERVER .....")
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client["users"]
    users = db["data"]
    sphone = encrypt(sphone, server_key)
    rphone = encrypt(rphone, server_key)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    existing_relation = users.find_one({"send_phone": sphone, "reciever_phone": rphone})

    if existing_relation:
        users.update_one(
            {"send_phone": sphone, "reciever_phone": rphone},
            {"$push": {"message_info": {"message": message, "timestamp": current_time}}}
        )
    else:
        users.insert_one({
            "send_phone": sphone,
            "reciever_phone": rphone,
            "message_info": [{"message": message, "timestamp": current_time}]
        })
    print("MESSAGE STORED .....")



def receive_file(sphone,rphone,client_socket, key):
    global server_key
    file_path = decrypt(client_socket.recv(1024).decode(),key)
    file_path = file_path.split(".")
    file_name = encrypt(file_path[0],server_key)
    enc_file_path = "storage\\"+file_name+datetime.now().strftime('%Y%m%d%H%M%S')+'.'+file_path[1]
    print(datetime.now().strftime('%Y%m%d%H%M%S'))
    # Receive and decrypt file data in chunks
    with open(enc_file_path, "w") as file:
        while True:
            encrypted_chunk = client_socket.recv(1024).decode()
            if  str(encrypted_chunk) == "end-of-file":
                file.close()
                store_sender_info(sphone,rphone,enc_file_path)
                print("File received successfully.")
                return
            decrypted_chunk = decrypt(encrypted_chunk, key)
            decrypted_chunk = encrypt(decrypted_chunk,server_key)
            file.write(decrypted_chunk)


def check_receiver(phone,server_key):
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client["users"]
    users = db["user_authentication"]
    phone = encrypt(phone,server_key)
    user_data = users.find_one({"phone": phone})
    if user_data is None:
        return "CLIENT NOT FOUND"
    return "FOUND"


def give_data(rphone,client_socket,key):
    print("RETREVING TEXT MESSAGES OF CLIENT.......")
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client["users"]
    users = db["data"]
    rphone = encrypt(rphone, server_key)
    user_data = users.find_one({"reciever_phone": rphone})
    information_to_send = []
    if user_data:
        if "message_info" in user_data:
            for message_info in user_data["message_info"]:
                information_to_send.append(f"{decrypt(user_data['send_phone'],server_key)}-{message_info['timestamp']} -[ {decrypt(message_info['message'],server_key)}]")
    else:
        information_to_send.append("No information found for reciever_phone {rphone}")
    
    client_socket.send(encrypt(str(len(information_to_send)),key).encode())
    time.sleep(0.1)
    for i in range(len(information_to_send)):
        client_socket.send(encrypt(information_to_send[i],key).encode())
        time.sleep(0.1)
    print("SEND ALL TEXT MESSAGE. ")

def give_files(rphone,client_socket,key):
    global server_key
    print("RETREVING FILES OF CLIENT.......")
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client["users"]
    users = db["data"]
    rphone = encrypt(rphone, server_key)
    user_data = users.find_one({"reciever_phone": rphone})
    information_to_send = []
    sender=[]
    timet = []
    m=""
    if user_data:
        if "file_info" in user_data:
            for message_info in user_data["file_info"]:
                information_to_send.append(message_info['file_name']);
                sender.append(decrypt(user_data['send_phone'],server_key))
                timet.append(message_info['timestamp'])
        m=str(len(information_to_send))
    else:
        m="0"

    client_socket.send(encrypt(m,key).encode())
    for i in range(len(information_to_send)):
        data =""
        with open(information_to_send[i],"r") as file:
            data += file.read()
            if not data:
                break
        data = decrypt(data,server_key)
        file_name = information_to_send[i].split("\\")
        file_name = file_name[1]
        file_name = file_name.split(".")
        file_name = file_name[0]
       
        t = file_name[-14:]
        file_name = file_name[:-14]
        file_name = decrypt(str(file_name),server_key)
        file_name+=t
        file_name+=".txt"
        send_by  = sender[i]
        send_by = encrypt(str(send_by),key)
        file_name = encrypt(file_name,key)
        time_s = encrypt(timet[i],key)
        data = encrypt(data,key)
        client_socket.send(send_by.encode())
        time.sleep(0.1)
        client_socket.send(file_name.encode())
        time.sleep(0.1)
        client_socket.send(time_s.encode())
        time.sleep(0.1)
        client_socket.send(data.encode())
        time.sleep(0.1)


    print("SEND ALL FILE. ")

def message_transfer(sphone,client_socket, client_id,key):
    global server_key
    option = decrypt(client_socket.recv(1024).decode(),key)
    
    
    if option == "1":
        receiver_id  = decrypt(client_socket.recv(1024).decode(),key)
        m1 = check_receiver(receiver_id,server_key)
        client_socket.send(encrypt(m1,key).encode())
        if(m1=="CLIENT NOT FOUND"):
            return "continue"
        print("MESSAGE TRANSFER INITIATING......")
        recieve_message(sphone,receiver_id,client_socket, key)
    elif option == "2":
        receiver_id  = decrypt(client_socket.recv(1024).decode(),key)
        m1 = check_receiver(receiver_id,server_key)
        client_socket.send(encrypt(m1,key).encode())
        if(m1=="CLIENT NOT FOUND"):
            return "continue"
        print("FILE TRANSFER INITIATING......")
        receive_file(sphone,receiver_id,client_socket, key)
    elif option == "3":
        give_data(sphone,client_socket,key)
    elif option == "4":
        give_files(sphone,client_socket,key)
    elif option == "5":
        print("DISCONNECT ACK")
        return "exit"
    return "continue"

def handle_client(client_socket, client_id):
    try:
        m = user_authentication()
        if(m[0]!="connected"):
            print(f"Client {client_id} disconnected.")
            return
        phone = m[1]
        key = generate_key()
        while(True):
            m4 = message_transfer(phone,client_socket, client_id,key)
            if(m4=="exit"):
                break
        current_log_in.remove(phone)
        print(f"Client {client_id} disconnected.")

    except Exception as e:
        print(f"ERROR OCCURRED: {str(e)}")
        print(f"Client {client_id} disconnected.")
        current_log_in.remove(phone)
        clients.remove(client_socket)
        

# Server setup
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 12345))
server.listen()

print("Server listening on port 12345")

clients = []
client_id_counter = 1

while True:
    client_socket, addr = server.accept()
    clients.append(client_socket)
    
    # Assign a unique ID to the client
    client_id = client_id_counter
    client_id_counter += 1

    # Start a thread to handle the client
    client_handler = threading.Thread(target=handle_client, args=(client_socket, client_id))
    client_handler.start()
    print(f"Client {client_id} connected.")
    print("")
