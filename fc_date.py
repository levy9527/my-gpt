from typing_extensions import TypedDict
import datetime
import json
import sys
from dataclasses import dataclass

from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI
client = OpenAI()

settings = {
    "model": "gpt-3.5-turbo-1106",
    "temperature": 0,
}

class DateDistance(TypedDict):
    type: str
    distance: int

def get_week_range(date: datetime) -> [str, str]:
    days_to_prev_monday = date.weekday()
    # Monday
    start_of_week = date - datetime.timedelta(days=days_to_prev_monday)
    # Sunday
    end_of_week = start_of_week + datetime.timedelta(days=6)
    return start_of_week.strftime('%Y-%m-%d'), end_of_week.strftime('%Y-%m-%d')

def get_date_distance(message: str) -> DateDistance:
    '''calculate date distance compared to today'''
    schema = {
        "properties": {
            "type": {"type": "string", "enum": ["day", "week", "month", "year", 'none'],
                     "description": "if can't get expected date info, type is none"},
            "distance": {"type": "number",
                         "description": "suppose type is day, then today's distance is 0, yesterday is -1, tomorrow is 1. "
                                        "same logic applies to week、month、and year"},
            
        },
        "type": "object",
    }
    import datetime
    resp = client.chat.completions.create(
        **settings,
        messages=[
            {
                "role": "user",
                "content": f"today is {datetime.date.today()}, "
                           f"get date distance compared to the following sentence: {message}",
            },
        ],
        functions=[{"name": "get_date_distance",
                    "description": "calculate expected date distance based on today", "parameters": schema}],
        function_call="auto",
    )
    return json.loads(resp.choices[0].message.function_call.arguments)

def get_formatted_date(date_distance: DateDistance):
    today = datetime.datetime.today()
    '''get formatted date string based on date_distance'''
    if date_distance['type'] == 'year':
        return str(today.year + date_distance['distance'])
    if date_distance['type'] == 'month':
        date = today.replace(month=today.month + date_distance['distance'])
        return date.strftime('%Y-%m')
    if date_distance['type'] == 'day':
        date = today.replace(day=today.day + date_distance['distance'])
        return date.strftime('%Y-%m-%d')
    if date_distance['type'] == 'week':
        date = today + datetime.timedelta(days=date_distance['distance'] * 7)
        week_range = get_week_range(date)
        return week_range[0] + ',' + week_range[1]


if __name__ == '__main__':
    now = datetime.datetime.now()
    day_str = now.strftime('%Y-%m-%d')
    month_str = now.strftime('%Y-%m')
    year_str = now.strftime('%Y')
    week_range = get_week_range(now)
    week_str = week_range[0] + ',' + week_range[1]
    
    expected_date_str = [day_str, month_str, year_str, week_str]
    date_distances = [DateDistance(type='day', distance=0),
                      DateDistance(type='month', distance=0),
                      DateDistance(type='year', distance=0),
                      DateDistance(type='week', distance=0)]
    for i, v in enumerate(date_distances):
        result = get_formatted_date(v)
        print(result)
        assert expected_date_str[i] == result
      
    sys.exit()
    
    expected_dis = [0,-1,1,0,-1,1,-1,-1,0,0,0,-1,1]
    expected_type = ['day', 'day', 'day', 'week', 'week', 'week', 'month', 'month', 'month', 'year', 'year', 'year', 'year']
    for i, v in enumerate(
        ['今天', '昨天', '明天', '本周', '上周', '下周', '上个月', '上月', '本月', '今年', '本年度', '去年', '明年']):
        result = get_date_distance(v)
        print(result)
        assert expected_type[i] == result['type']
        assert expected_dis[i] == result['distance']
