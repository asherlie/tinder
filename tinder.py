#  If you are having trouble obtaining your fb_token, I highly reccomend juliojgarciaperez's
#  simple ruby script at 
#  gist.github.com/juliojgarciaperez/31ccb391cb1fbcb04dc86a16038fca24

import requests
import json
#import math #used to calculate eye distance and standard deviations
							#moved inport into add_face_data()

#nothing will work without a json file containing fb_id and tinder fb token
auth_filename = "auth.json"

class User(object):
	def __init__(self):
		self.photos = []
		self.bio = ''
		self.birthday = ''

class Tinder(object):

	base = "https://api.gotinder.com/"

	def __init__(self):
		self.headers = {#check if these are the current headers for most updated version of tinder
			"User-Agent": "Tinder/5.3.2 (iPhone; iOS 9.3.2; Scale/2.00",
			"Accept-Language": "en-US",
			"host": "api.gotinder.com",
			"Connection": "keep-alive", 
			"app-version": 1637,
			"os-version": 90000300002,
			"platform": "ios",
			# "Content-Type": "application/json"

		}
		self._load_fb_auth()
		self.authed = False
		self.profiles = None
		self.surrounding = set()
#make it so that mps are an object so i can have methods in it like find() that will search for a user
	#TODO 
	#put everythign in an if else, if len(input) != 0 and 'participants' in input[0]
	#this would indicate that 
	def gen_match_profile(self, m): #match profile is just a set of User() objs - uncomment this for original usage
#	def gen_match_profile(self, m_updates): # usage: gen_match_profile(t._post('updates').json()['matches']
#	def gen_match_profile(self, matches_json):
		matches = []
		if len(m) != 0:
			if 'created_date' in m[0] or 'created' in m[0]:#determines if list is from post('updates').json()['matches']
		#		m = self._post('updates').json()['matches']  #- uncomment for original usage
				for i in m: # uncomment this for iginal usage
		#		for i in m_updates:
		#		for i in matches_json
		#common_friend_count ??? 
					if 'person' in i:
						temp = User()
						if 'created_date' in i:
							temp.match_date = i['created_date']
						else:
							temp.match_date = -1
		#				temp = User()
		#				temp.m_id = i['id'] #match id for sending msgs
						if 'id' in i: #match id for sending messages. check for existence f 'id' in case i'm generating a profile on ppl i havent matched with
											#change the name of function to reflect the fact that it doesnt have to be run on matches
							temp.m_id = i['id']
						temp.messages = i['messages'] #commented out bc of moral concerns
			#search strip meaningless data. get rid of from and to t_id's. sent and recieved are all i need
						temp._id = i['person']['_id']
						temp.bio = i['person']['bio']
						temp.name = i['person']['name']
						temp.gender = i['person']['gender']
						temp.birthday = i['person']['birth_date']
						temp.photos = []
						for pic in i['person']['photos']:
							temp.photos.append(pic['url'])
						matches.append(temp)
				return matches
			else: #if not from post('updates').json()['matches']
				for i in m:
					temp = User()
					temp._id = i['_id']
					temp.bio = i['bio']
					temp.name = i['name']
					temp.gender = i['gender']
					temp.birthday = i['birth_date']
					temp.photos = []
					for pic in i['photos']:
						temp.photos.append(pic['url'])
					matches.append(temp)
				return matches
		return -1



	def add_face_data(self, match_profile):
		denom = len(match_profile)
		#are these imports bad form?
		import face
		import math
		f = face.Face()
		c = 0
		for match in match_profile:
			pic_with_one = False #this var should be true iff there exists a photo with one subject
			pic_num = 0
			face_count = -1 #before facial anal
			list_faces = [] #later add all faces to this, then analyze them. i can do more complex
			for pic in match.photos: # analysis this way. like checking for conflicting genders to narrow it down
				pic_num+= 1
				temp_face = f.anal(pic)
				if 'face' in temp_face:		
					face_count = len(temp_face['face'])
					if face_count == 1:
						match.facial_attributes = temp_face #if there's on face in this pic. use it
						match.photo_used = pic_num
						pic_with_one = True 
						print('photo number ' + str(pic_num) + ' for _id ' + str(match._id) + ' has just one subject.')
						break 
					else:
				#get rid of this else. just put print the num of faces and if else print some other shit
						print('photo number ' + str(pic_num) + ' for _id ' + str(match._id) + ' had ' + str(face_count) + ' subjects. Trying next photo')
 
			
			if not pic_with_one:
				print('no photos found with just one subject. Defaulting to first photo')
				match.facial_attributes = f.anal(match.photos[0]) #default to pic #1 if there is no photo w one subject
				match.photo_used = 1	# later i'll check if there is any pic in which all but one subject is the wrong gender
			c = c + 1
			print(str(c) + '/' +str(denom) + ' face scans completed')
		print('facial attribute scan completed. now analyzing data')
			#the line below is the division between expensive scans and cheap analysis
		# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
		for match in match_profile:
			if 'face' in match.facial_attributes:
