#  If you are having trouble obtaining your fb_token, I highly reccomend juliojgarciaperez's
#  simple ruby script at 
#  gist.github.com/juliojgarciaperez/31ccb391cb1fbcb04dc86a16038fca24


import requests
import json
import math #used to calculate eye distance and standard deviations moved inport into add_face_data()


auth_filename = 'auth.json'

class User(object):
        def __init__(self):
                self.photos = []
                self.bio = ''
                self.birthday = ''

class Tinder(object):

        base = "https://api.gotinder.com/"

        def __init__(self):
                self.headers = {#check if these are the current headers for most updated version of tinder - almost definitely outdated
                        "User-Agent": "Tinder/5.3.2 (iPhone; iOS 9.3.2; Scale/2.00",
                        "Accept-Language": "en-US",
                        "host": "api.gotinder.com",
                        "Connection": "keep-alive", 
                        "app-version": 1637,
                        "os-version": 90000300002,
                        "platform": "ios",
                        # "Content-Type": "application/json"

                }
                if 'auth_filename' in globals(): #if auth filename declared - if no auth_filename, override_auth_file() must be called
                        self._load_fb_auth() 
                self.authed = False
                self.profiles = None
                self.surrounding = set()

        def friends_to_list(self, fl):
                m = []
                c = 0
                dem = len(fl)
                for i in fl:
                        c+=1
                        m.append(self.get_tinder_profile(i['user_id']))
                        print(str(c) + '/' + str(dem) + ' conversions complete')
                return m
#make it so that mps are an object so i can have methods in it like find() that will search for a user
        #TODO 
        #put everythign in an if else, if len(input) != 0 and 'participants' in input[0]
        #this would indicate that 
        def gen_match_profile(self, m): #match profile is just a set of User() objs - uncomment this for original usage
#       def gen_match_profile(self, m_updates): # usage: gen_match_profile(t._post('updates').json()['matches']
#       def gen_match_profile(self, matches_json):
                matches = []
                if len(m) != 0:
                        if 'created_date' in m[0] or 'created' in m[0]:#determines if list is from post('updates').json()['matches']
                #               m = self._post('updates').json()['matches']  #- uncomment for original usage
                                for i in m: # uncomment this for iginal usage
                #               for i in m_updates:
                #               for i in matches_json
                #common_friend_count ??? 
                                        if 'person' in i:
                                                temp = User()
                                                temp.anal = 0 #face has not been anal yet
                                                temp.mus = 0 #mus has not yet been added
                                                if 'created_date' in i:
                                                        temp.match_date = i['created_date']
                                                else:
                                                        temp.match_date = -1
                #                               temp = User()
                #                               temp.m_id = i['id'] #match id for sending msgs
                                                if 'id' in i: #match id for sending messages. check for existence f 'id' in case i'm generating a profile on ppl i havent matched with
                                                                                        #change the name of function to reflect the fact that it doesnt have to be run on matches
                                                        temp.m_id = i['id']
                                                temp.messages = i['messages'] #commented out bc of moral concerns - nvm lol
                                                        #strip messages of ridic amount of useless data before storing. all i need is _id from, _id to
                        #search strip meaningless data. get rid of from and to t_id's. sent and recieved are all i need
                                                temp._id = i['person']['_id']
                                                if 'bio' in i['person']: temp.bio = i['person']['bio']
                                                temp.name = i['person']['name']
                                                temp.gender = i['person']['gender']
                                                temp.birthday = i['person']['birth_date']
                                                temp.photos = []
                                                for pic in i['person']['photos']:
                                                        temp.photos.append(pic['url'])
                                                matches.append(temp)
                                return matches
                        else: #if not from post('updates').json()['matches']
                        #if this is a list of friends, does not work. if list of friends, detect and download each prof and add to list before applying these rules
                                for i in m:
                                        temp = User()
                                        temp.anal = 0 #face has not been anal yet
                                        temp.mus = 0 #mus has not been added yet
                                        if '_id' in i:
                                                temp._id = i['_id']
                                        else:
                                                temp._id = i['user_id']
                                        temp.bio = i['bio']
                                        temp.name = i['name']
                                        temp.gender = i['gender']
                                        temp.birthday = i['birth_date']
                                        temp.photos = []
                                        for pic in i['photos']:
                                                temp.photos.append(pic['url'])
                                        matches.append(temp)
                                return matches
