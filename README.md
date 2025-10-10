To use directory and one_student python files you must create a .env file with the following contents

USER=\<NCSU Email Address\>

PASSWORD=\<UnityID Password\>

For One Student, change the first and last name of student to get info for that student

For Sample_Builder, the output is in the .gitignore to avoid publicizing our student email list

# Useful resources:

Overview of how to adminster a survey at NCSU

https://uda.ncsu.edu/surveys/administering-a-survey-at-ncstate/

Policies at registering an NCSU survey

https://policies.ncsu.edu/regulation/reg-01-25-17/

Data management:

https://policies.ncsu.edu/regulation/reg-08-00-03/

registering survey:

https://uda.ncsu.edu/surveys/administering-a-survey-at-ncstate/register-your-survey/

-------------------------------------------------------------------------------------------

export_students.py will output st370_undergrads_college.csv that contains studnets and their attributes ordered by: unity_id,first_name,last_name,email,campus_id,college

select_by_college.py will take st370_undergrads_college.csv and sort it by college to then randomly select 40 students from each college to get the sample email list in two forms: email_list.txt and email_list.csv. 

email_list.csv is for qualtrics. email_list.txt is to see which studnets were selected from each college. 

select_700.py will randomly select 700 undergraduate students from st370_undergrads_college.csv and export them to email_list.csv