from sys import version_info
python_version = version_info.major

import random, re
from bs4.element import Comment, Doctype, NavigableString, Tag
from bs4 import BeautifulSoup
from collections import Counter
from datetime import datetime
from numpy import mean, median, std
if python_version == 2:
    from urlparse import urlparse
elif python_version == 3:
    from urllib.parse import urlparse
from re import IGNORECASE, match, MULTILINE, sub, UNICODE
flags = IGNORECASE|MULTILINE|UNICODE

from error_page import *
from headers import *
try:
    from http import *
except Exception as e:
    print("failed to import http module.  this is non critical but you will not be able to use http methods")
from statements import *

def getDomainFromUrlString(url):
    url_parsed = urlparse(url)
    return url_parsed.scheme + "://" + url_parsed.netloc

def isHrefDocument(href):
    return href[-4:] in [".pdf", ".doc", ".xls", ".xml"]

def isHrefFile(href):
    return href[-4:] in [".pdf", ".doc", ".xls", "xlsx", ".xml", ".mp3", ".mp4", "webm", ".mov"]

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
        percentage = float(countOfSpecial) / float(numberOfCharacters)
        if percentage > .01:
            return True
    return False

def isWikipediaArticle(text):
    return "From Wikipedia, the free encyclopedia" in text

#pass in the href and the domain it comes from
# if there's problems it fixes the href
# if not it just returns the href
def reformHref(domain, href):
    domain_parsed = urlparse(domain)
    href_parsed = urlparse(href)
    if href_parsed.scheme == "":
        if domain_parsed.scheme == "":
            url_string = "http"
        else:
            url_string = domain_parsed.scheme
    else:
        url_string = href_parsed.scheme

    url_string += "://"
    if href_parsed.netloc in ["", ".."] or "." not in href_parsed.netloc:
        url_string += domain_parsed.netloc
    else:
        url_string += href_parsed.netloc

    if href_parsed.path[:3] == "://":
        url_string += href_parsed[2:]
    else:
        url_string += href_parsed.path

    # if everything's blank except the fragment, add that
    if href_parsed.scheme == "" and href_parsed.netloc == "" and href_parsed.path == "" and href_parsed.params == "" and href_parsed.query == "":
        url_string += "#" + href_parsed.fragment

    if url_string.count("//") > 1:
        pass

    return url_string


def getRandomUserAgentString():
    listOfUserAgentStrings = ["Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)", "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36", "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36", "Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36", "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36", "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36", "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36", "Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36", "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36", "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)", "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; WOW64; Trident/6.0)", "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)", "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; ARM; Trident/6.0)", "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0", "Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0", "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20130401 Firefox/31.0", "Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0", "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20120101 Firefox/29.0", "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/29.0"]
    return random.choice(listOfUserAgentStrings)

def getTitleFromSoup(soup):
    soup_title = str(soup.title)
    if soup_title:
        return soup_title.replace("<title>","").replace("</title>","").split(" -")[0].strip().split(" |")[0].strip()
    else:
        return None

# do header keywords appear a lot
def isHeader(text):
    text = text.lower()
    return sum(word in text for word in ('about','contact','goals','principles')) >= 4


def getMostRepeatedContentFromSoup(soup, test=None, testTagName=None, testChildren=None):
    candidates = []
    for index, element in enumerate(list(soup.descendants)):

        if not isinstance(element, Doctype) and not isinstance(element, NavigableString) and not isinstance(element, Comment):

            children = list(element.children)

            #removes text nodes and divs with blank text for clearing
            children = [c for c in children if c.name and c.text.strip()]

            number_of_children = len(children)
            if number_of_children >= 5:
                names = [child.name for child in children]
                counter = Counter(names)
                tagName, count = counter.most_common(1)[0]

                # sometimes the most common tagName is None because it's like a string node, so get the next one
                if tagName is None:
                    tagName, count = counter.most_common(2)[1]

                if tagName and count >= 5 and testTagName(tagName) if testTagName else True:
                    ##print "tagName is", tagName
                    freq = float(count) / float(number_of_children)
                    if freq > 0.5:
                        if test(element):
                            posts = [child for child in children if child.name == tagName]
                            if 100 < median([len(child.text) for child in posts]) < 1000:
                                candidate = {}
                                candidate['element'] = element
                                candidate['children'] = posts
                                candidates.append(candidate)
    number_of_candidates = len(candidates)
    if number_of_candidates == 0:
        pass
        ##print "number_of_candidates = 0"
    elif number_of_candidates == 1:
        return list(candidates[0]['children'])
    elif number_of_candidates > 1:
        ##print "num cands", number_of_candidates
        for candidate in candidates:
            ##print "\n\n\ncandidate is", str(candidate['element'])[:1000].replace("\r","").replace("\n","")
            ##print "candidate .tagName is", candidate['element'].name
            candidate['average_length_of_child'] = median([len(child.text) for child in candidate['children']])
            ##print "candidate['average_length_of_child is", candidate['average_length_of_child']
            ##print "standard deviation is ", std([len(child.text) for child in candidate['children']])
            ##print "average_length_of_child = ", average_length_of_child
            #candidate['average_length_of_child'] = average_length_of_child
        candidates.sort(key = lambda x : -1*x['average_length_of_child'])
        ##print "candidates[0] is", candidates[0]