#               return -1
                return matches #nothing wrong with returnign an empty list. it's at least iterable


#add condition for if len(match.photos) == 1 -> use first photo
        def add_face_data(self, match_profile):
                denom = len(match_profile)
                import face
                import math
                f = face.Face()
                c = 0
                for match in match_profile:
                        c+=1 #count moved here to increment for every member of mp
                        if match.anal == 0:
#                               match.anal = 1 #this was making me skip over analysis section. moved this down to after analysis
                                pic_with_one = False #this var should be true iff there exists a photo with one subject
                                pic_num = 0
                                face_count = -1 #before facial anal
                                list_faces = [] #later add all faces to this, then analyze them. i can do more complex
                                for pic in match.photos: # analysis this way. like checking for conflicting genders to narrow it down
                                        pic_num+= 1
                                        temp_face = f.anal(pic)
                                        if temp_face.status_code != 200: temp_face = {}
                                        # lol - a shitty fix but 'face' will not be in temp_face so code won't break if pic can't be downloaded
                                        else: temp_face = temp_face.json()
                                        if 'face' in temp_face:         
                                                face_count = len(temp_face['face'])
                                                if face_count == 1:
                                                        match.facial_attributes = temp_face #if there's on face in this pic. use it
                                                        match.photo_used = pic_num
                                                        pic_with_one = True 
                                                        print('photo number ' + str(pic_num) + ' for _id ' + str(match._id) + ' has just one subject.')
                                                        break #break photo loop
                                                else:
                                        #get rid of this else. just put print the num of faces and if else print some other shit
                                                        print('photo number ' + str(pic_num) + ' for _id ' + str(match._id) + ' has ' + str(face_count) + ' subjects. Trying next photo')
         
                                
                                if not pic_with_one:
#TODO: do not default to first photo if it has zero subjects
                                        print('no photos found with just one subject. Defaulting to first photo')
                                        match.facial_attributes = f.anal(match.photos[0]).json() #default to pic #1 if there is no photo w one subject
                                        match.photo_used = 1    # later i'll check if there is any pic in which all but one subject is the wrong gender
#                               c += 1 #moved this increment above the check for match.anal == 0 for an accurate count
                                print(str(c) + '/' +str(denom) + ' face scans completed')
#                       print('facial attribute scan completed. now analyzing data') #moved a few lines below to only print when not yet analyzed
                return match_profile #this will be where i return once separated
                                #the line below is the division between expensive scans and cheap analysis
                        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  - the two are totally independent. a new loop starts below

                        #maybe make these two different functions - also get rid of the checks like match.anal or match.mus. i could change teh way i update my mp's by 
                        #after these are separate, rerun it bc i redefined some of the values
                        #preforming my data creation shit on them and then merging the old and new lists afterwards. 
