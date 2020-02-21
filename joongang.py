# -*- coding: utf-8 -*- 
import requests
from bs4 import BeautifulSoup
import pandas as pd
import pickle 
import time
import argparse
import datetime


def body_extractor(link):
    soup = BeautifulSoup(requests.get(link).content, 'html.parser')
    
    category = soup.select_one("meta[property='article:section']")["content"]

    return category, soup.select("#article_body")[0].text.strip().replace("\xa0", "").replace("▲", "").replace("▲", "")

def save_file(filename, result):

    df = pd.DataFrame()

    df["title"] = result[0]
    df["link"] = result[1]
    df["category"] = result[2]
    df["date"] = result[3]
    df["body"] = result[4]
    
    with open(filename, "wb") as f:
        pickle.dump(df, f)
    

def joongang_crawler(query, file_name="./joongang.bin", time_limit=None):
    
    # data containers 
    titles = []
    links = []
    categories = []
    dates = []
    bodies = []
    
    i = 1 
    nobody = 0

    count = 0 # to check how many time to wait

    cond_loop = True
    
    while cond_loop:
        try:
            print("-" * 30)
            print('{} page is start'.format(i))

            url = "https://search.joins.com/TotalNews?page={}&Keyword={}&SortType=New&SearchCategoryType=TotalNews".format(i, query)
            res = requests.get(url)
            soup = BeautifulSoup(res.content, 'html.parser')

            if len(soup.select(".guide")) != 0:
                print('***** no result! *****')
                break

            for art, da in zip(soup.select(".headline > a"), soup.select(".byline > em:nth-child(2)")):

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

            if time_limit :
                    
                    if datetime.datetime.strptime(date, "%Y.%m.%d %H:%M") < datetime.datetime.strptime(time_limit, "%Y-%m-%d"):
                        print("TIME LIMIT ! :: NO MORE CRAWLING AND SAVED DATA")
                        cond_loop = False

            print('{} page is done'.format(i))
            i += 1
        except Exception as ex:
            print(ex)
            print("**"*30)
            print("wait.....")
            print("**"*30)
            time.sleep(5)
            save_file(file_name, [titles, links, categories, dates, bodies])
            count += 1

            if count > 5:
                break
            continue


    save_file(file_name, [titles, links, categories, dates, bodies])
    return None # [titles, links, categories, dates, bodies], nobody

args = argparse.ArgumentParser()

args.add_argument('--query', type=str, default="")
args.add_argument('--file_name', type=str, default="./joongang.bin")
args.add_argument('--time_limit', type=str, default=None)

config = args.parse_args()

if config.query:
    joongang_crawler(config.query, config.file_name, config.time_limit)
else : 
    print("YOU should type query word at least 1.")




