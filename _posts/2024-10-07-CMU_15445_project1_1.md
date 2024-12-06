---
title: 缓存淘汰策略
date: 2024-10-07 18:00:00 +0800
categories: [Tech, CMU-15/445]
tags: [database, distributed, cmu 15-445]
description: 缓存淘汰的机制优劣和适用场景对比
author: Payne
math: true
mermaid: true
---

## 数据缓存

缓存机制广泛用在数据库和操作系统中，比如：
- 系统页面置换算法；
- 读取磁盘上的数据，需要内存的缓存；
- 读取远程存储上的数据，需要磁盘的缓存（常见于存算分离架构）；

缓存的平均访问时间为：

$$ T = m \times T_m + T_h + E$$

其中
- $$T$$为平均访问时间；
- $$m$$为未命中率或者缺页率；
- $$T_m$$为缓存未命中时访问下级存储（内存未命中访问磁盘/磁盘未命中访问远程存储）的时间；
- $$T_h$$为访问缓存延迟；
- $$E$$为其他次级因素，比如处理器系统的队列效应等。

衡量缓存性能的指标分为两个，命中延迟和命中率。

为了减少平均延迟，缓存的置换策略需要在**命中率，置换频率和缓存大小**间做权衡。

## 页面置换算法

常见的页面置换算法（参考[维基百科](https://en.wikipedia.org/wiki/Cache_replacement_policies)，分类上，有标记算法，保守算法等分类）包括：
- OPT，最佳置换算法，理想的淘汰机制；
- FIFO；
- CLOCK，时钟置换算法；
- LRU，最近最少使用算法；
- LFU，最不常用算法；

不常见的包括：
- NRU，Not recently used，最近未使用算法；
- NMFU，最常使用算法；

### OPT

理想情况下的页面置换算法，指令访问页面时，页面总存在内存中，即每次访问页面都不会发生缺页。

因为无法知道下一次访问页面是什么时候，所以该算法不可能实现。

### FIFO

FIFO（先进先出）的想法是选择主存中停留最久的页面置换，严格符合队列的添加删除规则。

FIFO适用于**总是顺序访问**的场景。

如果所置换的页面包括大量重复使用的变量，将其淘汰会导致大量缺页。会出现[Belady异常](https://en.wikipedia.org/wiki/B%C3%A9l%C3%A1dy%27s_anomaly)。

#### Second-Chance

基于FIFO的缺点改进形式称为Second-Chance算法，效果一般优于FIFO且代价很小。

它的工作原理是像 FIFO 一样查看队列的前面，但不是立即将该页面调出，而是检查其引用位是否已设置。如果没有设置，则页面将被换出。否则，将清除引用位，将该页面插入队列的后面（就像它是一个新页面一样），然后重复此过程。这**类似于是一个循环队列**。

如果所有页面的引用位都已设置，则在第二次遇到列表中的第一个页面时，该页面将被换出，因为它现在的引用位已被清除。如果所有页面的引用位都已清除，则Second-Chance机会算法将退化为纯 FIFO。

### CLOCK算法

时钟算法是FIFO的更高效的版本，它仅在实现上与Second-Chance不同，Clock算法使用环状的数据结构和指针实现。参考[这里](https://archive.org/details/modernoperatings00tane/page/218/mode/2up).

始终算法包括多种变体：
- GCLOCK：广义时钟页面替换算法；
- Clock-pro；
- WSClock；
- CAR，自适应替换时钟算法，性能与ARC相当，优于LRU和CLOCK；

### LFU 

Least frequently used，最不经常使用（注意区别LRU）。该算法要求置换具有最小计数的页面。

该算法的思路是使用更多的页面应该更晚被淘汰，但是如果有数据初期使用频繁之后存放在内存中，后续会一直占用内存不被淘汰。一种解决方案是定期将计数/2。

### LRU

Least recently used，最近最长时间未访问。该算法的思想是最近使用频繁的页面很有可能在接下来的指令中也大量使用。虽然理论上可以近似提供最佳性能（几乎跟ARC算法相当，已经是简单可以理解的逻辑中的接近最优了），但实际实现成本都比较昂贵。高性能的实现需要寄存器和栈的硬件支持。

该算法**为每个页面设置了一个访问字段，来记录页面自上次访问以来所经历的时间**。淘汰页面时选择现有页面中值最大的予以淘汰。

实现上经常使用哈希表+双向链表实现，以保证 Get 和 Put 操作都是 O(1) 的复杂度。可以参考[leetcode 146](https://labuladong.online/algo/data-structure/lru-cache/)或者[Doris LRU实现](https://github.com/apache/doris/blob/2cde7b0839d1607ef6dd619b7d9db95bc4c211ee/be/src/io/cache/block_file_cache.h#L189)。Linux内核的页面置换算法类似LRU。

实现代码Demo:
```cpp
// 为了避免值的复制，复杂类型的值建议使用智能指针包装
// 作为基础数据结构使用时，还需要考虑多线程的竞争关系
template <typename Key, typename Value>
class LRUQueue {
public:
    LRUQueue(int capacity): _capacity(capacity) {}

    std::optional<Value> get(Key key) {
        auto it = _map.find(key);
        if (it != _map.end()) {
            _queue.splice(_queue.end(), _queue, it->second);
            return it->second->second;
        }
        else {
            return std::nullopt;
        }
    }

    void put(Key key, Value value) {
        auto it = _map.find(key);
        if (it != _map.end()) {
            _queue.splice(_queue.end(), _queue, it->second);
            it->second->second = value;
            return;
        }
        else {
            if (_map.size() >= _capacity) {
                _map.erase(_queue.begin()->first);
                _queue.erase(_queue.begin());
            }
            auto new_iter = _queue.insert(_queue.end(), {key, value});
            _map.insert({key, new_iter});
            return;
        }
    }

private:
    int _capacity = 0;
    using Node = typename std::pair<Key, Value>;
    std::list<Node> _queue;
    using Iterator = typename std::list<Node>::iterator;
    std::unordered_map<Key, Iterator> _map; 
};
```

LRU的缺点,在许多常见的引用模式下，其性能往往下降
- 比如，如果 LRU 池中有 N 个页面，则对 N+1 个页面中的数据执行循环的应用程序将在每次访问时导致页面错误;
- 存在缓存污染的问题；

LRU有多种变体：
- LRU-K，淘汰最近第 K 次访问时间最久的页面，LRU-1 就是简单的 LRU 算法。 
- ARC；
- 2Q；

#### LRU-K

LRU-K的主要目的是为了解决LRU算法“缓存污染”的问题，其核心思想是将“最近使用过1次”的判断标准扩展为“最近使用过K次”。也就是说没有到达K次访问的数据并不会被缓存，这也意味着需要对于缓存数据的访问次数进行计数，并且访问记录不能无限记录，也需要使用替换算法进行替换。当需要淘汰数据时，LRU-K会淘汰第K次访问时间距当前时间最大的数据。

K值增大，命中率会更高，但是适应性差（清除一个缓存需要大量的数据访问，一般选择LRU-2）。

## Linux的页面置换策略

### 多级队列
Linux内核使用两个 LRU 队列来跟踪页面。最近访问过的页面保存在 “活动” 队列中，刚刚访问过的页面放在队列的开头。如果页面最近没有被访问过，则会从队列的末尾删除，并放在 “非活动” 队列的开头。该队列是一种炼狱；如果某个进程访问了非活动队列中的页面，它将被提升回活动队列。某些页面（例如上述顺序读取文件中的页面）从非活动队列开始，这意味着如果不再需要它们，它们将被相对较快地回收。

只区分活动/非活动队列过于粗略，无法做出准确的决策，而且页面最终往往会出现在错误的列表中。在控制组中使用独立列表使得内核很难比较不同组之间页面的相对年龄。内核长期以来倾向于驱逐文件支持的页面，原因有很多，这可能导致有用的文件支持的页面被丢弃，而空闲的匿名页面仍保留在内存中。这个问题在云计算环境中变得更加严重，因为客户端的本地存储空间相对较少，因此文件支持的页面相对较少。同时，扫描匿名页面的成本很高，部分原因是它使用了一种复杂的反向映射机制，当必须进行大量扫描时，这种机制的性能不佳。


## 存算分离的缓存淘汰策略

这里特指存算分离框架下，从远程存储缓存到本地磁盘的数据缓存。