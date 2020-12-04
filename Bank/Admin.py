import json
import os
import SHA
from getpass import getpass
import mysql.connector as sql


class Statsclass():
    def __init__(self):
        self.db = sql.connect(host='localhost', user='root', passwd='jerin@2002314618sql', database='bank')
        self.cursor = self.db.cursor()
    def getuserdetails(self, user):
        if str(user).isdigit(): 
            self.cursor.execute('select * from users where username = \'{}\' OR id = {}'.format(str(user),int(user)))
        else:
            self.cursor.execute('select * from users where username = \'{}\''.format(user))           
        users = self.cursor.fetchall()
        return users
    def datafunc(self,data):
        datan = []
        for act in data:
            if act.replace(' ', '') != '':
                act = act.split('  ')
                act[1] = act[1][:-1]
                for char in act:
                    if char == ':':
                        del act[act.index(char)]
        #print(data)

            datan.append(dict((
                ('date', act[0]),
                ('time', act[1]),
                ('type', act[2]),
                ('act', act[3])
            )))
        return datan
    def stats(self):
        with open('activities.info') as act:
            data = act.read()
            act.close()
        data = self.datafunc(data.splitlines())
        if 'userstat ' in self.cmd:
            buffer = []
            if ' /w' in self.cmd:
                for act in data:
                    if 'withdrawal' in act['type']:
                        buffer.append(act)
                self.cmd = self.cmd.replace('userstat ','')
                self.cmd = self.cmd.replace('/w', '')
                user = self.cmd.replace('/u','').replace(' ','') 
                if '/u ' in self.cmd:
                    users = self.getuserdetails(user)
                    userreturn = []
                    for user in users:
                        for bufferuser in buffer:
                            if int(bufferuser['act'].split()[1]) == user[0]:
                                userreturn.append(dict([
                                    ('act', bufferuser),
                                    ('userdetails', users)
                                ]))
                else:
                    userreturn = []
                    for bufferuser in buffer:
                        userid = int(bufferuser['act'].split()[1])
                        users = self.getuserdetails(userid)
                        userreturn.append(dict([
                            ('act', bufferuser),
                            ('userdetails', users)
                        ]))
                
                return None, userreturn
            elif ' /d' in self.cmd:
                for act in data:
                    if 'deposit' in act['type']:
                        buffer.append(act)
                self.cmd = self.cmd.replace('userstat ', '')
                self.cmd = self.cmd.replace('/d', '')
                user = self.cmd.replace('/u', '').replace(' ', '')
                if '/u ' in self.cmd:
                    users = self.getuserdetails(user)
                    userreturn = []
                    for user in users:
                        for bufferuser in buffer:
                            if int(bufferuser['act'].split()[1]) == user[0]:
                                userreturn.append(dict([
                                    ('act', bufferuser),
                                    ('userdetails', users)
                                ]))
                else:
                    userreturn = []
                    for bufferuser in buffer:
                        userid = int(bufferuser['act'].split()[1])
                        users = self.getuserdetails(userid)
                        userreturn.append(dict([
                            ('act', bufferuser),
                            ('userdetails', users)
                        ]))

                return None, userreturn
            elif ' /l' in self.cmd:
                for act in data:
                    if 'login' in act['type']:
                        buffer.append(act)
                self.cmd = self.cmd.replace('userstat ', '')
                self.cmd = self.cmd.replace('/l', '')
                userreturn = []
                if '/u' in self.cmd:
                    self.cmd = self.cmd.replace('/u', '')
                    user = self.cmd.strip()
                    users = self.getuserdetails(user)
                    username = user
                    for user in users:
                        for bufferuser in buffer:
                            if user[1] == username or str(user[0]) == username:
                                userreturn.append(dict([
                                    ('act', bufferuser),
                                    ('userdetails', users)
                                ]))
                else:
                   for bufferuser in buffer:
                        user = bufferuser['act'].strip()[0]
                        users = self.getuserdetails(user)
                        userreturn.append(dict([
                            ('act', bufferuser),
                            ('userdetails', users)
                        ]))   
                return None, userreturn
            return None,None
        elif 'userprof ' in self.cmd:
            user = self.cmd.replace('userprof ',''.strip())
            userdetails = self.getuserdetails(user)
            for user in userdetails:
                ret = ''
                ret += '{} User Profile {} {}'.format(7*'*', userdetails.index(user)+1, 7*'*') + '\n'
                ret += 'UserID: {}'.format(user[0]) + '\n'
                ret += 'Username: {}'.format(user[1]) + '\n'
                ret += 'Cash: {}'.format(user[3]) + '\n'
                self.cmd = 'userstat /l /u {}'.format(user[0])
                userreturn = self.stats()[1]
                lastlogin = '{}/{}/{} {}'.format(userreturn[-1]['act']['date'][:2], userreturn[-1]['act']['date'][2:4], userreturn[-1]['act']['date'][4:], userreturn[-1]['act']['time'])
                ret += 'Last Login: {}'.format(lastlogin) + '\n'
                if __name__ != "__main__":
                    return ret, None
                else:
                    print(ret);return None, None
        else:
            return None,None

