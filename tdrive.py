import tinder
import base64
import gnupg
import os

#TODO: define the below to be a further abstraction fo TinderStorage
# class StorageBlock(object):
    # i want this to be accesible like sb.files = []
    # def __init__(self):
        # self.convo

class TinderStorage(object):
    def __init__(self, match, pgp_pp):
        self.pgp_pp = pgp_pp
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
            print('using pgp key: ' + keys[0]['uids'][0])
            self.key_id = keys[0]['keyid']

    def encrypt(self, filename):
        with open(filename, 'rb') as f:
            ret = self.gpg.encrypt_file(f, self.key_id, armor=False)# output='.tmp_encrypted')
        return ret

    def decrypt(self, raw_data, tmp_fname, out_fname, pp):
        with open(tmp_fname, 'wb') as f:
            f.write(raw_data)
        with open(tmp_fname, 'rb') as f:
            self.gpg.decrypt_file(f, output=out_fname, passphrase=pp)
        os.popen('rm ' + tmp_fname)
    
    def prep_file_for_storage(self, filename, char_lim):
        encrypted_file = self.encrypt(filename).data
        file_segments = self.sp(str(base64.encodestring(encrypted_file)), char_lim)
        return file_segments
    
    def store_file(self, filename, s_filename=None):
        p_f = self.prep_file_for_storage(filename, 900)
        print('file will be stored in ' + str(len(p_f)) + ' messages')
        for i in p_f:
            self.t.send_message(self.mid, i)
        if s_filename != None: filename = s_filename
        info_tag = str(len(p_f)) + ' ' + filename
        to_send = str(base64.encodestring(self.gpg.encrypt(info_tag, self.key_id).data)).encode('utf-8').decode('unicode-escape')[2::][:-1:]
        self.t.send_message(self.mid, to_send)
    
    # TODO: only look at messages sent by user
    # could be difficult because i'd have to t.get_my_profile
    # it's kinda important though because otherwise if both users are sending b64 encoded pgp encrypted 
    # files, there will be many errors when i try to decrypt the pgp meant for another key

    def b64_decode_safe(self, strng):
        try:
            return base64.decodestring(strng)
        except ValueError:
            return -1

    def load_file(self, filenum, out_fname=None):
        data_str = ''
        c = 0
        msg = len(self.convo)-1
        while msg >= 0:
            tmp_decoded = self.b64_decode_safe(bytes(self.convo[msg]['message'], 'utf-8'))
            if tmp_decoded != -1:
                tmp_decrypted = self.gpg.decrypt(tmp_decoded, passphrase=self.pgp_pp)
                if tmp_decrypted.data != b'':
                    if tmp_decrypted.data.decode().split(' ')[0].isnumeric():
                        n_blocks = int(tmp_decrypted.data.decode().split(' ')[0])
                        o_fname = tmp_decrypted.data.decode()[len(str(n_blocks))+1::]
                        if filenum == c: # if we've gotten to the correct file
                            if out_fname == None: out_fname = o_fname
                            range_st = msg-n_blocks  # -1 ?
                            print('loading file \'' + o_fname + '\' from block ' + str(range_st) + ' to ' + str(msg))
                            for i in range(range_st, msg):
                                # TODO: handle removal of unneeded b' in store_file
                                clean_msg = self.convo[i]['message']
                                if i == range_st:
                                    clean_msg = clean_msg[2::]
                                if self.convo[i]['message'][len(self.convo[i]['message'])-1] == "'":
                                    clean_msg = clean_msg[:-1:]
                                data_str += clean_msg
                            break
                        # filenum != c but we found a valid descriptor block
                        else:
                            msg -= n_blocks
                        c += 1
            msg -= 1

        unb64 = base64.decodestring(bytes(data_str, 'utf-8').decode('unicode-escape').encode('utf-8'))
        self.decrypt(unb64, '.tmp_encrypted_file.gpg', out_fname, self.pgp_pp)

    def list_files(self):
        c = 0
        msg = len(self.convo)-1
        while msg >= 0:
            tmp_decoded = self.b64_decode_safe(bytes(bytes(self.convo[msg]['message'], 'utf-8').decode('unicode_escape'), 'utf-8'))
            if tmp_decoded != -1:
                pgp_prep = str(tmp_decoded).encode('utf-8').decode('unicode-escape')[2::][:-1:]
                tmp_decrypted = self.gpg.decrypt(pgp_prep.encode('utf-8'), passphrase=self.pgp_pp)
                if tmp_decrypted.data != b'':
                    if tmp_decrypted.data.decode().split(' ')[0].isnumeric():
                        n_blocks = int(tmp_decrypted.data.decode().split(' ')[0])
                        o_fname = tmp_decrypted.data.decode()[len(str(n_blocks))+1::]
                        print('file ' + str(c) + ': ' + o_fname) 
                        print('occupies ' + str(n_blocks) + ' blocks')
                        c+=1
                        # ignores the file blocks, we only care about descriptor blocks
                        msg -= n_blocks
            msg -= 1

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
                tmp_str = ''
            tmp_str += st[i]
        spl.append(tmp_str)
        return spl

def find_match(name):
    t = tinder.Tinder()
    m = t._post('updates').json()['matches']
    for i in m:
        if 'person' in i:
            if i['person']['name'].find(name) != -1:
                return i
