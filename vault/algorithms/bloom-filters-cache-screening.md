# ⚡ Space-Efficient Cache Screening Using Probabilistic Bloom Filters

> **Category**: Algorithms &nbsp;·&nbsp; **Difficulty**: `Intermediate` &nbsp;·&nbsp; **Published**: 2026-11-06  
> **Tags**: `#algorithms` `#bloom-filter` `#data-structures` `#caching`

---

## 📌 Executive Summary
Preventing cache pollution from one-hit-wonders using bitwise Bloom Filters with $O(k)$ operations and minimal memory overhead.

---

## 🧠 Architectural Deep-Dive & Core Concept
Over 70% of keys fetched in high-traffic web apps are 'one-hit-wonders'—requested once and never again. Storing them in LRU cache evicts hot entries prematurely. A Bloom filter acts as a frontline bouncer: an item is only admitted into the cache on its second appearance, saving massive memory without expensive database roundtrips.

---

## 💻 Production Implementation (Python)

```python
import math
import mmh3 # MurmurHash3
from bitarray import bitarray

class BloomFilter:
    def __init__(self, expected_items: int, false_positive_rate: float = 0.01):
        # m = - (n * ln(p)) / (ln(2)^2)
        self.size = int(- (expected_items * math.log(false_positive_rate)) / (math.log(2) ** 2))
        # k = (m / n) * ln(2)
        self.hash_count = int((self.size / expected_items) * math.log(2))
        self.bits = bitarray(self.size)
        self.bits.setall(0)

    def add(self, item: str):
        for seed in range(self.hash_count):
            index = mmh3.hash(item, seed) % self.size
            self.bits[index] = 1

    def contains(self, item: str) -> bool:
        for seed in range(self.hash_count):
            index = mmh3.hash(item, seed) % self.size
            if not self.bits[index]:
                return False
        return True
```

---

## 🔬 Benchmark & Engineering Trade-offs
### Trade-offs: Zero False Negatives, Controlled False Positives

A Bloom Filter never reports a false negative (if an element was added, `contains()` is guaranteed to return `True`). It can return a false positive, but the mathematical sizing ensures the error rate remains under 1% while using only 9.6 bits per item—over 100x more compact than a Redis set or hash map.

---

## 🚀 Key Takeaways for Senior Engineers
- **Production Safety**: Ensure error boundaries and proper retry logic handle edge cases gracefully.
- **Observability**: Expose telemetry counters and latency histograms for all critical operations.
- **Resource Footprint**: Keep memory allocations and network roundtrips minimized under high concurrency.

---
*Authored by [Hamza Ishaq (@Hamzaisadev)](https://github.com/Hamzaisadev) · Part of the [Daily Dev Vault](https://github.com/Hamzaisadev/daily-dev-vault).*
