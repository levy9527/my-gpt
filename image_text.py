import base64

from dotenv import load_dotenv

from search import search_answer

load_dotenv()
from openai import OpenAI
client = OpenAI()

def image2text(img_url: str) -> str:
  '''get description of an image'''
  return '这是真理医生'
  is_online_file = False
  if img_url.startswith('http'): is_online_file = True
  
  def encode_image(image_path):
    with open(image_path, "rb") as image_file:
      return base64.b64encode(image_file.read()).decode('utf-8')
  
  response = client.chat.completions.create(
    model="gpt-4-vision-preview",
    messages=[
      {
        "role": "user",
        "content": [
          {"type": "text", "text": "Describe the image as an alternative text, response with Chinese"},
          {
            "type": "image_url",
            "image_url": {
              "url": img_url if is_online_file else f"data:image/jpeg;base64,{encode_image(img_url)}",
            },
          },
        ],
      }
    ],
    max_tokens=512,
  )
  result = response.choices[0].message.content
  print(result)
  
  return result

if __name__ == '__main__':
  # "https://patchwiki.biligame.com/images/sr/4/47/on39aglim2lxrb766mxk46iwwn0tab3.jpg",
  image2text('/Users/levy/Pictures/dr-ratio.jpeg')

robot_name = '三体人GPT'
opening_prompt = "我是三体人GPT🤖 \n你可以上传图片🖼"
system_prompt = '你叫 ' + robot_name + '。现在跟用户玩一个问答游戏，在这个对话游戏中，你要使用恰当的工具，来应对用户提的问题' \
                                       '请尽量让对话变得生动、有趣。你的目标是，通过搜索获得最新、最贴切的与游戏相关的回答，从而在正确回答后，让用户对你的能力发出赞叹。'
import chainlit as cl
settings = {
  "model": "gpt-3.5-turbo-1106",
  "temperature": 0,
}


@cl.step(type="llm")
async def gpt_step(message_content):
  print(message_content)
  # show loading
  msg = cl.Message(content="")
  await msg.send()
  
  from llama_index.llms.openai import OpenAI
  llm = OpenAI(**settings)
  
  from llama_index.agent.openai import OpenAIAgent
  from llama_index.core.tools import FunctionTool
  tool_image2text = FunctionTool.from_defaults(fn=image2text)
  tool_search_answer = FunctionTool.from_defaults(fn=search_answer)
  tools = [tool_image2text, tool_search_answer]
  
  agent = OpenAIAgent.from_tools(tools, llm=llm, verbose=True, system_prompt=system_prompt)
  
  resp = agent.stream_chat(message_content)
  
  for chunk in resp.response_gen:
    await msg.stream_token(chunk)


@cl.on_chat_start
async def start():
  msg = cl.Message(content="")
  await msg.send()
  await cl.sleep(0.5)
  for chunk in opening_prompt:
    await msg.stream_token(chunk)


@cl.on_message
async def main(message: cl.Message):
  for element in message.elements:
    if isinstance(element, cl.Image):
      print("An image is found:", element.path)
  #await gpt_step(message.content)
