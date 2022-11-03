import requests
from bs4 import BeautifulSoup
import pandas as pd
import urllib

def make_indeed_url(search_job, search_location, job_age):
    '''
    This function takes in 3 search parameters and inserts them into an
    indeed.com url to search for jobs in those parameters
    input:
        search_job (str): job title being searched for
        search_location (str): city, state being searched
        job_age (int): 3 or 7, max age of job posting in days
    output:
        indeed_job_url (str): url to indeed jobs of the given parameters
    '''
    getVars = {'q' : search_job, 'l' : search_location, 'fromage' : job_age, 'sort' : 'date'}
    indeed_job_url = ('https://www.indeed.co.uk/jobs?' + urllib.parse.urlencode(getVars))

    #job = search_job.replace(' ', '%20')
    #location = search_location.replace(',', '%2C').replace(' ', '%20')
    #indeed_job_url = f'https://www.indeed.com/jobs?q={job}&l={location}&fromage={job_age}'
    return indeed_job_url

def scrape_job_card(job_meta):
    '''
    This function takes in a job_card_element from indeed.com and extracts the
    job title, company name, company location, and estimated salary
    input: 
        job_card_element, selenium webdriver object (specific to indeed.com)
    output: 
        - job_title, str
        - company_name, str
        - company_location, str
        - estimated_salary, str
    '''
    try:
        job_title = job_meta.find('h2', {'class':'jobTitle'}).get_text().lstrip('new\n')
    except:
        job_title = 'No job title found'
    try:
        company_name = job_meta.find('span',{'class':'companyName'}).get_text()
    except:
        company_name = 'No Company Name'
    try:
        company_location = job_meta.find('div', {'class':'companyLocation'}).get_text()
    except:
        company_location = 'No Location'
    try:
        estimated_salary = job_meta.find('div', {'class':'metadata salary-snippet-container'}).get_text()
    except:
        estimated_salary = 'No Estimated Salary'
    return job_title, company_name, company_location, estimated_salary

def scrape_job_description(job_desc_href):
    '''
    This function takes in a job_card_element from indeed.com and extracts the
    job description.
    input: 
        job_card_element: selenium webdriver object (specific to indeed.com)
    output: 
        job_desc, str, can be extremely long (avg 3,000-7,000 characters)
    '''
    try:
        page = web_scrape_api_call(job_desc_href)
        soup = BeautifulSoup(page.content, 'html.parser')
        job_desc = soup.find(id='jobDescriptionText')
        job_desc = job_desc.text.replace('\n', ' ').replace('\r', '')
    except:
        job_desc = 'No Job Description'
    return job_desc

def scrape_job_page_meta(url, job_page_html):
    '''
    This function takes in a html job page and uses beautiful soup to extract each jobs title, company name,
    estimated salary, job description href and then uses that href to open the job description page and
    extract that job description. While its looping through each job on the job page it is storing the 
    information in a pandas dataframe.
    input:
        job_page_html: html response from indeed search request
    output:
        jobs_df: pandas dataframe containing the scraped data from the job search page
    ''' 
    page = requests.get(url)
    page_soup = BeautifulSoup(page.content, "html.parser")
    df_columns = ['job_title', 'company_name', 'company_location', 'est_salary', 'job_href','job_desc']
    jobs_df = pd.DataFrame(columns = df_columns)
    for job in page_soup.find_all('div',{"id":"mosaic-provider-jobcards"}): 
        page_soup.find_all('div',{"id":"mosaic-provider-jobcards"})
        # Lets find the job title
        for href_post in job.find_all('a', href=True):
            if href_post.find('a', href=True):
                #this is for the url for the job posting
                job_desc_href = 'https://www.indeed.com'+str(href_post['href'])
                job_desc = scrape_job_description(job_desc_href)
                for job_meta in href_post.find_all('div',{"class":"job_seen_beacon"}):
                    job_title, company_name, company_location, estimated_salary = scrape_job_card(job_meta)

                    print(f'{job_title}, {job_desc_href}')        
                    input()
                    job_dict = {'job_title': job_title,
                                'company_name': [company_name],
                                'company_location': [company_location],
                                'est_salary': [estimated_salary],
                                'job_href': [job_desc_href],
                                'job_desc': [job_desc]}
                    j_df = pd.DataFrame.from_dict(job_dict)
                    jobs_df= jobs_df.append(j_df, ignore_index=True)
    return jobs_df



def job_loc_scrape(job,loc,job_age):
    indeed_url = make_indeed_url(job, loc, job_age)
    #indeed_response = web_scrape_api_call(indeed_url)
    #print("indeed_response")
    #print(indeed_response)
    #input()
    result_df = scrape_job_page_meta(indeed_url, indeed_url)

    return result_df



def web_scrape_api_call(url_to_scrape):
    '''
    sends the url that we would like to scrape to the webscrapingapi
    so that our calls can be ananomyzed. 
    '''
    url = "https://api.webscrapingapi.com/v1"
    params = {
    "api_key":"gWjtvXI83XJ2lS9x8xL1g2w2qyq8fbmm",
    "url":url_to_scrape
    }
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36', "Referrer Policy" : "strict-origin-when-cross-origin"}
    response = requests.request("GET", url, params=params)
    return response

    