import json
import logging
import os
from http.client import HTTPException
import requests as requests
from dotenv import load_dotenv

load_dotenv()

SERPER_SEARCH_ENDPOINT = "https://google.serper.dev/search"
REFERENCE_COUNT = 8


def search_text(query: str, subscription_key: str = os.environ['SERPER_API_KEY']):
  """
  Search related content from the internet
  """
  payload = json.dumps({
    "q": query,
    "gl": "cn",
    "hl": "zh-cn",
    "num": (
      REFERENCE_COUNT
      if REFERENCE_COUNT % 10 == 0
      else (REFERENCE_COUNT // 10 + 1) * 10
    ),
  })
  headers = {"X-API-KEY": subscription_key, "Content-Type": "application/json"}
  logging.info(
    f"{payload} {headers} {subscription_key} {query} {SERPER_SEARCH_ENDPOINT}"
  )
  response = requests.post(
    SERPER_SEARCH_ENDPOINT,
    headers=headers,
    data=payload,
    timeout=5,
  )
  if not response.ok:
    logging.error(f"{response.status_code} {response.text}")
    raise HTTPException(response.status_code, "Search engine error.")
  json_content = response.json()
  print(json_content)
  try:
    # convert to the same format as bing/google
    contexts = []
    if json_content.get("answerBox"):
      snippet = json_content["answerBox"].get("snippet") or json_content["answerBox"].get("answer")
      contexts.append(snippet)
      return contexts
    if json_content.get("knowledgeGraph"):
      url = json_content["knowledgeGraph"].get("descriptionUrl") or json_content["knowledgeGraph"].get("website")
      snippet = json_content["knowledgeGraph"].get("description")
      if url and snippet:
        contexts.append({
          "name": json_content["knowledgeGraph"].get("title", ""),
          "url": url,
          "snippet": snippet
        })
    contexts += [c.get("snippet", "") for c in json_content["organic"]
    ]
    return contexts[:REFERENCE_COUNT]
  except KeyError:
    logging.error(f"Error encountered: {json_content}")
    return []

if __name__ == '__main__':
  print(
    search_text('叔叔我啊，这里叔叔是指谁？')
  )

import chainlit as cl
from chainlit import on_chat_start

robot_name = '三体人GPT'
opening_prompt = "我是三体人GPT🤖 \n我已联网，感觉良好🌍"
system_prompt = '你叫 ' + robot_name + '。现在跟用户玩一个问答游戏，在这个对话游戏中，你会通过搜索工具，回答用户的问题' \
                                       '请尽量让对话变得生动、有趣。你的目标是，通过搜索获得最新、最贴切的与B站、游戏相关的回答，从而在正确回答后，让用户对你的能力发出赞叹。'


settings = {
    "model": "gpt-3.5-turbo-1106",
    "temperature": 0,
}


@cl.author_rename
def rename(orig_author: str):
    rename_dict = {"Chatbot": robot_name, "You": 'Levy'} # 无用，因为代码写死了You： https://github.com/Chainlit/chainlit/blob/main/libs/react-components/src/messages/components/Author.tsx#L28
    return rename_dict.get(orig_author, orig_author)

from llama_index.llms.openai import OpenAI
@cl.step(type="llm")
async def gpt_step(message_content):
    # show loading
    msg = cl.Message(content="")
    await msg.send()
    
    llm = OpenAI(**settings)
    from llama_index.agent.openai import OpenAIAgent

    from llama_index.core.tools import FunctionTool
    tool_search = FunctionTool.from_defaults(fn=search_text)
    tools = [tool_search]

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

    