#        return candidates[0]
    

# code that basically get the posts and the first link in the posts
def getPostUrlsFromSoup(soup):
    script = """
    var candidates = [];
    var elements = document.body.querySelector("*");
    for (var a = 0; a < elements.length; a++) {
        var element = elements[a];
    }

    """
    return driver.execute_script(script)

###################################################################

GET_POST_ELEMENTS_JAVASCRIPT = """

    var posts = [];

    var elements = Array.prototype.slice.call(document.body.getElementsByTagName("*"));

    elements = elements.filter(function(element){
        return element.textContent.length > 100;
    });

    elements = elements.filter(function(element){
        return element.clientHeight > 500;
    });

    elements = elements.filter(function(element){
        return element.clientWidth > 300;
    });


    for (var a = 0 ; a < elements.length; a++) {
        element = elements[a];
        children = Array.prototype.slice.call(element.children);
        children = children.filter(function(child){
            return child.textContent.length > 0;
        });

        if (children.length >= 5) {
            names = children.map(function(child){return child.tagName;});
            counter = {};
            names.forEach(function(name) {
                counter[name] = counter[name] + 1 || 1
            });
            most_common_tag_name = 0; most_common_count = 0;
            for (var tagName in counter) {
                if (counter[tagName] > most_common_count) {
                    most_common_count = counter[tagName];
                    most_common_tag_name = tagName;
                }
            }

            if (most_common_count >= 5) {
                console.log("children are", children);
                posts = posts.concat(children);
            }
        }
    }

"""

# basically sees if something repeats more than 5 times
def getPostsFromSoup(soup, selector_for_posts=None):
    #print "starting getPostsFromSoup with ", type(soup), str(soup)[:200]

    # see if any posts that match selector_for_posts exist
    # if true, just return them and don't bother with algorithmic finding
    # could probably improve this by validating list returned by soup.select
    if selector_for_posts:
        posts = soup.select(selector_for_posts)
        if posts:
            return posts

    candidates = []
    for index, element in enumerate(list(soup.descendants)):

        if not isinstance(element, Doctype) and not isinstance(element, NavigableString) and not isinstance(element, Comment):

            element_text = element.text
            if not isHeader(element_text) and len(element_text) > 100:

                #print "\nelement is", element.name, "#", element.get("id"), ".", element.get("class")

                children = list(element.children)

                #removes text nodes and divs with blank text for clearing
                children = [c for c in children if c.name and c.text.strip()]

                number_of_children = len(children)
                #print "\tnumber_of_children =", number_of_children

                if number_of_children >= 5:
                    names = [child.name for child in children]
                    counter = Counter(names)
                    tagName, count = counter.most_common(1)[0]

                    # sometimes the most common tagName is None because it's like a string node, so get the next one
                    if tagName is None:
                        tagName, count = counter.most_common(2)[1]

                    if tagName and count >= 5 and tagName not in ("p","head","script"):
                        #print tagName, "\tcount is greater than 5"
                        freq = float(count) / float(number_of_children)
                        #print "\tfreq is", freq
                        if freq > 0.5:
                            posts = [child for child in children if child.name == tagName]
                            number_of_posts = len(posts)

                            # filter by classes
                            # basically sometimes there's a pagination div that doesn't fit

                            # if there are classes used, there should be some overlap
                            counter_of_classes = Counter()
                            for post in posts:
                                counter_of_classes.update(post.get("class"))
                            shared_classes = []
                            for classname, count in counter_of_classes.iteritems():
                                if count >= number_of_posts - 1:
                                    shared_classes.append(classname)

                            if len(shared_classes) >= 4:
                                #print "\tfiltering out posts that don't share classes with all the other posts"
                                posts = [p for p in posts if any([sc in p.get("class") for sc in shared_classes])]

                            texts = [post.text.replace(" ","").replace("\n", "") for post in posts]
                            lengths_of_posts = [len(text) for text in texts]
                            #print "\tlengths_of_posts = ", lengths_of_posts
                            median_of_posts = median(lengths_of_posts) 
                            #print "\tmedian_of_posts is", median_of_posts
                            standard_deviation_of_posts = std(lengths_of_posts) 
                            #print "\tstandard_deviation_of_posts = ", standard_deviation_of_posts
                            if 100 < median_of_posts < 2000 and standard_deviation_of_posts < 200:
                                candidate = {}
                                candidate['element'] = element
                                candidate['children'] = posts
                                candidates.append(candidate)
    number_of_candidates = len(candidates)
    #print "number_of_candidates is", number_of_candidates
    if number_of_candidates == 0:
        pass
        #print "number_of_candidates = 0"
    elif number_of_candidates == 1:
        return list(candidates[0]['children'])
    elif number_of_candidates > 1:
        #print "num cands", number_of_candidates
        for candidate in candidates:
            #print "\n\n\ncandidate is", str(candidate['element'])[:5000].replace("\r","").replace("\n","")
            #print "candidate .tagName is", candidate['element'].name
            candidate['average_length_of_child'] = median([len(child.text) for child in candidate['children']])
            ##print "candidate['average_length_of_child is", candidate['average_length_of_child']
            ##print "standard deviation is ", std([len(child.text) for child in candidate['children']])
            ##print "class is", candidate['element']['class']
            ##print "average_length_of_child = ", average_length_of_child
            #candidate['average_length_of_child'] = average_length_of_child
        candidates_with_keywords = [c for c in candidates if findStatementsHrefFromSoup(c['element'])]
        number_of_candidates_with_keyword = len(candidates_with_keywords)
        if number_of_candidates_with_keyword == 0:
            candidates.sort(key = lambda x : -1 * x['average_length_of_child'])
            return candidates[0]['children']
        elif number_of_candidates_with_keyword == 1:
            return candidates_with_keywords[0]['children']
        elif number_of_candidates_with_keyword > 1:
            candidates_with_keywords.sort(key = lambda x : -1 * x['average_length_of_child'])
            return candidates_with_keywords[0]['children']


