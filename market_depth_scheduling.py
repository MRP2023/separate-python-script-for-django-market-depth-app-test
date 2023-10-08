import requests
from bs4 import BeautifulSoup
import datetime
import os
import json
from cache import Cache
import redis
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger


redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

def fetch_data_by_instr(instr_code):
    html_str = fetch_web_data(instr_code)
    result = instr_web_data_calc(html_str, instr_code)
    return result

def fetch_web_data(instr_code):    
    if instr_code == "KAY":
        instr_code = "KAY%26QUE"
    if instr_code == "AMCL":
        instr_code = "AMCL%28PRAN%29"
    
    company_name = instr_code.replace("&", "%26")
    api_url = "https://dsebd.org/ajax/load-instrument.php"

    s = requests.Session()

    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br, json',
        'accept-language': 'en-US,en;q=0.9',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://dsebd.org',
        'Referer': 'https://dsebd.org/mkt_depth_3.php',
        'sec-ch-ua': '"Chromium";v="107", "Not A(Brand";v="21", "Google Chrome";v="107"',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Length': "0",
    }

    r = s.post(api_url, data="inst=" + company_name, headers=headers)
    return r.text

    
def instr_web_data_calc(html_str, instr_code):
    tables = BeautifulSoup(html_str, "html.parser").findAll("table")

    output = {"buyers": [], "sellers": []}

    if len(tables) >= 4:
        buy_data = tables[2].findAll("td")
        sell_data = tables[3].findAll("td")

        if len(buy_data) > 2:
            i = 3
            while i + 1 <= len(buy_data):
                buyer = dict()
                buyer["Instr_Code"] = instr_code
                buyer["buyer_price"] = float(buy_data[i].text.replace(",", ""))
                buyer["buyer_volume"] = float(buy_data[i + 1].text.replace(",", ""))
                buyer["date"] = str(datetime.datetime.utcnow().strftime("%Y-%m-%d"))
                output["buyers"].append(buyer)
                i += 2

        if len(sell_data) > 2:
            i = 3
            while i + 1 <= len(sell_data):
                seller = dict()
                seller["Instr_Code"] = instr_code
                seller["seller_price"] = float(sell_data[i].text.replace(",", ""))
                seller["seller_volume"] = float(sell_data[i + 1].text.replace(",", ""))
                seller["date"] = str(datetime.datetime.utcnow().strftime("%Y-%m-%d"))
                output["sellers"].append(seller)
                i += 2
    return output

def get_market_depth_of_a_company(instr_code):
    return fetch_data_by_instr(instr_code)


scheduler = BackgroundScheduler()
trigger = IntervalTrigger(seconds=30)


# def update_cached_data():

#     all_keys = redis_client.keys("*")

#     for instr_code_bytes in all_keys:
#         instr_code = instr_code_bytes.decode("utf-8")
#         result = fetch_or_cache_data(instr_code)
#         print(f"Updated cached data for {instr_code}")

def start_operation():
    txt_filepath = os.path.join("./", "instrument_codes.txt")
    with open(txt_filepath, "r") as txt_file:
        for line in txt_file:
            instr_code = line.strip()
            print(f"Updating market depth for {instr_code}")
            result = get_market_depth_of_a_company(instr_code)
            redis_client.setex(instr_code, 60, json.dumps(result))
            # Process the result as needed
            print(result)





scheduler.add_job(start_operation, trigger=trigger)
scheduler.start()

try:
    while True:
        pass
except KeyboardInterrupt:
    pass