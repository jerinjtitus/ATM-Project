import socket
import os

import SHA
import json
import sys
from getpass import getpass

cwd = os.getcwd()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '192.168.0.105'
port = 25589

def connectf():
    try:
        s.connect((host, port))
        s.setblocking(True)
    except:
        print('Retrying')
        connectf()
connectf()

def admin():
    while True:
        cmd = input('$AdminShell>')
        if 'install' in cmd:
            install(cmd.replace('install ', ''))
        elif cmd == 'quit':
            break
def drive():
    s = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    s = list(s)
    drives = ['{}'.format(d) for d in s if os.path.exists('{}:\\'.format(d))]
    for d in drives:
        if os.path.exists('{}:\\bankadmin'.format(d)):
            return d
def install(macid):
    print('Enter admin pendrive to continue')
    try:
        driveletter = drive()
        os.chdir('{}:\\bankadmin'.format(driveletter))
    except:
        print('Access denied')
    try:
        with open('Password.txt') as passw:
            passwhash = passw.read()
            passw.close()
        passinput = getpass('Enter password: ')
        if SHA.sha_encode(passinput) == passwhash:
            os.chdir(cwd)
            os.system('mkdir "Cashvault"')
            os.chdir('Cashvault')
            os.system('type nul > cash.txt')
            with open('cash.txt', 'w') as vault:
                vault.write('0')
                vault.close()
            os.chdir(cwd)
            os.system('type nul > macid.info')
            with open('macid.info', 'w') as f:
                f.write(macid)
                f.close()
            os.system('attrib +s +h macid.info')
            os.system('attrib +s +h Cashvault')
            print('$AdminShell> Machine Installation was successful')
            sys.exit()
    except:
        pass
def macid():
    try:
        with open('macid.info', 'r') as f:
            return f.read()
    except FileNotFoundError:
        admin()

mac = macid()
s.send(mac.encode())

def cash():
    with open('Cashvault\\cash.txt') as vault:
        money = int(vault.read())
        vault.close()
    return money
def cashwd(money):
    cmoney = cash()
    with open('Cashvault\\cash.txt', 'w') as vault:
        vault.write(str(money + cmoney))
        vault.close()

def vaultrefillcheck():
    with open('Cashvault\\cash.txt') as vault:
        if int(vault.read()) <= 10000:
            s.send('cashreq'.encode())
            OTP = s.recv(65535)
            return [True, OTP]
        else:
            return [False]
def fill():
    output = vaultrefillcheck()
    if output[0] is True:
        vaultrefill(output[1])
def vaultrefill(OTP):
    while True:
        OTPpass = input('Enter OTP to refill: ')
        if str.encode(SHA.sha_encode(OTPpass)) == OTP:
            with open('Cashvault\\cash.txt') as vault:
                cash = int(vault.read())
                cash += 5000000
                vault.close()
            with open('Cashvault\\cash.txt', 'w') as vault:
                vault.write(str(cash))
                vault.close()
            break

def login():
    username = input('Enter your Username: ')
    s.send('loginreq {}'.format(username).encode())
    permission = s.recv(100).decode('utf-8')
    if permission == '#a':
        print('(Entered characters will not be printed!!)')
        password = getpass('Enter your Password: ')
        s.send(SHA.sha_encode(password).encode())
        permission = s.recv(100).decode('utf-8')
        if permission == '#a':
            s.send(' '.encode())
            userdetails = []
            x = s.recv(65536).decode('utf-8').replace("Decimal('",'')
            x = x[:-3]+']'
            userdetails = eval(x)
            
            while True:
                usercash = int(userdetails[3])

                print('Your Cash: {}'.format(str(usercash)))
                print('Enter your choice: ')
                print('1. Withdraw')
                print('2. Deposit')
                print('3. User Profile')
                print('4. Log Out')
                
                opt = input('> ')
                if opt == '1':
                    while True:
                        try:
                            cashw = int(input('Enter the money you want to withdraw: '))
                        except:
                            print('Enter an integer only')
                        if cashw <= usercash and cashw <= cash():
                            s.send('withdrawal {} {} {}'.format(userdetails[0], userdetails[2], str(cashw)).encode())
                            if s.recv(100).decode('utf-8') == '#d':
                                print('{} rupees has been withdrawn'.format(str(cashw)))
                                cashwd(int('-{}'.format(cashw)))
                            break
                        else:
                            print('Entered amount is more than your balance or ATM vault has not enough money')
                elif opt == '2':
                    try:
                        cashd = int(input('Enter the money you want to deposit: '))
                    except:
                        print('Enter an integer only')
                    s.send('depositreq {} {} {}'.format(userdetails[0], userdetails[2], str(cashd)).encode())
                    if s.recv(100).decode('utf-8') == '#d':
                        print('{} rupees has been deposited'.format(str(cashd)))
                        cashwd(int(cashd))
                elif opt == '3':
                    s.send('profreq {}'.format(userdetails[1]).encode())
                    print(s.recv(65535).decode('utf-8'))
                elif opt == '4':
                    break
                else:
                    continue
                x = s.recv(65536).decode('utf-8').replace("Decimal('", '')
                x = x[:-3]+']'
                userdetails = eval(x)
        else:
            print('Wrong Password')      
    else:
        print('Wrong Username')      
def main():
    while True:
        try:
            with open('Cashvault\\cash.txt', 'r') as vault:
                if int(vault.read()) < 10000:
                    print('Cash vault is empty....')
                    fill()
                vault.close()
        except:
            print('Can\'t find cashvault')
        print('Enter choice:\n1.Login\n2.Admin')
        cmd = input('-->')
        if cmd == '1':
            login()
        elif cmd == '2':
            admin()


main()
