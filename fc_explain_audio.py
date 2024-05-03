import logging

from openai import OpenAI
client = OpenAI()

system_prompt = '''
You're a good writer to beautify text based on the input.
You'll receive a long text with a short text(this can be a summary or a note written by human).
You should combine two text into one, which will be used as the description for a scene or music.
Please speak Chinese.
'''


settings = {
  "model": "gpt-3.5-turbo-1106",
  "temperature": 0,
}
def explain_audio(ai_text, human_text):
  completion = client.chat.completions.create(
    stream=True,
    **settings,
    messages=[
      {"role": "system", "content": system_prompt},
      {
        "role": "user",
        "content": f"long text: {ai_text} \n short text: {human_text}",
      },
    ],
  )
  # result = completion.choices[0].message.content
  # logging.info(f'explain_audio: {result}' )
  # return result
  
  # stream
  return completion
  # for chunk in stream:
  #     if chunk.choices[0].delta.content is not None:
  #         print(chunk.choices[0].delta.content, end="")

