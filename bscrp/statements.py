from re import IGNORECASE, MULTILINE, search, UNICODE
flags = IGNORECASE|MULTILINE|UNICODE

def findStatementsUrlsFromSoup(soup, domain):
    url = findStatementsUrlFromSoup(soup, domain)
    if url:
        return [url]

def findStatementsUrlFromSoup(soup, domain):
    href = findStatementsHrefFromSoup(soup)
    if href:
        if href.startswith("http"):
            return href
        else:
            return domain + href

"""
# bas\u0131n = press in Turkish
# bildirisi = statement in Turkish
# "b\u0130ld\u0130r\u0130ler\u0130" has capitalized I's, need to also add lowercase
# bildirileri = statements in Turkish 
# a\u00e7\u0131klamalar\u0131 = releases in Turkish
# presse = press in French
# \u0627\u0644\u0628\u064a\u0627\u0646\u0627\u062a = bayanaat
"""
def findStatementsHrefFromSoup(soup):
    terms = (u"a\u00e7\u0131klamalar\u0131",u"bas\u0131n",u"bildirisi",u"b\u0130ld\u0130r\u0130ler\u0130",u"daxuyan\xee","press", "statements", u"\u0628\u064a\u0627\u0646\u0627\u062a", u"\u0627\u0644\u0635\u062d\u0641\u064a\u0629", u"\u0627\u0644\u0635\u062d\u0641\u064a\u0629", u"\u0627\u0644\u0628\u064a\u0627\u0646\u0627\u062a \u0627\u0644\u0631\u0633\u0645\u064a\u0629","speeches",u"\u0628\u064a\u0627\u0646\u0627\u062a \u0627\u0644\u0647\u064a\u0626\u0629", u"\u0628\u064a\u0640\u0640\u0627\u0646\u0640\u0627\u062a \u0631\u0633\u0640\u0640\u0640\u0645\u064a\u0640\u0629",u"\u0052\u0065\u0073\u006d\u0069 \u0041\u00e7\u0131\u006b\u006c\u0061\u006d\u0061\u006c\u0061\u0072",u"resmi a\xe7\u0131klamalar", u"\u0627\u0635\u062f\u0627\u0631\u062a", u"\u0627\u0644\u0628\u064a\u0627\u0646\u0627\u062a", u"bayanaat", u"bayanat", u"bayyanat", u"comments", u"\u062a\u0635\u0631\u064a\u062d\u0627\u062a")
    hrefs = []
    for a in soup.findAll("a", href=True):
        href = a['href']
        #print "href is", href
        href_lower = href.lower()
        href_length = len(href_lower)
        text = a.text.strip().lower()
        #print "text is", [text]
        text_length = len(text)
        if text:
            for term in terms:
                if (term in text and len(term) + 10 > text_length) or (term in href_lower and len(href_lower) < 50):
                    if "wordpress" not in text and "wordpress" not in href_lower and href != "#":
                        #print "term is ", [term]
                        hrefs.append(href)
                        #print "hrefs are now", hrefs
                        break
    hrefs.sort(key=len)
    if hrefs:
        return hrefs[0]

def findStatementsUrlFromDriver(driver):
    script = """
        var terms = ["a\u00e7\u0131klamalar\u0131","bas\u0131n","bildirisi","b\u0130ld\u0130r\u0130ler\u0130","press", "statements", "\u0627\u0644\u0635\u062d\u0641\u064a\u0629", "\u0627\u0644\u0635\u062d\u0641\u064a\u0629"];
        var a_tags = document.getElementsByTagName('a');
        for (var i = 0; i < a_tags.length; i++) {
            var a_tag = a_tags[i];
            var href = a_tag.href;
            if (href) {
                var text = a_tag.textContent;
                for (var t  = 0; t < terms.length; t++) {
                    var term = terms[t];
                    if (href.indexOf(term) + text.indexOf(term) != -2) {
                        if (href.startsWith("http") > -1) {
                            return href;
                        } else {
                            return document.location.origin + href
                        }
                    }
                }
            }
        }
    """
    return driver.execute_script(script)
