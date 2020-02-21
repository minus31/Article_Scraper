# -*- coding: utf-8 -*- 

import requests
from bs4 import BeautifulSoup
import time
import pickle 
import pandas as pd
import argparse
import datetime

def body_extractor(link):
    
    soup = BeautifulSoup(requests.get(link).content, 'html.parser')
    category = soup.select_one(".category").text

    return category, soup.select_one("div.text").text.strip().replace(r"\n", "").replace(r"\r", "").replace(r"■", "").replace(r"▲", "")


def save_file(filename, result):

    df = pd.DataFrame()

    df["title"] = result[0]
    df["link"] = result[1]
    df["category"] = result[2]
    df["date"] = result[3]
    df["body"] = result[4]
    
    with open(filename, "wb") as f:
        pickle.dump(df, f)
        

def hankyerae_crawler(query, file_name="./han.bin", time_limit=None):
    
    
    # data containers 
    titles = []
    links = []
    categories = []
    dates = []
    bodies = []
    
    i = 0 
    nobody = 0
    cond_loop = True
    
    while cond_loop:
        try:
            print("-" * 30)
            print('{} page is start'.format(i+1))

            url = "http://search.hani.co.kr/Search?command=query&keyword={}&media=news&sort=d&period=all&datefrom=2000.01.01&dateto=2019.06.05&pageseq={}".format(query, i)
            res = requests.get(url)
            soup = BeautifulSoup(res.content, 'html.parser')

            if len(soup.select(".search-none")) != 0:
                print('***** no result! *****')
                break

            for art, da in zip(soup.select("dt > a"), soup.select(".date > dl > dd")):

                title = art.text
                if len(title) == 0:
                    nobody += 1
                    continue

                link = art["href"]
                if len(link) == 0:
                    nobody += 1
                    continue

                date = da.text
                if len(date) == 0:
                    date = "unknown_date"

                try:
                    category, body = body_extractor(link)
                    if len(body) == 0:
                        print("no body")
                        nobody += 1
                        continue
                    if len(category) == 0:
                        category = 'unknown_category'

                except Exception as ex:
                    print(ex)
                    nobody += 1
                    continue

                titles.append(title)
                links.append(link)
                categories.append(category) 
                dates.append(date)
                bodies.append(body)
                
                # try :
                #     if str(date[:4]) < 2010:
                #         print("No Need before 2010 ")
                #         save_file(file_name, [titles, links, categories, dates, bodies])
                #         cond_loop = False

                # except:
                #     pass
            if time_limit :
                    
                    if datetime.datetime.strptime(date, "%Y.%m.%d %H:%M") < datetime.datetime.strptime(time_limit, "%Y-%m-%d"):
                    
                        print("TIME LIMIT ! :: NO MORE CRAWLING AND SAVED DATA")
                        cond_loop = False


            print('{} page is done'.format(i+1))

            i += 1
            
        except:
            print("**"*30)
            print("wait.....")
            print("**"*30)
            time.sleep(5)
            save_file(file_name, [titles, links, categories, dates, bodies])
            continue
    print("NOBODY : {}".format(nobody))
    save_file(file_name, [titles, links, categories, dates, bodies])

    return None



args = argparse.ArgumentParser()

args.add_argument('--query', type=str, default="")
args.add_argument('--file_name', type=str, default="./hankyerae.bin")
args.add_argument('--time_limit', type=str, default=None)

config = args.parse_args()

if config.query:
    hankyerae_crawler(config.query, config.file_name, config.time_limit)
else : 
    print("YOU should type query word at least 1.")