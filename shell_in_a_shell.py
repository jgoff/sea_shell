#!/usr/bin/python3
# Author: Guillaume Germain


#from pycookiecheat import chrome_cookies
import requests, readchar, pprint, time, logging, json, http.client, http.cookiejar
import os, sys, threading, re, urllib.parse, seas_login


# Put your email, password and customer ID here
email = 'ggermain@hpe.com'
password = ''
customer_id = 'f1c2d0e7e2dd4bec998833116c0628e9'
serial_number = 'CP0008065'

# Probably only supported for internal at the moment, no point in changing this for now
url_suffix = 'https://internal-ui.central.arubanetworks.com/'




http.client.HTTPConnection.debuglevel = 0

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig(filename='logs.txt', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


## Determining width and height of console
height, width = os.popen('stty size', 'r').read().split()

rcs_url = ""
rcs_session_id = ""


pp = pprint.PrettyPrinter(indent=4)

url_start =  url_suffix + 'console/ssh/start/' + serial_number + '?stamp=' + str(int(round(time.time() * 1000))) 
url_status = url_suffix + 'console/ssh/status/' + serial_number + '?stamp='
url_token_url = '/rcs/token/'


cookieJar = http.cookiejar.CookieJar()
reqSession = requests.Session()








 
        
def wasRedirected(response):

    if response.history:
        logging.debug("Request was redirected")
        for resp in response.history:
            logging.debug(resp.status_code, resp.url)

    return response.url



def sendCharacter(key_hit_by_user):
    hex_to_send = key_hit_by_user.hex() + '';


    logging.debug("Sending char " + hex_to_send.upper())
    reqSession.post(rcs_url + "/?", cookies=cookieJar, headers={'referer': rcs_url}, data={'width': width, 'height': height, 'session': rcs_session_id, 'keys': hex_to_send.upper()})

    return



def fetchDataLoop():

    logging.debug("[fetchDataLoop] Starting main data display loop")

    while True:
        logging.debug("[fetchDataLoop] Requesting data...")

        r = reqSession.post(rcs_url + "/?", cookies=cookieJar, headers={'referer': rcs_url, 'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'}, data={'width': width, 'height': height, 'session': rcs_session_id})

        print(r.json()['data'], end="", flush=True)
        
        logging.debug("[fetchDataLoop] Data received: " + pp.pformat(r.json()))



def main_loop():
    while True:
        key_hit = readchar.readkey().encode('utf-8')


        if key_hit is b'Z':
            exit()

        key_hex = key_hit.hex() + '';

        #print(key_hit.decode('utf-8'), end="", flush=True)

        t = threading.Thread(target=sendCharacter, kwargs={'key_hit_by_user': key_hit})
        t.start()
   


# Load cookie from jar




seas_login.loginToSite(url_suffix, reqSession, cookieJar, email, password, customer_id)

coookie = reqSession.cookies.get_dict()

headers = {'content-type': 'application/json', 'x-requested-with': 'XMLHttpRequest', 'referer': url_suffix + 'frontend/',  'X-CSRF-Token': coookie['csrftoken']}



# Initiating initial connection to shell

r = reqSession.post(url_start, cookies=cookieJar, headers=headers)

connection_data = r.json()
print("Connection data output\n")
pp.pprint(connection_data)

if 'error' in connection_data:
    print(connection_data['error'])
    print("Login to the " + url_suffix + " url before proceeding")
    exit()
if connection_data.get('status') == 'busy':
    print("Connexion is busy and is unavailable, please try again soon")
    
    exit()
if connection_data.get('status') == "error":
    print(connection_data['message'])
    exit()

# If this hasn't failed, then we query to see the connection state and loop this until the status is 'processed'


print("Querying to see connection state... ")

status_req = {}
status_req['status'] = 'not started'



while status_req['status'] != 'processed':
    time.sleep(3)

    r = reqSession.get(url_status + str(int(round(time.time() * 1000))), cookies=cookieJar, headers={'content-type': 'application/json', 'referer': 'https://internal-ui.central.arubanetworks.com/frontend/'})
    
 
    status_req = r.json()



# If this has passed then the connection has been processed and we are good to go



print("Connection initiated to " + connection_data['host'] + ' for device ' + serial_number)




r = reqSession.get('https://' + connection_data['host'] + url_token_url + connection_data['otc'], cookies=cookieJar, headers={'referer': 'https://internal-ui.central.arubanetworks.com/frontend/'}, allow_redirects=False)

rcs_url = r.headers['Location']




# Opening actual session to webserver and saving session_id

r = reqSession.post(rcs_url + "/?", cookies=cookieJar, headers={'referer': rcs_url, 'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'}, data={'width': width, 'height': height, 'rooturl': rcs_url})

rcs_session_id = r.json()['session']


# Starting main display loop

fetchDataThread = threading.Thread(target=fetchDataLoop)
fetchDataThread.start()



main_loop()



