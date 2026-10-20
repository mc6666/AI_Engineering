# 結構化輸出(Structured Outputs)測試
## 載入套件
from openai import OpenAI
from pydantic import BaseModel

## 定義輸出類別
class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]

class CalendarEventList(BaseModel):
    event_list: list[CalendarEvent]
    

# 建立OpenAI用戶端物件
client = OpenAI()

# 提示
prompt = '''
Alice and Bob are going to a science fair on Friday. 
John will attend IEEE seminar next Monday.
'''

# 提示
target = 'Extract the event information.'

# 呼叫API
response = client.responses.parse(
    model="gpt-5.6-luna",
    input=[
        {"role": "system", "content": target},
        {
            "role": "user",
            "content": prompt,
        },
    ],
    text_format=CalendarEventList,
)

event = response.output_parsed
print(event)

## 美化輸出結果
print(f'name\tdate\tparticipants')
for item in event.event_list:
    print(f'{item.name}\t{item.date}\t{item.participants}')

## 中文測試
class Winner(BaseModel):
    sport_name: str
    medal: str
    participants: list[str]

class Winner_list(BaseModel):
    winner_list: list[Winner]

# 提示
prompt = '''
本屆代表團在羽球項目拿下2金3銀1銅，其中混雙包辦「金、銀、銅」史無前例，丁彥宸也搶下世大運史上第2面男單金牌。
跆拳道部分，品勢女團奪金，男團收穫銅牌；對打項目進帳3銀1銅。
桌球不但粉碎中國男團挑戰7連霸大業，更一舉摘金改寫隊史！女子部分在女單奪銀，女雙、女團各獲得兩面銅牌。
湯智鈞在反曲弓個人賽帶回睽違20年的金牌，田徑項目靠著傅兆玄跳高摘銀，「台灣蝶王」王冠閎也進帳一面銀牌。
網球女雙由林芳安／李羽芸攜手搶下銀牌，首度代表台灣的陳瑞安一人奪兩塊獎牌，在全能項目鍍銅，平衡木再拿下1銀。
'''

# 目標
target = 'Extract the winner information.'

# 呼叫API
response = client.responses.parse(
    model="gpt-5.6-luna",
    input=[
        {"role": "system", "content": target},
        {
            "role": "user",
            "content": prompt,
        },
    ],
    text_format=Winner_list,
)

output = response.output_parsed
print(output)

print(f'運動項目\t獎牌\t選手')
for item in output.winner_list:
    print(f'{item.sport_name}\t{item.medal}\t{item.participants}')

## 命名實體識別(Named Entity Recognition, NER)測試
from enum import Enum

# 定義人/事/時/地/物
class NerEnum(str, Enum):
    Person = 'Person'
    Organization = 'Organization'
    Location = 'Location'
    DateTime = 'DateTime'
    
class Entity(BaseModel):
    name: str
    type: str
    enum: NerEnum
    
class Entity_list(BaseModel):
    entity_list: list[Entity]

# 提示
prompt = '''
Samuel Harris Altman (born April 22, 1985) is an American entrepreneur and investor 
best known as the CEO of OpenAI since 2019 
(he was briefly fired and reinstated in November 2023).
'''

# 目標
target = '''
You are a Named Entity Recognition (NER) assistant.
Your job is to identify and return all entity names and their 
types for a given piece of text. You are to strictly conform
only to the following entity types: Person, Location, Organization
and DateTime. If uncertain about entity type, please ignore it.
Be careful of certain acronyms, ignore role titles "CEO", "CTO"
'''

# 呼叫API
response = client.responses.parse(
    model="gpt-5.6-luna",
    input=[
        {"role": "system", "content": target},
        {
            "role": "user",
            "content": prompt,
        },
    ],
    text_format=Entity_list,
)

output = response.output_parsed
print(output)

for item in output.entity_list:
    print(f'{item.name}\t{item.type}\t{item.enum}')



