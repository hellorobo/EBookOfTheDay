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
print("BS parse result:{}".format(dotd))

API_KEY = os.environ['MJ_APIKEY_PUBLIC']
API_SECRET = os.environ['MJ_APIKEY_PRIVATE']

mailjet = Client(auth=(API_KEY, API_SECRET), version='v3')
fromname = 'MessangerAPI'
sender = 'messanger@tutamail.com'
recipients = [{'Email': 'ignorethismessage@gmail.com'}]
subject = 'Pact Publishing Book of The Day!'
message = "Today\'s Pact Book: {}\n URL: {}".format(dotd,url)


email = {
	'FromName': fromname,
	'FromEmail': sender,
	'Subject': subject,
	'Text-Part': message,
	'Recipients': recipients
}

response = mailjet.send.create(email)
print("MailJet response:{}".format(response))

#dotd_image = soup.select('bookimage imagecache imagecache-dotd_main_image')
