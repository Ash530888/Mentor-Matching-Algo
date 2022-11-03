# Mentor-Matching-Algo BETA
Developing an in-house mentor matching algorithm for Queen Mary University of London's mentoring programme QMentoring.
OUPUT: output.xlsx spreadsheet where column names are mentors and all mentees ranked from highest compatibility to lowest for each.

Instructions:
- Name mentee data and mentor data spreadsheets Mentee_Data.xlsx, Mentor_Data.xlsx respectively
- Make sure that spreadsheets are in the same folder as executable file
- NOTE: Very early, beta version so need to manually check decisions made by algo (DO NOT TRUST BLINDLY) - it outputs if no match found, and if match found outputs why they were matched


Dependencies:
- [to do]

Decisions:
- Using the Levenshtein similarity method to compare values typed in by mentees or mentors.

To Improve: 
- Smarter analysis/comparison of qualifications and job/industry - very naive approach currently used where:
    - job/industy: match keywords from limited dataset
    - qualifications: look for shared words between mentor and mentee qualifications