# basically filter out the most repeated content by text length
# because a post is highly unlikely to consist of less than 100 characters!
def OLDgetAPostsFromSoup(soup):
    #make sure posts average post is at least 100 characters long
    testChildren = lambda x: mean([len(e) for e in x]) > 100

    # and posts are highly unlikely to be grouped as paragraph tags
    # paragraph tags are more likely to be paragraphs in a post!
    testTagName = lambda tagName: not tagName in ("p","head","script")

    return getMostRepeatedContentFromSoup(soup, test=test, testTagName=testTagName, testChildren=testChildren)

def getPostsFromText(text):
    return getPostsFromSoup(BeautifulSoup(text,'html.parser'))

def removeCommentsFromElement(element):
    ##print "\t\t\tstarting removeCommentsFromElement"
    descendants = list(element.descendants)
    ##print "descendants are", type(descendants)
    for tag in descendants:
        if tag and isinstance(tag, Comment):
            try:
                tag.extract()
            except:
                pass
    ##print "\t\t\tfinishing removeCommentsFromElement"
    return element

def trimElement(soup):
    ##print "starting trimSoup", type(soup)
    descendants = list(soup.descendants)
    ##print "len descendants is", len(descendants)
    for tag in soup.descendants:
        ##print "for tag", str(tag)[:100]
        if isinstance(tag, Comment):
            tag.extract()
        elif isinstance(tag, NavigableString):
            pass
        elif isinstance(tag, Tag):
            pass
#        elif tag.get('id') in ("ja-footer","ja-left","ja-right"):
            ##print "tag.get('id') is ", type(tag), tag.get("id"), tag.get("class"), tag.string[:100]

            #tag.extract()
    ##print "finishing trimSoup"

    return soup


def getVisibleTextFromElement(element):
    ##print "\t\tstarting getVisibleTextFromElement with", type(element)

    [e.decompose() for e in body('script')]
    [e.decompose() for e in body('style')]
    [e.decompose() for e in body('title')]
    [e.extract() for e in body(text=lambda x: isinstance(x, Comment))]
 
    return " ".join([unicode(e) for e in element(text=True)])

