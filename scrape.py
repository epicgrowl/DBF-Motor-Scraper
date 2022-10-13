import requests
import math
from bs4 import BeautifulSoup




url = 'https://innov8tivedesigns.com/products/brushlessmotors/'


def collectGroup(url, group):
    
    print("Beginning group " + group)
    
    collection = []
    
    #determine number of pages
    r = requests.get(url + group)
    soup = BeautifulSoup(r.text, 'html.parser')
    items = soup.findAll('p', attrs={"id":"toolbar-amount"})
    pagest = items[0].text
    pagest = ''.join([c for c in pagest if c in ' 1234567890-'])
    pagest = pagest[pagest.find('-')+1 :]
    last = int(pagest[: pagest.find(' ')])
    final = int(pagest[pagest.find('  ')+2 :])
    pages = int(math.ceil(final/last))
    print("Detected " + str(pages) + " pages")
    #what's a regex
    
    #per page
    for p in range(1, pages+1):
        r = requests.get(url + group + "?p=" + str(p))

        soup = BeautifulSoup(r.text, 'html.parser')

        items = soup.findAll('a', attrs={"class":"product-item-link"})
        
        items = items[: len(items) - 2] #last two items are always not products
        
        print("Found " + str(len(items)) + " items on page " + str(p))
        #for item in items:
            #print(item['href'])
        
        collection = collection + items
        p=p+1
    
    motors = []
    for item in collection:
        if item.text.lower().find('kv') != -1:
            motors.append(item)
    
    print("Found " + str(len(motors)) + " likely motors out of " + str(len(collection)) + " items\n")
    
    return motors, collection
    



def collectGroups(url, targets):
    print('--BEGINNING '+ str(len(targets)) +' GROUP JOB--\n')

    motors = []
    collection = []

    for target in targets:
        g = collectGroup(url, target)
        motors = motors + g[0]
        collection= collection + g[1]
    
    print('--TOTAL OF ' + str(len(motors)) + ' LIKELY MOTORS OUT OF ' + str(len(collection)) + ' ITEMS--')
    return motors, collection






url = 'https://innov8tivedesigns.com/products/brushlessmotors/'
types = ['cobra-aircraft-motors.html', 'badass-airplane-motors.html', 'tempest-airplane-motors.html']
collectGroups(url, types)