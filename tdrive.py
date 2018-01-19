import tinder
import base64
import gnupg
import os

class TinderStorage(object):
    def __init__(self):
        # self.gpg = gnupg.GPG(gnupghome='/Users/asherli')
        self.t = tinder.Tinder()
        self.gpg = gnupg.GPG()
        self.gpg.encoding = 'utf-8'
        self.key_id = -1
        keys = self.gpg.list_keys()
        if keys == []:
            print('no keys found')
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
    
    def store_file(self, mid, filename):
        p_f = self.prep_file_for_storage(filename, 500)
        for i in p_f:
            self.t.send_message(mid, i)
        self.t.send_message(mid, str(len(p_f)))
    
    # TODO: store original filename
    def load_file(self, mid, out_fname, pgp_pp):
        m = self.t._post('updates').json()['matches']
        for i in m:
            if i['id'] == mid:
                g = i['messages']
        data_str = ''
        range_st = len(g)-int(g[len(g)-1]['message'])-1
        for i in range(range_st, len(g)-1):
            # TODO: handle removal of unneeded b' in store_file
            clean_msg = g[i]['message']
            if i == range_st:
                clean_msg = clean_msg[2::]
            if g[i]['message'][len(g[i]['message'])-1] == "'":
                clean_msg = clean_msg[:-1:]
            data_str += clean_msg
        unb64 = base64.decodestring(bytes(data_str, 'utf-8').decode('unicode-escape').encode('utf-8'))
        self.decrypt(unb64, '.tmp_encrypted_file.gpg', out_fname, pgp_pp)

    def find_mid(self, name):
        m = self.t._post('updates').json()['matches']
        for i in m:
            if 'person' in i:
                if i['person']['name'].find(name) != -1:
                    return i['id']
        
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
