import logging

import chromadb

client = chromadb.Client()
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
from chromadb.utils.data_loaders import ImageLoader

embedding_function = OpenCLIPEmbeddingFunction()
image_loader = ImageLoader()

collection = client.create_collection(
    name='multimodal_collection',
    embedding_function=embedding_function,
    data_loader=image_loader)

prefix = './images/'
images = ['Aventurine1.png', 'Aventurine2.png', 'Aventurine3.png', 'Aventurine4.png', ]
documents = ['游戏人物，男性角色，砂金。背面照，星穹铁道游戏画面', '游戏人物，男性角色，砂金。正面照，星穹铁道游戏画面', '砂金。cosplay照片，模糊',
             '砂金。cosplay照片，清晰,　带帽子，有眼镜']

uris = [prefix + image for image in images]
ids = [str(i) for i in range(len(images))]

collection.add(ids=ids, uris=uris, documents=documents)


def query_image_by_uri(uri, n_results = 1):
    '''
    search similar image by image uri, it can help you explain the image
    '''
    retrieved = collection.query(query_uris=[uri], include=['uris', 'documents',
                                                            'distances'
                                                            ],
                                 n_results=n_results)
    return retrieved

def query_image_by_text(text, n_results = 1):
    '''
    search similar image by image description
    该方法不适合 function calling + chat, 主要还是显示的问题：
    返回的uri数据，AI不能直接显示图片。而原有的结构化数据，经过chat后，又变成非结构化了
    '''
    retrieved = collection.query(query_texts=[text], include=['uris', 'documents',
                                                              'distances'
                                                              ], n_results=n_results)
    logging.info(f'query_image_by_text: {retrieved}')
    return retrieved


if __name__ == '__main__':
    # retrieved = collection.query(query_texts=["砂金正面照"], include=['uris'], n_results=1)
    retrieved = collection.query(query_uris=["./images/Aventurine5.png"], include=['uris', 'documents', 'distances'],
                                 n_results=1)
    
    print(retrieved)


