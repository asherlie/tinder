import requests
import json
import tinder

class Face:
	base = "https://faceplusplus-faceplusplus.p.mashape.com/detection/detect"
	def anal(self, url): 
		param = {
			'url': url
			}
		response = requests.get(self.base, params=param, headers={'X-Mashape-Key': 'kBIPO5Vn1RmshW6fOF4SkqHlKC12p1Jqo44jsnFLtfZoFj0LPT', 'API_KEY': '40e7a6f21ef79ca564cec719a347513d', 'API_SECRET': 'VcZo3RnusaOmRfINMYo8lOzu8bWyyVPt'})
		return response.json()
