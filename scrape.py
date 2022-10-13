import requests
import math
import re
from bs4 import BeautifulSoup
from tqdm import tqdm
import os
import json

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
    
    for p in range(1, pages+1): #loop through each page
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
        collection = collection + g[1]
    
    #print('--TOTAL OF ' + str(len(motors)) + ' LIKELY MOTORS OUT OF ' + str(len(collection)) + ' ITEMS--')
    return motors, collection

def itemURL(item, location):
    return item['href']

def collectItemURLs(items, location):
    urls = []
    for item in items:
        urls.append(itemURL(item, location))
    
    return urls
    
def isolateNumbersInChart(targetText, soup, i, n):
    targetText = targetText.lower()
    values = soup.findAll('td')
    #print(targetText)
    num = '-1'
    c = -1
    
    for td in values:
        #print(targetText)
        if re.search(targetText, td.text.lower()):
            c = c + 1
            if c != n:
                #print('not')
                continue
            #print('\n--')
            td = td.text
            #print(td)
            
            
            td = ''.join([c for c in td if c in '1234567890-. '])
            
            sp = td.split(' ')
            while '' in sp:
                sp.remove('')
            #print('--')
            #print(sp)
            
            
            sp = sp[i]
            #print(sp)
            
            num = sp
            #print(num)
            
            try:
                return float(num)
            except:
                return -2
            
            
    
    return float(num)

def generateDictionary(urls, mainpage):
    
    totalProg = float(len(urls))
    currentProg = -1
    
    _404 = 0
    
    #print(urls[0])
    
    dict = {}
    
    for url in tqdm(urls, unit='motor', desc='Searching for datasheets: '):
        
        currentProg = currentProg + 1
        
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        name = soup.title
        #name = soup.findAll('p', attrs={"id":"toolbar-amount"})
        
        #find data sheet link
        links = soup.findAll('a')
        for link in links:
            #print(link.text)
            if link.text.find("Data Chart") != -1:
                datalink = mainpage + link['href']
            elif link.text == 'CLICK HERE':
                datalink = mainpage + link['href']
        
        r = requests.get(datalink)
        
        #print(datalink)
        #print(r.status_code)
        
        #if soup.title.text.find('404') != -1:#make sure datasheet exist
        if r.status_code == 404:
            _404 = _404 + 1
            continue
            
        soup = BeautifulSoup(r.text, 'html.parser')
        
        
        specs = {
            'Motor kV' : isolateNumbersInChart('rpm/volt', soup, 0, 0),
            'Motor Resistance' : isolateNumbersInChart('^rm = ', soup, 0, 0),
            'I Max' : isolateNumbersInChart('amps$', soup, 0, 0),
            'P Max' : isolateNumbersInChart(' w$', soup, 0, 0),
            'Outside Diameter' : isolateNumbersInChart(' in.$', soup, 1, 0),
            'Body Length' : isolateNumbersInChart(' in.$', soup, 1, 1),
            'Total Shaft Length' : isolateNumbersInChart(' in.$', soup, 1, 2),
            'Motor Weight' : isolateNumbersInChart(' oz$', soup, 1, 0),
        }
        
        rows = soup.findAll('tr', attrs={"style":"mso-height-source:userset;height:14.1pt"})
        alt = soup.findAll('tr', attrs={"style":"mso-height-source:userset;height:18.0pt"})
        
        if len(alt) > len(rows):
            rows = alt
        
        #print(len(rows))
        #print(rows[3].text)
       
        #rows = rows[2 :]
        
        #print(rows[0])
        
        propSizes = {}
        
        for row in rows:
            rowList = row.text.split('\n')
            rowList = list(filter(None, rowList))
            rowList.append('_')
        
            if 'APCGWSMASGraupnerHQ'.find(rowList[0]) == -1:
                continue
                


            
            
            #if ['GWS'].find rowList[0] filter colors here
            
            #print(rowList) DEMONSTRATEDEMONSTRATEDEMONSTRATEDEMONSTRATEDEMONSTRATEDEMONSTRATEDEMONSTRATE
            
            formRow = {
                rowList[1] :
                {
                'Prop Manf' : rowList[0],
                'Input Voltage' : rowList[2],
                'Motor Amps' : rowList[3],
                'Watts Input' : rowList[4],
                'Prop RPM' : rowList[5],
                'Pitch Speed' : rowList[6],
                'Thrust Grams' : rowList[7],
                'Thrust Ounces' : rowList[8],
                'Thrust Eff Grams/W' : rowList[9],
                }
            }
            
            propSizes = propSizes | formRow
        
        #print('\n')
        #print(row)
        
        
        #print('\n')
        
        spread = {
        
        }
        
        part = {
            name.text :
            {
                'url' : url,
                'data_url' : datalink,
                'specs' : specs,
                'prop_sizes' : propSizes
            }
        }
        
        
        
        #print(1)
        dict = dict | part
    
    if _404 > 0:
        print('Info: ' + str(_404) + ' 404 errors encountered')
    
    if _404 + len(dict) < len(urls):
        print('Info: ' + str(len(urls) - _404 - len(dict)) + ' product pages missing datasheet links')
    
    print('Finished with ' + str(len(dict)) + ' motor datasheets read')
        
    return dict
    


def testCase():
    url = 'https://innov8tivedesigns.com/products/brushlessmotors/'
    types = ['cobra-aircraft-motors.html', 'badass-airplane-motors.html', 'tempest-airplane-motors.html']
    #types = ['cobra-aircraft-motors.html']
    items = collectGroups(url, types)
    
    productLocation = 'https://innov8tivedesigns.com/'
    urls = collectItemURLs(items[0], productLocation)
    #print('\nSearching ' + str(len(urls)) + ' motor urls for datasheets...')
    data = generateDictionary(urls, productLocation)
    #print(data)
    
    filename = input('Output .json name: ')
    filename = filename + '.json'

    with open(filename, "w") as outfile:
        json.dump(data, outfile, indent=4)
    
testCase()

input('\nPress enter to close.')