def getMainPartFromSoup(soup, selector=None):
    ##print "\t starting getMainPartFromSoup with ", type(soup), selector
    found_via_selector = False

    if selector:
        soup_select_selector = soup.select(selector)
        if len(soup_select_selector) == 1:
            ##print "found main part via selector", selector
            element = soup_select_selector[0]
            selected = {'element': element, 'text': element.text, 'selector': selector}
            found_via_selector = True

    if not found_via_selector:

        body = soup.body

        regex_side = re.compile(".*side.*")
        [e.decompose() for e in body('iframe')]
        [e.decompose() for e in body('script')]
        [e.decompose() for e in body('style')]
        [e.decompose() for e in body('title')]
        [e.extract() for e in body(text=lambda x: isinstance(x, Comment))]
        [e.extract() for e in body(id=regex_side)]

        # urgh, sometimes the main part of the text is contained by
        # div#main-content.container.sidebar-left
        #[e.extract() for e in body(class_=regex_side)]
        [e.extract() for e in body(class_="articles_section")]
        [e.extract() for e in body('header')]
        [e.extract() for e in body(id=re.compile(".*header.*"))]
        [e.extract() for e in body(class_="header")]
        [e.extract() for e in body('footer')]
        [e.extract() for e in body(id=re.compile(".*footer.*"))]
        [e.extract() for e in body(class_="footer")]




        text = body.text
        length = len(text)    
        selected = {"element": body, "length": length, "text": text}
        ##print "\tselected is", type(selected)

        count = 0
        while True:
            ##print "while True"
            max_length = 0
            candidate = None
            children = selected['element'].contents
            ##print "children is", children
            for child in children:
                if not isinstance(child, Doctype) and not isinstance(child, NavigableString):
                    if child.name not in ("script", "link") and child.get("id") not in ("ja-right","ja-left"):
                        ##print "for child"
                        ##print "\ttype(child) is", type(child)
                        ##print "\tchild.name is", child.name
                        ##print "\tchild.get('id') is", child.get('id')
                        ##print "\tchild.get('class') is", child.get("class")
                        text = child.text
                        length = len(text)
                        ##print "\tlen is", length
                        ##print "\ttext is", text[:300]
                        if length > max_length:
                            max_length = length
                            candidate = {"element": child, "length": length, "text": text}
            ##print "    max_length is", max_length
            if candidate and float(candidate['length']) / float(selected['length']) > .5:
                ##print "selected", candidate['text'].replace("\r","").replace("\n","")[:300]
                selected = candidate
            else:
                break
            if count > 2000:
                break
            else:
                count += 1
        selected['selector'] = getSelectorFromElement(selected['element'].parent) + " > " + getSelectorFromElement(selected['element'])
    ##print "\t\tabout to calc result"
    #result = "\r\n\r\n".join([paragraph for paragraph in selected['text'].splitlines() if paragraph and not isJavaScript(paragraph) and paragraph.lower() not in ("tweet","powered by web marketing")])
    text = sub("[\r\n]+[\r\n\t ]*[\r\n]+", "\r\n\r\n", selected['text'], flags=flags)
    text = sub("\t+"," ", text)
    text = text.replace(u'\xa0', u' ')
    selected['text'] = text
    text = text.strip()
    ##print "\t finishing getMainPartFromSoup with ", selected
    return selected

def getSelectorFromElement(element):
    ##print "starting getSelectorFromElement with", type(element)
    selector = element.name
    element_id = element.get("id")
    if element_id:
        selector += "#" + element_id
    classAsList = element.get("class")
    if classAsList:
        selector += "." + ".".join(classAsList)
    ##print "finishing getSelectorFromElement with", selector
    return selector
   
def getMainPartFromText(text, selector=None):
    ##print "starting getMainPartFromText"
    mainPart = getMainPartFromSoup(BeautifulSoup(text, 'html5lib'), selector=selector)
    ##print "finishing getMainPartFromText with", type(mainPart)
    return mainPart

def getCleanTextFromSoup(soup):

    body = soup.body

    regex_side = re.compile(".*side.*")
    [e.decompose() for e in body('script')]
    [e.decompose() for e in body('style')]
    [e.decompose() for e in body('title')]
    [e.extract() for e in body(text=lambda x: isinstance(x, Comment))]
    [e.extract() for e in body(id=regex_side)]
    #[e.extract() for e in body(class_=regex_side)]
    [e.extract() for e in body(class_="articles_section")]
    [e.extract() for e in body('header')]
    [e.extract() for e in body(id=re.compile(".*header.*"))]
    [e.extract() for e in body(class_="header")]
    [e.extract() for e in body('footer')]
    [e.extract() for e in body(id=re.compile(".*footer.*"))]
    [e.extract() for e in body(class_="footer")]

    text = body.text

    text = sub("[\r\n]+[\r\n\t ]*[\r\n]+", "\r\n\r\n", text, flags=flags)
    text = sub("\t+"," ", text)
    text = text.replace(u'\xa0', u' ')
    return text

