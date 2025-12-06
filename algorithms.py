"""
Algoritma Kütüphanesi
=====================
Sıralama, Arama, Grafik ve Dinamik Programlama Algoritmaları
Her algoritma çalışırken metrik bilgilerini de döndürür.
"""

import random
import time
import sys
import heapq
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

# Recursion limitini artır (derin algoritmalar için)
sys.setrecursionlimit(2000)


@dataclass
class AlgorithmMetrics:
    """Algoritma çalışma metrikleri"""
    comparisons: int = 0
    swaps: int = 0
    iterations: int = 0
    memory_accesses: int = 0
    recursive_calls: int = 0
    operations: int = 0  # Genel işlem sayısı (matris çarpımı vb. için)


# ========================================
# DIVIDE & CONQUER (BÖL VE YÖNET)
# ========================================

def merge_sort(arr: List[int]) -> Tuple[List[int], AlgorithmMetrics]:
    metrics = AlgorithmMetrics()
    
    def merge(left: List[int], right: List[int]) -> List[int]:
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            metrics.comparisons += 1
            metrics.iterations += 1
            metrics.memory_accesses += 2
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
            metrics.memory_accesses += 1
        result.extend(left[i:])
        result.extend(right[j:])
        metrics.memory_accesses += len(left[i:]) + len(right[j:])
        return result
    
    def sort(arr: List[int]) -> List[int]:
        if len(arr) <= 1:
            return arr
        metrics.recursive_calls += 1
        mid = len(arr) // 2
        left = sort(arr[:mid])
        right = sort(arr[mid:])
        return merge(left, right)
    
    result = sort(arr.copy())
    return result, metrics

def quick_sort(arr: List[int]) -> Tuple[List[int], AlgorithmMetrics]:
    arr = arr.copy()
    metrics = AlgorithmMetrics()
    
    def partition(low: int, high: int) -> int:
        pivot = arr[high]
        metrics.memory_accesses += 1
        i = low - 1
        for j in range(low, high):
            metrics.iterations += 1
            metrics.comparisons += 1
            metrics.memory_accesses += 1
            if arr[j] <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
                metrics.swaps += 1
                metrics.memory_accesses += 2
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        metrics.swaps += 1
        metrics.memory_accesses += 2
        return i + 1
    
    def sort(low: int, high: int):
        if low < high:
            metrics.recursive_calls += 1
            pi = partition(low, high)
            sort(low, pi - 1)
            sort(pi + 1, high)
    
    if len(arr) > 0:
        sort(0, len(arr) - 1)
    return arr, metrics

