import logging

from search import search_answer

logging.basicConfig(level=logging.INFO)

from dotenv import load_dotenv

import fc_explain_audio
import qwenvl

load_dotenv()
from openai import OpenAI
client = OpenAI()

from chroma_robin import init_Robin, query_audio_by_text, query_by_text

init_Robin()


robot_name = '三体人GPT'
opening_prompt = "我是三体人GPT🤖 \n我懂得了欣赏音乐，现在是知更鸟的粉丝🎶"
system_prompt = '你叫 ' + robot_name + '。现在跟用户玩进行一个对话，在这个对话中，所有内容都与《崩坏：星穹铁道》这个游戏有关。' \
                                       '请根据上下文或使用恰当的工具，获得更多的信息，以便更好的理解用户。' \
                                       '用户会与你讨论游戏人物、音乐、剧情、心理感受等话题，你要能照顾对方的感受，回应对方的情绪。' \
                                       '对方有时会说的比较少，你最好能直接猜出对方的想法，这才能给对方惊喜，让用户觉得你很懂他。' \
                                       '请尽量让对话变得生动、有活力，展示你的共情能力。同时简洁，不要啰嗦。如果用户夸奖你，跟你开玩笑，请深度幽默地回应。'
import chainlit as cl
settings = {
  # "model": "gpt-3.5-turbo",
  "model": "gpt-3.5-turbo-1106",
  "temperature": 0,
}

from llama_index.llms.openai import OpenAI
llm = OpenAI(**settings)

from llama_index.agent.openai import OpenAIAgent
from llama_index.core.tools import FunctionTool

tool_search = FunctionTool.from_defaults(fn=search_answer)
tool_explain_img = FunctionTool.from_defaults(fn=query_by_text)
tools = [
  # search_answer,
  tool_explain_img
]

chat_history = []


@cl.step(type="llm")
async def chat(message_content):
  # show loading
  msg = cl.Message(content="", elements=[], author=robot_name)
  await msg.send()
  
  agent = OpenAIAgent.from_tools(tools, llm=llm, verbose=True, system_prompt=system_prompt, chat_history=chat_history)
  resp = agent.stream_chat(message_content,
                           # chat_history=chat_history,
                           # tool_choice="query_by_text"
                           )
  
  for chunk in resp.response_gen:
    await msg.stream_token(chunk)
    
  # 暂特殊不处理 agent 的逻辑，为演示，这里先写死了。
  if '另一个' in message_content:
    result = query_by_text(text='使一颗心免于哀伤', exclude_keyword='知更鸟')
    images = result['metadatas'][0][0]['images'].split(';')
    desc = result['metadatas'][0][0]['desc'].split(';')
    
    elements = []
    for i,path in enumerate(images):
      elements.append(
        cl.Image(path=path, display="inline", name=desc[i])
      )
    
    msg.elements = [elements[0]]
    await msg.update()
  
    await cl.sleep(0.5)
    image = cl.Message(content="", elements=[elements[1]], author=robot_name)
    await image.send()


@cl.on_message
async def main(message: cl.Message):
  images = []
  for element in message.elements:
    if isinstance(element, cl.Image):
      print("An image is found:", element.path)
      images.append(element.path)
      
  if len(images):
    msg = cl.Message(content="", author=robot_name)
    await msg.send()
    
    text = qwenvl.explain_image_by_qwenvl(images[0])
    
    result = query_audio_by_text(text)
    content = result['metadatas'][0][0]['desc']
    audio_element = cl.Audio(path=result['metadatas'][0][0]['mp3'], name=content, display="inline")
    msg.elements = [audio_element]
    await msg.update()
    
    # explain = cl.Message(content="", author=robot_name)
    # stream = fc_explain_audio.explain_audio(ai_text=text, human_text=result['metadatas'][0][0]['desc'])
    
    # content = []
    # for chunk in result['documents'][0][0]:
      # if chunk.choices[0].delta.content is not None:
        # data = chunk.choices[0].delta.content
        # content.append(chunk)
        # await explain.stream_token(chunk)
      
    from llama_index.core.types import ChatMessage, MessageRole
    chat_history.append(ChatMessage(role = MessageRole.ASSISTANT, content = content))
    return
  
  await chat(message.content)

@cl.on_chat_start
async def start():
  msg = cl.Message(content="")
  await msg.send()
  await cl.sleep(0.5)
  for chunk in opening_prompt:
    await msg.stream_token(chunk)


