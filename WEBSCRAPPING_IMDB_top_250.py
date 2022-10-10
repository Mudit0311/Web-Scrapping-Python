#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import re

pd.set_option("display.max_rows",None)
pd.set_option("display.max_columns",None)
pd.set_option('display.max_colwidth',None)

import requests
from bs4 import BeautifulSoup

import json

from tqdm import tqdm
import re
from tabulate import tabulate


# In[2]:


def extract_data():
    
    movie_name=[]
    movie_year=[]
    movie_rating=[]
    movie_cast=[]
    movie_director=[]
    movie_users=[]
    
    movie_genre=[]
    movie_production=[]
    movie_release_month=[]
    
    movie_budget=[]
    movie_collection_US_Canada=[]
    movie_weekend_collection= []
    movie_collection_worldwide=[]
    
    
    movie_duration=[]
    
    movie_meta_score=[]
    
    movie_origin=[]

    def total_users(users):
        users= users.replace(',','')
        pattern= re.compile(r' \d+')
        matches= pattern.finditer(users)

        for match in matches:
            return(match.group().strip())
        
        
    
    def only_currency(str):
        return round((float((re.findall(r'[\d,]+', str))[0].replace(',',''))),2)
    
    
    url= 'https://www.imdb.com/chart/top/'
    page = requests.get(url)

    soup = BeautifulSoup(page.text, 'html.parser')

    movies = soup.find('tbody', class_= 'lister-list' )
    all_tr_movies = movies.find_all('tr')

    
    for x in tqdm(all_tr_movies):
        y = x.find_all('td')
        y=y[1:3]
        name = y[0].find('a').text
        cast= y[0].find('a')['title']
        year = y[0].find('span').text
        rating = y[1].find('strong').text
        users= y[1].find('strong')['title']
        
        
    
        movie_name.append(name)
        
        movie_cast.append(cast.split(',',1)[1].strip())
        movie_director.append(cast.split(',',1)[0].replace('(dir.)','').strip())
        
        movie_year.append(int((year).replace('(','').replace(')','')))
        movie_users.append(int(total_users(users)))
        movie_rating.append(float(rating))
        
        
        
        movie_info = x.find('td', class_ = 'titleColumn').find('a')['href']
        movie_info = 'https://www.imdb.com/'+ str(movie_info)
    
        page = requests.get(movie_info)
        soup = BeautifulSoup(page.text, 'html.parser')
        
        soup_2= soup.find('script', type= 'application/json')
        json_data = json.loads(soup_2.contents[0])
        
        movie_release_month.append((json_data['props']['pageProps']['aboveTheFoldData']['releaseDate']['month']))
        
        movie_genre.append((json_data['props']['pageProps']['aboveTheFoldData']['genres']['genres'][0]['text']))
        
        movie_production.append((json_data['props']['pageProps']['aboveTheFoldData']['production']['edges'][0]['node']['company']['companyText']['text']))

        soup_3 = soup.find_all('div', class_ = 'sc-f65f65be-0 ktSkVi')
       
        for p in soup_3:
            if 'title-boxoffice-section' in str(p):
                soup_3= p  
            
                
        try:
            soup_4 = soup_3.find_all('span', class_ = 'ipc-metadata-list-item__label') #detail 
            
        
            a=[]
            for q in soup_4:
                a.append(q.text)
        
        
            soup_3= soup_3.find_all('span', class_ = 'ipc-metadata-list-item__list-content-item')
       
            if 'Budget' in a:
                   movie_budget.append(only_currency(soup_3[0].text))
                   movie_origin.append(soup_3[0].text)
                   
            else:
                movie_budget.append(None)
                soup_3.insert(0,None)
                movie_origin.append(None)
                
            
            if 'Gross US & Canada' in a:
                movie_collection_US_Canada.append(only_currency(soup_3[1].text))
            else:
                movie_collection_US_Canada.append(None)
                soup_3.insert(1,None)
            
            if 'Opening weekend US & Canada' in a:
                movie_weekend_collection.append(only_currency(soup_3[2].text))
            else:
                movie_weekend_collection.append(None)
                soup_3.insert(2,None)
                soup_3.insert(3,None)
            
            if 'Gross worldwide' in a:
                movie_collection_worldwide.append(only_currency(soup_3[4].text))
            else:
                movie_collection_worldwide.append(None)
                soup_3.insert(4,None)
            
            
        except Exception as e:
            movie_budget.append(None)
            movie_collection_US_Canada.append(None)
            movie_weekend_collection.append(None)
            movie_collection_worldwide.append(None)
            movie_origin.append(None)


            print(e)
            
            
        soup_5 = soup.find_all('ul', class_ = 'ipc-inline-list ipc-inline-list--show-dividers sc-8c396aa2-0 kqWovI baseAlt')
       
        for g in soup_5:
            if 'hero-title-block__metadata' in str(g):
                soup_5= g
        soup_5= (soup_5).find_all('li', class_= 'ipc-inline-list__item')  
        
        s=(soup_5[-1]).text
        time = re.findall('\d+', s)
        if len(time)==1:
            duration = int(time[0])*60
        else:
            duration= int(time[0])*60 + int(time[1])
        
        movie_duration.append(duration)
        
        meta_score_tag = soup.find('span' , class_ = 'score-meta')
        if meta_score_tag !=None:
            meta_score = meta_score_tag.text
            movie_meta_score.append(int(meta_score))
        else:
            movie_meta_score.append(None)
        
        
        
        
        
    return(pd.DataFrame(list(zip(movie_name, movie_year, movie_release_month, movie_duration, movie_cast, movie_director, movie_users, 
                        movie_production, movie_genre, movie_budget,  movie_collection_US_Canada, movie_weekend_collection,
                        movie_collection_worldwide, movie_meta_score,movie_origin,movie_rating )),
               columns =['Name', 'Year', 'Month', 'duration','Cast','Director', 'Users', 'Production', 'Genre' ,'Budget','US_Canada_Collection', 
                         'Weekend_Collection', 'Worlwide_Collection', 'Meta_Score','Origin_Currency_Symbol','Rating']) )
      
    
    

# soup is page we get after we click on any movie present on the page - top 250


# In[3]:


choice = input('Enter "YES" to extract the imdb data for top 250 movies')
if choice == 'YES':
    df = extract_data()
    print(tabulate(df, headers = 'keys', tablefmt = 'psql'))


# In[47]:


#df.to_excel (r'C:\Users\Dell\Desktop\250_IMDB_final.xlsx', index = False, header=True)


# In[4]:


#display(df)


# In[ ]:




