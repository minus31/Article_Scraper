# -*- coding: utf-8 -*- 
import requests
from bs4 import BeautifulSoup
import pandas as pd
import pickle 
import time


def body_extractor(link):
    soup = BeautifulSoup(requests.get(link).content, 'html.parser')
    
    text = ""    
    for con in soup.select_one(".article_txt").contents:
        try:
            con.text
            continue
        except :
            if con == r"\ufeff【서울=뉴시스】":
                continue
            text += " " + con
    return text.strip()

def save_file(filename, result):

    df = pd.DataFrame()

    df["title"] = result[0]
    df["link"] = result[1]
    df["category"] = result[2]
    df["date"] = result[3]
    df["body"] = result[4]
    
    with open(filename, "wb") as f:
        pickle.dump(df, f)
    

def doonga_crawler(query, period=None):
    
    file_name = "./DoongA/0.bin"
    
    # data containers 
    titles = []
    links = []
    categories = []
    dates = []
    bodies = []
    
    i = 1 
    nobody = 0
    
    cond_loop = True
    
    while cond_loop:
        try:
            print("-" * 30)
            print('{} page is start'.format(i//15 + 1))

            url = "http://news.donga.com/search?p={}&query={}&check_news=1&more=1&sorting=1&search_date=1&v1=&v2=&range=1".format(i, query)
            res = requests.get(url)
            soup = BeautifulSoup(res.content, 'html.parser')

            if len(soup.select('p.tit')) == 0:
                print('***** no result! *****')
                break

            for art, cate, da in zip(soup.select("p.tit > a"), soup.select(".loc"), soup.select("p.tit > span")):

                title = art.text
                if len(title) == 0:
                    nobody += 1
                    continue

                link = art["href"]
                if len(link) == 0:
                    nobody += 1
                    continue

                category = cate.text
                if len(category) == 0:
                    category = 'unknown_category'

                date = da.text
                if len(date) == 0:
                    date = "unknown_date"

                try:
                    body = body_extractor(link)
                    if len(body) == 0:
                        print("no body")
                        nobody += 1
                        continue

                except Exception as ex:
                    print(ex)
                    nobody += 1
                    continue

                titles.append(title)
                links.append(link)
                categories.append(category) 
                dates.append(date)
                bodies.append(body)
                
                try : 
                    if int(date[:4]) < 2010:
                        print("No need to 2010")
                        save_file(file_name, [titles, links, categories, dates, bodies])
                        cond_loop = False
                except :
                    pass

            print('{} page is done'.format(i//15 + 1))
                          
            if ((i//15) / 1000) == 0:

                #save file
                save_file(file_name, [titles, links, categories, dates, bodies])

                # reset collections
                file_name = "./DoongA/{}.bin".format(str(i//15))
                titles = []
                links = []
                categories = []
                dates = []
                bodies = []
                
            i += 15
        
        except:
            print("**"*30)
            print("wait.....")
            print("**"*30)
            time.sleep(5)
            continue
            
#     return [titles, links, categories, dates, bodies], nobody
    return None


doonga_crawler('전기요금')