##                      if match.anal == 0:
#                       match.anal = 1
        def analyze_face_data(self, match_profile):
                print('facial attribute scan completed. now analyzing data')
                for match in match_profile:
                        if match.anal == 0:
                                match.anal = 1
                                if 'face' in match.facial_attributes:
        #                               match.has_face = True
                                        match.f_num = len(match.facial_attributes['face'])
                                        if match.f_num > 0:
                                                match.has_face = True
                                        else:
                                                match.has_face = False

                                        if match.f_num == 1:
                                                match.face_gender = match.facial_attributes['face'][0]['attribute']['gender']['value']
                                                if match.face_gender == 'Male':
                                                        match.face_gender = 0
                                                else:
                                                        match.face_gender = 1
                                                match.face_gender_confidence = match.facial_attributes['face'][0]['attribute']['gender']['confidence']
                                                match.race = match.facial_attributes['face'][0]['attribute']['race']['value']
                                                match.race_confidence = match.facial_attributes['face'][0]['attribute']['race']['confidence']
                                                match.face_age = match.facial_attributes['face'][0]['attribute']['age']['value']
                                                match.face_age_range = match.facial_attributes['face'][0]['attribute']['age']['range']
        #gross looking line below is just the distance formula expressed using the **2 operator
                                                raw_eye_dist = math.sqrt((match.facial_attributes['face'][0]['position']['eye_right']['x'] - match.facial_attributes['face'][0]['position']['eye_left']['x'])**2 + (match.facial_attributes['face'][0]['position']['eye_right']['y'] - match.facial_attributes['face'][0]['position']['eye_left']['y'])**2)

                                                if match.facial_attributes['face'][0]['position']['width'] == match.facial_attributes['face'][0]['position']['height']:
                                                        match.face_size = match.facial_attributes['face'][0]['position']['width']
                                                else:
                                                        match.face_size = (match.facial_attributes['face'][0]['position']['width']+match.facial_attributes['face'][0]['position']['height'])/2
        #raw eye distance must be adjusted to the scale of the image which is stored in face_size.if width!=height take avg
                                                match.eye_dist = raw_eye_dist*100/match.face_size #multiply by 100 for more reasonable numbers
                                        
                                        else: # TODO: check if any photo has multiple faces with only one subject of the correct gender
                #this else handles items with more than one face
                                                match.race = 'inconclusive'
                                                match.face_age = 'inconclusive'
                                                match.eye_dist = -1 #idk why but this is not a good criteria -it is. more than one face in teh pic so it cant decide who is the right person
                                                match.face_size = -1
                                                
                                else:#no faces in first pic!
                                        match.has_face = False
                                        match.f_num = -1#idk why but this makes sense
                        else: 
                                print('skipped over already scanned user')
                return match_profile

        def top_mp(self, mp, pn):
                li = []
                for i in mp:
                        if hasattr(i, 'messages'):
                                if len(i.messages) >= 100:
                                        li.append(i)
                                for msg in i.messages:
                                        if (msg['message'].find(pn) != -1) or (msg['message'].find('snapchat') != -1):
                                                li.append(i)
                                                break
                return li

        def add_stats_data(self, match_profile):
                                
#TODO
        #add generated stats to a tinder user object just for stats
        #including race proportions, standard dev for set, mean e_d
