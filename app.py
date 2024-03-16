import chainlit as cl


@cl.on_message
async def main(message: cl.Message):
    # Your custom logic goes here...

    # Send a response back to the user
    from openai import OpenAI
    client = OpenAI()
    
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are a helpful assistant, try your best to answer user's question"},
            {"role": "user", "content": f"{message.content}"}
        ]
    )
    
    await cl.Message(
        content=f"{completion.choices[0].message}",
    ).send()
    

