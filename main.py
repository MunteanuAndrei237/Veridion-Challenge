import pandas as pd
from pyquery import PyQuery as pq
from collections import deque
import threading
import requests
from requests.exceptions import SSLError
from requests.exceptions import ConnectionError
from fake_useragent import UserAgent
import random
from geopy.geocoders import Nominatim
import re
import csv

user_agent = UserAgent()
geolocator = Nominatim(user_agent=user_agent.random)
timeout_time=5 # 5 seconds is more than enough , you can pass a smaller number if you want
searching_limit=5 # pass a huge number if you want it to search all the pages , 5 -10 recomended
threads_number=1 # do not change , I will add multithreading later
min_address_requirements = 4 # number of fields in an address to be considered valid
total_tests = 100
tests=0

address_keywords = ['street', 'road', 'avenue', 'lane', 'boulevard', 'highway', 'route', 'zip', 'postcode', 'city', 'town', 'village', 'county', 'region', 'state', 'province', 'country', 'postal', 'zip']
link_keywords= ['about', 'contact', 'address', 'location', 'find', 'visit', 'reach', 'where', 'map']
link_german_keywords = ['uber', 'kontakt', 'adresse', 'standort', 'finden', 'besuchen', 'erreichen', 'wo', 'karte']
domain_dictionary = {".au": "Australia", ".at": "Austria", ".br": "Brazil", ".ca": "Canada", ".cn": "China", ".fr": "France", ".de": "Germany", ".in": "India", ".it": "Italy", ".jp": "Japan", ".mx": "Mexico", ".nl": "Netherlands", ".ru": "Russia", ".kr": "South Korea", ".es": "Spain", ".ch": "Switzerland", ".uk": "United Kingdom", ".us": "United States", ".ae": "United Arab Emirates", ".se": "Sweden", ".fi": "Finland", ".no": "Norway", ".dk": "Denmark", ".nz": "New Zealand", ".sg": "Singapore", ".pl": "Poland", ".pt": "Portugal", ".gr": "Greece", ".ie": "Ireland", ".be": "Belgium", ".cz": "Czech Republic", ".hu": "Hungary", ".ro": "Romania", ".tr": "Turkey", ".il": "Israel", ".user_agent": "Ukraine", ".ar": "Argentina", ".cl": "Chile", ".co": "Colombia", ".za": "South Africa", ".fi": "Finland", ".se": "Sweden", ".no": "Norway", ".dk": "Denmark", ".nz": "New Zealand", ".sg": "Singapore", ".pl": "Poland", ".pt": "Portugal", ".gr": "Greece", ".ie": "Ireland", ".be": "Belgium", ".cz": "Czech Republic", ".hu": "Hungary", ".ro": "Romania", ".tr": "Turkey", ".il": "Israel", ".user_agent": "Ukraine", ".ar": "Argentina", ".cl": "Chile", ".co": "Colombia", ".za": "South Africa", }
postal_regex_dictionary = {".au": r"(?:^|[\s>])\d{4}(?:$|[\s<])", ".at": r"(?:^|[\s>])\d{4}(?:$|[\s<])", ".br": r"(?:^|[\s>])\d{5}-\d{3}(?:$|[\s<])", ".ca": r"(?:^|[\s>])[ABCEGHJKLMNPRSTVXY]\d[A-Z] \d[A-Z]\d(?:$|[\s<])", ".cn": r"(?:^|[\s>])\d{6}(?:$|[\s<])", ".fr": r"(?:^|[\s>])\d{5}(?:$|[\s<])", ".de": r"(?:^|[\s>])\d{5}(?:$|[\s<])", ".in": r"(?:^|[\s>])\d{6}(?:$|[\s<])", ".it": r"(?:^|[\s>])\d{5}(?:$|[\s<])", ".jp": r"(?:^|[\s>])\d{3}-\d{4}(?:$|[\s<])", ".mx": r"(?:^|[\s>])\d{5}(?:$|[\s<])", ".nl": r"(?:^|[\s>])\d{4}\s?[A-Z]{2}(?:$|[\s<])", ".ru": r"(?:^|[\s>])\d{6}(?:$|[\s<])", ".kr": r"(?:^|[\s>])\d{5}(?:$|[\s<])", ".es": r"(?:^|[\s>])\d{5}(?:$|[\s<])", ".ch": r"(?:^|[\s>])\d{4}(?:$|[\s<])", ".uk": r'\b[A-Z]{1,2}[0-9][A-Z0-9]? [0-9][ABD-HJLNP-UW-Z]{2}\b', ".us": r"(?:^|[\s>])\d{5}(-\d{4})?(?:$|[\s<])", ".ae": r"(?:^|[\s>])\d{5}(?:$|[\s<])", ".se": r"(?:^|[\s>])\d{3}\s?\d{2}(?:$|[\s<])", ".fi": r"(?:^|[\s>])\d{5}(?:$|[\s<])", ".no": r"(?:^|[\s>])\d{4}(?:$|[\s<])", ".dk": r"(?:^|[\s>])\d{4}(?:$|[\s<])", ".nz": r"(?:^|[\s>])\d{4}(?:$|[\s<])", ".sg": r"(?:^|[\s>])\d{6}(?:$|[\s<])", ".pl": r"(?:^|[\s>])\d{2}-\d{3}(?:$|[\s<])", ".pt": r"(?:^|[\s>])\d{4}-\d{3}(?:$|[\s<])", ".gr": r"(?:^|[\s>])\d{3}\s?\d{2}(?:$|[\s<])", ".ie": r"(?:^|[\s>])[A-Z]\d{2}\s?[A-Z]{4}(?:$|[\s<])", ".be": r"(?:^|[\s>])\d{4}(?:$|[\s<])", ".cz": r"(?:^|[\s>])\d{3}\s?\d{2}(?:$|[\s<])", ".hu": r"(?:^|[\s>])\d{4}(?:$|[\s<])", ".ro": r"(?:^|[\s>])\d{6}(?:$|[\s<])", ".tr": r"(?:^|[\s>])\d{5}(?:$|[\s<])", ".il": r"(?:^|[\s>])\d{5}(?:$|[\s<])", ".user_agent": r"(?:^|[\s>])\d{5}(?:$|[\s<])", ".ar": r"(?:^|[\s>])[A-Z]\d{4}[A-Z]{3}(?:$|[\s<])", ".cl": r"(?:^|[\s>])\d{7}(?:$|[\s<])", ".co": r"(?:^|[\s>])\d{6}(?:$|[\s<])", ".za": r"(?:^|[\s>])\d{4}(?:$|[\s<])"}
street_regex = re.compile(r'\d{1,4}\s[a-z]{1,12}\s[a-z]{0,12}\s?(?:street|st|avenue|ave|road|rd|highway|hwy|square|sq|trail|trl|drive|dr|court|ct|parkway|pkwy|circle|cir|boulevard|blvd)\W?(?=[^\w\s,]|$)')