def getCleanTextFromText(text):
    return getCleanTextFromSoup(BeautifulSoup(text, 'html5lib'))

def getMainTextFromSoup(text):
    return getMainPartFromSoup(soup)['text']

def getMainTextFromText(text):
    ##print "starting getMainTextFromText with", text[:300]
    return getMainPartFromSoup(BeautifulSoup(text, 'html5lib'))['text']

def getMainTextFromUrl(url):
    return getMainTextFromText(getAnonymouslyViaCurl(url)['html'])

x = getMainTextFromText


terms = {}
terms['ar'] = ("ar","arabic",u"\u0639\u0631\u0628\u064a")
terms['en'] = ("en","english")
terms['fr'] = ("fr","french")
terms['tr'] = ("tr","turkish",u'\u0054\u00fc\u0072\u006b\u00e7\u0065')
terms['ku'] = ('ku','kurdish')

# Sorani version of Kurdish
terms['ku-so'] = ('sorani',u'\u0643\u0648\u0631\u062f\u0649')

# Kurmanci version of Kurdish
terms['ku-ku'] = ('kurmanci','kurmanji','kurmangi',u'\u004b\u0075\u0072\u0064\u00ee',u'Daxuyan\xee')

def getLanguageVersionUrlsFromDriver(driver):
    d = {}
    script = """
    result = {};
    var terms = {};
    terms.ar = ["ar","arabic","\u0639\u0631\u0628\u064a","\u0061\u0072\u0061\u0062\u0069\u0063  \u0639\u0631\u0628\u064a"];
    terms.en = ["en","english"];
    terms.fr = ["fr","french"];
    terms.tr = ["tr","turkish"];
    terms.ku = ["ku","kurdish"];
    terms.ku_so = ["sorani"];
    terms.ku_ku = ["kurmanci","kurmanji","kurmangi"];
    var a_tags = document.getElementsByTagName("a");
    for (var i = 0; i < a_tags.length; i++) {
        a_tag = a_tags[i];
        href = a_tag.href;
        if (href) {
            // the regex trims it
            text = a_tag.textContent.toLocaleLowerCase().replace(/^\s+|\s+$/g, '');
            if (text) {
                for (var key in terms) {
                    var key_terms = terms[key];
                    if (key_terms.indexOf(text) > -1) {
                        if (href.startsWith("http")) {
                            result[key] = href;
                        }
                        else {
                            result[key] = document.location.origin + href;
                        }
                    }
                }
            }
        }
    }
    return result;
    """
    return driver.execute_script(script)


# get the different language version of a website
def getLanguageVersionUrlsFromSoup(soup, domain):
    d = {}
    for a in soup.findAll("a", href=True):
        text = a.text.lower().strip()
        href = a['href']
        for key, values in terms.iteritems():
            if text in values:
                ##print "text is", [text]
                ##print "match!"
                ##print "\thref is", href
                if href.startswith("http"):
                    d[key] = href
                else:
                    d[key] = domain + href
    return d
           
def getLanguageVersionUrlsFromText(text):
    return getLanguageVersionUrlsFromSoup(BeautifulSoup(text))

def guessLanguageOfUrl(url):
    for key, values in terms.iteritems():
        if re.search("(" + "|".join(values) + ")", url):
            return key

# get the links to different posts from the soup
# different than getting hrefs or posts, because this way get full absolute url because have to pass in domain
def getUrlsFromSoup(soup, domain, selectors_for_post=None):
    domain = domain.lower()
    #print "\nstarting getUrlsFromSoup with", type(soup), "and", domain
    posts = getPostsFromSoup(soup, selectors_for_post)
    #print "\tposts from getPostsFromSoup = ", len(posts or [])
    if posts:
        hrefs = []
        for post in posts:
            for a in post.findAll("a", href=True):
                href = a['href']
                href_lower = href.lower()
                #print "\thref is", href
                if not any(href_lower.endswith(ext) for ext in ('gif','jpeg','jpg','png')):
                    #print "\thref passed"
                    if href_lower.startswith("http"):
                        if href_lower.startswith(domain):
                            hrefs.append(href)
                    elif href_lower.startswith("javascript"):
                        pass
                    else:
                        hrefs.append(domain + href)
        #print "\treturning hrefs", len(hrefs), "\n"
        return hrefs

def getUrlsFromText(text, domain):
    open("/tmp/text.html","wb").write(text.encode("utf-8"))
    return getUrlsFromSoup(BeautifulSoup(text, "html5lib"), domain)
