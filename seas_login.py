import logging, time
import urllib.parse
import re

def loginToSite(site_url, reqSession, cookieJar, email, password, customer_id):

    logging.debug("[loginToSite] Sending step 1")
    resp = reqSession.get(site_url, cookies=cookieJar)

    logging.debug("[loginToSite] Sending step 2")
    resp2 = reqSession.get(resp.url, cookies=cookieJar) 
    resp2urlparse = urllib.parse.urlparse(resp2.url)

    # Sends to https://internal-portal.central.arubanetworks.com/platform/login/validate/userid
    logging.debug("[loginToSite] Sending step 3")
    req3URL = 'https://' + resp2urlparse.netloc + '/platform/login/validate/userid'
    resp3 = reqSession.post(req3URL, cookies=cookieJar, data={'userid': email, 'language': 'en_US'})


    # Sends to https://sso.arubanetworks.com/idp/startSSO.ping
    logging.debug("[loginToSite] Sending step 4")
    resp4 = reqSession.post(resp3.json()['auth_url'], cookies=cookieJar, data={'pf.username': email})


    # Send to https://sso.arubanetworks.com:443
    logging.debug("[loginToSite] Sending step 5")
    resp5 = reqSession.get(resp4.url, cookies=cookieJar)
    resp5urlparse = urllib.parse.urlparse(resp5.url)


    # Send to 
    logging.debug("[loginToSite] Sending step 6")
    
    req6URLend = 'PartnerIdpId=login.ext.hpe.com&TargetResource=' + urllib.parse.quote('https://sso.arubanetworks.com/idp/startSSO.ping?PartnerSpId=PRD:Athena:SP&TargetResource=https://internal-portal.central.arubanetworks.com/platform/login/user', safe='')

    req6URL = 'https://' + resp5urlparse.netloc + '/sp/startSSO.ping?' + req6URLend
    resp6 = reqSession.get(req6URL, cookies=cookieJar)     


    # Extract SAML information
    req7URL = re.search('method="post" action="([^\"]+)', resp6.text).group(1)
    SAMLRequest = re.search('name="SAMLRequest" value="([^\"]+)', resp6.text).group(1)
    RelayState = re.search('name="RelayState" value="([^\"]+)', resp6.text).group(1)


    logging.debug("[loginToSite] Sending step 7")    
    resp7 = reqSession.post(req7URL, data={'SAMLRequest': SAMLRequest, 'RelayState': RelayState}, cookies=cookieJar)


    # Extract SAML information
    req8URL = re.search('method="post" action="([^\"]+)', resp7.text).group(1)
    SAMLRequest = re.search('name="SAMLRequest" value="([^\"]+)', resp7.text).group(1)
    RelayState = re.search('name="RelayState" value="([^\"]+)', resp7.text).group(1)


    logging.debug("[loginToSite] Sending step 8") 
    resp8 = reqSession.post(req8URL, data={'SAMLRequest': SAMLRequest, 'RelayState': RelayState}, cookies=cookieJar)
    resp8urlparse = urllib.parse.urlparse(resp8.url) 
 
    logging.debug("[loginToSite] Sending step 9")
    resp9URL = re.search('method="POST" action="([^\"]+)', resp8.text).group(1)

    resp9 = reqSession.post('https://' + resp8urlparse.netloc + resp9URL, data={'pf.username': email, 'pf.pass': password, 'pf.ok': 'clicked', 'pf.cancel': ''}, cookies=cookieJar)



    SAMLResponse = re.search('name="SAMLResponse" value="([^\"]+)', resp9.text).group(1)
    RelayState = re.search('name="RelayState" value="([^\"]+)', resp9.text).group(1)
    resp10URL = re.search('method="post" action="([^\"]+)', resp9.text).group(1)


    logging.debug("[loginToSite] Sending step 10")
    resp10 = reqSession.post(resp10URL, data={'RelayState': RelayState, 'SAMLResponse': SAMLResponse}, cookies=cookieJar)


    SAMLResponse = re.search('name="SAMLResponse" value="([^\"]+)', resp10.text).group(1)
    RelayState = re.search('name="RelayState" value="([^\"]+)', resp10.text).group(1)
    resp11URL = re.search('method="post" action="([^\"]+)', resp10.text).group(1)



    logging.debug("[loginToSite] Sending step 11")
    resp11 = reqSession.post(resp11URL, data={'RelayState': RelayState, 'SAMLResponse': SAMLResponse}, cookies=cookieJar)


    SAMLResponse = re.search('name="SAMLResponse" value="([^\"]+)', resp11.text).group(1)
    RelayState = re.search('name="RelayState" value="([^\"]+)', resp11.text).group(1)
    resp12URL = re.search('method="post" action="([^\"]+)', resp11.text).group(1)


    logging.debug("[loginToSite] Sending step 12")
    resp12 = reqSession.post(resp12URL, data={'RelayState': RelayState, 'SAMLResponse': SAMLResponse}, cookies=cookieJar)



    REF = re.search('name="REF" value="([^\"]+)', resp12.text).group(1)
    TargetResource = re.search('name="TargetResource" value="([^\"]+)', resp12.text).group(1)
    resp13URL = re.search('method="post" action="([^\"]+)', resp12.text).group(1)


    logging.debug("[loginToSite] Sending step 13")
    resp13 = reqSession.post(resp13URL, data={'REF': REF, 'TargetResource': TargetResource}, cookies=cookieJar)


    logging.debug("[loginToSite] Sending step 15")
    resp14 = reqSession.post('https://internal-portal.central.arubanetworks.com/platform/login/customers/selection', cookies=cookieJar, headers = {'content-type': 'application/json'}, json={"cid": customer_id})




    # Login to internal-ui
    logging.debug("[loginToSite] Sending step 16")
    resp15 = reqSession.get('https://internal-portal.central.arubanetworks.com/platform/login/apps/nms/launch?_=' + str(int(round(time.time() * 1000))), cookies=cookieJar)