#maybe make a struct for keeping track of stats nicely. struct.mp is [...,tinder.User(),...,]
#struct.stats is a json
#write a function that returns an mp of ppl i find attractive. takes param of phone number and searches for phone 
#make a function that checks for ppl with no facesk
#number sending and the word snapchat.
#add func for updating a match profile. import, append, export
#add var for if face was anal or not to help w above func - if fnum != 1
#make gen_match_profile take a parameter of a list of matches obtained from t._post('updates').json()['matches'] -- this way i can analyze individual ppl if i want to #maybe remove all that makes it specific to a match - like date matched maybe.
                num = 0
                count = 0       
                for match in match_profile:
                        if hasattr(match, 'eye_dist'):
                                if match.eye_dist != -1:
                                        num+=1
                                        count += match.eye_dist
                if num == 0:
                        print('fuck, no valid members of match profile.')
                        print('valid entails having a face and scannable eye distance')
                        return -1
                else:
                        mean = count/num
                print('eye distance mean is: ' + str(mean))
                count = 0
                for m in match_profile:
                        if hasattr(m, 'eye_dist'):
                                if m.eye_dist != -1:
                                        count+= (m.eye_dist - mean)**2
                sd = math.sqrt(count/num)       
                print('standard deviation is: ' + str(sd))

                for m in match_profile:
                        if hasattr(m, 'eye_dist'):
                                if m.eye_dist != -1:
                                        m.sd = (m.eye_dist-mean)/sd #fails if only one member of list, divides by zero
                        #calc standard deviation. add points for each sd away from mean it is   
                        # gen list of tinder use objects based on all surrounding people until recs exhausted
                return match_profile
        def matches_of_interest(self, mp):
            def has_phone_num(strn):
                if len(strn) >= 10:
                    for i in range(len(strn)-9):
                        tmp = ''
                        for spot in range(10):
                            tmp += strn[i+spot]
                        if tmp.isnumeric():
                            return True
                    return False
                else:
                    return False

            def msg_interest(usr):
                if hasattr(i, 'messages'):
                    if len(i.messages) >= 50: return True
                    for msg in i.messages:
                        if msg['message'].find('snap') != -1 or msg['message'].find('snapchat') != -1 or has_phone_num(msg['message']):
                            return True
                return False

            return [i for i in mp if msg_interest(i)]

        def gen_playlist(self, mp):
            return [i.anthem for i in mp if i.has_anthem]

        def gen_friend_playlist(self):
            plist = []
            for i in self.get_friends('q')['results']:
                tmp = self.get_tinder_profile(i['user_id'])
                if 'spotify_theme_track' in tmp:
                    plist.append(tmp['spotify_theme_track']['uri'])
            return plist
        
        def gen_playlist_legacy(self, mp): # this playlist gen uses a version of match profiles that did not include anthem url in anthem attribute - very slow
            plist = []
            c = 0
            outof = ('/' + str(len(mp)) + ' songs added')
            for i in mp:
                if hasattr(i, 'anthem'):
                    tmp_prof = self.get_tinder_profile(i._id)
                    if 'spotify_theme_track' in tmp_prof:
                        plist.append(tmp_prof['spotify_theme_track']['uri'])
                        print('added some music')
                    c+=1
                    print(str(c) + + outof)
            return plist
        
        def add_music_data(self, match_profile): #this is in a separate method bc it's inneficient in that it re - get_tinder_prof() every user. data not stored in list of matches
                denom = len(match_profile)
                c=0
                for i in match_profile:
                        if i.mus == 0: #mus will be 1 if user has been checked for music already
                                i.mus = 1
                                c+=1
                                temp_prof = self.get_tinder_profile(i._id)
                                if 'spotify_theme_track' in temp_prof:
                                        i.anthem = {'artist': temp_prof['spotify_theme_track']['artists'][0]['name'], 'name': temp_prof['spotify_theme_track']['name']} #make it work for multiple artists 
                                print(str(c) + '/' +str(denom) + ' music data added') #add more meaningful output that distinguishes between success and failure
                        else:
                                c+=1
                                print('skipping. music already added for this user.')
                return match_profile
        
        def gen_mus_profile(self, match_profile):
                mu_p = {}
                for i in match_profile:
                        if hasattr(i, 'anthem'):
                                if not i.anthem['artist'] in mu_p:
                                        mu_p[i.anthem['artist']] = {}
                                if not i.anthem['name'] in mu_p[i.anthem['artist']]:
