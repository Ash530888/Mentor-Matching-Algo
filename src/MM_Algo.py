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


def levenshtein_distance_percentage(s1: str, s2: str) -> float:
    #Computes the Levenshtein dis
    assert min(len(s1), len(s2)) > 0, "One of the given string is empty"
    return 1. - distance(s1, s2) / min(len(s1), len(s2))


def main(argv):
    parser = argparse.ArgumentParser()
    #parser.add_argument("--data_filepath", help="Data file path",
    #                    default="../data/Matching_Template.xlsx") 
    #parser.add_argument("--mentee_sheet", help="Mentee sheet's name in excel spreadsheet",
    #                    default="Mentee_data")
    #parser.add_argument("--mentor_sheet", help="Mentor sheet's name in excel spreadsheet",
    #                   default="Mentor_data")

    parser.add_argument("--mentee_data_filepath", help="Mentee Data file path",
                        default="data/Mentee_Data.xlsx")
    parser.add_argument("--mentor_data_filepath", help="Mentor Data file path",
                        default="data/Mentor_Data.xlsx")


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

    columns = [0, 4, 5, 7, 11, 12, 14, 15, 16, 17, 18, 19, 20, 22, 23]
    colNames = ["name", "gender", "otherGender", "qualifications", "ethnicitiy", "otherEthnic", "menteeGender", "otherMenteeGender", "QMULschool", "matchPref", "job", "company", "industry", "support", "otherSupport"]
    #mentorData = pd.read_excel(filepath, sheet_name = mentor, header = None, names = columns)
    mentorData = pd.read_excel(mentorFile, header = None, usecols = columns, names = colNames)
    mentorData.drop(index=mentorData.index[0], axis=0, inplace=True)

    columns = []

    outputDF = {}

    # iterate through mentors
    for i in range(len(mentorData)):

        mentorName = mentorData["name"].iloc[i]
        columns.append(mentorName)
        columns.append("Matching Attributes")

        mentorSupport = mentorData["support"].iloc[i].split(",")

        ranking = []
        # iterate through mentees
        for j in range(len(menteeData)):
            menteeSupport = (menteeData["support"].iloc[j]).split(",")
            score = 0
            attributes = ""

            # check which type of mentor preference
            # if mentee wants to be matched based on qualifications
            if menteeData["whichMentor"].iloc[j] == "Option 1 - A mentor who studied the same degree as me but works in any industry/job role":
                # check degree similarity between mentor and mentee

                # mentor has list of qualifications which each need to be processed individually
                # so split into list
                mentorQualifications = (mentorData["qualifications"].iloc[i]).split(", ")
                input(mentorQualifications)
                # remove numbers i.e. dates
                mentorQualifications = [i for i in mentorQualifications if not i.isnumeric()]

                for q in mentorQualifications:
                    s = levenshtein_distance_percentage(menteeData["course"].iloc[j], q)
                    if s>=0.55: 
                        score+=1
                        attributes += "Qualifications; "
                        break
            # if mentee wants to be matched based on industry/job
            if menteeData["whichMentor"].iloc[j] == "Option 2 - A mentor who works in the industry/job role that I am interested in":
                stopWords = [".", "/","or", "and"]
                menteeJob = (menteeData["industry/job"].iloc[j]).split(",")
                menteeJob = [x for x in menteeJob if x.lower() not in stopWords]
                mentorJob = mentorData["job"].iloc[j]
                mentorIndustry = mentorData["industry"].iloc[j]
                mentorCompany = mentorData["company"].iloc[j]

                found = False

                for x in menteeJob:
                    print(x)
                    jobs = find_jobs_from("CWjobs", x, "uk")

                    titles = []
                    companies = []

                    titles = [y[1].upper() for y in jobs if y not in titles]
                    companies = [y[0].upper() for y in jobs if y not in companies]
                    
                    if mentorJob.upper() in titles or mentorIndustry.upper() in titles:
                        if mentorCompany in companies: 
                            score+=0.5
                            attributes+= "Company; "
                        score+=1
                        attributes+= "Job/Industry; "
                        found = True
                        break

                    if found: break



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
                if "Developing entrepreneurial skills" in menteeSupport and "Developing entrepreneurial skills" in mentorSupport:
                    score+=1
                    attributes += "Developing Entrepreneurial Skills; "

                if "Support with setting up or growing a business" in menteeSupport and "Support with setting up or growing a business" in mentorSupport:
                    score+=1
                    attributes += "Starting/Growing Business; "
                
                if (menteeData["entrepreneurStage"].iloc[j])[6] == "1":
                    score+=1
                    attributes+="Exploring Entrepreneurship; "

                elif (menteeData["entrepreneurStage"].iloc[j])[6] == "2":
                    score+=2
                    attributes+="Aspiring Entrepreneur with Business Idea; "

                elif (menteeData["entrepreneurStage"].iloc[j])[6] == "3":
                    score+=3
                    attributes+="Current Entrepreneur; "


            
            
            # compare mentee goals and mentor offerings
            if "Planning for the future and goal setting" in menteeSupport and "Planning for the future and goal setting" in mentorSupport:
                score+=1
                attributes += "Planning/Setting Goals; "
            if "Gaining insight to an industry/profession" in menteeSupport and "Gaining insight to an industry/profession" in mentorSupport:
                # need to only add to score if industry/profession same
                score+=1
                attributes += "Industry Insight; "
            if "Building a professional network" in menteeSupport and "Building a professional network" in mentorSupport:
                score+=1
                attributes += "Networking; "
            if "Writing/improving CVs, job applications and covering letters" in menteeSupport and "Writing/improving CVs, job applications and covering letters" in mentorSupport:
                score+=1
                attributes += "CVs/Applications; "
            if "Interview practice and preparation" in menteeSupport and "Interview practice and preparation" in mentorSupport:
                score+=1
                attributes += "Interviews; "
            if "Finding work experience (shadowing/internships/part-time work)" in menteeSupport and "Finding work experience (shadowing/internships/part-time work)" in mentorSupport:
                score+=1
                attributes += "Shadowing/Internships/Work; "


            # check mentor and mentee gender preferences
            if menteeData["mentorGender"].iloc[j] != "No preference" and  mentorData["menteeGender"].iloc[i] != "No preference":
                if menteeData["mentorGender"].iloc[j] == mentorData["gender"].iloc[i] and menteeData["gender"].iloc[j] == mentorData["menteeGender"].iloc[i]:
                    score+=1
                    attributes += "Both Mentee and Mentor Gender Pref. Met; "
                elif menteeData["mentorGender"].iloc[j] == mentorData["gender"].iloc[i]:
                    score+=0.5
                    attributes += "Only Mentee Gender Pref. Met; "
                elif menteeData["gender"].iloc[j] == mentorData["menteeGender"].iloc[i]:
                    score+=0.5
                    attributes += "Only Mentor Gender Pref. Met; "
            else:
                if mentorData["menteeGender"].iloc[i] == "No preference" and menteeData["mentorGender"].iloc[j] == mentorData["gender"].iloc[i]:
                    score+=1
                    attributes += "Mentee Gender Pref. Met; "
                elif menteeData["mentorGender"].iloc[j] == "No preference" and menteeData["gender"].iloc[j] == mentorData["menteeGender"].iloc[i]:
                    score+=1
                    attributes += "Mentor Gender Pref. Met; "


            # check QMUL School
            if menteeData["dept"].iloc[j] == mentorData["QMULschool"].iloc[i]: score+=1

            # Compare Mentor's and Mentee's additional match preferences
            #menteePref = menteeData["matchPref"].iloc[j]
            #menteePref = word_tokenize(menteePref)
            #menteePref = nltk.pos_tag(menteePref)
            #menteePref = [x[0].upper() for x in menteePref if "VB" in x[1] or "NN" in x[1]]
            

            #mentorPref = mentorData["matchPref"].iloc[i]
            #mentorPref = word_tokenize(mentorPref)
            #mentorPref = nltk.pos_tag(mentorPref)
            #mentorPref = [x[0].upper() for x in mentorPref if "VB" in x[1] or "NN" in x[1]]

            #attributeAdded = False
            #for x in menteePref:
            #    if x in mentorPref:
            #        score+=0.25
            #        if not attributeAdded: 
            #            attribute+="Mentee/Mentor Other Pref.; "
            #            attributeAdded = True


            # name, attributes, score
            ranking.append([str(menteeData["fname"].iloc[j]) +" "+ str(menteeData["lname"].iloc[j])+ " "+  str(menteeData["ID"].iloc[j]) , attributes, score])
        
        ranking = sorted(ranking, key=lambda x: x[2], reverse=True)
        outputDF[mentorName] = []
        outputDF[mentorName+"'s Matching Attributes"] = []

        for k in range(len(ranking)):
            outputDF[mentorName].append(ranking[k][0])
            outputDF[mentorName+"'s Matching Attributes"].append(ranking[k][1])




            


    
    matches = pd.DataFrame(outputDF)

    print(matches)

    matches.to_excel("data/output.xlsx") 

if __name__=="__main__":
    main(sys.argv)



