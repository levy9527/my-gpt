import logging
logging.basicConfig(level=logging.INFO)
import os
from dotenv import load_dotenv
load_dotenv()

import chromadb

client = chromadb.Client()
import chromadb.utils.embedding_functions as embedding_functions

robin_collection = None

logging.basicConfig(level=logging.INFO)

def init_Robin():
  documents = [
    '''图中是一位蓝发的女性动漫角色，她有着绿色的眼睛和白色的皮肤。她的头发被编成了一个侧边辫子，并且在脑后挽了一个优雅而简洁的发型。这位女士穿着一件紫色的衣服，在胸部的位置有一条金色装饰带作为点缀。
此外，画面左侧还有一位男性角色相伴，他留着蓝色长发并身穿深色服装。两位角色都处于室内环境中，背景看起来像是夜晚的城市景色或是一处现代建筑内部。整个场景给人一种温馨而又神秘的感觉''',
    '''图中是一位蓝发少女，她有着长长的头发和一双明亮的绿色眼睛。她的穿着非常华丽：身着一件蓝色长裙，并且在领口处有一条黑色的丝带作为装饰；此外，在脖子上还戴着一条金色项链，上面镶嵌着一颗颗小珍珠。更引人注目的是，她在胸前佩戴了一枚大大的金色徽章，显得既威严又高贵。总的来说，这位角色给人一种优雅而神秘的感觉。''',
    '''图中是一位蓝发少女，她有着长长的银色头发和蓝色的眼睛。她的耳朵上戴着一只精美的耳环，并且脖子上还挂着一条项链。此时的她正闭着眼睛，似乎在沉思或者休息之中。''',
    '''图中是一位银发女子，她身穿黑色西装和白色衬衫。她的头发被蓝色的光芒环绕着，并且在身后形成了一对类似翅膀的东西。她闭着眼睛，左手向前伸展，右手向后背到腰间的位置弯曲成半握拳的样子。整体上给人一种优雅而神秘的感觉。''',
  ]
  audio_dir = './audio/'
  image_dir = './images/'
  metadatas = [
    {'mp3': f'{audio_dir}night.MP3', 'desc': '知更鸟，坐在车上。对应歌词：这窗外夜色流光溢彩'},
    {'mp3': f'{audio_dir}welcome.MP3', 'desc': '知更鸟，战斗场景，释放终结技, 效果：全队拉条。玩家不禁评论：知更鸟小姐，带我们再冲一次吧！。对应歌曲名：welcome to my world'},
    {'mp3': f'{audio_dir}heart.MP3', 'desc': '知更鸟，死亡场面。对应歌曲名：使一颗心免于哀伤'},
    {'mp3': f'{audio_dir}heart.MP3', 'desc': '流萤，死亡场面。对应歌曲名：使一颗心免于哀伤', 'image': f'{image_dir}Firefly.png'},
  ]
  ids = [str(i) for i in range(len(documents))]
  
  openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.environ['OPENAI_API_KEY'],
    api_base=os.environ['OPENAI_API_BASE'],
    model_name="text-embedding-3-small",
  )
  global robin_collection
  robin_collection = client.create_collection(name="robin_collection", embedding_function=openai_ef)
  
  robin_collection.add(ids=ids, documents=documents, metadatas=metadatas)
  logging.info('init robin done')
  
def query_audio_by_text(text, n_results=1):
  '''
  search similar audio by description
  '''
  retrieved = robin_collection.query(query_texts=[text], include=['documents',
                                                            'distances', 'metadatas'
                                                            ], n_results=n_results)
  logging.info(f'query_audio_by_text: {retrieved}')
  return retrieved


if __name__ == '__main__':
    init_Robin()
    query_audio_by_text('这窗外夜色流光溢彩')