#                                       mu_p[i.anthem['artist']][i.anthem['name']] = 0
                                        mu_p[i.anthem['artist']][i.anthem['name']] = []
                                #mu_p[i.anthem['artist']][i.anthem['name']] +=1 #increment song
                                mu_p[i.anthem['artist']][i.anthem['name']].append(i) #increment song
                return mu_p

        def cons_mus_profile(self, mus_p):
                 ret = {}
                 for i in mus_p:
                         ret[i] = []
                         for j in mus_p[i]: 
                                 for x in mus_p[i][j]:
                                         ret[i].append(x)
                 return ret

        def mus_prof_anal(self, mp):
             mmp = self.cons_mus_profile(self.gen_mus_profile(mp))
             ret = {}
             for i in mmp:
                 whi = {'White': 0, 'Asian': 0, 'Black': 0, 'inconclusive': 0}
                 for j in mmp[i]:
                     if hasattr(j, 'race'):
                         whi[j.race]+=1
                 ret[i] = max(whi)
             return ret

                        
        def export_match_profile(self, match_profile, filename):
                j_file = []
        
                for match in match_profile:
                        temp_dic = {}
                        for i in match.__dict__:
                                temp_dic[i] = match.__getattribute__(i)

                        j_file.append(temp_dic)
                self.dump2json(j_file, filename)
                        

        def import_match_profile(self, filename):
        #filename should be an mp, or [] of tinder.User() objects
                mp_json = self.writeJson2mem(filename)
                mp = []
                for i in mp_json:
                        tmp = User()
                        for key in i.keys():
                                tmp.__setattr__(key, i[key])
                        mp.append(tmp)
                return mp
        def export_mp_as_json(self, filename):
                mp = self.add_stats_data(self.add_face_data(self.gen_match_profile(t._post('updates').json()['matches'])))
                self.export_match_profile(mp, filename)
        
        def compare_matches(self, mp0, mp1):
#this method is inherently problematic. it strips the meaning from the standard deviation attribute.
                #statistic data in list returned is from the 0th argument
                if mp0 == mp1:
                        return mp0
                u = []
                for i in mp0:
                        for j in mp1:
                                if i._id == j._id:
                                        u.append(i)
                return u

#change name to new match_mp - doesn't update within this method. then i could
#get rid of the vars like match.anal and .mus
#or make this separate_unique_members(mp1,mp2)
        def separate_unique_members(self, m_l, mp_s): #large and small
        #this takes in complete update dlist of matches and current mp 
#       def update_match_profile(self, mp): # i can improve this method to have it more in line with the capabilities of my others if i let this take a second param that has a new list with some items to add 

        #def update_match_profile(self, mp, addition_mp):
#               if len(mp1) == 0:
#                       print('empty mp error')
#                       return mp
                checker = {}#add the new then the old, all that are left with zeros are new matches
#               m = self._post('updates').json()['matches']
                for i in m_l:
                        if 'person' in i:
                                checker[i['person']['_id']] = 0
                for i in mp_s:
                        if i._id in checker:# i need to check in case of people who unmatched
                                checker[i._id]+=1
                new = []
                for i in checker: #this collection of loops creates a list in the correct format to generate an mp
                        if checker[i] == 0: #if new match
                                for j in m_l:
                                        if 'person' in j:
                                                if i == j['person']['_id']:
                                                        new.append(j)
#               for i in self.gen_match_profile(new):
#                       mp.append(i)
                        #i can make this function return new_mp
                return new                      
#               return mp

        def update_mp(self,mp):
                m=self._post('updates').json()['matches']
                new = self.add_music_data(self.analyze_face_data(self.add_face_data(self.gen_match_profile(self.separate_unique_members(m, mp)))))
                for i in new:
                        mp.append(i)
                self.add_stats_data(mp)
                print('added ' + str(len(new)) + ' new matches')
                return mp

        def scan_for_emptiness(self, match_profile):
                u = []
                for i in match_profile:
                        if hasattr(i, 'race'):
                                if len(i.bio) == 0 and i.race == 'inconclusive' and i.f_num == 0:
                                        u.append(i)
