# Network Science Data

## Data Sources

All network data from [Stanford SNAP](https://snap.stanford.edu/data/).

## Networks

| File | Nodes | Edges | Type | Source |
|------|-------|-------|------|--------|
| karate_club.txt | 34 | 78 | Social | Zachary 1977 |
| facebook_combined.txt | 4,039 | 88,234 | Social | SNAP |
| email_enron.txt | 36,692 | 183,831 | Email | SNAP |
| ca_grqc.txt | 5,242 | 14,496 | Collaboration | SNAP |
| ca_hepth.txt | 9,877 | 25,998 | Collaboration | SNAP |

## File Format

Edge list format:
```
node1 node2
node1 node3
...
```

## Usage

```python
import networkx as nx

# Load network
G = nx.read_edgelist("karate_club.txt", comments='#')
print(f"Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
```

## References

1. Leskovec, J., & Krevl, A. (2014). SNAP Datasets: Stanford Large Network Dataset Collection.
2. Zachary, W. W. (1977). An information flow model for conflict and fission in small groups.

*Downloaded: 2025-12-28*
