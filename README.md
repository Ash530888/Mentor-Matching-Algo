# Mentor-Matching-Algo BETA
Developing an in-house mentor matching algorithm for Queen Mary University of London's mentoring programme QMentoring.
OUPUT: output.xlsx spreadsheet where column names are mentors and all mentees ranked from highest compatibility to lowest for each.

Instructions:
- Name mentee data and mentor data spreadsheets Mentee_Data.xlsx, Mentor_Data.xlsx respectively
- Make sure that spreadsheets are in the folder MM_Algo folder
- Double click MM_ALGO executable file inside MM_Algo folder to run algorithm
- Progress update messages are printed out on pup-up window
- NOTE: Very early, beta version so need to manually check decisions made by algo (DO NOT TRUST BLINDLY) - it indicates in output why no match found if that's the case, and if match found outputs why they were matched


Dependencies:
- [to do]

Decisions:
- Using the Levenshtein similarity method to compare values typed in by mentees or mentors.

To Improve: 
- Smarter analysis/comparison of qualifications and job/industry - very naive approach currently used where:
    - job/industy: match keywords from limited dataset
        - tried web scraping to find related roles and compare mentee and mentor jobs but realised this would be unreliable since html structure of                 websites likely to change
    - qualifications: look for shared words between mentor and mentee qualifications
    

