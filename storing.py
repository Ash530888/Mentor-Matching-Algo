for row in menteeJobsDict[j]:
                        print(row)
                        for job in row:
                            if len(job) > 2:
                                print("not a match ", job)
                                if (("teach" in job and row[0] in teachingJobs) or "teach" not in job) and (mentorJob in job or job in mentorJob or mentorIndustry in job or job in mentorIndustry):
                                #if mentorJob in job or job in mentorJob or mentorIndustry in job or job in mentorIndustry:
                                    #print("mentee ", menteeData["industry/job"].iloc[j])
                                    #print("from csv: ",job)
                                    #print("mentor: ",mentorJob)
                                    #print(mentorIndustry)
                                    #input()
                                    score+=2
                                    found = True
                                    attributes+= "Job/Industry Mentee("+menteeData["industry/job"].iloc[j]+"), Mentor("+mentorJob+"/"+mentorIndustry+"); "
                                    break
                        if found: break
                    
                    if not found:
                        print(menteeJobsDict[j])
                        print("mentee ", menteeData["industry/job"].iloc[j])
                        print("mentor: ",mentorJob)
                        print(mentorIndustry)
                        input("NOT FOUND!!")