result=[["domain","country", "region", "city", "postcode", "road", "road_numbers","errorType"]]

input_file_path = './list of company websites.snappy.parquet'
domain_input = pd.read_parquet(input_file_path, engine='pyarrow')
domain_list = domain_input['domain'].values
random.shuffle(domain_list)

def filter_links_by_keyword(queue, linkKeywords=link_keywords):
    queue_from_keywords = deque()
    queue_with_keywords = deque()
    queue_without_keywords = deque()

    # Iterate over the queue and check if there are any link_keywords in the url.If so, add the url to the front of the queue
    for url in queue:
        if any(keyword == url.lower()[url.lower().rfind('/')+1:] for keyword in linkKeywords):
            queue_from_keywords.append(url)
        elif any(keyword in url.lower() for keyword in linkKeywords):
            queue_with_keywords.append(url)
        else:
            queue_without_keywords.append(url)
    return queue_from_keywords + queue_with_keywords + queue_without_keywords


#Applies street and postal regex on all the text from the page
def scrape_addresses_brute(document, address_dictionary, TLD):
    if TLD in postal_regex_dictionary:
        postalRegex=postal_regex_dictionary[TLD]
    else:
        postalRegex=r"(?:[\s>])(\d{5,6}(?:[-]\d{4})?)(?:[\s<])"
    compiled_pattern=re.compile(postalRegex)
    #Get the postal codes and sort them by importance
    postal_codes = compiled_pattern.findall(pq(document).html())
    postal_codes = [code.strip(" <>\t\n") for code in postal_codes]
    postal_codes = set([code for code in postal_codes if not re.match(r"\b(?:19[9-9][0-9]|20(?:[0-1][0-9]|2[0-9]|100000|100000|1000))\b", code)])
    postal_codes = list(reversed(sorted(postal_codes, key=len)))

    streets = street_regex.findall(pq(document).html())
    index=0
    #If a postal code is found , try to get an address from geolocator based on it , then add the fields to address_dictionary
    if postal_codes:
        while index< len(postal_codes) and not geolocator.geocode(postal_codes[index]) :
            index+=1
        if index< len(postal_codes) and geolocator.geocode(postal_codes[index]):
            location=geolocator.geocode(postal_codes[index]).address.split(',')
            if address_dictionary["country"]==None:
                address_dictionary["country"]=location[-1]
            if address_dictionary["region"]==None:
                address_dictionary["region"]=location[-2]
            if address_dictionary["city"]==None:
                address_dictionary["city"]=location[-3]
            if address_dictionary["postcode"]==None:
                address_dictionary["postcode"]=postal_codes[index]
    if streets:
        street_number, street_name = streets[0].split(maxsplit=1)
        if address_dictionary["road"]==None:
            address_dictionary["road"]=street_name
        if address_dictionary["road_numbers"]==None:
            address_dictionary["road_numbers"]=street_number
    return address_dictionary


