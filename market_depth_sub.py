from bs4 import BeautifulSoup
import os
import redis
import json

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# Define a function to fetch data from the web or cache
def cache_read(instr_code):
    output = redis_client.get(instr_code)
    return str(output, 'UTF-8') if output != None  else ""  

# Rest of your code remains the same
def get_market_depth_of_a_company(instr_code):
    return cache_read(instr_code)



def execute():
    txt_filepath = os.path.join("./", "instrument_codes.txt")
    with open(txt_filepath, "r") as txt_file:
        for line in txt_file:
            instr_code = line.strip()
            result = get_market_depth_of_a_company(instr_code)
            print("{0}-> {1}".format(instr_code, result))


report = execute()
print (report)

# Read instrument codes from a text file
