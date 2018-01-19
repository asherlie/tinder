import tinder
import base64
import gnupg
import os

#TODO: define the below to be a further abstraction fo TinderStorage
# class StorageBlock(object):
    # i want this to be accesible like sb.files = []
    # sb.tinderstorage.list_files if i give ts a param of messages to use i could avoid this shit
    # def __init__(self):
        # self.convoG

class TinderStorage(object):
    def __init__(self, match):
        # self.gpg = gnupg.GPG(gnupghome='/Users/asherli')
        self.recently_updated = True
        self.convo = match['messages']
        self.mid = match['id']
        self.t = tinder.Tinder()
        self.gpg = gnupg.GPG()
        self.gpg.encoding = 'utf-8'
        self.key_id = -1
        keys = self.gpg.list_keys()
        if keys == []:
            print('please create a pgp key')
        else:
            print('using ' + keys[0]['uids'][0])
            self.key_id = keys[0]['keyid']

    def encrypt(self, filename):
        with open(filename, 'rb') as f:
            ret = self.gpg.encrypt_file(f, self.key_id, armor=False)# output='.tmp_encrypted')
        return ret

    # TODO store original filename in messages
    def decrypt(self, raw_data, tmp_fname, out_fname, pp):
        with open(tmp_fname, 'wb') as f:
            f.write(raw_data)
        with open(tmp_fname, 'rb') as f:
            self.gpg.decrypt_file(f, output=out_fname, passphrase=pp)
        os.popen('rm ' + tmp_fname)
    
    def prep_file_for_storage(self, filename, char_lim):
        encrypted_file = self.encrypt(filename).data
        # file_segments = self.sp(base64.encodebytes(encrypted_file), char_lim)
        file_segments = self.sp(str(base64.encodestring(encrypted_file)), char_lim)
        # cant forget to first base64.decodestring() then add them up and gpg decrypt
        return file_segments
    
    # switched to more class based imp
    # def store_file(self, mid, filename):
    def store_file(self, filename):
        p_f = self.prep_file_for_storage(filename, 900)
        print('file will be stored in ' + str(len(p_f)) + ' messages')
        for i in p_f:
            self.t.send_message(self.mid, i)
        self.t.send_message(self.mid, str(len(p_f)))
    
    # TODO: store original filename
    # TODO: only look at messages sent by user
    # def load_file(self, convo, filenum, out_fname, pgp_pp):
    def load_file(self, filenum, out_fname, pgp_pp):
        data_str = ''
        c = 0
        for msg in range(len(self.convo)-1, 0, -1):
            if self.convo[msg]['message'].isnumeric():
                if filenum == c: # if we've gotten to the correct file
                    range_st = msg-int(self.convo[msg]['message'])  # -1 ?
                    print('from ' + str(range_st) + ' to ' + str(msg))
                    for i in range(range_st, msg):
                        # TODO: handle removal of unneeded b' in store_file
                        clean_msg = self.convo[i]['message']
                        if i == range_st:
                            clean_msg = clean_msg[2::]
                        if self.convo[i]['message'][len(self.convo[i]['message'])-1] == "'":
                            clean_msg = clean_msg[:-1:]
                        data_str += clean_msg
                        
                c += 1
        # print(data_str)

        unb64 = base64.decodestring(bytes(data_str, 'utf-8').decode('unicode-escape').encode('utf-8'))
        self.decrypt(unb64, '.tmp_encrypted_file.gpg', out_fname, pgp_pp)

    # def list_files(self, convo):
    def list_files(self):
        c = 0
        for i in range(len(self.convo)-1, 0, -1):
            if self.convo[i]['message'].isnumeric(): # assuming any numeric message is block count
                print('file number ' + str(c)) 
                print('occupies ' + self.convo[i]['message'] + ' blocks')
                c+=1
                # for block in range()

    def update(self):
        m = self.t._post('updates').json()['matches']
        for i in m:
            if i['id'] == self.mid:
                self.convo = i['messages']

        
    # TODO: move this into store_file for speed
    def sp(self, st, le):
        spl = []
        tmp_str = ''
        for i in range(len(st)):
            if i%le == 0 and i != 0:
                spl.append(tmp_str)
                # print(tmp_str)
                tmp_str = ''
            tmp_str += st[i]
        # print(tmp_str)
        spl.append(tmp_str)
        return spl

def find_match(name):
    t = tinder.Tinder()
    m = t._post('updates').json()['matches']
    for i in m:
        if 'person' in i:
            if i['person']['name'].find(name) != -1:
                return i
