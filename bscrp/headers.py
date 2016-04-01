from bs4 import BeautifulSoup
from bs4.element import Comment, Doctype, NavigableString, Tag
from collections import Counter

def getHeaderFromText(text):
    soup = BeautifulSoup(text, "html5lib")
    return getHeaderFromSoup(soup)

def getHeaderFromSoup(soup):
    #print "starting getHeaderFromSoup with", type(soup), len(soup.text), soup.text[:300]
    header = soup.header
    if not header:
        nodelist = soup.select("div#header")
        if nodelist:
            header = nodelist[0]

    if not header:
        header = soup
    print "header is", type(header)

    # could first get potential headers and then sort by number of children

    potential_headers = []

    for element in [header] + list(header.descendants):
        if isinstance(element, Tag):
            print "\nfor element", element.name, "#", element.get("id"), ".", element.get("class")
            most_common = Counter([child.name for child in element.children if isinstance(child, Tag)]).most_common()
            print "\tmost_common is", most_common
            if most_common:
                tagName, count = most_common[0]
                print "\ttagName =", tagName
                print "\tcount =", count
                #raw_input()
                if tagName and count >= 4:
                    print "tagName and count over equal 4"
                    #raw_input()
                    results = {}
                    for child in element.children:
                        if isinstance(child, Tag):
                            aTags = child.select("a")
                            print "aTags are", aTags
                            for a in aTags:
                                text = a.text.strip()
                                href = a.get("href")
                                if text and href != "#":
                                    print "\ttext = ", text[:200]
                                    print "\thref = ", href[:200]
                                    results[text] = href
                    potential_headers.append(results)

    print "potential_headers are", len(potential_headers), potential_headers
    if potential_headers:
        selected = sorted(potential_headers, key= lambda d: -1 * len(d))[0]

        print "selected is", selected
        #raw_input()
        return selected
