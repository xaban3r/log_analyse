from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import config
import time
import json
import requests
import user_agents
import query_string
from loader import db

class Handler(FileSystemEventHandler):
    def on_modified(self, event):
        file_reading = open(config.PATH, 'r')
        query_str = file_reading.readlines()[-1]
        print(query_str)
        try:
            visitor_info = query_analyse(query_str) # анализ полученной строки
            if visitor_info:
                insert_visit(visitor_info)
        except Exception as e:
            pass

def insert_visit(parameters: dict): # добавление записи в БД
    db.add_visit(host=parameters["webserver_info"]["host"],
                 server_name=parameters["webserver_info"]["server_name"],
                 time=parameters["webserver_info"]["time"],
                 date=parameters["webserver_info"]["date"],
                 country_name=parameters["geoip_info"]["country_name"],
                 region_name=parameters["geoip_info"]["region_name"],
                 city_name=parameters["geoip_info"]["city_name"],
                 os_family=parameters["useragent"]["os_family"],
                 browser_family=parameters["useragent"]["browser_family"],
                 device_family=parameters["useragent"]["device_family"],
                 other_duid=parameters["query"]["other_duid"])

def query_analyse(query):
    query = json.loads(query)
    if query["query_string"]:
        processed_result = {}
        date_time = query["time"].split('T')
        processed_result["webserver_info"] = {"host": query["host"],
                                                   "server_name": query["server_name"],
                                                   "date": date_time[0],
                                                   "time": date_time[-1]}
        try:
            response = requests.get(url=f'http://ip-api.com/json/{query["remote_addr"]}').json()
            processed_result["geoip_info"] = {"country_name": response.get("country"),
                                                   "region_name": response.get("regionName"),
                                                   "city_name": response.get("city"),
                                                   "IP": response.get("query")}

        except requests.exceptions.ConnectionError:
            print('[!] Please check your connection!')

        if len(query["user_agent"]) > 0:
            user_agent = user_agents.parse(query["user_agent"])
            processed_result["useragent"] = {"os_family": user_agent.os.family,
                                                  "os_version_string": user_agent.os.version_string,
                                                  "browser_family": user_agent.browser.family,
                                                  "browser_version_string": user_agent.browser.version_string,
                                                  "device_family": user_agent.device.family,
                                                  "device_brand": user_agent.device.brand,
                                                  "device_model": user_agent.device.model,
                                                  "simple": str(user_agent)}
        request_query_string = query["query_string"]
        if len(request_query_string) > 0:
            query_dict = query_string.parse(request_query_string)
        if "query_dict" in locals() and query_dict != None:
            processed_result["query"] = {"other_duid": query_dict["duid"]}
        return processed_result


if __name__ == "__main__":
    observer = Observer()
    observer.schedule(Handler(), path=config.PATH, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()