def strassen_matrix_mult(data: List[int]) -> Tuple[List[List[int]], AlgorithmMetrics]:
    """
    Strassen Matris Çarpımı
    Not: Girdi olarak tek bir liste alır, bunu iki kare matrise dönüştürür.
    """
    metrics = AlgorithmMetrics()
    
    # Listeyi kare matris boyutuna uygun hale getir (sqrt(n/2))
    n = len(data)
    size = int((n // 2) ** 0.5)
    if size < 2: size = 2
    
    # İki matris oluştur
    matrix_a = [data[i*size:(i+1)*size] for i in range(size)]
    matrix_b = [data[n//2 + i*size : n//2 + (i+1)*size] for i in range(size)]
    
    # Matris boyutlarını 2'nin kuvvetine tamamla (padding)
    def next_power_of_2(x):
        return 1 if x == 0 else 2**(x - 1).bit_length()
    
    new_size = next_power_of_2(size)
    
    def pad_matrix(M, new_size):
        padded = [[0] * new_size for _ in range(new_size)]
        for i in range(len(M)):
            for j in range(len(M[0])):
                padded[i][j] = M[i][j]
        return padded
    
    A = pad_matrix(matrix_a, new_size)
    B = pad_matrix(matrix_b, new_size)
    
    def add(M1, M2):
        n = len(M1)
        C = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                metrics.operations += 1
                metrics.memory_accesses += 3
                C[i][j] = M1[i][j] + M2[i][j]
        return C

    def subtract(M1, M2):
        n = len(M1)
        C = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                metrics.operations += 1
                metrics.memory_accesses += 3
                C[i][j] = M1[i][j] - M2[i][j]
        return C

    def strassen(A, B):
        n = len(A)
        metrics.recursive_calls += 1
        
        if n <= 64:  # Base case: standart çarpım
            C = [[0] * n for _ in range(n)]
            for i in range(n):
                for k in range(n):
                    for j in range(n):
                        metrics.operations += 2
                        metrics.memory_accesses += 3
                        C[i][j] += A[i][k] * B[k][j]
            return C
        
        mid = n // 2
        A11 = [row[:mid] for row in A[:mid]]
        A12 = [row[mid:] for row in A[:mid]]
        A21 = [row[:mid] for row in A[mid:]]
        A22 = [row[mid:] for row in A[mid:]]
        
        B11 = [row[:mid] for row in B[:mid]]
        B12 = [row[mid:] for row in B[:mid]]
        B21 = [row[:mid] for row in B[mid:]]
        B22 = [row[mid:] for row in B[mid:]]
        
        metrics.memory_accesses += n*n*2  # Bölme maliyeti
        
        M1 = strassen(add(A11, A22), add(B11, B22))
        M2 = strassen(add(A21, A22), B11)
        M3 = strassen(A11, subtract(B12, B22))
        M4 = strassen(A22, subtract(B21, B11))
        M5 = strassen(add(A11, A12), B22)
        M6 = strassen(subtract(A21, A11), add(B11, B12))
        M7 = strassen(subtract(A12, A22), add(B21, B22))
        
        C11 = add(subtract(add(M1, M4), M5), M7)
        C12 = add(M3, M5)
        C21 = add(M2, M4)
        C22 = add(subtract(add(M1, M3), M2), M6)
        
        C = [[0] * n for _ in range(n)]
        for i in range(mid):
            for j in range(mid):
                C[i][j] = C11[i][j]
                C[i][j + mid] = C12[i][j]
                C[i + mid][j] = C21[i][j]
                C[i + mid][j + mid] = C22[i][j]
                metrics.memory_accesses += 4
                
        return C

    result = strassen(A, B)
    return result, metrics


# ========================================
# DYNAMIC PROGRAMMING (DİNAMİK PROGRAMLAMA)
# ========================================

def knapsack_01(data: List[int]) -> Tuple[int, AlgorithmMetrics]:
    """
    0/1 Knapsack Problemi
    Veriyi (değer, ağırlık) çiftlerine böler.
    """
    metrics = AlgorithmMetrics()
    
    n = len(data) // 2
    if n == 0: return 0, metrics
    
    values = data[:n]
    weights = data[n:2*n]
    capacity = sum(weights) // 2  # Toplam ağırlığın yarısı kapasite olsun
    
    # DP tablosu
    K = [[0 for x in range(capacity + 1)] for x in range(n + 1)]
    metrics.memory_accesses += (n + 1) * (capacity + 1)
    
    for i in range(n + 1):
        for w in range(capacity + 1):
            metrics.iterations += 1
            if i == 0 or w == 0:
                K[i][w] = 0
            elif weights[i-1] <= w:
                metrics.comparisons += 1
                metrics.operations += 1
                metrics.memory_accesses += 4
                val1 = values[i-1] + K[i-1][w-weights[i-1]]
                val2 = K[i-1][w]
                K[i][w] = max(val1, val2)
            else:
                metrics.memory_accesses += 2
                K[i][w] = K[i-1][w]
                
    return K[n][capacity], metrics

def floyd_warshall(data: List[int]) -> Tuple[List[List[int]], AlgorithmMetrics]:
    """
    Floyd-Warshall Algoritması
    Veriyi adjacency matrix'e dönüştürür.
    """
    metrics = AlgorithmMetrics()
    
    # Kare matris boyutu
    V = int(len(data) ** 0.5)
    if V < 2: V = 2
    
    # Grafı oluştur (sonsuz değerleri ile)
    INF = 999999
    dist = [[INF] * V for _ in range(V)]
    
    # Veriyi matrise doldur
    idx = 0
    for i in range(V):
        dist[i][i] = 0
        for j in range(V):
            if i != j and idx < len(data):
                # Pozitif ağırlıklar kullan
                weight = abs(data[idx]) % 100 + 1
                dist[i][j] = weight
                idx += 1
                metrics.memory_accesses += 1
    
    # Algoritma
    for k in range(V):
        for i in range(V):
            for j in range(V):
                metrics.iterations += 1
                metrics.memory_accesses += 3
                metrics.comparisons += 1
                
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    metrics.operations += 1
                    metrics.memory_accesses += 1
                    
    return dist, metrics

def bellman_ford(data: List[int]) -> Tuple[List[int], AlgorithmMetrics]:
    """
    Bellman-Ford Algoritması
    """
    metrics = AlgorithmMetrics()
    
    V = int((len(data) / 2) ** 0.5) # Yaklaşık vertex sayısı
    if V < 2: V = 2
    
    # Kenarları oluştur
    edges = []
    for i in range(0, len(data)-2, 3):
        u = abs(data[i]) % V
        v = abs(data[i+1]) % V
        w = data[i+2] % 100  # Negatif olabilir
        edges.append((u, v, w))
        metrics.memory_accesses += 3
    
    if not edges: # Kenar yoksa rastgele oluştur
        for i in range(V):
            edges.append((i, (i+1)%V, 1))
            
    # Başlangıç
    src = 0
    INF = float("Inf")
    dist = [INF] * V
    dist[src] = 0
    metrics.memory_accesses += V
    
    # Gevşetme (Relaxation)
    for _ in range(V - 1):
        metrics.iterations += 1
        for u, v, w in edges:
            metrics.memory_accesses += 3
            metrics.comparisons += 1
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                metrics.operations += 1
                metrics.memory_accesses += 1
                
    # Negatif döngü kontrolü
    for u, v, w in edges:
        metrics.memory_accesses += 3
        if dist[u] != INF and dist[u] + w < dist[v]:
            # Negatif döngü var
            pass
            
    return dist, metrics


# ========================================
# GREEDY ALGORİTMALAR (AÇGÖZLÜ)
# ========================================

def dijkstra(data: List[int]) -> Tuple[List[int], AlgorithmMetrics]:
    """
    Dijkstra Algoritması
    """
    metrics = AlgorithmMetrics()
    
    V = int((len(data) / 2) ** 0.5)
    if V < 2: V = 2
    
    # Adjacency list
    graph = [[] for _ in range(V)]
    for i in range(0, len(data)-2, 3):
        u = abs(data[i]) % V
        v = abs(data[i+1]) % V
        w = abs(data[i+2]) % 100 + 1 # Pozitif ağırlık
        graph[u].append((v, w))
        graph[v].append((u, w)) # Undirected
        metrics.memory_accesses += 1
        
    src = 0
    dist = [float('inf')] * V
    dist[src] = 0
    pq = [(0, src)]
    metrics.memory_accesses += V
    
    while pq:
        metrics.iterations += 1
        d, u = heapq.heappop(pq)
        metrics.operations += 1
        
        if d > dist[u]:
            continue
            
        for v, weight in graph[u]:
            metrics.memory_accesses += 2
            metrics.comparisons += 1
            if dist[u] + weight < dist[v]:
                dist[v] = dist[u] + weight
                heapq.heappush(pq, (dist[v], v))
                metrics.operations += 1
                metrics.memory_accesses += 1
                
    return dist, metrics

def prim_mst(data: List[int]) -> Tuple[int, AlgorithmMetrics]:
    """
    Prim's Minimum Spanning Tree
    """
    metrics = AlgorithmMetrics()
    
    V = int((len(data) / 2) ** 0.5)
    if V < 2: V = 2
    
    # Adjacency matrix
    graph = [[0] * V for _ in range(V)]
    idx = 0
    for i in range(V):
        for j in range(i+1, V):
            if idx < len(data):
                w = abs(data[idx]) % 100 + 1
                graph[i][j] = w
                graph[j][i] = w
                idx += 1
                metrics.memory_accesses += 2
                
    key = [float('inf')] * V
    parent = [None] * V
    key[0] = 0
    mst_set = [False] * V
    
    parent[0] = -1
    
    for _ in range(V):
        metrics.iterations += 1
        
        # Min key bul
        min_val = float('inf')
        min_index = -1
        
        for v in range(V):
            metrics.comparisons += 1
            if key[v] < min_val and not mst_set[v]:
                min_val = key[v]
                min_index = v
                
        u = min_index
        if u == -1: break
        
        mst_set[u] = True
        
        for v in range(V):
            metrics.memory_accesses += 1
            metrics.comparisons += 1
            if graph[u][v] > 0 and not mst_set[v] and key[v] > graph[u][v]:
                key[v] = graph[u][v]
                parent[v] = u
                metrics.memory_accesses += 2
                
    total_weight = sum(k for k in key if k != float('inf'))
    return total_weight, metrics

def huffman_coding(data: List[int]) -> Tuple[Dict, AlgorithmMetrics]:
    """
    Huffman Coding
    Veri frekanslarını kullanarak ağaç oluşturur.
    """
    metrics = AlgorithmMetrics()
    
    # Frekans haritası oluştur (basitçe sayıların tekrarı)
    freq = {}
    for num in data[:100]: # İlk 100 sayıyı karakter gibi düşün
        char = str(num % 26) # A-Z gibi
        freq[char] = freq.get(char, 0) + 1
        metrics.memory_accesses += 1
        metrics.iterations += 1
        
    # Heap oluştur
    heap = [[weight, [sym, ""]] for sym, weight in freq.items()]
    heapq.heapify(heap)
    metrics.operations += len(heap)
    
    while len(heap) > 1:
        metrics.iterations += 1
        lo = heapq.heappop(heap)
        hi = heapq.heappop(heap)
        metrics.operations += 2
        
        for pair in lo[1:]:
            pair[1] = '0' + pair[1]
            metrics.memory_accesses += 1
        for pair in hi[1:]:
            pair[1] = '1' + pair[1]
            metrics.memory_accesses += 1
            
        heapq.heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])
        metrics.operations += 1
        
    return heap[0] if heap else [], metrics


# ========================================
# ALGORİTMA KAYIT DEFTERİ
# ========================================

ALGORITHMS = {
    'divide_conquer': {
        'merge_sort': {
            'func': merge_sort,
            'name': 'Merge Sort',
            'complexity_time': 'O(n log n)',
            'complexity_space': 'O(n)',
            'category': 'divide_conquer'
        },
        'quick_sort': {
            'func': quick_sort,
            'name': 'Quick Sort',
            'complexity_time': 'O(n log n)',
            'complexity_space': 'O(log n)',
            'category': 'divide_conquer'
        },
        'strassen': {
            'func': strassen_matrix_mult,
            'name': 'Strassen Matrix Mult.',
            'complexity_time': 'O(n^2.81)',
            'complexity_space': 'O(n^2)',
            'category': 'matrix'
        }
    },
    'dynamic_programming': {
        'knapsack': {
            'func': knapsack_01,
            'name': '0/1 Knapsack',
            'complexity_time': 'O(n*W)',
            'complexity_space': 'O(n*W)',
            'category': 'optimization'
        },
        'floyd_warshall': {
            'func': floyd_warshall,
            'name': 'Floyd-Warshall',
            'complexity_time': 'O(n³)',
            'complexity_space': 'O(n²)',
            'category': 'graph'
        },
        'bellman_ford': {
            'func': bellman_ford,
            'name': 'Bellman-Ford',
            'complexity_time': 'O(V*E)',
            'complexity_space': 'O(V)',
            'category': 'graph'
        }
    },
    'greedy': {
        'dijkstra': {
            'func': dijkstra,
            'name': 'Dijkstra',
            'complexity_time': 'O(V^2)',
            'complexity_space': 'O(V)',
            'category': 'graph'
        },
        'prim': {
            'func': prim_mst,
            'name': "Prim's MST",
            'complexity_time': 'O(V^2)',
            'complexity_space': 'O(V)',
            'category': 'graph'
        },
        'huffman': {
            'func': huffman_coding,
            'name': 'Huffman Coding',
            'complexity_time': 'O(n log n)',
            'complexity_space': 'O(n)',
            'category': 'compression'
        }
    }
}
