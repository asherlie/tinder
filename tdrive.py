import tinder
import base64
import gnupg
import os

class TinderStorage(object):
    def __init__(self, match, pgp_pp, char_lim=900, pgp_un=None):
        self.char_lim = char_lim
        self.pgp_pp = pgp_pp
        self.convo = match['messages']
        self.mid = match['id']
        self.t = tinder.Tinder()
        self.gpg = gnupg.GPG()
        self.gpg.encoding = 'utf-8'
        self.key_id = -1
        self.offset_table = {}
        keys = self.gpg.list_keys()
        key_name = ''
        if keys == []:
            print('please create a pgp key')
        else:
            for i in keys:
                if i['keyid'] == pgp_un:
                    self.key_id = pgp_un
                    key_name = i['uids'][0]
            # use first key if specified key does not exist
            if self.key_id == -1:
                self.key_id = keys[0]['keyid']
                key_name = keys[0]['uids'][0]
            print('using pgp key: ' + key_name)

    def encrypt(self, filename):
        with open(filename, 'rb') as f:
            ret = self.gpg.encrypt_file(f, self.key_id, armor=False, always_trust=True)
        return ret

    def decrypt(self, raw_data, tmp_fname, out_fname, pp):
        with open(tmp_fname, 'wb') as f:
            f.write(raw_data)
        with open(tmp_fname, 'rb') as f:
            self.gpg.decrypt_file(f, output=out_fname, passphrase=pp)
        os.popen('rm ' + tmp_fname)
    
    def prep_file_for_storage(self, filename, s_filename=None):
        encrypted_file = self.encrypt(filename).data
        fs = self.sp(str(base64.b85encode(encrypted_file))[2::][:-1:], self.char_lim)
        if s_filename != None: filename = s_filename
        info_tag = str(len(fs)) + ' ' + filename
        fs.append(str(base64.b85encode(self.gpg.encrypt(info_tag, self.key_id, always_trust=True).data)).encode('utf-8').decode('unicode-escape')[2::][:-1:])
        return fs

    def file_block_size(self, filename):
        return len(self.prep_file_for_storage(filename))
    
    def store_file(self, filename, s_filename=None):
        p_f = self.prep_file_for_storage(filename, s_filename)
        print('file will be stored in ' + str(len(p_f)-1) + ' blocks')
        for i in p_f:
            self.t.send_message(self.mid, i)
            # creating temporary message-like entries in self.convo to avoid self.update()
            self.convo.append({'message': i})
        if s_filename != None: filename = s_filename
        # offset_table will be overwritten next time list_files is called
        for i in range(len(self.offset_table), 0, -1):
            self.offset_table[i] = self.offset_table[i-1]
        prev_end = -1
        if len(self.offset_table) > 1:
            prev_end = self.offset_table[1][2]
        self.offset_table[0] = (filename, prev_end+1, len(p_f)+prev_end)
    
    # TODO: only look at messages sent by user
    # could be difficult because i'd have to t.get_my_profile
    # it's kinda important though because otherwise if both users are sending b64 encoded pgp encrypted 
    # files, there will be many errors when i try to decrypt the pgp meant for another key

    def b64_decode_safe(self, byte_str):
        try:
            return base64.decodestring(byte_str)
        except ValueError:
            return -1

    def b85_decode_safe(self, byte_str):
        try:
            return base64.b85decode(byte_str)
        except ValueError:
            return -1

    def load_file(self, filenum, out_fname=None):
        def block_range_to_data_str(c_b, c_e, o_fn):
            data_str = ''
            print('loading file \'' + o_fn + '\' from block ' + str(c_b) + ' to ' + str(c_e))
            for i in range(c_b, c_e):
                clean_msg = self.convo[i]['message']
                if i == c_b and clean_msg[:2:] == "b'": 
                    clean_msg = clean_msg[2::]
                if self.convo[i]['message'][len(self.convo[i]['message'])-1] == "'":
                    clean_msg = clean_msg[:-1:]
                data_str += clean_msg
            return data_str

        if self.offset_table != {}:
            if out_fname == None: out_fname = self.offset_table[filenum][0]
            unb64 = base64.b85decode(bytes(block_range_to_data_str(self.offset_table[filenum][1], self.offset_table[filenum][2], self.offset_table[filenum][0]), 'utf-8').decode('unicode-escape').encode('utf-8'))
            self.decrypt(unb64, '.tmp_encrypted_file.gpg', out_fname, self.pgp_pp)
            return

    def list_files(self, silent=False, use_ot=True):
        if use_ot and self.offset_table != {}:
            for i in self.offset_table:
                print('file ' + str(i) + ': \'' + self.offset_table[i][0] + '\' occupies ' + str(self.offset_table[i][2]-self.offset_table[i][1]) + ' blocks')
            return
        c = 0
        msg = len(self.convo)-1
        while msg >= 0:
            # tmp_decoded = self.b64_decode_safe(bytes(bytes(self.convo[msg]['message'], 'utf-8').decode('unicode_escape'), 'utf-8'))
            tmp_decoded = self.b85_decode_safe(bytes(bytes(self.convo[msg]['message'], 'utf-8').decode('unicode_escape'), 'utf-8'))
            if tmp_decoded != -1:
                pgp_prep = str(tmp_decoded).encode('utf-8').decode('unicode-escape')[2::][:-1:]
                tmp_decrypted = self.gpg.decrypt(pgp_prep.encode('utf-8'), passphrase=self.pgp_pp)
                if tmp_decrypted.data != b'':
                    if tmp_decrypted.data.decode().split(' ')[0].isnumeric():
                        n_blocks = int(tmp_decrypted.data.decode().split(' ')[0])
                        o_fname = tmp_decrypted.data.decode()[len(str(n_blocks))+1::]
                        self.offset_table[c] = (o_fname, msg-n_blocks, msg)
                        if not silent:
                            print('file ' + str(c) + ': \'' + o_fname + '\' occupies ' + str(n_blocks) + ' blocks')
                        c+=1
                        # ignores the file blocks, we only care about descriptor blocks
                        msg -= n_blocks
            msg -= 1

    def update(self):
        m = self.t._post('updates').json()['matches']
        for i in m:
            if i['id'] == self.mid:
                self.convo = i['messages']
        self.list_files(True, False)
        
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
