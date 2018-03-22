import requests
from bs4 import BeautifulSoup
from mailjet_rest import Client
import os


url = "https://www.packtpub.com/packt/offers/free-learning"
agent = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}
resp = requests.get(url, headers=agent)
print ("Requests repponse:{}".format(resp.status_code))

soup = BeautifulSoup(resp.text, 'html.parser')
dotd = soup.select('.dotd-title')
dotd = dotd[0].text.strip()
dotd_txt = soup.find("div", class_="dotd-main-book-summary float-left").select("div")[2].text.strip()
dotd_image = soup.find("div", class_="dotd-main-book-image float-left")
image_src = "https:"+dotd_image.a.noscript.img.get('src')

print("BS parse result:{}".format(dotd))

API_KEY = os.environ['MJ_APIKEY_PUBLIC']
API_SECRET = os.environ['MJ_APIKEY_PRIVATE']

mailjet = Client(auth=(API_KEY, API_SECRET), version='v3')
fromname = 'MessangerAPI'
sender = 'messanger@tutamail.com'
recipients = [{'Email': 'ignorethismessage@gmail.com'}]
subject = f'{dotd} - Pact Publishing Book of The Day!'
#message = "Today\'s Pact Book: {}\n URL: {}".format(dotd,url)

css = '''
<style type="text/css">
body {font-family: Verdana, Geneva, Arial, Helvetica, sans-serif;}
h2 {clear: both;font-size: 130%; }
h3 {clear: both;font-size: 115%;margin-left: 20px;margin-top: 30px;}
p {margin-left: 20px; font-size: 12px;}
</style>
'''

html_head = '''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Frameset//EN" "http://www.w3.org/TR/html4/frameset.dtd">
<html><head><title>{}</title>
{}
</head>
'''.format(subject,css)

html_body = '''
<body>

<h2>Today\'s Pact Book: {0}\n</h2>

<p>
<a href="{2}"><img border="0" alt="DOTD" src="{3}" width="224" height="276"></a>
</p>
<p>{1}</p>
<h3> {2} </h3>
</body>
'''.format(dotd,dotd_txt,url,image_src)

html_foot = '</html>'

message = html_head + html_body + html_foot

email = {
	'FromName': fromname,
	'FromEmail': sender,
	'Subject': subject,
	'Html-Part': message,
	'Recipients': recipients
}

response = mailjet.send.create(email)
print("MailJet response:{}".format(response))

#dotd_image = soup.select('bookimage imagecache imagecache-dotd_main_image')