#Looks inside address tag , google maps links (I removed google maps ifrmaes because it was impossible to get data from them)
def scrape_addresses_smart(document, address_dictionary, TLD):
    address_elements = document('address')
    google_maps_link = document('a[href*="google.com/maps"]')

    if google_maps_link:
        coordinates_sub_str = google_maps_link.attr('href')[google_maps_link.attr('href').find('@') + 1:]
        latitude  = coordinates_sub_str.split(',')[0]
        longitude  = coordinates_sub_str.split(',')[1]
        # Extract coordinates , then try to get an address from geolocator based on it , then add the fields to address_dictionary
        if(geolocator.geocode((latitude,longitude))):
            location = geolocator.geocode((latitude,longitude)).address.split(',')
            if address_dictionary["country"] == None:
                address_dictionary["country"] = location[-1]
            if address_dictionary["region"] == None:
                address_dictionary["region"] = location[-3]
            if address_dictionary["city"] == None:
                address_dictionary["city"] = location[-5]
            if address_dictionary["postcode"] == None:
                address_dictionary["postcode"] = location[-2]
            if bool(re.match(r'^-?\d+$',location[1] )):
                if address_dictionary["road_numbers"]==None:
                    address_dictionary["road_numbers"]=location[1]
                if address_dictionary["road"]==None:
                    address_dictionary["road"]=location[2]
            else:
                if address_dictionary["road"]==None:
                    address_dictionary["road"]=location[1]

    if len(address_elements) > 0:
        for address_elem in address_elements:
            address_dictionary=scrape_addresses_brute(pq(address_elem[0]), address_dictionary, TLD)
    return address_dictionary

