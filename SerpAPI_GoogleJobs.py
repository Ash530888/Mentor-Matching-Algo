import pandas as pd
from serpapi import GoogleSearch
import sqlite3
import datetime as dt

import config

def google_job_search(job_title, city_state, post_age="week"):
    '''
    job_title(str): "Data Scientist", "Data Analyst"
    city_state(str): "Denver, CO"
    post_age,(str)(optional): "3day", "week", "month"
    '''
    params = {
            "engine": "google_jobs",
            "q": f"{job_title} {city_state}",
            "hl": "en",
            "api_key": "61a7d0c61c97f648bebcce95fff0bd3a97bf15bd573c2964800519092db57d86",
            "chips":f"date_posted:{post_age}", 
            }
    search = GoogleSearch(params)
    results = search.get_dict()
    jobs_results = results['jobs_results']
    job_columns = ['title', 'company_name']
    df = pd.DataFrame(jobs_results, columns=job_columns)
    return df

def sql_dump(df, db, table):
    con = sqlite3.connect(db) #db="data\jobs.db"
    df.to_sql(table, con, if_exists='append') #table='jobs_data'
    con.close()

