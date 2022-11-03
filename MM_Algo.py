from operator import truediv
import sys
import argparse
import pandas as pd
import math
from Levenshtein import distance
from job_scraper import find_jobs_from
import nltk
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from SerpAPI_GoogleJobs import google_job_search
from BS4_Indeed_functional import job_loc_scrape

#from sklearn.feature_extraction.text import CountVectorizer
#from sklearn.metrics.pairwise import cosine_similarity


from csv import reader


def levenshtein_distance_percentage(s1: str, s2: str) -> float:
    #Computes the Levenshtein dis
    assert min(len(s1), len(s2)) > 0, "One of the given string is empty"
    return 1. - distance(s1, s2) / min(len(s1), len(s2))

def compute_jaccard_similarity_score(x, y):
    """
    Jaccard Similarity J (A,B) = | Intersection (A,B) | /
                                    | Union (A,B) |
    """
    intersection_cardinality = len(set(x).intersection(set(y)))
    union_cardinality = len(set(x).union(set(y)))

    return intersection_cardinality / float(union_cardinality)


def main(argv):
    parser = argparse.ArgumentParser()
    #parser.add_argument("--data_filepath", help="Data file path",
    #                    default="Matching_Template.xlsx") 
    #parser.add_argument("--mentee_sheet", help="Mentee sheet's name in excel spreadsheet",
    #                    default="Mentee_data")
    #parser.add_argument("--mentor_sheet", help="Mentor sheet's name in excel spreadsheet",
    #                   default="Mentor_data")

    parser.add_argument("--mentee_data_filepath", help="Mentee Data file path",
                        default="Mentee_Data.xlsx")
    parser.add_argument("--mentor_data_filepath", help="Mentor Data file path",
                        default="Mentor_Data.xlsx")


    args = parser.parse_args()
    #filepath = args.data_filepath
    #mentee = args.mentee_sheet
    #mentor = args.mentor_sheet

    menteeFile = args.mentee_data_filepath
    mentorFile = args.mentor_data_filepath


    # Read excel sheets with 
    columns = [3, 4, 6, 8, 10, 11, 17, 18, 29, 30, 32, 33, 34, 39, 40, 41]
    colNames = ["fname", "lname", "ID", "course", "dept", "faculty", "nationality", "gender", "bursary", "matchPref", "industry/job", "otherGender", "entrepreneurStage", "support", "mentorGender", "whichMentor"]
    #menteeData = pd.read_excel(filepath, sheet_name = mentee, header = None, names = columns)
    menteeData = pd.read_excel(menteeFile, header = None, usecols = columns, names = colNames)
    menteeData.drop(index=menteeData.index[0], axis=0, inplace=True)

    columns = [0, 4, 5, 7, 11, 12, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24]
    colNames = ["name", "gender", "otherGender", "qualifications", "ethnicitiy", "otherEthnic", "menteeGender", "otherMenteeGender", "QMULschool", "matchPref", "job", "company", "industry", "support", "otherSupport", "extraInfo"]
    #mentorData = pd.read_excel(filepath, sheet_name = mentor, header = None, names = columns)
    mentorData = pd.read_excel(mentorFile, header = None, usecols = columns, names = colNames)
    mentorData.drop(index=mentorData.index[0], axis=0, inplace=True)

    columns = []

    outputDF = {}

    #print("0% Complete", end = "\r")

    done = 0
    tot = len(mentorData) * len(menteeData)

    menteeJobsDict = {}

    for j in range(len(menteeData)):
        if not isinstance(menteeData["industry/job"].iloc[j], float):
            if "," in menteeData["industry/job"].iloc[j]: menteeJob = (menteeData["industry/job"].iloc[j]).split(",")
            elif "or" in menteeData["industry/job"].iloc[j]: menteeJob = (menteeData["industry/job"].iloc[j]).split("or")
            elif "and" in menteeData["industry/job"].iloc[j]: menteeJob = (menteeData["industry/job"].iloc[j]).split("and")
            elif "/" in menteeData["industry/job"].iloc[j]: menteeJob = (menteeData["industry/job"].iloc[j]).split("/")
            else: menteeJob = menteeData["industry/job"].iloc[j]

            menteeJobsDict[j] = []

            #print("mentee: ", menteeJob)

            if isinstance(menteeJob, str): 
                if len(menteeJob) != 0:
                    with open('2019_free_title_data.csv', 'r') as read_obj:
                        csv_reader = reader(read_obj)
                        next(csv_reader)
                        for row in csv_reader:
                            row = [r.strip() for r in row]
                            #print(row)
                            #input()
                            for job in row:
                                if len(job) > 2:
                                    if menteeJob.lower() in job or job in menteeJob.lower():
                                        #menteeJobsDict[j].append(job)
                                        menteeJobsDict[j].append(row)
                                        break
            else:
                menteeJob = [x.lower() for x in menteeJob if len(x) > 0]
                for x in menteeJob:
                    with open('2019_free_title_data.csv', 'r') as read_obj:
                        csv_reader = reader(read_obj)
                        next(csv_reader)
                        for row in csv_reader:
                            row = [r.strip() for r in row]
                            #print(row)
                            #input()
                            for job in row:
                                if len(job) > 2:
                                    if x in job or job in x: 
                                        #print("csv: ",job)
                                        #input()
                                        #menteeJobsDict[j].append(job)
                                        menteeJobsDict[j].append(row)
                                        break
                                    

                    #if len(menteeJobsDict[j]) == 0:
                    #    with open('2019_free_title_data.csv', 'r') as read_obj:
                     #       csv_reader = reader(read_obj)
                     #       next(csv_reader)
                     #       for row in csv_reader:
                      #          row = [r.strip() for r in row]
                     #           for job in row:
                      #              if levenshtein_distance_percentage(x, job) > 0.7:
                      #                  menteeJobsDict[j] = row
                      #                  break
                      #          break

    mentorJobsDict = {}
    mentorIndsDict = {}

    # iterate through mentors
    for i in range(len(mentorData)):
        done+=1

        mentorName = mentorData["name"].iloc[i]
        columns.append(mentorName)
        columns.append("Matching Attributes")

        mentorSupport = mentorData["support"].iloc[i].split(",")

        ranking = []

        if not isinstance(mentorData["job"].iloc[i], float):
            if "," in mentorData["job"].iloc[i]: mentorJob = (mentorData["job"].iloc[i]).split(",")
            elif "or" in mentorData["job"].iloc[i]: mentorJob = (mentorData["job"].iloc[i]).split("or")
            elif "and" in mentorData["job"].iloc[i]: mentorJob = (mentorData["job"].iloc[i]).split("and")
            elif "/" in mentorData["job"].iloc[i]: mentorJob = (mentorData["job"].iloc[i]).split("/")
            else: mentorJob = mentorData["job"].iloc[i]

            mentorIndustry = mentorData["industry"].iloc[i]

            mentorJobsDict[i] = []
            mentorIndsDict[i] = []

            #print("mentee: ", menteeJob)

            

            if isinstance(mentorJob, str): 
                if len(mentorJob) != 0:
                    with open('2019_free_title_data.csv', 'r') as read_obj:
                        csv_reader = reader(read_obj)
                        next(csv_reader)
                        for row in csv_reader:
                            found = False
                            row = [r.strip() for r in row]
                            #print(row)
                            #input()
                            for job in row:
                                if len(job) > 2:
                                    if mentorJob.lower() in job or job in mentorJob.lower():
                                        mentorJobsDict[i].append(job)
                                        found = True
                                        #mentorJobsDict[i].append(row)
                                    if mentorIndustry.lower() in job or job in mentorIndustry.lower():
                                        found = True
                                        mentorIndsDict[i].append(job)
                                        #mentorIndsDict[i].append(row)
                                        
                                    #if found: break
            else:
                mentorJob = [x.lower() for x in mentorJob if len(x) > 0]
                for x in mentorJob:
                    with open('2019_free_title_data.csv', 'r') as read_obj:
                        csv_reader = reader(read_obj)
                        next(csv_reader)
                        for row in csv_reader:
                            found = False
                            row = [r.strip() for r in row]
                            #print(row)
                            #input()
                            for job in row:
                                if len(job) > 2:
                                    if x in job or job in x: 
                                        #print("csv: ",job)
                                        #input()
                                        mentorJobsDict[i].append(job)
                                        #mentorJobsDict[i].append(row)
                                        found = True
                                    if mentorIndustry in job or job in mentorIndustry: 
                                        #print("csv: ",job)
                                        #input()
                                        mentorIndsDict[i].append(job)
                                        #mentorIndssDict[i].append(row)
                                        found = True
                                #if found: break
                                
        # iterate through mentees
        for j in range(len(menteeData)):
            done+=1
            #menteeSupport = (menteeData["support"].iloc[j]).split(",")
            score = 0
            attributes = ""

            # check which type of mentor preference
            # if mentee wants to be matched based on qualifications
            if menteeData["whichMentor"].iloc[j] == "Option 1 - A mentor who studied the same degree as me, but works in any industry/job role":
                
                # check degree similarity between mentor and mentee

                # mentor has list of qualifications which each need to be processed individually
                # so split into list
                menteeQualifaction = (menteeData["course"].iloc[j]).split(" ")
                menteeQualifaction = menteeQualifaction[2:]
                
                mentorQualifications = (mentorData["qualifications"].iloc[i]).split(", ")
                
                # remove numbers i.e. dates
                mentorQualifications = [i for i in mentorQualifications if not i.isnumeric()]


                stopwords = ["with", "a", "an", "and", "placement", "industrial", "experience", "professional", "year", "in"]


                found = False
                if isinstance(mentorQualifications, str):
                    if isinstance(menteeQualifaction, str):
                        if mentorQualifications.lower() in menteeQualifaction.lower() or menteeQualifaction.lower() in mentorQualifications.lower():
                            score+=1
                            

                            attributes += "Qualifications  (Mentee: "+menteeData["course"].iloc[j]+"), (Mentor: "+mentorQualifications+"); "
                            found = True
                            break

                        s = levenshtein_distance_percentage(menteeQualifaction, mentorQualifications)
                        if s>=0.55: 
                            score+=1
                            attributes += "Qualifications  (Mentee: "+menteeData["course"].iloc[j]+"), (Mentor: "+mentorQualifications+"); "
                            found = True
                            break
                    else:
                        for menteeq in menteeQualifaction:
                            if menteeq.lower() in stopwords: continue
                            if mentorQualifications.lower() in menteeq.lower() or menteeq.lower() in mentorQualifications.lower():
                                
                                score+=1
                                attributes += "Qualifications  (Mentee: "+menteeData["course"].iloc[j]+"), (Mentor: "+mentorQualifications+"); "
                                found = True
                                break

                            s = levenshtein_distance_percentage(menteeq, mentorQualifications)
                            if s>=0.55: 
                                score+=1
                                attributes += "Qualifications  (Mentee: "+menteeData["course"].iloc[j]+"), (Mentor: "+mentorQualifications+"); "
                                found = True
                                break
                else:
                    for q in mentorQualifications:
                        if q.lower() in stopwords: continue
                        if isinstance(menteeQualifaction, str):
                            if q.lower() in menteeQualifaction.lower() or menteeQualifaction.lower() in q.lower():
                                
                                score+=1
                                attributes += "Qualifications  (Mentee: "+menteeData["course"].iloc[j]+"), (Mentor: "+q+"); "
                                found = True
                                break

                            s = levenshtein_distance_percentage(menteeQualifaction, q)
                            if s>=0.55: 
                                score+=1
                                attributes += "Qualifications  (Mentee: "+menteeData["course"].iloc[j]+"), (Mentor: "+q+"); "
                                found = True
                                break
                        else:
                            for menteeq in menteeQualifaction:
                                if menteeq.lower() in stopwords: continue
                                if q.lower() in menteeq.lower() or menteeq.lower() in q.lower():
                                    
                                    score+=1
                                    attributes += "Qualifications  (Mentee: "+menteeData["course"].iloc[j]+"), (Mentor: "+q+"); "
                                    found = True
                                    break

                                s = levenshtein_distance_percentage(menteeq, q)
                                if s>=0.55: 
                                    score+=1
                                    attributes += "Qualifications  (Mentee: "+menteeData["course"].iloc[j]+"), (Mentor: "+q+"); "
                                    found = True
                                    break
                        if found: break

                if not found:
                    attributes+="Qualifications didn't match (Mentee: "+menteeData["course"].iloc[j]+"), (Mentor: "+q+"); "


            # if mentee wants to be matched based on industry/job
            if menteeData["whichMentor"].iloc[j] == "Option 2 - A mentor who works in the industry/job role that I am interested in":
                if not isinstance(menteeData["industry/job"].iloc[j], float):
                    #print("Industry...")
                    #print("mentee ", menteeData["industry/job"].iloc[j])
                    
                    mentorJob = (mentorData["job"].iloc[i]).lower()
                    mentorIndustry = (mentorData["industry"].iloc[i]).lower()
                    mentorCompany = mentorData["company"].iloc[i]

                    found = False
                    #for row in menteeJobsDict[j]:
                        #input()
                        #if (mentorJob in job or job in mentorJob) or (mentorIndustry in job or job in mentorIndustry):
                            #if x.lower() in job or job in x.lower(): 

                    teachingJobs = ["teacher", "instructor","assistant professor", "lecturer", "principle", "teaching assistant"]

                    for row in menteeJobsDict[j]:
                        #print(row)
                        for job in row:
                            if len(job) > 2:
                                #print("not a match ", job)
                                if (("teach" in job and row[0] in teachingJobs) or "teach" not in job) and (mentorJob in job or job in mentorJob or mentorIndustry in job or job in mentorIndustry):
                                #if mentorJob in job or job in mentorJob or mentorIndustry in job or job in mentorIndustry:
                                    #print("mentee ", menteeData["industry/job"].iloc[j])
                                   #print("from csv: ",job)
                                    #print("mentor: ",mentorJob)
                                   # print(mentorIndustry)
                                    #input()
                                    score+=2
                                    found = True
                                    attributes+= "Job/Industry Mentee("+menteeData["industry/job"].iloc[j]+"), Mentor("+mentorJob+"/"+mentorIndustry+"); "
                                    break
                        if found: break
                    
                    if not found:
                        attributes+= "Job/Industry didn't match Mentee("+menteeData["industry/job"].iloc[j]+"), Mentor("+mentorJob+"/"+mentorIndustry+"); "
                        #print(menteeJobsDict[j])
                        #print("mentee ", menteeData["industry/job"].iloc[j])
                        #print("mentor: ",mentorJob)
                        #print(mentorIndustry)
                        #input("NOT FOUND!!")

                    #if (set(menteeJobsDict[j]) & set(mentorJobsDict[i])) or (set(menteeJobsDict[j]) & set(mentorIndsDict[i])):
                     #   score+=2
                    #    attributes+= "Job/Industry Mentee("+menteeData["industry/job"].iloc[j]+"), Mentor("+mentorJob+"/"+mentorIndustry+"); "
                        #print("mentor", mentorJob)
                        #print("mentor", mentorIndustry)
                        #print(set(menteeJobsDict[j]) & set(mentorJobsDict[i]))
                        #print(set(menteeJobsDict[j]) & set(mentorIndsDict[i]))
                        #input()

                    #for job in menteeJobsDict[j]:
                    #    if len(job) > 2:
                    #        print("not a match ", job)
                    #        if (("teach" in job and row[0] in teachingJobs) or "teach" not in job) and (mentorJob in job or job in mentorJob or mentorIndustry in job or job in mentorIndustry):
                    #        #if mentorJob in job or job in mentorJob or mentorIndustry in job or job in mentorIndustry:
                    #            print("mentee ", menteeData["industry/job"].iloc[j])
                    #            print("from csv: ",job)
                    #            print("mentor: ",mentorJob)
                    #            print(mentorIndustry)
                    #            input()
                    #            score+=2
                    #            found = True
                    #            attributes+= "Job/Industry Mentee("+menteeData["industry/job"].iloc[j]+"), Mentor("+mentorJob+"/"+mentorIndustry+"); "
                    #            break

                    

                        #if row in  mentorJobsDict[i]:
                         #   score+=2
                         ##   attributes+= "Job/Industry Mentee("+menteeData["industry/job"].iloc[j]+"), Mentor("+mentorJob+"/"+mentorIndustry+"); "
                        #    break

                        #if (levenshtein_distance_percentage(mentorJob, job) > 0.7) or (levenshtein_distance_percentage(mentorIndustry, job) > 0.7):
                        #    score+=1
                        #    print("match found j/i")
                        #    input()
                        #    attributes+= "Job/Industry Mentee("+menteeData["industry/job"].iloc[j]+"), Mentor("+mentorJob+"/"+mentorIndustry+"); "


                    

                            

                    #for x in menteeJob:

                        #jobs = google_job_search(x, "uk", "month")
                        #jobs = find_jobs_from("Indeed", x, "uk")
                        #jobs = find_jobs_from("CWjobs", x, "uk")

                        #titles = jobs["job_title"]
                        #companies = jobs["company_name"]

                        #titles = [t.upper() for t in titles if t not in titles]
                        #companies = [c.upper() for c in companies if c not in companies]
                        
                        #if mentorJob.upper() in titles or mentorIndustry.upper() in titles:
                        #    if mentorCompany in companies: 
                        #        score+=0.5
                        #        attributes+= "Relevant Company; "
                        #    score+=1
                        #    attributes+= "Job/Industry; "
                        #    found = True
                        #    break

                        #if found: break



                #industry = levenshtein_distance_percentage(menteeData["industry/job"].iloc[j], mentorData["industry"].iloc[i])
                #job = levenshtein_distance_percentage(menteeData["industry/job"].iloc[j], mentorData["job"].iloc[i])

                #if industry>=0.55: 
                #    score+=1
                #    attributes += "Industry; "
                #if job>=0.55: 
                #    score+=1
                #    attributes += "Job; "

            # if mentee interested in entrepreneurship
            if menteeData["whichMentor"].iloc[j] == "Option 3 - A mentor who can support with entrepreneurship":
                if not isinstance(mentorSupport, float):
                    if "Developing entrepreneurial skills" in mentorSupport:
                        score += 1
                        attributes += "Developing Entrepreneurial Skills; "

                    if "Support with setting up or growing a business" in mentorSupport:
                        score += 1
                        attributes += "Starting/Growing Business; "
                
                # list of keywords
                # some spelt incorrectly to capture more variations of the word
                keywords = {"sale" : "sale; ", "market" : "market; ", "business" : "business; ", "financ" : "finance; ", "manag" : "management; ", "ceo" : "CEO; ", "cfo" : "CFO; ", "entrepreneur" : "entrepreneur; ", "sell" : "sell; ", "produc" : "production; ", "build" : "build; ", "organise" : "organise; ", "present" : "present; ", "start-up" : "start-up; ", "start up" : "start-up; ", "venture" : "venture; ", "profit" : "profit;", "invest" : "invest; ", "incubat" : "incubate; ", "network" : "network; ", "patent" : "patent; ", "trademark" : "trademark; ", "launch" : "launch; ", "pitch" : "pitch; ", "associate" : "associate; ", "partner" : "partner; ", "capital" : "capital; ", "acqui" : "acquisition; ", "advertis" : "advertisement; "}

                mentorJob = (mentorData["job"].iloc[i]).lower()
                mentorIndustry = (mentorData["industry"].iloc[i]).lower()
                extra = (mentorData["extraInfo"].iloc[i]).lower()

                for kw in keywords:
                    if kw in mentorJob or kw in mentorIndustry or kw in extra:
                        score+=0.5
                        attributes+=keywords[kw]



                # entrpreuenal stage and support 

                #if "Developing entrepreneurial skills" in menteeSupport and "Developing entrepreneurial skills" in mentorSupport:
                #    score+=1
                #    attributes += "Developing Entrepreneurial Skills; "

                #if "Support with setting up or growing a business" in menteeSupport and "Support with setting up or growing a business" in mentorSupport:
                #    score+=1
                #    attributes += "Starting/Growing Business; "
                
                #if (menteeData["entrepreneurStage"].iloc[j])[6] == "1":
                #    score+=1
                #    attributes+="Exploring Entrepreneurship; "

                #elif (menteeData["entrepreneurStage"].iloc[j])[6] == "2":
                #    score+=2
                #    attributes+="Aspiring Entrepreneur with Business Idea; "

                #elif (menteeData["entrepreneurStage"].iloc[j])[6] == "3":
                #    score+=3
                #    attributes+="Current Entrepreneur; "


            
            
            # compare mentee goals and mentor offerings
            #if "Planning for the future and goal setting" in menteeSupport and "Planning for the future and goal setting" in mentorSupport:
            #    score+=1
            #    attributes += "Planning/Setting Goals; "
            #if "Gaining insight to an industry/profession" in menteeSupport and "Gaining insight to an industry/profession" in mentorSupport:
            #    # need to only add to score if industry/profession same
            #    score+=1
            #    attributes += "Industry Insight; "
            #if "Building a professional network" in menteeSupport and "Building a professional network" in mentorSupport:
            #    score+=1
            #    attributes += "Networking; "
            #if "Writing/improving CVs, job applications and covering letters" in menteeSupport and "Writing/improving CVs, job applications and covering letters" in mentorSupport:
            #    score+=1
            #    attributes += "CVs/Applications; "
            #if "Interview practice and preparation" in menteeSupport and "Interview practice and preparation" in mentorSupport:
            #    score+=1
            #    attributes += "Interviews; "
            #if "Finding work experience (shadowing/internships/part-time work)" in menteeSupport and "Finding work experience (shadowing/internships/part-time work)" in mentorSupport:
            #    score+=1
            #    attributes += "Shadowing/Internships/Work; "


            # check mentor and mentee gender preferences
            if menteeData["mentorGender"].iloc[j] != "No preference" and  mentorData["menteeGender"].iloc[i] != "No preference":
                if menteeData["mentorGender"].iloc[j] == mentorData["gender"].iloc[i] and menteeData["gender"].iloc[j] == (mentorData["menteeGender"].iloc[i])[0].upper():
                    score+=0.25
                    attributes += "Both Mentee and Mentor Gender Pref. Met; "
                elif menteeData["mentorGender"].iloc[j] == mentorData["gender"].iloc[i]:
                    score+=0.15
                    attributes += "Only Mentee Gender Pref. Met; "
                elif menteeData["gender"].iloc[j] == (mentorData["menteeGender"].iloc[i])[0].upper():
                    score+=0.15
                    attributes += "Only Mentor Gender Pref. Met; "
            else:
                if mentorData["menteeGender"].iloc[i] == "No preference" and menteeData["mentorGender"].iloc[j] == mentorData["gender"].iloc[i]:
                    score+=0.25
                    attributes += "Mentee Gender Pref. Met; "
                elif menteeData["mentorGender"].iloc[j] == "No preference" and menteeData["gender"].iloc[j] == (mentorData["menteeGender"].iloc[i])[0].upper():
                    score+=0.25
                    attributes += "Mentor Gender Pref. Met; "


            # check QMUL School
            if mentorData["QMULschool"].iloc[i] != "No preference":
                mentorSchools = (mentorData["QMULschool"].iloc[i]).split(",")

                for s in mentorSchools:
                    if s in menteeData["dept"].iloc[j]: 
                        score+=1
                        attributes+="QMUL School; "

            # Compare Mentor's and Mentee's additional match preferences
            menteePref = menteeData["matchPref"].iloc[j]
            mentorPref = mentorData["matchPref"].iloc[i]

            if not isinstance(menteePref, float) and not isinstance(mentorPref, float):
                stopwords = ["WANT", "LIKE", "PREFER", "ENJOY", "HAVE", "USE", "MATCHED", "WORK", "SPEAK"]
                menteePref = word_tokenize(menteePref)
                menteePref = nltk.pos_tag(menteePref)
                
                #menteePref = [x[0].upper() for x in menteePref if "VB" in x[1] and x[0].upper() not in stopwords]
                menteePref = [x[0].upper() for x in menteePref if "JJ" in x[1] and x[0].upper() not in stopwords]

                #print(menteePref)
                #input()
                
                mentorPref = word_tokenize(mentorPref)
                mentorPref = nltk.pos_tag(mentorPref)
                #mentorPref = [x[0].upper() for x in mentorPref if "VB" in x[1] and x[0].upper() not in stopwords]
                mentorPref = [x[0].upper() for x in mentorPref if "JJ" in x[1] and x[0].upper() not in stopwords]

                attributeAdded = False
                
                for x in menteePref:
                    if len(x) < 3: continue
                    if x in mentorPref:
                        score+=0.25
                        if not attributeAdded: 
                            attributes+="Mentee/Mentor Other Pref."
                            attributeAdded = True

            #toCompare = [menteePref, mentorPref]
            #cv = CountVectorizer()
            #count_matrix = cv.fit_transform(toCompare)

            #match = cosine_similarity(count_matrix)[0][1]

            # name, attributes, score
            ranking.append([str(menteeData["fname"].iloc[j]) +" "+ str(menteeData["lname"].iloc[j])+ " "+  str(menteeData["ID"].iloc[j]) , attributes, score])
        
        ranking = sorted(ranking, key=lambda x: x[2], reverse=True)
        
        outputDF[mentorName] = []
        outputDF["Matching Attributes ",i] = []
        outputDF["Scores ",i] = []

        for k in range(len(ranking)):
            outputDF[mentorName].append(ranking[k][0])
            outputDF["Matching Attributes ",i].append(ranking[k][1])
            outputDF["Scores ",i].append(ranking[k][2])

        #print(str((done/tot)*100)+"% Complete", end = "\r")




            


    
    matches = pd.DataFrame(outputDF)
    print(matches)
    matches.to_excel("output.xlsx") 

if __name__=="__main__":
    main(sys.argv)


