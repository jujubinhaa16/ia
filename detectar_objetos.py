import torch
from collections import Counter

# Carregar o modelo YOLOv5
modelo = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)


def contar_objetos(frame):
    # Detectar objetos na imagem
    resultados = modelo(frame)

    # Extrair as classes detectadas
    classes_detectadas = resultados.pandas().xyxy[0]['name']

    # Contar a quantidade de cada produto
    contagem_produtos = Counter(classes_detectadas)

    return dict(contagem_produtos)
