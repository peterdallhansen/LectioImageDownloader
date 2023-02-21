import base64
from pyexpat import model
import requests
from bs4 import BeautifulSoup
import re
import os
import pwinput
import time
url = "https://www.lectio.dk/lectio/31/login.aspx?prevurl=FindSkema.aspx%3ftype%3dstamklasse"

print("Please provide Lectio.dk login credentials:")
user_ = input("Username:")
pass_ = pwinput.pwinput(prompt="Password:")
st = time.time()

payload = {
    
	'time': '0',
	'__EVENTTARGET': 'm$Content$submitbtn2',
	'__EVENTARGUMENT': '',
	'__LASTFOCUS': '',
	'__SCROLLPOSITION': '',
	'__VIEWSTATEX': 'wwAAAGlpZQotOTA0NjQxOTI2aWwCawCBbAJoaWRsAmcDaWwCawFlA29mZmwCZwNpZGwCZwVpZGwCgWlkbAJnCWlkbASBaWwCawJlFE4mIzIzMDtydW0gR3ltbmFzaXVtZGcJaWRsAoFpZGwCgWlqaWwCawNwZGRkZHIBZR5fX0NvbnRyb2xzUmVxdWlyZVBvc3RCYWNrS2V5X19sAmUMbSRDaG9vc2VUZXJtZRZtJENvbnRlbnQkQXV0b2xvZ2luQ2J4BAAAABNWYWxpZGF0ZVJlcXVlc3RNb2RlDGF1dG9jb21wbGV0ZQlpbm5lcmh0bWwHQ2hlY2tlZAD0nvsxY7wDI1o3xUUJ64ypm7UkZA==',
	'__VIEWSTATEY_KEY': '',
	'__VIEWSTATE': '',
	'__EVENTVALIDATION': 'oWV1CGHJSKGiWZGJESpuJV9osp+WAYcaAbLw+7JqDCFQbA+pFyxSD3CAge+yf41e4clK0C7zYL1dtOpd60q0sRBk7oCjDZLNoIuqdbliFxJVgyhQC1H7MU0JeiJLYxiPsN5L18H+2fnsRG1X6nx8C3wCTG0Rkl+l0KdVQ8pUQpYiLJcze2o9JQfJ6CsDPNRY8d4lc8bMx0bCAi/cG+usQm35vznifAiL2qdq//IL7NA=',
	'm$Content$username': user_,
	'm$Content$password': pass_,
	
	'LectioPostbackId': ''
}

#Log in using payload
s = requests.Session()
r = s.post(url, payload)
r.raise_for_status()
soup = BeautifulSoup(r.text, "html.parser")
if 'Log ud' in r.text:
    print('Login successful')   
else:
    print('Login failed')

#Get the URLs for each class on the main schedule page
classurls = soup.find_all('a', {'href': re.compile("/lectio/31/SkemaNy.aspx?")})
class_name_divs = soup.find_all('a',{'href' : re.compile("type=stamklasse")})
class_names = [div.get_text() for div in class_name_divs]

#Get the Image URLs for each class
for index, url in enumerate(classurls):
	respone = s.get('https://lectio.dk'+ url['href'])
	#Checks if request was successful
	if 'Elever' in respone.text:
		print("Successful")
	else:
		print("Failed")
		classurls.pop(index)
	urlindex = url['href'].find("klasseid=")
	klasseid = url['href'][urlindex:]
	klasseurl = f'https://www.lectio.dk/lectio/31/subnav/members.aspx?{klasseid}&showstudents=1&reporttype=classpicture'
	reply = s.get(klasseurl)
	Imgsoup = BeautifulSoup(reply.text, "html.parser")
	imageurls = Imgsoup.find_all('img', {'src': re.compile("/lectio/31/GetImage.aspx")})
	#Create a path for each class
	if not os.path.exists(f"images/{class_names[index]}"):
		os.makedirs(f"images/{class_names[index]}")
		print(f"created directory: images/{class_names[index]}")

	#Downloads all images from each class to respective folder
	for idx, imageurl in enumerate(imageurls):
		image = s.get(f"https://www.lectio.dk{imageurl['src']}")
		with open(f"images/{class_names[index]}/{idx+1}.jpg", "wb") as file:
			file.write(image.content)
			print(f"Image {idx+1} downloaded successfully to images/{class_names[index]}")

#For performance analysis
et = time.time()
elapsed_time = et - st
print('Execution time:', elapsed_time, 'seconds')
#Open images folder
os.startfile('images')