# assets/gesture_classifier.py
"""Gesture Classifier

Este módulo contém a lógica de classificação de gestos a partir dos 21 pontos
(x, y) fornecidos pelo HuskyLens. O algoritmo básico utiliza a distância
entre pontos-chave para distinguir entre "palm" (mão aberta), "fist"
(punho fechado) e "victory" (sinal de vitória).

A implementação aqui é um placeholder simples que pode ser refinado com
modelos de machine‑learning ou regras mais avançadas.
"""

from typing import List, Tuple

# Tipos de retorno esperados
GESTURE_PALM = "palm"
GESTURE_FIST = "fist"
GESTURE_VICTORY = "victory"
GESTURE_UNKNOWN = "unknown"

def _centroid(points: List[Tuple[int, int]]) -> Tuple[float, float]:
    """Calcula o centroide (média) dos pontos."""
    if not points:
        return 0.0, 0.0
    xs, ys = zip(*points)
    return sum(xs) / len(xs), sum(ys) / len(ys)

def _bounding_box_area(points: List[Tuple[int, int]]) -> float:
    """Retorna a área do retângulo que envolve todos os pontos."""
    xs, ys = zip(*points)
    width = max(xs) - min(xs)
    height = max(ys) - min(ys)
    return width * height

def classify_gesture(points: List[Tuple[int, int]]) -> str:
    """Classifica o gesto com base em heurísticas simples.

    - **Palm**: área de bounding box grande e distância média ao centroide
      acima de um limiar.
    - **Fist**: área pequena e pontos concentrados.
    - **Victory**: padrão de dois dedos separados – detectado quando há
      duas sub‑regiões de alta distância dentro da caixa.
    """
    if not points or len(points) != 21:
        return GESTURE_UNKNOWN

    area = _bounding_box_area(points)
    cx, cy = _centroid(points)
    # Distância média ao centroide
    avg_dist = sum(((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 for x, y in points) / len(points)

    # Heurísticas (valores arbitrários – ajustar conforme teste real)
    if area > 2000 and avg_dist > 30:
        return GESTURE_PALM
    if area < 800 and avg_dist < 15:
        return GESTURE_FIST
    # Detectar "victory" – simplificado: presença de dois picos de distância
    # aqui usamos um critério de variação de y entre pontos extremos
    ys = [y for _, y in points]
    if max(ys) - min(ys) > 80:
        return GESTURE_VICTORY
    return GESTURE_UNKNOWN
