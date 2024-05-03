import logging

system_prompt = """You're a chatbot. You need to classify user intention based on user input,
return either `IMAGE_SEARCH` or `OTHER`

If the user are requesting image, then return `IMAGE_SEARCH`, otherwise, just return `OTHER`


examples:
input:
- 来张正面照
- 看看他的 cosplay
- 有没有相关的 coser 照片
return IMAGE_SEARCH

input:
- 这是谁
- 你好啊
return OTHER
"""

from openai import OpenAI


def is_search_image(message):
  client = OpenAI()
  completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
      {"role": "system", "content": system_prompt},
      {
        "role": "user",
        "content": f"{message}",
      },
    ],
  )
  result = completion.choices[0].message
  logging.info(f'is_search_image: {result}')
  return True if str(result.content) == 'IMAGE_SEARCH' else False

