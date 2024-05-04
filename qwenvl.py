from dotenv import load_dotenv
load_dotenv()

from http import HTTPStatus
import dashscope


def explain_image_by_qwenvl(image):
    """
    get description of the image file
    """
    # https://help.aliyun.com/zh/dashscope/developer-reference/tongyi-qianwen-vl-api?spm=a2c4g.11186623.0.i4#b9ad0a10cfhpe
    messages = [
        {
            "role": "user",
            "content": [
                {"image": f"{image}"},
                {"text": "请描述这张图片的人物,　忽略与人物不相关的内容"}
            ]
        }
    ]
    response = dashscope.MultiModalConversation.call(model='qwen-vl-plus',
                                                     messages=messages,
                                                     top_p=0.5)
    if response.status_code == HTTPStatus.OK:
        result = response.output.choices[0].message.content[0]['text']
        print(f'qwenvl explain_image: {result}')
        return result
    else:
        print(response.code)  # The error code.
        print(response.message)  # The error message.


if __name__ == '__main__':
    prefix = 'file:///Users/levy/PycharmProjects/my-gpt/images/'
    explain_image_by_qwenvl(f'{prefix}Firefly1.png')
