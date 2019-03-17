import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from mailjet_rest import Client
import os


url = os.environ['URL']
agent = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}

wantedString = os.environ['WANTED_STRING']
chrome_bin = os.environ['GOOGLE_CHROME_BIN']
chrome_driver = os.environ['CHROMEDRIVER_PATH']

if os.environ['DEBUG'] == 'true':
    debug_on = True
else:
    debug_on = False


chrome_options = Options()
chrome_options.binary_location = chrome_bin
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(executable_path=chrome_driver,
#                           service_args=service_args,
#                           service_log_path=service_log_path,
                           chrome_options=chrome_options)
driver.get(url)

# wait for needed content to load
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
timeout = 5

try:
    element_present = EC.presence_of_element_located((By.ID, wantedString))
    WebDriverWait(driver, timeout).until(element_present)
    isPageLoaded = True
    print("Web page loaded completely")
except TimeoutException:
    isPageLoaded = False
    print ("Timed out waiting for page to load")

if isPageLoaded:
    resp = driver.page_source
    driver.close()

    soup = BeautifulSoup(resp, 'lxml')
    # dotd = soup.find(id='free-learning-dropin')
    dotd = soup.find("div", class_="product")
    # if debug_on:
    #         print('==== resp beginning =====')
    #         print(dotd)
    #         print('==== resp end ===========')
    # dotd = dotd[0].text.strip()
    dotd_right = dotd.find("div", class_="product__right")
    dotd_title = dotd_right.select("h2")[0].text.strip()
    # dotd_author = dotd.find("div", class_="product__right").find("p", class_="product__author").text.strip()
    dotd_details = dotd_right.findAll("p")
    dotd_product_details = ''
    for detail_r in dotd_details:
        dotd_product_details = dotd_product_details + '<p>' + detail_r.text.strip() + '</p>'

    dotd_right_lists = dotd_right.ul.findAll("li")
    dotd_product_lists = '<ul>'
    for list_r in dotd_right_lists:
        dotd_product_lists = dotd_product_lists + '<li>' + list_r.text.strip() +'</li>'

    dotd_left = dotd.find("div", class_="product__left")
    dotd_image_src = dotd_left.a.img.get('src')

    if debug_on: print(dotd_image_src)

    subject = f'\"{dotd_title} - Pact Publishing Book of The Day!\"'

    html_body = '''
    <body>
    <h2>Today\'s Pact Book: {0}\n</h2>
    <p>
    <a href=\"{2}\"><img border=\"0\" alt=\"product_picture\" src=\"{3}\" width=\"224\" height=\"276\"></a>
    </p>
    <p></p>
    <p>product details: {1}</p>
    <p>{4}</p>
    <h3> {2} </h3>
    </body>
    '''.format(dotd_title,dotd_product_details,url,dotd_image_src,dotd_product_lists)
else:
    html_body = f'<body><h2>Couldn\'t retrieve {url} contents</h2>'
    subject = 'Oh, no! Couldn\'t retrieve today\'s Ebook of the day from Pact Publishing'

css = '''
<style type=\"text/css\">
body {font-family: Verdana, Geneva, Arial, Helvetica, sans-serif;}
h2 {clear: both;font-size: 130%; }
h3 {clear: both;font-size: 115%;margin-left: 20px;margin-top: 30px;}
p {margin-left: 20px; font-size: 12px;}
</style>
'''

html_head = '''
<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Frameset//EN\" \"http://www.w3.org/TR/html4/frameset.dtd\">
<html><head><title>{}</title>
{}
</head>
'''.format(subject,css)

html_foot = '</html>'

message = f"{html_head}{html_body}{html_foot}"

if debug_on: print(message)

API_KEY = os.environ['MJ_APIKEY_PUBLIC']
API_SECRET = os.environ['MJ_APIKEY_PRIVATE']
MAIL_FROM = os.environ['MAIL_FROM']
MAIL_FROM_NAME = os.environ['MAIL_FROM_NAME']
MAIL_TO = os.environ['MAIL_TO']

mailjet = Client(auth=(API_KEY, API_SECRET), version='v3.1')
mail_from = {"Email": MAIL_FROM, "Name": MAIL_FROM_NAME}
mail_to = [{"Email": MAIL_TO}]
mail_subject = subject
mail_htmlpart = message

email = {
    'Messages': [{
        "From": mail_from,
        "To": mail_to,
        "Subject": mail_subject,
        "HTMLPart": mail_htmlpart}
    ]
}

response = mailjet.send.create(data=email)
print("MailJet response:{}".format(response))
