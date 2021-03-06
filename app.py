import os
import calendar, time 
import datetime
from slack_bolt import App, Ack
from slack import WebClient
import json
import random
import string
import pandas as pd
from frame import *

app = App(
    signing_secret = os.environ.get("SLACK_SIGN"),

# Initialize a Web API client
    token=os.environ.get("SLACK_BOT_TOKEN")
)

def write_json(new_data,section, filename):
    with open(filename,'r+') as file:
          # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data inside emp_details
        if section not in file_data:
            file_data.update(new_data)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 4)

def write_json_option(new_data,section,num, filename='question.json'):
    with open(filename,'r+') as file:
          # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data inside emp_details
        if new_data not in file_data[section][num]["elements"][0]["options"]:
            file_data[section][num]["elements"][0]["options"].append(new_data)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 4)

def wow():
    xl=pd.ExcelFile('chatbot.xlsx',engine='openpyxl')
    sheets_numb = len(xl.sheet_names)
    home_tab = {
        "WELCOME_BLOCK": home()
    }
    write_json(home_tab,"WELCOME_BLOCK",'home.json')
    for i in range(sheets_numb):
        data = pd.read_excel('chatbot.xlsx',sheet_name=i,engine='openpyxl')
        dictionary = {
            xl.sheet_names[i]: question_block(xl.sheet_names[i],"block","select")
        }
        buttonchoose = headers(xl.sheet_names[i],f"value-{i}")
        write_json(dictionary,xl.sheet_names[i],'question.json')
        write_json_option(buttonchoose,"WELCOME_BLOCK",0,'home.json')
        df=pd.DataFrame(data, columns= ['questions','answers'])
        for j in range(len(df.index)):
            write_json_option(option_block(df.iloc[j]['questions'],f"value-{j}"),xl.sheet_names[i],1,'question.json')

    other_block = {
        "Other/C??u h???i kh??c": other()
    }
    write_json_option(headers("Other/C??u h???i kh??c","other"),"WELCOME_BLOCK",0,'home.json')
    write_json(other_block,"Other/C??u h???i kh??c",'question.json')

@app.shortcut("sophie")
def sophie(event, say, ack, client,shortcut, body):
    ack()
    try:
        with open('home.json','r+') as file:
            # First we load existing data into a dict.
            file_data = json.load(file)
            client.chat_postMessage(channel=shortcut['user']['id'], text=f":hugging_face: Xin ch??o <@{body['user']['id']}>, T??i l?? Sophie - HR Helpdesk. B???n c?? c??u h???i n??o cho Sophie - H??y b???m v??o m???c li??n quan b??n d?????i nh??!")
            client.chat_postMessage(channel=shortcut['user']['id'], blocks=file_data["WELCOME_BLOCK"])
    except:
        print("error")

@app.action("action_id")
def onboard(event, say, ack, client,body,action):
    ack()
    try:
        with open('question.json','r+') as file:
            # First we load existing data into a dict.
            file_data = json.load(file)
            title = action["selected_option"]["text"]["text"]
            client.chat_postMessage(channel=body['user']['id'], blocks=file_data[title])
    except:
        print("error")

@app.action("select")
def onboard(event, say, ack, client,body,action):
    header=body['message']['blocks'][0]['text']['text']
    val=action["selected_option"]["value"]
    value=int(val[6:])
    data = pd.read_excel('chatbot.xlsx',sheet_name=header,engine='openpyxl')
    df=pd.DataFrame(data, columns=['answers'])
    ack()
    try:
        new=df.iloc[value]['answers'].replace(r'\n', '\n')
        client.chat_postMessage(channel=body['user']['id'], text=f"{new}")
    except:
        print("error")

@app.action("back")
def back(event, say, ack, client,body,action):
    ack()
    try:
        with open('home.json','r+') as file:
            # First we load existing data into a dict.
            file_data = json.load(file)
            client.chat_postMessage(channel=body['user']['id'], text=f":hugging_face: Xin ch??o <@{body['user']['id']}>, T??i l?? Sophie - HR Helpdesk. B???n c?? c??u h???i n??o cho Sophie - H??y b???m v??o m???c li??n quan b??n d?????i nh??!")
            client.chat_postMessage(channel=body['user']['id'], blocks=file_data["WELCOME_BLOCK"])
    except:
        print("error")