#                                       print(i.name)
#                                       for pic in i.photos:
#                                               print(pic)
                return u


                #pass over once anal is done. if zero faces, scan second pic
        
        def _load_fb_auth(self):
                with open(auth_filename) as file:
                        self.fb_auth = json.load(file)

        def set_gender_pref(self, pref): # 0 for men, 1 for women
                head = {'gender_filter': pref}
                if not self.authed:
                        self._authenticate_facebook()
                    req = requests.post(self.base + 'profile', headers=self.headers, data=head)
                    if req.status_code != 200:
                            print('failed to update gender preference')
                    else:
                            print('succesfully updated gender preference!')
                    return req

        def set_distance_filter(self, max_distance):
                head = {"distance_filter": max_distance}
                if not self.authed:
                        self._authenticate_facebook()
                req = requests.post(self.base + 'profile', headers=self.headers, data=head)
                if req.status_code != 200:
                        print("failed to update profile distance filter")
                else:
                        print("succesfully updated distance filter")

                return req

        def get_recs(self):
                return self._post('user/recs')

	def get_user_list(self, stop_at=-1):
	    def expand_user_list(ul):
		ul_f = []
		for i in ul:
		    for usr in i:
			# dupe check v slow could always just make get_ul return a tuple w/ _id in the first part
			if 'user' in usr and usr['user']['_id'] not in [x['_id'] for x in ul_f]:
			    ul_f.append(usr['user'])
		return ul_f
	    ll = []
	    while True:
		tmp = self.get_recs()
		if (stop_at != -1 and len(ll) >= stop_at) or tmp.status_code != 200 or 'results' not in tmp.json(): break
		else: ll.append(tmp.json()['results'])
		print('scraped ' + str(len(ll)) + ' user clumps so far')
	    return expand_user_list(ll)

        # pretty print
        def pp(self, usr):
            print(usr['name'])
            if 'bio' in usr: print(usr['bio'])
            for p in usr['photos']:
                print(p['url'])

	def update_user_list(self):
	    ul = self.get_user_list()
	    old_users = self.writeJson2mem('user_list')
	    old_len = len(old_users)
	    old_id = [x['_id'] for x in old_users]
	    for i in ul:
		if i['_id'] not in old_id:
		    old_users.append(i)
	    self.dump2json(old_users, 'user_list')
	    print(str(len(old_users)-old_len) + ' users added')
	    return old_users

	def build_school_prof(self, ul):
	    ul_s = [i for i in ul if 'schools' in i and i['schools'] != []]
	    # make it work for all their schools
	    dic = {x['schools'][0]['name']: [] for x in ul_s}
	    for i in ul_s:
		dic[i['schools'][0]['name']].append(i)
	    return dic

        def find_school(self, s_name, school_p):
            ret = []
            for i in school_p:
                if (str(i).upper()).find(s_name.upper()) != -1:
                    ret.append(i)
            return ret

        def t_school(self, s_name, school_p):
            return school_p[self.find_school(s_name, school_p)[0]]

        def users_of_school(self, s_name, school_p, name=-1):
            for i in self.t_school(s_name, school_p):
                if (name == -1) or (name != -1 and i['name'].find(name) != -1):
                    self.pp(i)
                    print('~~~~~~~~~~~')

        # makes user lists compatible with music profile generation
        def operate(self, ul):
            c = 0
            id_d = {x['_id']: x for x in ul}
            mp = self.gen_match_profile(ul)
            for i in mp:
                if 'spotify_theme_track' in id_d[i._id] and id_d[i._id]['spotify_theme_track'] != None:
                    temp_prof = id_d[i._id]
                    print(type(temp_prof))
                    c+=1
                    i.has_anthem = True
                    i.anthem = []
                    i.anthem.append({'artist': temp_prof['spotify_theme_track']['artists'][0]['name'], 'name': temp_prof['spotify_theme_track']['name']})
                    i.anthem.append(temp_prof['spotify_theme_track']['uri'])
                else:
                    i.has_anthem = False
            print('found music for ' + str(c) + ' users')
            return mp

        def get_bio_list(self, stop_at=-1):
            ll = []
            while True: 
                tmp = self.get_recs()
                if ((stop_at != -1) and (len(ll) >= stop_at)) or tmp.status_code != 200 or 'results' not in tmp.json(): break
                else: ll += tmp.json()['results']
                print('scraped ' + str(len(ll))  + ' users so far')
            return [i for i in {x['user']['bio']: x for x in ll if 'user' in x and 'bio' in x['user']}] # gets rid of duplicates


        def override_auth_file(self,fb_id, fb_tok):
                self.fb_auth = {'facebook_id': fb_id, 'facebook_token':fb_tok}

        def _authenticate_facebook(self):
                print("trying to authenticate facebook")
                response = requests.post(self.base + "auth", data=self.fb_auth)
                if response.status_code == 200:
                        self.headers["X-Auth-Token"] = response.json()["token"]
                        self.authed = True
                        print("facebook authed") #for ___ add name to statement
                        # print("authenticated facebook and extracted token for " + response.json()["full_name"])
                else:
                        print("authentication failed due to invalid credentials")
        def change_location(self, lat, lon):
                if not self.authed:
                        self._authenticate_facebook()
                response = requests.post(self.base + "user/ping", headers=self.headers, data={"lat": lat, "lon": lon})
                print(response.status_code)
                if 'error' in response.json():
                        print('error: ' + response.json()['error'])
                else:
                        print('location update succesfull. you are now in ' + str(lat) + ', ' + str(lon) + '.')
                return response

        def _get(self, url):
                if not self.authed:
                        self._authenticate_facebook()
                response = requests.get(self.base + url, headers=self.headers)

                return response
        def _post(self, url):#can not be used with 'data=' param of requests.post
                if not self.authed:
                        self._authenticate_facebook()
                response = requests.post(self.base + url, headers=self.headers)
                return response

        def get_match(self, m_id):#maybe make a match class that produces a set of match objects
                return self._get('user/matches/' + m_id)


        

        def send_message(self, m_id, message):# m_id is match ID -- !tid
                if not self.authed:
                        self._authenticate_facebook()
                #response = requests.post(self.base + 'user/matches/' + tid, headers=self.headers, data={"message": message + ""})
                response = requests.post(self.base + 'user/matches/' + m_id, headers=self.headers, data={"message": message + ""})
                return response 

        def search_messages(self, term):
                resp = self._post('updates').json()
                for usr in resp['matches']:
                        for msg in usr['messages']:
                                if msg['message'].find(term) != -1:
                                        if 'person' in usr:
                                                print(msg['message'] + ' ' + usr['person']['name'] + ' ' + str(usr['person']['_id']))
                
        def get_my_prof(self):
                return self._get('profile')

        def get_friends(self, check):
                if not self.authed:
                        self._authenticate_facebook()
                frnds = self._get("group/friends").json()
                if check == "v":
                        for user in frnds["results"]:
                                print(user["name"])
                return frnds

        def frnd_tinder(self, name):
