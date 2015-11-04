from bs4.element import Doctype, NavigableString
from bs4 import BeautifulSoup
from collections import Counter
from datetime import datetime
from urlparse import urlparse
import random, re

def getDomainFromUrlString(url):
    url_parsed = urlparse(url)
    return url_parsed.scheme + "://" + url_parsed.netloc

def isHrefDocument(href):
    return href[-4:] in [".pdf", ".doc", ".xls", ".xml"]

def isHrefHttp(href):
    return urlparse(href).scheme in ["http", "https", ""]

def isUrlRelevant(url):
    return not any(word in url for word in ["about", "amazon", "ads", "captcha", "condition", "contact", "cookie", "copyright", "wikipedia.org/w/index.php?title=", "log", "privacy", "registrat", "robot", "sign", "term"])

def isEnoughText(text):
    totalNumberOfChars = len(text)
    totalNumberOfBlankChars = text.count(" ") + text.count("\n") + text.count("\r")
    totalNumberOfNonBlankChars = totalNumberOfChars - totalNumberOfBlankChars
    if totalNumberOfNonBlankChars > 20:
        return True
    else:
        return False

def isHtml(text):
    return text.count("<") > 5 and text.count(">") > 5

def isJavaScript(inputString):
    numberOfCharacters = len(inputString)
    if numberOfCharacters != 0:
        countOfSpecial = inputString.count(";") + inputString.count("=") + inputString.count("var") + inputString.count("{") + inputString.count("}") + inputString.count(":") + inputString.count("\"")
        #print "countOfSpecial is", countOfSpecial
        #print "numberOfCharacters is", numberOfCharacters
        percentage = float(countOfSpecial) / float(numberOfCharacters)
        #print "percentage of special characters is", percentage
        if percentage > .01:
            return True
    return False

def isWikipediaArticle(text):
    return "From Wikipedia, the free encyclopedia" in text

#pass in the href and the domain it comes from
# if there's problems it fixes the href
# if not it just returns the href
def reformHref(domain, href):
#    print "starting reformHref with", domain, "and", href
    domain_parsed = urlparse(domain)
#    print "domain_parsed is", domain_parsed
    href_parsed = urlparse(href)
#    print "href_parsed is", href_parsed

    if href_parsed.scheme == "":
#        print "href_parsed.scheme is blank"
        if domain_parsed.scheme == "":
#            print "domain_parsed.scheme is blank, so setting to http"
            url_string = "http"
        else:
#            print "domain_parsed.scheme is not blank"
            url_string = domain_parsed.scheme
    else:
#        print "href_parsed.scheme is not blank"
        url_string = href_parsed.scheme

    url_string += "://"
#    print "url_string is", url_string

    if href_parsed.netloc in ["", ".."] or "." not in href_parsed.netloc:
        url_string += domain_parsed.netloc
    else:
        url_string += href_parsed.netloc

#    print "url_string is", url_string

    if href_parsed.path[:3] == "://":
        url_string += href_parsed[2:]
    else:
        url_string += href_parsed.path

#    print "url_string is", url_string

    # if everything's blank except the fragment, add that
    if href_parsed.scheme == "" and href_parsed.netloc == "" and href_parsed.path == "" and href_parsed.params == "" and href_parsed.query == "":
        url_string += "#" + href_parsed.fragment

#    print "urlstring is", url_string
    if url_string.count("//") > 1:
#        print "ERRROROROROR "
        pass

    return url_string


def getRandomUserAgentString():
    listOfUserAgentStrings = ["Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)", "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36", "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36", "Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36", "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36", "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36", "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36", "Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36", "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36", "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)", "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; WOW64; Trident/6.0)", "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)", "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; ARM; Trident/6.0)", "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0", "Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0", "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20130401 Firefox/31.0", "Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0", "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20120101 Firefox/29.0", "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/29.0"]
    userAgentString = random.choice(listOfUserAgentStrings)
    print "userAgentString is", userAgentString
    return userAgentString

def getTitleFromSoup(soup):
    soup_title = str(soup.title)
    if soup_title:
        return soup_title.replace("<title>","").replace("</title>","").split(" -")[0].strip().split(" |")[0].strip()
    else:
        return None

def getMostRepeatedContentFromSoup(soup, test=None, testTagName=None):
    candidates = []
    for element in soup.descendants:
        if not isinstance(element, Doctype) and not isinstance(element, NavigableString):
            children = list(element.children)
            number_of_children = len(children)
            if number_of_children > 5:
                names = [child.name for child in children]
                counter = Counter(names)
                tagName, count = counter.most_common(1)[0]
                if tagName and count >= 5 and testTagName(tagName) if testTagName else True:
                    freq = float(count) / float(number_of_children)
                    if freq > 0.5:
                        if test(element):
                            candidate = {}
                            candidate['element'] = element
                            candidate['children'] = [child for child in children if child.name == tagName]
                            candidates.append(candidate)
    number_of_candidates = len(candidates)
    if number_of_candidates == 0:
        pass
    elif number_of_candidates == 1:
        return list(candidates[0]['children'])
    elif number_of_candidates > 1:
        print "candidates are", len(candidates)

# basically filter out the most repeated content by text length
# because a post is highly unlikely to consist of less than 100 characters!
def getPostsFromSoup(soup):
    test = lambda x: len(x.text) > 100

    # and posts are highly unlikely to be grouped as paragraph tags
    # paragraph tags are more likely to be paragraphs in a post!
    testTagName = lambda tagName: tagName != "p"

    return getMostRepeatedContentFromSoup(soup, test=test, testTagName=testTagName)

def getPostsFromText(text):
    return getPostsFromSoup(BeautifulSoup(text,'html.parser'))
