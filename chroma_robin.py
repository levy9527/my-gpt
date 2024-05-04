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
    '''图中是一位蓝发的女性动漫角色知更鸟，她有着绿色的眼睛和白色的皮肤。她的头发被编成了一个侧边辫子，并且在脑后挽了一个优雅而简洁的发型。这位女士穿着一件紫色的衣服，在胸部的位置有一条金色装饰带作为点缀。 此外，画面左侧还有一位男性角色相伴，他留着蓝色长发并身穿深色服装。两位角色都处于室内环境中，背景看起来像是夜晚的城市景色或是一处现代建筑内部。整个场景给人一种温馨而又神秘的感觉''',
    '''图中是一位蓝发少女知更鸟，她有着长长的头发和一双明亮的绿色眼睛。她的穿着非常华丽：身着一件蓝色长裙，并且在领口处有一条黑色的丝带作为装饰；此外，在脖子上还戴着一条金色项链，上面镶嵌着一颗颗小珍珠。更引人注目的是，她在胸前佩戴了一枚大大的金色徽章，显得既威严又高贵。总的来说，这位角色给人一种优雅而神秘的感觉。''',
    '''图中是一位蓝发少女知更鸟，她有着长长的银色头发和蓝色的眼睛。她的耳朵上戴着一只精美的耳环，并且脖子上还挂着一条项链。此时的她正闭着眼睛，似乎在沉思或者休息之中。''',
    '''图中是一位银发女子流萤，她身穿黑色西装和白色衬衫。她的头发被蓝色的光芒环绕着，并且在身后形成了一对类似翅膀的东西。她闭着眼睛，左手向前伸展，右手向后背到腰间的位置弯曲成半握拳的样子。整体上给人一种优雅而神秘的感觉。''',
  ]
  audio_dir = './audio/'
  image_dir = './images/'
  metadatas = [
    {'mp3': f'{audio_dir}night.MP3', 'desc': '''夜幕低垂，城市的灯火如星辰闪烁。知更鸟举杯靠在窗边，如夜的精灵，绿眸深邃，紫衣轻裹，金色的装饰带在灯光下熠熠生辉。 身旁，蓝发的他，默默守护，与她共赏这流光溢彩的不眠之夜。《不眠之夜》的旋律在空气中缓缓流淌，知更鸟的歌声与之和鸣，编织出一段温柔的旋律。'''},
    {'mp3': f'{audio_dir}welcome.MP3', 'desc': '''她身着一件紫色的深V领露肩装，外披一件黑色的披风，银白色的项链在她的颈间熠熠生辉，衣袖的银边装饰增添了几分高贵的气息。她闭着眼睛，面带微笑，左手轻握着一把竖琴，右手在空中划出优雅的弧线，仿佛在弹奏着一曲只属于她的旋律。 当战斗的号角响起，知更鸟，释放终结技，如同在星空中绽放的绚烂光芒，每一个音符都转化为她的力量。在这《Welcome to my world》的激昂旋律中，她邀请所有人进入她的世界，感受她的音乐，她的战斗，和她的梦想。'''},
    {'mp3': f'{audio_dir}heart.MP3', 'desc': '''在一片宁静之中，一位蓝发少女轻闭双眼，仿佛沉浸在深深的沉思或宁静的休息中。然而，这个场景并非只是平静的休憩，而是一个关于告别与哀伤的故事。知更鸟，这个常常与春天和新生联系在一起的生灵，在这里却面临着死亡的场面。它象征着生命的脆弱和美丽，以及我们对逝去之物的深深怀念。“是谁杀死了知更鸟？”　随着《使一颗心免于哀伤》的旋律缓缓响起，每一个音符都像是在探寻真相，又像是在抚慰受伤的心灵。音乐中蕴含的力量，试图驱散迷雾，揭开隐藏在夜色中的谜团。'''},
    {'mp3': f'{audio_dir}heart.MP3', 'desc': '在“秘密基地”的静谧角落，流萤与星留下了最后的合影;流萤被“何物朝向死亡”击杀场面',
     'images': f'{image_dir}Firefly1.png;{image_dir}Firefly2.png', 'image_captions': '在“秘密基地”的静谧角落，流萤与星留下了最后的合影。流萤，银发如瀑布般泻下，高马尾束起，黑色菱形发带映衬着她的神秘。她身着深蓝与纯白，粉色蝴蝶结轻轻系在领间，如同她生命中最后的温柔。星，灰发轻垂，金色眼眸里藏着坚毅的光芒。她以黄色衬衫搭配黑红外套，牛仔裤与手套彰显着她的不羁。两人并肩而立，笑容中带着青春的无邪和对未知的憧憬。然而，命运的阴影已悄然笼罩，流萤的离去，成为了星心中不可触碰的痛。如今，回望这张照片，是对流萤的深情怀念，也是对那段逝去时光的哀婉颂歌。《使一颗心免于哀伤》的旋律，如同夜风中飘荡的萤火，温柔地抚慰着每一颗因失去而哀伤的心。;夜色深沉，一位银发女子，本应是优雅的化身，此刻却在高空中无力坠落。她的身体被刺穿，血液在夜风中几乎看不见，只有那件黑色西装上隐约的深色斑点，透露出悲剧的真相。她的头发依旧被蓝色光芒环绕，但那对光芒形成的翅膀不再是守护的象征，而是怪物的伪装。女子闭着眼睛，她的左手无力地向前伸展，右手半握成拳，背到腰间，这个姿态不再是力量的象征，而是生命即将消逝的无奈。流萤在她的周围飞舞，它们的光芒在夜空中逐渐黯淡，似乎在为这位女子的坠落哀悼。《使一颗心免于哀伤》的旋律在此刻响起，每一个音符都充满了悲痛和哀伤，它们试图抚慰那些因失去而感到痛苦的心，却也揭露了真相的残酷。大家震惊于这突如其来的转折，不敢相信，这位女子的生命，竟然就这样走向了终结。'
     },
  ]
  ids = [str(i) for i in range(len(documents))]
  
  openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.environ['MY_OPENAI_API_KEY'],
    api_base=os.environ['MY_OPENAI_API_BASE'],
    model_name="text-embedding-ada-002",
  )
  global robin_collection
  robin_collection = client.create_collection(name="robin_collection", embedding_function=openai_ef)
  
  robin_collection.add(ids=ids, documents=documents, metadatas=metadatas)
  logging.info('init robin done')
  
def query_audio_by_text(text, n_results=1):
  '''
  search similar audio by description
  '''
  retrieved = robin_collection.query(query_texts=[text], include=['documents', 'distances', 'metadatas'], n_results=n_results)
  logging.info(f'query_audio_by_text: {retrieved}')
  return retrieved

def query_by_text(text, exclude_keyword :str = 'nothing', n_results = 1):
  '''
  search related content by description, it's optional to use keyword to exclude some data
  invoke example: if the user say a_song which is related to a_person, reminds him another thing, but don't mention what another thing is.
  you can invoke this function like query_by_text(text=a_song, exclude_keyword=a_person)
  '''
  retrieved = robin_collection.query(query_texts=[text], where_document={"$not_contains": exclude_keyword}, n_results=n_results)
  logging.info(f'query_by_text: {retrieved}')
  return retrieved


if __name__ == '__main__':
    init_Robin()
    # query_audio_by_text('这窗外夜色流光溢彩')
    query_by_text(text='使一颗心免于哀伤', exclude_keyword='知更鸟')
