import requests
from concurrent.futures import ThreadPoolExecutor

def remove_un_data(t:list):
    data_to_del = ['id','termDesc','meetingsFaculty','faculty',
               'isSectionLinked','creditHourIndicator','creditHourLow',
               'creditHourHigh','crossListAvailable','crossListCount',
               'crossListCapacity','crossList','creditHours','courseTitle',
               'scheduleTypeDescription','campusDescription','subjectDescription',
               'subject','courseNumber','partOfTerm','linkIdentifier','sectionAttributes',
               'reservedSeatSummary','openSection']
    for i in t:
        for j in data_to_del:
            i.pop(j)
            
def get_cookies(term:str, course:str, choice = 0):
    course_name = course.rstrip('0123456789')
    course_num = course[len(course_name):]

    response1 = requests.post(
        'https://banner9-registration.kfupm.edu.sa/StudentRegistrationSsb/ssb/term/search',
        data={'term': f'20{term}0','studyPath': '','studyPathText': '','startDatepicker': '','endDatepicker': ''},
    )

    response2 = requests.get( 
        'https://banner9-registration.kfupm.edu.sa/StudentRegistrationSsb/ssb/searchResults/searchResults',
        params={"txt_subject": course_name.upper(), "txt_courseNumber": course_num, "txt_term": f'20{term}0', "startDatepicker": "", "endDatepicker": "", "pageOffset": "0", "pageMaxSize": "10", "sortColumn": "subjectDescription", "sortDirection": "asc"},
        cookies={"JSESSIONID" : response1.cookies.get("JSESSIONID")},
    )
    
    if choice: # to get the number of results -how many courses-
        return response2.json()["totalCount"] 
    return response1.cookies.get("JSESSIONID")


def search_course(term:str, course:str ="", crn:str = ""):
    """
    -This method will return all courses for the entered term
    
    -Pass course name(optional) to return all courses belong to it, example: "ICS".
    if u pass it like this "ICS108" it will return all ICS108 courses.

    -Pass crn(optional) to return specific course. 
    Note: pass a crn and the course name with it to get the data faster.
    """

    temp = []

    course_name = course.rstrip('0123456789') # remove the number in the text
    course_num = course[len(course_name):] # have only the numbers

    number_of_results = get_cookies(term, course=course, choice=1)
    
    cookies = {
        "JSESSIONID" : get_cookies(term,course=course),
    }

    # inner func to use Thread on it
    def get_data(i):
        params = {
            'txt_subject': course_name.upper(),
            'txt_courseNumber': course_num,
            'txt_term': f'20{term}0',
            'startDatepicker': '',
            'endDatepicker': '',
            'pageOffset': f'{i}',
            'pageMaxSize': '50',
            'sortColumn': 'subjectDescription',
            'sortDirection': 'asc',
        }

        response = requests.get(
            'https://banner9-registration.kfupm.edu.sa/StudentRegistrationSsb/ssb/searchResults/searchResults',
            params=params,
            cookies=cookies,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',},
        )
        temp.extend(response.json()["data"])
    
    #Threading
    with ThreadPoolExecutor() as ex:
        [ex.submit(get_data,i) for i in range(0,number_of_results,50)]
    
    # keep the important data
    remove_un_data(temp)

    

    if crn: # if pass crn
        for i in temp:
            if i["courseReferenceNumber"] == str(crn):
                return i
        return "Crn not found."
    if not temp: # if empty then no course found
        return "not found."
    
    # sort the data by crn
    temp.sort(key=lambda x: x['courseReferenceNumber'], reverse=False) 
    return temp
    
            



        
