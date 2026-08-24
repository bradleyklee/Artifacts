# Benchmark 0: authority vs navigation prior

Corpus: 18 nodes / 49 edges. Tasks: 9. No pagination.

## flat

| ordering | success | mean bodies | mean edges |
|---|---:|---:|---:|
| hits-authority | 8/9 | 2.50 | 0.00 |
| indegree | 8/9 | 2.50 | 0.00 |
| pagerank | 8/9 | 2.75 | 0.00 |
| id | 8/9 | 3.12 | 0.00 |
| alphabetical | 8/9 | 3.25 | 0.00 |
| hits-hub | 8/9 | 3.25 | 0.00 |
| random-fixed | 8/9 | 3.50 | 0.00 |
| reverse-pagerank | 8/9 | 3.50 | 0.00 |
| outdegree | 8/9 | 3.75 | 0.00 |

## dfs

| ordering | success | mean bodies | mean edges |
|---|---:|---:|---:|
| alphabetical | 9/9 | 3.78 | 2.78 |
| hits-authority | 9/9 | 3.78 | 2.78 |
| random-fixed | 9/9 | 3.89 | 2.89 |
| indegree | 9/9 | 4.22 | 3.22 |
| hits-hub | 9/9 | 4.56 | 3.56 |
| id | 9/9 | 4.56 | 3.56 |
| pagerank | 9/9 | 4.56 | 3.56 |
| reverse-pagerank | 9/9 | 4.78 | 3.78 |
| outdegree | 9/9 | 5.00 | 4.00 |

## bfs

| ordering | success | mean bodies | mean edges |
|---|---:|---:|---:|
| hits-authority | 9/9 | 2.56 | 1.56 |
| indegree | 9/9 | 3.00 | 2.00 |
| alphabetical | 9/9 | 3.22 | 2.22 |
| random-fixed | 9/9 | 3.33 | 2.33 |
| pagerank | 9/9 | 3.44 | 2.44 |
| id | 9/9 | 3.67 | 2.67 |
| outdegree | 9/9 | 4.00 | 3.00 |
| reverse-pagerank | 9/9 | 4.11 | 3.11 |
| hits-hub | 9/9 | 4.22 | 3.22 |

## shallow-guided

| ordering | success | mean bodies | mean edges |
|---|---:|---:|---:|
| hits-authority | 9/9 | 2.33 | 1.33 |
| indegree | 9/9 | 2.56 | 1.44 |
| alphabetical | 9/9 | 2.67 | 1.33 |
| pagerank | 9/9 | 2.78 | 1.56 |
| random-fixed | 9/9 | 3.00 | 1.56 |
| reverse-pagerank | 9/9 | 3.22 | 2.11 |
| outdegree | 9/9 | 3.33 | 2.11 |
| id | 9/9 | 3.56 | 1.89 |
| hits-hub | 9/9 | 3.67 | 2.11 |

## guided-dfs

| ordering | success | mean bodies | mean edges |
|---|---:|---:|---:|
| random-fixed | 9/9 | 2.67 | 1.67 |
| alphabetical | 9/9 | 3.00 | 2.00 |
| hits-hub | 9/9 | 3.00 | 2.00 |
| hits-authority | 9/9 | 3.11 | 2.11 |
| indegree | 9/9 | 3.22 | 2.22 |
| pagerank | 9/9 | 3.33 | 2.33 |
| outdegree | 9/9 | 3.44 | 2.44 |
| id | 9/9 | 3.56 | 2.56 |
| reverse-pagerank | 9/9 | 3.56 | 2.56 |

## guided-bfs

| ordering | success | mean bodies | mean edges |
|---|---:|---:|---:|
| hits-authority | 9/9 | 2.33 | 1.33 |
| indegree | 9/9 | 2.56 | 1.56 |
| alphabetical | 9/9 | 2.67 | 1.67 |
| pagerank | 9/9 | 2.67 | 1.67 |
| random-fixed | 9/9 | 2.78 | 1.78 |
| outdegree | 9/9 | 3.11 | 2.11 |
| id | 9/9 | 3.22 | 2.22 |
| reverse-pagerank | 9/9 | 3.22 | 2.22 |
| hits-hub | 9/9 | 3.33 | 2.33 |

