import requests
import argparse
import re 
import json
import csv
import os

#Cut the url into 2 where the postal code should be in between both url1 and url2
url1 = "https://www.onemap.gov.sg/api/common/elastic/search?searchVal="
url2 = "&returnGeom=Y&getAddrDetails=Y"

#Regex for exactly 6 digits
pattern = r'^\d{6}$'

#Checks that the postal code is 6 digit code 
def validate_addr(addr: str) -> bool:
    #convert string to integer 
    return bool(re.match(pattern, addr))


#This function takes in a postal code and returns the lat and lon
def convert_addr(addr: str):
    print(f"Processing the postal code now...")
    response = requests.get(addr)

    if response.status_code == 200:
        # print(f"result: {response.text}")

        #Convert to json
        r = json.loads(response.text)['results'][0]

        lat = r["LATITUDE"]
        lon = r["LONGITUDE"]

        print(f"lat is {lat}. lon is {lon}.")
        return lat, lon

    else:
        print(f"Received 400 response from ONEMAP api :(")
        return None, None


def process_csv(filePath: str):
    #read in the csv
    data = []
    headers = None
    with open(filePath, 'r') as file:
        csv_reader = csv.reader(file)
        # Skip header row if present
        headers = next(csv_reader)
        for row in csv_reader:
            data.append(row)

    # print(data[1])

    output = [
        headers
    ]
    output[0].append('latitude')
    output[0].append('longitude')

    dir = os.path.dirname(filePath)
    oFilePath = dir+'/results.csv'
    with open(oFilePath, 'w', newline='') as file:
        writer = csv.writer(file)
        
        #Add in the header
        writer.writerow(output)

        #Add in the data
        for row in data: 
            #Get the result first
            query = row[0] + " " + row[1]
            lat, lon = convert_addr(url1+query+url2)
            row.append(lat)
            row.append(lon)
            writer.writerow(row)


#Start of script
parser = argparse.ArgumentParser(
                prog='convert_addr_to_latlon',
                description='this program converts a postal code to decimal lat long coodinates')
parser.add_argument('addr', type=str, action='store', help='postal code of the address')
parser.add_argument('--csv', action='store_true')
parser.add_argument('--input', type=str, action='store', help='input file path of the csv with block names')


args = parser.parse_args()

addr = args.addr
csvMode = args.csv
print(f"Received the address postal code: {addr}")
print(f"Received the csv flag: {csvMode}")

if not csvMode:
    #Check that there are exactly 6 digits in the postal code 
    # if validate_addr(addr):
    #     #get the address of the postal code 
    #     convert_addr(url1+addr+url2)
    # else:
    #     print(f"The postal code entered is not valid. Try again with a 6 digit number")
    convert_addr(url1+addr+url2)

else: #process a csv of postal codes
    csvFilePath = args.input
    print(f"Received the file path of the csv file: {csvFilePath}")

    if not os.path.exists(csvFilePath): 
        print(f"Cannot find csv file!")
    else:
        process_csv(csvFilePath)