class Admin():
    def __init__(self):
        self.access = False
    def drive(self):
        s = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        s = list(s)
        drives = ['{}'.format(d) for d in s if os.path.exists('{}:\\'.format(d))]
        for d in drives:
            if os.path.exists('{}:\\bankadmin'.format(d)):
                return d
    def adminaccess(self):
        print('Enter admin pendrive to continue')
        cwd = os.getcwd()
        while True:
            try:
                driveletter = self.drive()
                os.chdir('{}:\\bankadmin'.format(driveletter))
                with open('Password.txt') as passw:
                    passwhash = passw.read()
                    passw.close()
                    
                passinput = getpass('Enter password: ')
                if SHA.sha_encode(passinput) == passwhash:
                    
                    self.access = True
                else:
                    pass
                if self.access:
                    os.chdir(cwd)
                    break
            except:
                pass

def cashamt(history, cashamount):
    if cashamount != '':
        return history['act']['act'].split()[-1]
    else:
        return cashamount
def logtype(history):
    t = history['act']['type']
    if 'login.' in t:
        t = t.replace('login.', '')
        if t == 'req':
            return 'Request'
        elif t == 'req.acc':
            return 'Request accepted'
        elif t == 'succ':
            return 'Successful'
        elif t == 'succ.fail':
            return 'Fail'
    elif 'withdrawal.' in t:
        t = t.replace('withdrawal.', '')
        if t == 'req':
            return 'Request'
        elif t == 'succ':
            return 'Successful'
    elif 'deposit.' in t:
        t = t.replace('deposit.', '')
        if t == 'req':
            return 'Request'
        elif t == 'succ':
            return 'Successful'
    else:
        return ''
def resultprint(userreturn, amount, cashamount):
    result = ''
    result += '               {} {} history {}'.format(7*'*', userreturn[0]['act']['type'].split('.')[0].upper(), 7*'*') + '\n'
    result += ' Date           Time        UserID     Username             {}          {}'.format(amount, 'Status') + '\n'
    for history in userreturn:
        if history['userdetails'] != []:
            if amount == 'Amount':
                result += '{}  {}    {}{}  {}{}  {}{}{}'.format(history['act']['date'], history['act']['time'], history['userdetails'][0][0], (11-len(str(history['userdetails'][0][0])))*' ', history['userdetails'][0][1], ((16-len(history['userdetails'][0][1]))*' '), cashamt(history, cashamount), ((16-len(cashamt(history, cashamount)))*' '), logtype(history)) + '\n'
            else:
                result += '{}  {}    {}{}  {}{}  {}'.format(history['act']['date'], history['act']['time'], history['userdetails'][0][0], (11-len(str(history['userdetails'][0][0])))*' ', history['userdetails'][0][1], ((16-len(history['userdetails'][0][1]))*' '), logtype(history)) + '\n'
        else:
            if amount == 'Amount':
                result += '{}  {}    {}{}  {}{}  {}{}{}'.format(history['act']['date'], history['act']['time'], '-', (11-len('-'))*' ', history['act']['act'], ((16-len(history['act']['act']))*' '), cashamt(history, cashamount), 16*' ', 'Fail') + '\n'
            else:
                result += '{}  {}    {}{}  {}{}  {}'.format(history['act']['date'], history['act']['time'], '-', (11-len('-'))*' ', history['act']['act'], ((16-len(history['act']['act']))*' '), 'Fail') + '\n'
    return result
def main():
    admin = Admin()
    admin.adminaccess()
    if admin.access:
        while True:
            cmd = input('$AdminShell>')
            if cmd == 'exit' or cmd == 'quit':
                break
            elif cmd == 'stats':
                while True:
                    cmd = input('$AdminShell: Stats>')
                    if cmd == 'exit' or cmd == 'quit':
                        break
                    userinput(cmd)
                    #print(userreturn)
                    global userreturn
                    if userreturn is not None:
                        print(resultprint(userreturn,amount,cashamount))

def userinput(cmd):
    global amount,cashamount,userreturn
    amount = ''
    cashamount = ''
    stats = Statsclass()
    stats.cmd = cmd
    result, userreturn = stats.stats()
    if userreturn is not None:
        if userreturn != []:
            if 'withdrawal' not in userreturn[0]['act']['type'] and 'deposit' not in userreturn[0]['act']['type']:
                amount = ''
                cashamount = ''
            else:
                amount = 'Amount'
                cashamount = ' '
        else:
            print('Such an user doesn\'t exist. For accessing such info you should do it manually only')
    if __name__ != "__main__":
        return result
if __name__ == "__main__":
    main()