#               if self.frnd_has_tinder(name) > 1:
                li = []
                frnds = self.get_friends("quiet")
                for f in frnds["results"]:
                        if f["name"].find(name) != -1:
                        #this only returns the first match
                                profile = self.get_tinder_profile(f["user_id"])
                                li.append(profile)
#                               return profile  
                                return li

        def frnd_has_tinder(self, name, check): #maybe return a set of matches
                x = 0
                frnds = self.get_friends("quiet")
                if check == "v":
                        print(str(len(frnds["results"])) + " of your friends were found")
                for f in frnds["results"]:
                        if f["name"].find(name) != -1:
                                if check == "v":
                                        print(f["name"])
                                x = x + 1
                if x == 0:
                        print("nobody in your friends list matches " + name)
                        return False
                if x != 0:
                        if x > 1:
                                print(str(x) + " people with matching names")
                        return True
        def remaining_likes(self):
                if not self.authed:
                        self._authenticate_facebook()
                likes = self._get("meta").json()["rating"]["likes_remaining"]
                # keys = self._get("meta").json()["rating"]
                # print(keys.keys())
                print(likes)
                return likes

        def pics(self, user):
                #friends = self._get("group/friends")
                #if user in friends     
                print(user['name'] + "'s photos: ") 
                for pic in user['photos']:
                        print(pic['url'])

        def get_tinder_profile(self, tid):
                if len(tid) != 24: 
                        print("not even going to bother authenticating with a bullshit tid like that")
                        return -1
                profile_data = self._get("user/" + tid).json()
                if not 'results' in profile_data: #add more descriptive error message
                        print("fuck off. there's no way this is a valid tid (this error message comes from tinder.py:Tinder:get_tinder_profile)")
