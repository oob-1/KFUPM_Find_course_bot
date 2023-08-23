from concurrent.futures import ProcessPoolExecutor
from courses_api import search_course
import telebot
import json
import copy # to use the deep copy


BOT = telebot.TeleBot("")
CURRENT_TERM = '231'

isStart = False
isFinish = False
input_courses = []


# get all courses in the current term
all_courses = search_course(term = CURRENT_TERM)
for i in all_courses:
    i.pop('term')
    i.pop('sequenceNumber')
    i.pop('maximumEnrollment')
    i.pop('enrollment')
    i.pop('seatsAvailable')
    i.pop('waitCapacity')
    i.pop('waitCount')
    i.pop('waitAvailable')


def read_users_data():
    try:
        with open('users.json', 'r') as f:
            temp = json.load(f)
    except:
        temp = {}
    return temp

def write_users_data(data):
    with open('users.json', 'w') as f:
        f.write(json.dumps(data,indent = 4))



def format(d):
    return f"Course: {d['subjectCourse']}\nAvailable seats: {d['seatsAvailable']}\nAvailable waitList: {d['waitCapacity']}"

def reset(user_id):
    global isStart,isFinish, input_courses
    isStart = False
    isFinish = False
    input_courses = []

    # delete the user if he stop the bot
    temp = read_users_data()
    for i in temp:
        try:
            temp[i].remove(user_id)
        except:
            continue
    write_users_data(temp)


def send_to_users(dif):
    temp = read_users_data()
    for course in dif: # thre
        if course['subjectCourse'] in temp:
            for user_id in temp[course['subjectCourse']]:
                BOT.send_message(user_id,format(course))
        if course['courseReferenceNumber'] in temp:
            for user_id in temp[course['courseReferenceNumber']]:
                BOT.send_message(user_id,format(course))


def is_correct_course(course): # return True if the course in the current term
    for i in all_courses: 
        if course.upper() == i['subjectCourse'] or course == i['courseReferenceNumber']:
            return True
    return False

def is_registered(user_id): # return True if the user have registered
    temp = read_users_data()
    for ideeeees in temp.values():
        if user_id in ideeeees:
            return True
    return False
            

def add_user(user_courses,user_chat_id):
    try:
        temp = read_users_data()
        for course in user_courses:
            if course in temp:
                temp[course].append(user_chat_id)
                temp[course] = list(set(temp[course])) # remove duplicate
            else:
                temp[course] = [user_chat_id]
        write_users_data(temp)
    except:
        for course in user_courses:
            temp[course] = [user_chat_id]
        write_users_data(temp)




@BOT.message_handler(commands=["start","registered","finish","stop"],chat_types=['private'])
def welcome(msg):
    global isStart, isFinish, input_courses

    if msg.text == "/start":
        isStart = True
        BOT.send_message(msg.chat.id,'''
                         يا أهلًا وسهلًا في بوت مراقبة الكورسات🙋‍♂️

ارسل اسم الكورس او CRN وراح يرسلك البوت اذا يمديك تسجل أو لا:

                         ''')

    if msg.text == "/registered": 
        if is_registered(msg.chat.id):
            BOT.send_message(msg.chat.id,"Yes!")
        else:
            BOT.send_message(msg.chat.id,"No!")

    if msg.text == "/finish" and isStart:
        isFinish = True
        add_user(input_courses,msg.chat.id)
        input_courses = []
        BOT.send_message(msg.chat.id,"Done!, when course Available the bot will send you.")

    if msg.text == "/stop":
        reset(msg.chat.id)
        BOT.send_message(msg.chat.id,"Done!")


@BOT.message_handler(chat_types=['private'])
def boooo(msg):
    global isStart, isFinish

    if isStart and not isFinish:
        if is_correct_course(msg.text):
            input_courses.append(msg.text.upper())
            BOT.reply_to(msg,'added.')
            BOT.send_message(msg.chat.id,'add another course or write (/finish) to start:')
        else:
            BOT.reply_to(msg,'course not found!')
            BOT.send_message(msg.chat.id,text='Try again:')



def a1():
    BOT.infinity_polling()

def a2(): # check if there any change in the courses
    base = search_course(term = CURRENT_TERM)
    while True:
        difference = []
        chang = search_course(term = CURRENT_TERM)
        idx = 0
        while True:
            try:
                if chang[idx] != base[idx]:
                    difference.append(chang[idx])
                idx+=1
            except:
                base = copy.deepcopy(chang) # update the base

                # send to users if there is change in the course
                if difference:
                    send_to_users(difference)
                break

def main():
    with ProcessPoolExecutor() as executor: # multiprocessing
        executor.submit(a1).result()
        executor.submit(a2).result()

if __name__ == '__main__':
    main()