@app.event("team_join")
def ask_for_introduction(event, say, client, body, ack):
    day2 = datetime.datetime.today() + datetime.timedelta(days=1)
    day3 = datetime.datetime.today() + datetime.timedelta(days=2)
    scheduled_time = datetime.time(hour=9, minute=30, second=10)
    schedule_timestamp1 = datetime.datetime.combine(day2, scheduled_time).strftime('%s')
    schedule_timestamp2 = datetime.datetime.combine(day3, scheduled_time).strftime('%s')
    ack()
    user_id = event["user"]['id']
    text2 = f"hugging_face: Xin ch??o, <@{user_id}> l?? nh??n vi??n m???i ????ng kh??ng? H??y h???i Sophie nh???ng ??i???u th???c m???c nh??! (b???ng c??ch b???m v??o m???c li??n quan b??n d?????i nh??)"
    try:
        say(text=text2, channel=user_id)
        with open('home.json','r+') as file:
            # First we load existing data into a dict.
            file_data = json.load(file)
            client.chat_postMessage(channel=user_id, blocks=file_data["WELCOME_BLOCK"])
            client.chat_scheduleMessage(channel=user_id,text=f"Xin ch??o, ng??y h??m nay c???a b???n th??? n??o? B???n l??u ?? ho??n th??nh c??c kh??a h???c E-Learning - ????o t???o h???i nh???p trong 3 ng??y t??? ng??y gia nh???p v?? Ho??n thi???n h??? s?? nh??n s??? tr?????c 29 nh??. C?? th???c m???c kh??c h??y h???i Sophie! Ch??c b???n lu??n vui, kh???e! :grin:", blocks=file_data["WELCOME_BLOCK"], post_at=schedule_timestamp1)
            client.chat_scheduleMessage(channel=user_id,text=f"Xin ch??o, B???n ???? nghe v??? 1office? Hmm. Ng??y c??ng tr??n 1office ???????c d??ng ????? t??nh l????ng cho ch??nh b???n. H??y truy c???p ngay, ki???m tra v?? t???o ng??y c??ng ch??nh x??c ????? nh???n ????? l????ng th??ng. L??u ?? h??? th???ng ch??? cho ph??p t???o trong v??ng 5 ng??y, do ????, b???n c???n ki???m tra h??ng ng??y nh??. N???u kh??ng r?? c??ch l??m, h??y b???m v??o m???c VII. CH???M C??NG - T??NH L????NG ????? Sophie h?????ng d???n b???n! :v:", blocks=file_data["WELCOME_BLOCK"], post_at=schedule_timestamp2)
    except:
        print("error")


@app.action("submit")
def other_text(event, say, ack, client,body,action,button):
    text = body['state']['values']['block_h']['other_input']['value']
    ts = body['message']['ts']
    ack()
    #N???u nh?? channel c???a HR ?????i th?? l???y ID c???a channel m???i r???i thay v??o
    try:
        client.chat_postMessage(channel = 'C025751TS0P', text = f"You have a new question from <@{body['user']['id']}>:\n:point_right: {text}")
        client.chat_update(ts=ts, channel = body['container']['channel_id'], blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"G???i c??u h???i th??nh c??ng.\nC???m ??n b???n. Ph??ng Nh??n s??? s??? ph???n h???i b???n trong th???i gian s???m nh???t!"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Back",
                            "emoji": True
                        },
                        "value": "click_back",
                        "action_id": "back"
                    }
                ]
            },
            {
                "type": "divider"
            }
        ])
    except:
        print(os.error)

def delete_json():
    jsonFile = open("home.json", "w+")
    jsonFile.write(json.dumps({}))
    jsonFile = open("question.json", "w+")
    jsonFile.write(json.dumps({}))

if __name__ == "__main__":
    delete_json()
    wow()
    app.start(port=int(os.environ.get("PORT", 8000)))