#                       return -1 #this is problematic for add_music_data() bc i try to check for a dict item for a value and this sometimes returns int
                        return {} #my hacky solution is to return empty {} - might break other shit idk

                #commented below out for cleaner output for parsing json
                #print(profile_data["name"] + "'s profile: "  + profile_data["bio"])
                return profile_data['results']
                #d2j is meant for playing around in jsons when i dont want to wase precious reccomendations
        def dump2json(self, data, filename):
                with open(filename, "w") as file:
                        json.dump(data, file)

                        #no varname param, just set some var equal to this func
        def writeJson2mem(self, filename):
                with open(filename, "r") as file:
                        arbitrary_var = json.load(file)
                return arbitrary_var

        def like_recs(self, dist):#dist param used in case of groups
        #very powerful tool when used with location spoofing
                r = self._post('user/recs').json()['results']
#               if r['message'] == 'recs exhauseted':
                        #increase distance by 1-
                for usr in r:
                        if usr['type'] == 'user':
                                l = self.like(usr['user']['_id'])
#                               if l.json()['likes_remaining'] == 0:
#                                       return -1
                                if l.json()['match']:
                                        print('matched!')
                        if 'group' in usr:
                                for mmbr in usr['group']['members']:
                                        if mmbr['distance_mi'] <= dist:
                                                l = self.like(mmbr['_id'])
                                                if l.json()['match']:
                                                        print('matched!')
        #make my_min an instance var. self.my_min gets changed when update_prf
                #is called
        #need this bc some group members are not in the same location
                return l.json()['likes_remaining']

        def bio_term(self, match_list, term):
                c = 0 
                for i in match_list:
                        if i.bio.find(term) != -1:
                                c = c + 1
                                print(i.bio)
                                print(i.photos[0])
                                print(i._id)
                print(str(c) + ' matches')
                
        def list_of_matches(self): #deprecated - use gen_match_profile()
                matches = []
                m = self._post('updates').json()['matches']
                for i in m:
                        if 'person' in i:
                                tmp = User()#change init def
                                tmp._id = i['person']['_id']
                                tmp.bio = i['person']['bio']
                                tmp.birthday = i['person']['birth_date']
                                for pic in i['person']['photos']:
                                        tmp.photos.append(pic['url'])
                                matches.append(tmp)
                return matches
#       def add_face_anal_to_match_list(self, match_list):
#this shouldnt be done here bc i'd have to import face                  
                
                #matches maybe add
        def use_all_likes(self): #likes all people nearby until likes are spent
                dist_filt = self.get_my_prof().json()['distance_filter']
                res = 1
                count = -1
                while res != 0:#res returns # of remainnig likes
                        res = self.like_recs(dist_filt) 
#                       count = count + 1
                print('all likes exhausted')
#               print('liked ' + str(count) + ' users')
                #return array of matches

        def num_matches(self):
                return len(self._post('updates').json()['matches'])

        def orientation(self): #returns 0 if straight 1 if gay
                if self.get_my_prof().json()['gender'] != self.get_my_prof().json()['gender_filter']:
                        return 0
                else:
                        return 1

        def like(self, tid):
                user_info = self._get("user/" + tid).json()['results']
                print("attempting to like " + user_info["name"] + " with the _id: " + str(tid) +  " who is " + str(user_info["distance_mi"]) + " miles away, and has the bio: '" + user_info["bio"] + "'")
                print(user_info["photos"][0]["url"])
                request = self._get("like/" + tid)
                if request.json()['likes_remaining'] == 0:
                        print('OUT OF LIKES')
                else:
                        if request.status_code == 200:
                                print("like successful")

                        if request.json()['match']:
                                print("it's a match!!!")
                return request
