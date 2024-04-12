import json

from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI
client = OpenAI()

def get_date_distance(message: str):
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
        model="gpt-3.5-turbo",
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
    


if __name__ == '__main__':
    expected_dis = [0,-1,1,0,-1,1,-1,-1,0,0,0,-1,1]
    expected_type = ['day', 'day', 'day', 'week', 'week', 'week', 'month', 'month', 'month', 'year', 'year', 'year', 'year']
    for i, v in enumerate(
        ['今天', '昨天', '明天', '本周', '上周', '下周', '上个月', '上月', '本月', '今年', '本年度', '去年', '明年']):
        result = get_date_distance(v)
        print(result)
        assert expected_type[i] == result['type']
        assert expected_dis[i] == result['distance']