#Create a BFS like algorithm to jump from page to page , call scrape_addresses_smart for each one , then look for a tags , and if the href matches the
#domain add to filtered_urls. If it is a relative address , create it based on root then add it to filtered_urls.
def BFS_pages(queue, url_argument, domain_name, visited, pages_searched, address_dictionary, TLD):
    global min_address_requirements
    if(pages_searched<searching_limit):
        headers = {
            'User-Agent': user_agent.random
        }
        try:
            response = requests.get(url_argument, headers=headers, timeout=timeout_time)
            document = pq(response.text)

            address_dictionary=scrape_addresses_smart(document, address_dictionary, TLD)

            urls = [a.attrib.get('href') for a in document('a') if a.attrib.get('href') and '#' not in a.attrib.get('href')]
            domain_regex = re.compile(rf'^(?:https?://)?(?:www\.)?{re.escape(domain_name)}/.*')
            filtered_urls = [url.rstrip('/') for url in urls if domain_regex.match(url)]
            #Create relative address and add it to filtered_urls
            for url in urls:
                if url[:4] != "http":
                    if url[-1]=="/":
                        url=url[:-1]
                    if url != "" and url != '.':
                        if url[0] == '.':
                            current_address=queue[0]+"/"
                            while(url[0] == '.'):
                                url=url[1:]
                                current_address=current_address[:current_address.rfind('/')]
                                if url=="":
                                    break
                            filtered_urls.append(current_address+url)
                        elif url[0] == '/':
                            if queue[0][:queue[0].rfind('/')]+url not in filtered_urls:
                                filtered_urls.append(queue[0] + url)
                        else:
                            if ":" not in url:
                                if queue[0][:queue[0].rfind('/')] + "/" + url not in filtered_urls:
                                    filtered_urls.append(queue[0]+"/"+url)

            for url in filtered_urls:
                if url not in visited:
                    visited.add(url)
                    queue.append(url)
            queue.popleft()
            if(TLD!=".de"):
                queue=filter_links_by_keyword(queue)
            else:
                queue = filter_links_by_keyword(queue, link_german_keywords)
            if (sum(1 for value in address_dictionary.values() if value is None) <= 6- min_address_requirements):
                return address_dictionary
            if queue:  # Check if queue is not empty
                BFS_pages(queue, queue[0], domain_name, visited, pages_searched + 1, address_dictionary, TLD)
        except requests.RequestException:
            pass
    return address_dictionary

#Send a request to the domain , if everything ok , look for the address and add it into result . If error , we add the error to the result
def make_request(domain_name, protocol="https://"):
    global result
    url = protocol + domain_name
    headers = {
        'User-Agent': user_agent.random
    }
    errorType= None
    try:
        response = requests.get(url, headers=headers, timeout=timeout_time)  # Set timeout to 5 seconds
        if response.status_code == 200:
            TLD = domain_name[domain_name.rfind('.'):]

            keys = ["country", "region", "city", "postcode", "road", "road_numbers"]
            address_dictionary = {key: None for key in keys}

            if TLD in domain_dictionary:
                address_dictionary["country"] =domain_dictionary[TLD]
            #Call brute search for first page
            address_dictionary=scrape_addresses_brute(pq(response.text), address_dictionary, TLD)
            #If brute search dfid not work , try BFS with smart search on other pages
            if (sum(1 for value in address_dictionary.values() if value is None) >= 6- min_address_requirements):
                address_dictionary=BFS_pages(deque([url]), url, domain_name, set([url]), 0, address_dictionary, TLD)

            result.append([domain_name, address_dictionary["country"], address_dictionary["region"], address_dictionary["city"], address_dictionary["postcode"], address_dictionary["road"], address_dictionary["road_numbers"], errorType])

        else:
            result.append([domain_name, None, None, None, None, None, None, "Error code: " + str(response.status_code)])
    except requests.Timeout:
        if protocol=="https://":
            make_request(domain_name, protocol="http://")
        else:
            result.append([domain_name, None, None, None, None, None, None, "Timeout"])
    except SSLError as e:
        if protocol=="https://":
            make_request(domain_name, protocol="http://")
        else:
            result.append([domain_name, None, None, None, None, None, None, "SSL error: " + str(e)])
    except ConnectionError as e:
        result.append([domain_name, None, None, None, None, None, None, "Connection error: " + str(e)])
    except Exception as e:
            result.append([domain_name, None, None, None, None, None, None, "Other error: " + str(e)])

# Iterate through domain_list and make request for each URL , check the number of tests and finally write the result to the csv file
def process_chunk(chunk):
    global tests
    for domain_name in chunk:
        tests+=1
        make_request(domain_name)
        #print(result[-1]) #remove comment if you want to see address for every domain in console
        if tests>=total_tests:
            with open("allTests.csv", mode='a', newline='', encoding='utf-16') as file:
                writer = csv.writer(file)
                writer.writerows(result)
            break
#Main function , splits the domain list into chunks , appends the chunk to a thread , then calls process_chunk
def main():
    chunk_size = len(domain_list) // threads_number
    domain_chunks = [domain_list[i:i + chunk_size] for i in range(0, len(domain_list), chunk_size)]

    threads = []
    for chunk in domain_chunks:
        thread = threading.Thread(target=process_chunk, args=(chunk,))
        thread.start()
        threads.append(thread)

main()

