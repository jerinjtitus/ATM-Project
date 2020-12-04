import socket
import threading
import sys
import os
import json
import SHA
import string
import random
import datetime
import mysql.connector as sql
import Admin

try:
    db = sql.connect(host='localhost', user='root',passwd='jerin@2002314618sql', database='bank')
except ConnectionError as err:
    print('{}\nDatabase is not online'.format(err))

cursor = db.cursor()

allConnections = []
allAddress = []
allMachineID = []
def createSocket():
    try:
        global host 
        global port
        global s
        host = ''
        port = 25589
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as msg:
        print('Error: Socket creation error \n{}'.format(msg))
def bindSocket():   
    try:
        global host
        global port
        global s

        s.bind((host,port))
        s.listen(100)
    except socket.error:
        print('Error: Binding the host and port was unsuccessful\n Retrying...')
        bindSocket()

def multiclient():
    for c in allConnections:
        c.close()

    del allConnections[:]
    del allAddress[:]
    del allMachineID[:]
    while True:
        try:
            conn, addr = s.accept()
            allConnections.append(conn)
            allAddress.append(addr)
            macid = conn.recv(4)
            if not macid.isdigit():
                print('Unauthorized attempt to connect from : {}'.format(addr))
                del allConnections[len(allConnections)-1]
                del allConnections[len(allAddress)-1]
                save('UA.attempt', 'Unauthorized attempt to connect from : {}'.format(addr))
            else: 
                allMachineID.append(macid)
                print('Connection has been established | IP: {} | MachineID : {}'.format(addr[0], str(macid)))
                s.setblocking(True)
                threading._start_new_thread(main, (conn,))
                save('CONN.estb', 'Connection has been established | IP: {} | MachineID : {}'.format(addr[0], str(macid)))
        except:
            print('Error accepting connection')

def listConnection():
    result = ''
    print('Clients:')
    for i, conn in enumerate(allConnections):
        try:
            conn.send(str.encode(' '))
            conn.recv(3000)
        except:
            del allConnections[i]
            del allAddress[i];del allMachineID[i]
            continue
        result = str(i) + '  ' + \
            str(allAddress[i][0]) + '  ' + str(allAddress[i][1])
        print(result)
def getmacid(conn):
    for i in range(len(allConnections)):
        if allConnections[i] == conn:
            return allMachineID[i]
def save(type, cmd):
    with open('activities.info', 'a') as act:
        act.write('{}  {}:  {}  :  {}\n'.format(datetime.datetime.now().strftime('%d%m%Y'), str(datetime.datetime.time(datetime.datetime.now())),type, cmd))
        act.close()

def admin():
    while True:
        cmdadm = input('$AdminShell>')
        if cmdadm == 'list conn':
            listConnection()
        elif cmdadm == 'quit':
            break
        else:
            print('{} is not identified as command'.format(cmdadm))
def randomString(stringLength=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))
def main(conn):
    while True:
        cmd = conn.recv(65536).decode('utf-8')
        if 'cashreq' in cmd:
            OTP = randomString()
            conn.send(str.encode(SHA.sha_encode(OTP)))
            with open('bank\\cashreq.txt', 'a') as cashreq:
                cashreq.write('MachineID: {}\tOTP: {}\n'.format(getmacid(conn),OTP))
            save('cashreq', 'MachineID: {}\tOTP: {}'.format(getmacid(conn), OTP))
            if conn.recv(100).decode('utf-8') == '#done':
                save('cashv.refill.succ', 'MachineID: {}'.format(getmacid(conn)))
        elif 'loginreq' in cmd:
            cursor.execute('select * from users')
            usersdetails = cursor.fetchall()
            username = cmd.replace('loginreq ', '')
            save('login.req', username)
            for user in usersdetails:
                if user[1] == username:
                    conn.send('#a'.encode())
                    save('login.req.acc', '{}   MachineID: {}'.format(username, getmacid(conn)))
                    password = conn.recv(10000).decode('utf-8')
                    if password ==  user[2]:
                        conn.send('#a'.encode())
                        save('login.succ', '{}   MachineID: {}'.format(username, getmacid(conn)))
                        if conn.recv(100).decode('utf-8') == ' ':
                            conn.send(str(list(user)).encode())
                    else:
                        conn.send(' '.encode())
                        save('login.succ.fail', '{}   MachineID: {}'.format(username, getmacid(conn)))
                else:
                    conn.send(' '.encode())            
                
        elif 'withdrawal' in cmd:
            cmdf = cmd
            save('withdrawal.req',cmdf)
            cmd = cmd.replace('withdrawal', '')
            cmd = cmd.split()
            
            cursor.execute('select * from users')
            usersdetails = cursor.fetchall()
            
            for user in usersdetails:
                user = list(user)
                user[3] = float(str(user[3]).replace("Decimal(')", ''))
                user[3] = float(str(user[3]).replace("')'", ''))

                if int(cmd[0]) == user[0] and cmd[1] == user[2]:
                    if int(cmd[2]) < user[3]:
                        user[3] -= int(cmd[2])
                        conn.send('#d'.encode())
                        save('withdrawal.succ', cmdf)
            cursor.execute('update users set cash = {} where id = {}'.format(user[3], user[0]))   
            db.commit()
            conn.send(str(list(user)).encode())  

        elif 'depositreq' in cmd:
            cmdf = cmd
            save('deposit.req', cmdf)
            cmd = cmd.replace('depositreq', '')
            cmd = cmd.split()
            
            cursor.execute('select * from users')
            usersdetails = cursor.fetchall()
            
            for user in usersdetails:
                user = list(user)
                user[3] = float(str(user[3]).replace("Decimal(')",''))
                user[3] = float(str(user[3]).replace("')'", ''))
                
                if int(cmd[0]) == user[0] and cmd[1] == user[2]:
                    if float(cmd[2]) < user[3]:
                        user[3] += float(cmd[2])
                        conn.send('#d'.encode())
                        save('deposit.succ', cmdf)
            cursor.execute('update users set cash = {} where id = {}'.format(user[3], user[0]))   
            db.commit()
            conn.send(str(list(user)).encode())
        elif '#ins' in cmd:
            macid = getmacid(conn)
            i = allMachineID.index(macid)
            allConnections.pop(i)
            allAddress.pop(i)
            with open('bank\\users.json', 'r') as users:
                userdetails = json.load(users)
                userdetails['Machine'].append(macid)
                users.close()
            with open('bank\\users.json', 'a') as users:
                json.dump(userdetails, users, indent=2)
                users.close()
        elif 'profreq' in cmd:
            conn.send(Admin.userinput('userprof {}'.format(cmd.replace('profreq ',''))).encode())
            conn.send(str(list(user)).encode())
createSocket()
bindSocket()
multiclient()
