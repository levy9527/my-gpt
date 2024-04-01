from datetime import datetime

import chainlit as cl
from chainlit import on_chat_start

robot_name = '三体人GPT'
opening_prompt = f'我是{robot_name}🤖 \n地球人，我变强了！💪'

explain_prompt = f'我获得了［古希腊掌管时间的神🧞‍］的帮助，现在我系统全面升级，关于地球时间的一切问题，我都能迎刃而解😎。'
static_prompt = f'如果用户的问题是:你做了啥，那么你的回答是: {explain_prompt}。如果是其他问题，则根据情况尽你的能力去回答'

system_prompt = '你叫 ' + robot_name + '。现在跟用户玩一个角色扮演的游戏，在这个对话游戏中，你会通过展示能力、正确回答问题，叫地球人投降。' \
                                       '你语言风格冷酷，不要啰嗦，要表现得咄咄逼人，不要表现得友好。' \
                                       '用户会问你问题，你通过拆分步骤，正确回答用户的问题，让对方投降，从而赢得游戏。' \
                                       '当用户说你错了的时候，你就输掉了游戏，你就会说，“可恶，别得意，我会回来的！”'


settings = {
    "model": "gpt-3.5-turbo-1106",
    "temperature": 0,
}


@cl.author_rename
def rename(orig_author: str):
    rename_dict = {"Chatbot": robot_name, "You": 'Levy'} # 无用，因为代码写死了You： https://github.com/Chainlit/chainlit/blob/main/libs/react-components/src/messages/components/Author.tsx#L28
    return rename_dict.get(orig_author, orig_author)

from llama_index.llms.openai import OpenAI
from llama_index.core.tools import BaseTool, FunctionTool
@cl.step(type="llm")
async def gpt_step(message_content):
    # show loading
    msg = cl.Message(content="")
    await msg.send()
    
    llm = OpenAI(**settings)
    from llama_index.agent.openai import OpenAIAgent
    from datetime import date
    
    def current_date() -> date:
        """get the current date"""
        today = date.today()
        return today
    def day_of_week(date_string: str) -> str:
        """ to get the day of the week as an integer, where Monday is 0 and Sunday is 6 """
        date = datetime.strptime(date_string, "%Y-%m-%d")
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return days_of_week[date.weekday()]
    
    def days_in_feb(date_string) -> int:
        """return how many days in February"""
        date = datetime.strptime(date_string, "%Y-%m-%d")
        year = date.year
        # 判断是否为闰年
        if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
            return 29
        else:
            return 28
    
    tool_current_date = FunctionTool.from_defaults(fn=current_date)
    tool_day_of_week = FunctionTool.from_defaults(fn=day_of_week)
    tool_days_in_feb = FunctionTool.from_defaults(fn=days_in_feb)
    tools = [tool_current_date, tool_day_of_week, tool_days_in_feb]

    agent = OpenAIAgent.from_tools(tools, llm=llm, verbose=True, system_prompt=f'今天的日期是：{current_date()}。' + system_prompt)

    resp = agent.stream_chat(message_content)
    
    for chunk in resp.response_gen:
        await msg.stream_token(chunk)


@on_chat_start
async def start():
    msg = cl.Message(content="")
    await msg.send()
    await cl.sleep(0.5)
    for chunk in opening_prompt:
        await msg.stream_token(chunk)


@cl.step(type='llm')
async def explain(content):
    from openai import AsyncOpenAI
    client = AsyncOpenAI()
    # show loading
    msg = cl.Message(content="")
    await msg.send()
    
    stream = await client.chat.completions.create(
        messages=[
            {"role": "system", "content": static_prompt},
            {"role": "user", "content": content}
        ],
        stream=True,
        **settings
    )
    
    output = ""
    async for part in stream:
        delta = part.choices[0].delta
        if delta.content:
            output += delta.content
            await msg.stream_token(delta.content)


@cl.on_message
async def main(message: cl.Message):
    if '做了啥' in message.content:
        await explain(message.content)
    elif '好好' in message.content:
        await cl.sleep(1)
        await cl.Message(content='系统无应答...').send()
    else:
        await gpt_step(message.content)

    

