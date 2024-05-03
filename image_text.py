import base64
from dotenv import load_dotenv

import fc_classify
from search import search_answer

load_dotenv()
from openai import OpenAI
client = OpenAI()

from chroma_multi_modal import query_image_by_uri, query_image_by_text, init_Aventurine
init_Aventurine()


# deprecated, 理由：太贵
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

robot_name = '三体人GPT'
opening_prompt = "我是三体人GPT🤖 \n我现在已经懂得了欣赏图片🖼"
system_prompt = '你叫 ' + robot_name + '。现在跟用户玩一个图片相关的问答游戏，在这个对话游戏中，所有内容都与《崩坏：星穹铁道》这个游戏有关。请根据上下文或使用恰当的工具，来应对用户提的问题' \
                                       '如果用户请求解释图片或其问题带有图片的相关信息，格式为：uri: xxx' \
                                       '如果用户请求返回图片，说明你需要根据工具进行图片搜索' \
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

# tool_image2text = FunctionTool.from_defaults(fn=image2text)
tool_search_answer = FunctionTool.from_defaults(fn=search_answer)
# tool_search_img = FunctionTool.from_defaults(fn=query_image_by_text, return_direct=True)
tool_explain_img = FunctionTool.from_defaults(fn=query_image_by_uri)
tools = [tool_search_answer, tool_explain_img]

# chat_history = []
agent = OpenAIAgent.from_tools(tools, llm=llm, verbose=True, system_prompt=system_prompt,
                               # chat_history=chat_history
                               )


@cl.step(type="llm")
async def gpt_step(message_content, images):
  print(message_content, images)
  # image_element = cl.Image(path=img_infos[0]['uri'], name=img_infos[0]['text'], display="inline")
  
  # if len(img_infos):
  #   message_content += f'\n图片相关信息: ```text: {img_infos[0]["text"]}, uri: {img_infos[0]["uri"]}```'
  if images:
    message_content += f'\n图片相关信息: uri: {images[0]}'
  
  # show loading
  msg = cl.Message(content="", elements=[])
  await msg.send()
  
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
  # img2text
  image_infos = []
  if fc_classify.is_search_image(message.content):
    # show loading
    msg = cl.Message(content="", elements=[])
    await msg.send()
    
    resp = query_image_by_text(message.content)
    image_element = cl.Image(path=resp['uris'][0][0], name=resp['documents'][0][0], display="inline")
    msg.elements = [image_element]
    await msg.update()
    return
    
  
  images = []
  for element in message.elements:
    if isinstance(element, cl.Image):
      print("An image is found:", element.path)
      images.append(element.path)
      # result = query_image_by_uri(element.path)
      # image_infos.append(
      #   {
      #     'text': result['documents'][0][0],
      #     'uri': result['uris'][0][0],
      #   }
      # )
      # print(result)
      
  await gpt_step(message.content, images)
  
if __name__ == '__main__':
  # "https://patchwiki.biligame.com/images/sr/4/47/on39aglim2lxrb766mxk46iwwn0tab3.jpg",
  image2text('/Users/levy/Pictures/dr-ratio.jpeg')

