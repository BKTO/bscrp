from bs4 import BeautifulSoup

def isErrorPageFromSoup(soup):
    print "starting isErrorPageFromSoup with", len(soup.text)
    text = soup.text.lower().strip()
    for phrase in (u"\u063a\u064a\u0631 \u0645\u0648\u062c\u0648\u062f", "404"):
        print "phrase is", [phrase]
        if phrase in text:
            return True
    return False

def isErrorPageFromHtmlText(html):
    return isErrorPageFromSoup(BeautifulSoup(html, "html5lib"))

def isErrorPageFromTextContent(textContent):

    textContent = textContent.lower().strip()
    for phrase in [u"\u063a\u064a\u0631 \u0645\u0648\u062c\u0648\u062f", "404"]:
        if phrase in textContent:
            return True
    return False
