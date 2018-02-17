from sys import version_info
python_version = version_info.major

from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
from re import search
if python_version == 2:
    from urlparse import urlparse
elif python_version == 3:
    from urllib.parse import urlparse
from selenium.webdriver import Firefox, FirefoxProfile
from selenium import webdriver
from subprocess import check_output
from os.path import dirname, realpath, isfile

path_to_cache = dirname(realpath(__file__)) + "/cache"

def getTextContentViaSelenium(url):
    display = Display(visible=0, size=(1024, 768)).start()
    driver = webdriver.Firefox()
    driver.get(url)
    textContent = driver.execute_script("return document.documentElement.textContent")
    driver.quit()
    display.stop()
    return textContent

def getPageViaDriver(driver):
    try: driver.get(url)
    except: pass
    html = driver.execute_script("return document.documentElement.outerHTML")
    text = driver.execute_script("return document.documentElement.textContent")
    final_url = driver.current_url;
    open("/tmp/html.html","wb").write(html.encode("utf-8"))
    #driver.save_screenshot("/tmp/screenshot.png")
    return {'html': html, 'text': text, 'final_url': final_url}

def getAnonymousSeleniumDriver(userAgentString=None):
    display = Display(visible=0, size=(1024, 768))
    display.start()
    firefox_profile = webdriver.FirefoxProfile()
    if userAgentString:
        firefox_profile.set_preference("general.useragent.override", userAgentString)
    firefox_profile.set_preference("network.proxy.socks", "127.0.0.1")
    firefox_profile.set_preference("network.proxy.socks_port", 9050)
    firefox_profile.set_preference("network.proxy.type", 1)
    driver = webdriver.Firefox(firefox_profile=firefox_profile)
    driver.set_page_load_timeout(5)
    return driver
    #display will keep running

def getAnonymouslyViaSelenium(url, userAgentString=None):
    display = Display(visible=0, size=(1024, 768))
    display.start()
    firefox_profile = webdriver.FirefoxProfile()
    if userAgentString:
        firefox_profile.set_preference("general.useragent.override", userAgentString)
    firefox_profile.set_preference("network.proxy.socks", "127.0.0.1")
    firefox_profile.set_preference("network.proxy.socks_port", 9050)
    firefox_profile.set_preference("network.proxy.type", 1)
    #firefox_profile.set_preference("permissions.default.image", 2)
    driver = webdriver.Firefox(firefox_profile=firefox_profile)
    driver.set_page_load_timeout(5)
    result = getPageViaDriver()
    driver.quit()
    display.stop()
    return result
 
def getAnonymouslyViaCurl(url, userAgentString="", ua="", number_of_tries=1, use_cache=True, max_time=30):

    userAgentString = userAgentString or ua

    newurl = None
    text = None
    count = 0

    while count < 10:
        count += 1

        if len(url) < 200:
            path_to_cache_of_url = path_to_cache + "/" + url.replace("/","_").replace(":","_").replace("?","_").replace("/","_").replace(".","_")
        else:
            path_to_cache_of_url = path_to_cache + "/" + url.__hash__().__str__()

        if use_cache and isfile(path_to_cache_of_url):
            #print "webpage of", url," in cache so get that instead of making a call"
            with open(path_to_cache_of_url) as f:
                text = f.read()

        if not text:
            for n in range(number_of_tries):
                try:
                    text = check_output(['curl','--connect-timeout','15','--location','--max-time',str(max_time),'--user-agent',"'"+userAgentString+"'",'--socks5-hostname','127.0.0.1:9050','--url',url])
                    break
                except Exception as e:
                    print(e)

        if not text:
            return {'html': '', 'final_url': url}

        try:
            text = text.decode('utf-8')
        except:
            try:
                text = text.decode('latin-1')
            except:
                text = ""

        try:
            #print "about to write"
            with open(path_to_cache_of_url,"wb") as f:
                f.write(text.encode("utf-8"))
                #print "wrote ", url, "to ", path_to_cache_of_url
            #print "wrote"
        except Exception as e: 
            print(e)


        try: soup = BeautifulSoup(text, 'html.parser')
        except:
            try: soup = BeautifulSoup(text, "html5lib")
            except: soup = ""

        element = soup.find('meta', attrs={'http-equiv': 'refresh'})
        if element:
            if 'content' in element:
                content = element['content']
                if "url=" in content:
                    newurl = search("(?<=url=)[^;]*", content).group(0)
                    if not newurl.startswith("http"):
                        url_parsed = urlparse(url)
                        newurl = url_parsed.scheme + "://" + url_parsed.netloc + newurl
        #print "newurl is", newurl
        if newurl:
            url = newurl
            newurl = None
        else:
            break

    finalurl = newurl or url
    return {'html': text, 'final_url':finalurl}

def postAnonymouslyViaCurl(url, userAgentString="", ua="", params={}, number_of_tries=1, use_cache=True):

    userAgentString = userAgentString or ua

    newurl = None
    text = None

    data = "&".join([key+"="+value for key, value in params.iteritems()])

    while True:

        path_to_cache_of_url = path_to_cache + "/" + url.replace("/","_").replace(":","_").replace("?","_").replace("/","_").replace(".","_") + data.replace("&","_").replace("=","_").replace(" ","_")
        if use_cache and isfile(path_to_cache_of_url):
            #print "webpage of", url," in cache so get that instead of making a call"
            with open(path_to_cache_of_url) as f:
                text = f.read()

        if not text:
            for n in range(number_of_tries):
                try:
                    text = check_output(['curl','--connect-timeout','15','--location','--max-time','30','--user-agent',"'"+userAgentString+"'",'--socks5-hostname','127.0.0.1:9050','--url',url,'--data',data])
                    break
                except Exception as e:
                    print(e)
        
        try:
            text = text.decode('utf-8')
        except:
            text = text.decode('latin-1')

        with open(path_to_cache_of_url,"wb") as f:
            f.write(text.encode("utf-8"))
            #print "wrote ", url, "to ", path_to_cache_of_url

        soup = BeautifulSoup(text, 'html.parser')
        element = soup.find('meta', attrs={'http-equiv': 'refresh'})
        if element:
            #print "element is", element
            newurl = search("(?<=url=)[^;]*",element['content']).group(0)
            if not newurl.startswith("http"):
                url_parsed = urlparse(url)
                newurl = url_parsed.scheme + "://" + url_parsed.netloc + newurl
#        print "newurl is", newurl
        if newurl:
            url = newurl
            newurl = None
        else:
            break

    finalurl = newurl or url
    return {'html': text, 'final_url':finalurl}


