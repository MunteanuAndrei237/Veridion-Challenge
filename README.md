# Veridion Challenge - Address Extraction
Write a program that extracts all the valid addresses that are found on a list of company websites. The format in which you will have to extract this data is the following: country, region, city, postcode, road, and road numbers. 
# Disclaimer
This is only the first version , with only a succes rate of 36% .In next versions, I plan to introduce multithreading to enhance speed and integrate Pyppeteer for executing JavaScript in a headless Chrome or Chromium browser. Additionally, I aim to refine existing regular expressions and expand the use of keywords to enhance address detection. While the initial focus was on simplicity and speed, I believe that with these enhancements, I can significantly improve the success rate of the program.
# Approach 
I aimed to develop a fast and customizable program that can be easily adapted to varying needs. For instance, users have the flexibility to adjust parameters such as the timeout duration for requests, the maximum number of pages to be explored within a domain before termination, the number of concurrent threads, the keywords, and the criteria for determining the validity of an address. To ensure efficiency, the program utilizes high-performance libraries such as PyQuery for page scraping, Nominatim for address validation, and potentially Pyppeteer for executing JavaScript in a headless Chrome/Chromium browser.
# Program and solution
The program iterates through domains and sends requests to their servers, using an user agent. Upon receiving a successful response (status code 200), it conducts a brute-force search on the first page using regex patterns for postal codes and street addresses. This initial search is based on the assumption that vital address information might be present in common sections like the footer, header, or main content area. If the address is not found, the program employs a breadth-first search (BFS) algorithm to navigate through subsequent pages, focusing on essential elements such as Google Maps links, iframes, and address tags. The search process terminates when the maximum number of pages to be explored (defined by the 'searchingLimit') is reached.

URLs for BFS exploration are gathered from anchor tags ('<a>') with 'href' attributes, and a regex search is performed to identify the domain presence. Additionally, relative URLs (those starting with '.' or '/') are constructed based on the current path. URLs are prioritized based on keywords indicative of importance (e.g., 'about', 'location', 'map', 'contact'). If postal codes, coordinates, or street names are discovered, the program utilizes Nominatim to retrieve additional address details.

The final result includes the found address, the corresponding domain, and any errors encountered during the process and is written in a .csv file.
# Important decisions and their reasoning
No Request Retries:

Based on extensive testing (1000 tests), not a single request returned a status code 200 after failing initially. Therefore, we opt not to retry requests, as there was no observable benefit from doing so.
Timeout Period of 5 Seconds:

After analyzing test results (100 tests), it was found that none of the requests responded after a period of 5 seconds. Hence, we decided to set the timeout period to 5 seconds, as this action consumed the most time without yielding positive results.
Brute-Force Search on First Page Only:

The decision to conduct a brute-force search exclusively on the first page is based on the observation that websites often display address information in prominent sections like the footer, header, or menu. This approach capitalizes on the higher likelihood of finding address details on the initial page.
Considering Only the First Address Encountered:

Given that most websites typically display only one address or the first encountered address is often the correct one, we choose to consider only the first address encountered. Additionally, establishing a robust algorithm to link domains with specific addresses would require additional resources, such as using the Google Maps API, which may not be feasible due to cost considerations.
Limiting BFS to First 5 Pages:

Based on testing (1000 tests), address discovery beyond the first 5 pages occurred only twice. Consequently, we limit the breadth-first search (BFS) algorithm to explore only the first 5 pages, focusing on essential pages such as 'about', 'location', 'contact', etc., where address information is most likely to be found.
# Results
I have attached two files: "100tests.csv" and "1000tests.csv". On average, the program processed one domain every 3-4 seconds. In both datasets, we achieved a 36% success rate in obtaining a valid address. Additionally, 11% of websites were unreachable, primarily due to being down or having lost their license. Furthermore, based on manual testing, 12% of websites either did not have a visible address or the address was in a language other than the one supported by our program. Therefore, if we consider only the websites that are "human-readable," our success rate increases to 46%.
# Requirements
Python 3.10.11
pip 24.0
# Installation 
1. open an empty folder
2. run git clone https://github.com/MunteanuAndrei237/Veridion-challenge.git
3. cd Veridion-challenge
4. run pip install -r modules.txt
5. either edit configuration and press Run or run python3 main.py
