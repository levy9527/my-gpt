import logging
logging.basicConfig(level=logging.INFO)

from dotenv import load_dotenv

import fc_explain_audio
import qwenvl

load_dotenv()
from openai import OpenAI
client = OpenAI()

from chroma_robin import init_Robin, query_audio_by_text
init_Robin()


robot_name = '三体人GPT'
opening_prompt = "我是三体人GPT🤖 \n我懂得了欣赏音乐，现在是知更鸟的粉丝🎶"
system_prompt = '你叫 ' + robot_name + '。现在跟用户玩一个相关的问答游戏，在这个对话游戏中，所有内容都与《崩坏：星穹铁道》这个游戏有关。请根据上下文或使用恰当的工具，来应对用户提的问题' \
                                       '你需要根据情况来处理以下情况：用户有可能问纯文字问题，也有可能会在问题中带上图片，图片格式为：uri: xxx' \
                                       '请尽量让对话变得生动、有趣。你的目标是，通过搜索获得最新、最贴切的与游戏相关的回答，从而在正确回答后，让用户对你的能力发出赞叹。'
import chainlit as cl
settings = {
  "model": "gpt-3.5-turbo-1106",
  "temperature": 0,
}

from llama_index.llms.openai import OpenAI
llm = OpenAI(**settings)

from llama_index.agent.openai import OpenAIAgent
from llama_index.core.tools import FunctionTool

tool_explain_img = FunctionTool.from_defaults(fn=query_audio_by_text)
tools = [tool_explain_img]

agent = OpenAIAgent.from_tools(tools, llm=llm, verbose=True, system_prompt=system_prompt)



@cl.step(type="llm")
async def gpt_step(message_content, images):
  logging.info(message_content, images)
  
  if images:
    message_content += f'\n图片相关信息: uri: {images[0]}'
  
  # show loading
  msg = cl.Message(content="", elements=[], author=robot_name)
  await msg.send()
  
  resp = agent.stream_chat(message_content)
  
  for chunk in resp.response_gen:
    await msg.stream_token(chunk)


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
    audio_element = cl.Audio(path=result['metadatas'][0][0]['mp3'], display="inline")
    msg.elements = [audio_element]
    await msg.update()
    
    msg = cl.Message(content="")
    await msg.send()
    stream = fc_explain_audio.explain_audio(ai_text=text, human_text=result['metadatas'][0][0]['desc'])
    
    for chunk in stream:
      if chunk.choices[0].delta.content is not None:
        await msg.stream_token(chunk.choices[0].delta.content)
    return
  
  await gpt_step(message.content, images)

@cl.on_chat_start
async def start():
  msg = cl.Message(content="")
  await msg.send()
  await cl.sleep(0.5)
  for chunk in opening_prompt:
    await msg.stream_token(chunk)