#				match.has_face = True
				match.f_num = len(match.facial_attributes['face'])
				if match.f_num > 0:
					match.has_face = True
				else:
					match.has_face = False

				if match.f_num == 1:
		#face_gender will be inaccurate bc 0 and 1 are switched between tinder's api and f++
					match.face_gender = match.facial_attributes['face'][0]['attribute']['race']['value']
					match.face_gender_confidence = match.facial_attributes['face'][0]['attribute']['race']['confidence']
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
				
				else:#later make this else check if any of the other pics have just 1 subject
	#this else handles items with more than one face
#					if match.f_num > 1:#if there are multiple faces, check for num of pics.
#						for i in #wont need this inner if bc all the things that have a big fnum at this piont should have inconclusive
					match.race = 'inconclusive'
					match.face_age = 'inconclusive'
					match.eye_dist = -1 #idk why but this is not a good criteria -it is. more than one face in teh pic so it cant decide who is the right person
					match.face_size = -1
					
			else:#no faces in first pic!
				match.has_face = False
				match.f_num = -1#idk why but this makes sense
		return match_profile

	def top_mp(self, mp, pn):
		li = []
		for i in mp:
			if hasattr(i, 'messages'):
				for msg in i.messages:
					if (msg['message'].find(pn) != -1) or (msg['message'].find('snapchat') != -1):
						li.append(i)
						break #wat?
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
					m.sd = (m.eye_dist-mean)/sd
			#calc standard deviation. add points for each sd away from mean it is	
			# gen list of tinder use objects based on all surrounding people until recs exhausted
		return match_profile
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
#this method is inherently problematic. it strips the meaning from the standard deviation attribute
		#statistic data in list returned is from the 0th argument
		if mp0 == mp1:
			return mp0
		u = []
		for i in mp0:
			for j in mp1:
				if i._id == j._id:
					u.append(i)
		return u

#	def update_match_profile(self, mp):
#		m = self._post('updates').json()['matches']
#		for i in m:
#			if 'person' in m:
#				for j in mp:
#					if ilkweiodsklwedsweds
				
	def scan_for_emptiness(self, match_profile):
		u = []
		for i in match_profile:
			if hasattr(i, 'race'):
				if len(i.bio) == 0 and i.race == 'inconclusive' and i.f_num == 0:
					u.append(i)
#					print(i.name)
#					for pic in i.photos:
#						print(pic)
		return u


		#pass over once anal is done. if zero faces, scan second pic
	
	def _load_fb_auth(self):
		with open(auth_filename) as file:
			self.fb_auth = json.load(file)

	def update_profile(self, max_distance):
		head = {"distance_filter": max_distance}
		if not self.authed:
			self._authenticate_facebook()
		req = requests.post(self.base + 'profile', headers=self.headers, data=head)
		if req.status_code != 200:
			print("failed to update profile")
		else:
			print("succesfully updated profile")

		return req


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
#		if self.frnd_has_tinder(name) > 1:
		li = []
		frnds = self.get_friends("quiet")
		for f in frnds["results"]:
			if f["name"].find(name) != -1:
			#this only returns the first match
				profile = self.get_tinder_profile(f["user_id"])
				li.append(profile)
#				return profile	
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
		if len(tid) != 24: #noticed that some early tids have a diff amount of digits - look into this more later
			print("not even going to bother authenticating with a bullshit tid like that")
			return -1
		profile_data = self._get("user/" + tid).json()
		if not 'results' in profile_data:
			print("fuck off. there's no way this is a valid tid (this error message comes from tinder.py:Tinder:get_tinder_profile)")
			return -1
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
		r = self._get('user/recs').json()['results']
#		if r['message'] == 'recs exhauseted':
			#increase distance by 1-
		for usr in r:
			if usr['type'] == 'user':
				l = self.like(usr['user']['_id'])
#				if l.json()['likes_remaining'] == 0:
#					return -1
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
#	def add_face_anal_to_match_list(self, match_list):
#this shouldnt be done here bc i'd have to import face			
		
		#matches maybe add
	def use_all_likes(self): #likes all people nearby until likes are spent
		dist_filt = self.get_my_prof().json()['distance_filter']
		res = 1
		count = -1
		while res != 0:#res returns # of remainnig likes
			res = self.like_recs(dist_filt) 
#			count = count + 1
		print('all likes exhausted')
#		print('liked ' + str(count) + ' users')
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

