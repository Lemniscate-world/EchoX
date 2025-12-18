import re
from collections import defaultdict


def parse_links(source: str) -> list[str]:
    """Parse Obsidian-style [[links]] from source text."""
    links = re.findall(r'\[\[([^\]]+)\]\]', source)
    return links


def build_graph(memory_items: list) -> dict[str, list[str]]:
    """Build adjacency list: note_path -> list of linked note_paths."""
    graph = defaultdict(list)
    note_to_path = {item['note_path']: item['id'] for item in memory_items}
    
    for item in memory_items:
        links = parse_links(item['source'])
        for link in links:
            # Assume link is note name, map to note_path if possible
            # For simplicity, use link as key, but ideally normalize to note_path
            if link in note_to_path:
                graph[item['note_path']].append(link)
    
    return graph


def compute_pagerank(graph: dict[str, list[str]], damping=0.85, max_iter=100, tol=1e-6) -> dict[str, float]:
    """Compute PageRank centrality."""
    nodes = list(graph.keys())
    n = len(nodes)
    if n == 0:
        return {}
    
    # Initialize ranks
    rank = {node: 1.0 / n for node in nodes}
    
    for _ in range(max_iter):
        new_rank = {}
        for node in nodes:
            # Damping factor + sum from incoming links
            incoming = sum(rank[pred] / len(graph[pred]) for pred in nodes if node in graph[pred])
            new_rank[node] = (1 - damping) / n + damping * incoming
        
        # Check convergence
        diff = sum(abs(new_rank[node] - rank[node]) for node in nodes)
        rank = new_rank
        if diff < tol:
            break
    
    return rank


def compute_centrality(memory_items: list) -> dict[str, float]:
    """Compute centrality for memory items."""
    graph = build_graph(memory_items)
    pagerank = compute_pagerank(graph)
    
    # Map back to item ids
    centrality = {}
    for item in memory_items:
        path = item['note_path']
        centrality[item['id']] = pagerank.get(path, 0.0)
    
    return centrality
