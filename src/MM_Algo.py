import sys
import argparse
import pandas as pd


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_filepath", help="Data file path",
                        default="../data/Matching_Template.xlsx")
    parser.add_argument("--mentee_sheet", help="Mentee sheet's name in excel spreadsheet",
                        default="Mentee data")
    parser.add_argument("--mentor_sheet", help="Mentor sheet's name in excel spreadsheet",
                        default="Mentor data")

    args = parser.parse_args()
    filepath = args.data_filepath
    mentee = args.mentee_sheet
    mentor = args.mentor_sheet


    # Read excel sheets
    columns = ["firstName", "surname:", "emailAddress:", "contactNumber:", "studentID", "gender", "selfDescribeGender", "academicSchool", "courseTitle", "yearOfStudy",	"ethnicity", "otherEthnic", "disabled", "preferredGender", "other", "typeMentor", 	"industry_job", "otherPreferences", "why", "bursary"]
    menteeData = pd.read_excel(filepath, sheet_name = mentee, header = None, names = columns)

    columns = ["firstName", "surname:", "emailAddress:", "homeAddress", "contactNumber:", "gender", "selfDescribeGender", "formerQMUL", "qualifications",	"ethnicity", "otherEthnic", "disabled", "preferredGender", "other", "menteeSchools", "otherPreferences", "jobTitle", "company", "industry", "jobDesc", "skills_exp", "dataCollection"]
    mentorData = pd.read_excel(filepath, sheet_name = mentor, header = None, names = columns)


if __name__=="__main__":
    main(sys.argv)