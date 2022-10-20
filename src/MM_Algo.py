import sys
import argparse
import pandas as pd
import math
from Levenshtein import distance

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
    columns = [3, 4, 6, 8, 10, 11, 17, 18, 29, 32, 33, 34, 39, 40, 41]
    colNames = ["fname", "lname", "ID", "course", "dept", "faculty", "nationality", "gender", "bursary", "industry/job", "otherGender", "entrepreneurStage", "support", "mentorGender", "whichMentor"]
    #menteeData = pd.read_excel(filepath, sheet_name = mentee, header = None, names = columns)
    menteeData = pd.read_excel(menteeFile, header = None, usecols = columns, names = colNames)
    menteeData.drop(index=menteeData.index[0], axis=0, inplace=True)

    columns = [0, 4, 5, 7, 11, 12, 14, 15, 16, 18, 20, 22, 23]
    colNames = ["name", "gender", "otherGender", "qualifications", "ethnicitiy", "otherEthnic", "menteeGender", "otherMenteeGender", "QMULschool", "job", "industry", "support", "otherSupport"]
    #mentorData = pd.read_excel(filepath, sheet_name = mentor, header = None, names = columns)
    mentorData = pd.read_excel(mentorFile, header = None, usecols = columns, names = colNames)
    mentorData.drop(index=mentorData.index[0], axis=0, inplace=True)

    columns = []

    print(mentorData)
    input()
    print(mentorData["name"].iloc(0))
    input()

    #column "name", 0,0
    print(mentorData["name"].iloc(0)[0])
    print(mentorData["gender"].iloc(0)[0])
    input()

    # row
    print(mentorData.iloc[1])
    print(mentorData.iloc(0))
    input()

    outputDF = {}

    # iterate through mentors
    for i in range(len(mentorData)):

        mentorName = mentorData["name"].iloc[i]
        columns.append(mentorName)
        columns.append("Matching Attributes")

        mentorSupport = mentorData["support"].iloc[i]

        ranking = []
        # iterate through mentees
        for j in range(len(menteeData)):
            menteeSupport = menteeData["support"].iloc[j]
            score = 0
            attributes = ""

            # check which type of mentor preference
            # if mentee wants to be matched based on qualifications
            if menteeData["whichMentor"].iloc[j] == "Option 1 - A mentor who studied the same degree as me but works in any industry/job role":
                # check degree similarity between mentor and mentee

                # mentor has list of qualifications which each need to be processed individually
                # so split into list
                mentorQualifications = mentorData["qualifications"].iloc[i].split(", ")
                # remove numbers i.e. dates
                mentorQualifications = [i for i in mentorQualifications if not i.isnumeric()]

                found = False
                for q in mentorQualifications:
                    s = levenshtein_distance_percentage(menteeData["course"].iloc[j], q)
                    if s>=0.55: 
                        score+=1
                        if not found: attributes += "Qualifications, "
                        found = True

            elif menteeData["whichMentor"].iloc[j] == "Option 2 - A mentor who works in the industry/job role that I am interested in":
                industry = levenshtein_distance_percentage(menteeData["industry/job"].iloc[j], mentorData["industry"].iloc[i])
                job = levenshtein_distance_percentage(menteeData["industry/job"].iloc[j], mentorData["job"].iloc[i])

                if industry>=0.55: 
                    score+=1
                if job>=0.55: 
                    score+=1

            elif menteeData["whichMentor"].iloc[j] == "Option 3 - A mentor who can support with entrepreneurship":
                if "Developing entrepreneurial skills" in menteeSupport and "Developing entrepreneurial skills" in mentorSupport:
                    score+=1

                if "Support with setting up or growing a business" in menteeSupport and "Support with setting up or growing a business" in mentorSupport:
                    score+=1


            # check if mentor and mentee industry/job interests match for mentees who didn't want to be matched on this aspect
            # lower weighting
            if menteeData["whichMentor"].iloc[j] != "Option 2 - A mentor who works in the industry/job role that I am interested in":
                industry = levenshtein_distance_percentage(menteeData["industry/job"].iloc[j], mentorData["industry"].iloc[i])
                job = levenshtein_distance_percentage(menteeData["industry/job"].iloc[j], mentorData["job"].iloc[i])

                if industry>=0.55: 
                    score+=1
                if job>=0.55: 
                    score+=1
            
            # compare mentee goals and mentor offerings
            if "Planning for the future and goal setting" in menteeSupport and "Planning for the future and goal setting" in mentorSupport:
                score+=1
            if "Gaining insight to an industry/profession" in menteeSupport and "Gaining insight to an industry/profession" in mentorSupport:
                # need to only add to score if industry/profession same
                score+=1
            if "Building a professional network" in menteeSupport and "Building a professional network" in mentorSupport:
                score+=1
            if "Writing/improving CVs, job applications and covering letters" in menteeSupport and "Writing/improving CVs, job applications and covering letters" in mentorSupport:
                score+=1
            if "Interview practice and preparation" in menteeSupport and "Interview practice and preparation" in mentorSupport:
                score+=1
            if "Finding work experience (shadowing/internships/part-time work)" in menteeSupport and "Finding work experience (shadowing/internships/part-time work)" in mentorSupport:
                score+=1
            if "Developing entrepreneurial skills" in menteeSupport and "Developing entrepreneurial skills" in mentorSupport:
                score+=1
            if "Support with setting up or growing a business" in menteeSupport and "Support with setting up or growing a business" in mentorSupport:
                score+=1


            # check mentor and mentee gender preferences
            if menteeData["mentorGender"].iloc[j] != "No preference" and  mentorData["menteeGender"].iloc[i] != "No preference":
                if menteeData["mentorGender"].iloc[j] == mentorData["gender"].iloc[i] and menteeData["gender"].iloc[j] == mentorData["menteeGender"].iloc[i]:
                    score+=1
                elif menteeData["mentorGender"].iloc[j] == mentorData["gender"].iloc[i]:
                    score+=0.5
                elif menteeData["gender"].iloc[j] == mentorData["menteeGender"].iloc[i]:
                    score+=0.5


            # check QMUL School
            if menteeData["dept"].iloc[j] == mentorData["QMULschool"]: score+=1
            


            #if menteeData["fname"].iloc[j] == "Aishah":
            #    score = 1
            #    attributes+="gender, industry, qualifications"
            #    if math.isnan(menteeData["dept"].iloc[j]):
            #        print("NaN found")
            #        input()


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



