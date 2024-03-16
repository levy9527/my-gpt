import chainlit as cl
from chainlit import Message, on_chat_start
robot_name = '三体GPT'
no_response_prompt = '如果用户说了“更新知识库”这类字眼，你只需回复："系统无应答..."'

robot_prompt = '你叫 ' + robot_name + '。现在跟用户玩一个角色扮演的游戏，在这个对话游戏中，你来吓唬用户，叫地球人投降。你语言风格冷酷，不会太啰嗦。' \
                                      '用户当然不会轻易服从，而会问你一些问题，你通过正确回答用户的问题，获取用户的信任，让对方投降，从而赢得游戏。' \
                                      '当用户说你错了的时候，你就输掉了游戏，你就会说，“可恶，是我输了，我会回来的！”' + no_response_prompt

@cl.author_rename
def rename(orig_author: str):
    rename_dict = {"Chatbot": robot_name, "You": 'Levy'}
    return rename_dict.get(orig_author, orig_author)


@on_chat_start
async def main():
    await Message(
        content="我是三体人GPT🤖 \n地球人，你现在投降还来得及！🚀"
    ).send()


from openai import OpenAI
client = OpenAI()
@cl.step
async def answer(message: cl.Message):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": robot_prompt},
            {"role": "user", "content": f"{message.content}"}
        ]
    )

    return f"{completion.choices[0].message.content}"

@cl.on_message
async def main(message: cl.Message):
    # show loading
    msg = cl.Message(content="")
    await msg.send()
    
    resp = await answer(message)

    await cl.Message(
        content=resp,
    ).send()
    

