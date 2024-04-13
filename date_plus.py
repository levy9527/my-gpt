import chainlit as cl
from chainlit import on_chat_start

import fc_date

robot_name = '三体人GPT'
opening_prompt = "我是三体人GPT🤖 \n我可以回答任何有关时间的问题。⏳"

system_prompt = '你叫 ' + robot_name + '。为了正确回答时间相关的问题，你需要使用工具：先计算时间距离，再输出格式回答。'


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
    
    tool_formatted_date = FunctionTool.from_defaults(fn=fc_date.get_formatted_date)
    tool_day_distance = FunctionTool.from_defaults(fn=fc_date.get_date_distance)
    tools = [tool_day_distance, tool_formatted_date]

    agent = OpenAIAgent.from_tools(tools, llm=llm, verbose=True, system_prompt=system_prompt)

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


@cl.on_message
async def main(message: cl.Message):
    await gpt_step(message.content)

    

