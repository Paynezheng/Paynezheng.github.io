---
title: 分布式时钟
date: 2024-03-01 20:00:00 +0800
categories: [Tech, Database]
tags: [database, distributed, server]     # TAG names should always be lowercase
description: 分布式时钟介绍和实现.
math: true
mermaid: true
---

## 介绍

乐观并发控制技术中，需要使用时间戳来作为标识事务串行化顺序的标识符。由于在一些场景中（比如高并发低竞争），悲观并发
控制中很多锁都是没有实际用处的。乐观并发控制技术的“乐观”思想体现在其避免了没有实际用处的加锁，通过时间复用，使用时
间戳的比对来保证事务的隔离性和处理器的高利用率。

在一个单点的服务内部，可以简单的使用系统时钟，或者更严格些的话可以使用单调时钟（比如C++的`std::chrono::steady_clock`），
但在一个分布式系统中，节点之间的时间戳有可能有一定误差，因此需要一个时钟系统来提供（或者说保证）一个误差足够小能够满足
使用的时间戳。

时间戳获取的实现根据节点数量主要分为两种：
  - 集中式时间戳：授时中心称为性能瓶颈，且单点难以实现高可用。
  - 分布式时间戳：高可用，但时钟顺序维护较为复杂。

## 集中式时钟

有单点服务提供时间戳，可以保证时间戳的强单调性。

## 分布式时钟

分布式时钟主要用于生成多版本并发控制中的时间戳。

分布式系统中的时间问题：
- 每台机器有自己的时钟，如何保证不同机器的时间一致；
- 时间同步存在网络延迟，如何判断不同节点上发生的事件的先后顺序。

如果使用物理时钟：精度有限，晶体振荡器时钟存在时钟漂移；原子钟很准但是需要复杂同步。

### 逻辑时钟
实现：每个节点内部维护一个本地逻辑时钟，初始值为0；节点内部每发生一个事件，如事务开始，就将本地逻辑时钟的值加一。

如果节点A向节点B发送了一条消息，则节点A在发送消息时附带上本地逻辑时钟的值，节点B收到消息后， 比较自身的本地时钟
和节点A发送的本地时钟，将本地时钟更新为二者的较大值加一。

<div style="text-align: center;">
  <img src="assets/img/posts/2024-03-01-distributed_clock/image1.png" alt="逻辑时钟" style="display: block; margin: 0 auto;">
  <p style="font-size: medium;"><em>逻辑时钟</em></p>
</div>


特点：只是偏序，不是全序，某些场景无法判断两个事务先后，例如两个节点之间没有消息传递。

### 向量时钟

实现：每个节点不仅存储本地时钟的值，还存储了其他节点的逻辑时钟；所有节点的逻辑时钟值组成一个向量，向量维度与系统
中的节点数目相同。

对于事件A和事件B对应的时钟`V(A)`和`V(B)`，如果`V(A)` < `V(B)`，即向量`V(A)`的每个分量都小于向量`V(B)`，则可以确定事件A
发生在事件B之前。即向量时钟存在严格大小和无法区分两种状态。

<div style="text-align: center;">
  <img src="assets/img/posts/2024-03-01-distributed_clock/image2.png" alt="向量时钟" style="display: block; margin: 0 auto;">
  <p style="font-size: medium;"><em>向量时钟</em></p>
</div>


### 混合逻辑时钟

包含物理时钟和逻辑时钟，既可以如逻辑时钟一样表示事件之间的因果关系，又保证了混合逻辑时钟值与物理时钟尽可能接近。
每个混合逻辑时钟由三个标识构成，对于给定时间e：
1. e.pt为事件e发生的物理时间；
2. e.l表示事件e发生时所感知到的物理时钟的最大值；
3. e.c用于记录事件之间的因果关系。

实现特点：
1. 如果事件e发生在事件f之前，那么e的时间戳小于f的时间戳；
2. 时间戳的存储空间大小是固定的，空间消耗不会随着系统节点数的增加而增大；
3. 时间戳值存在上界，不会无限增长；
4. 时间戳的值与物理时钟接近，二者的差值是有界的。

举个🌰：

<div style="text-align: center;">
  <img src="assets/img/posts/2024-03-01-distributed_clock/image3.png" alt="混合逻辑时钟" style="display: block; margin: 0 auto;">
  <p style="font-size: medium;"><em>混合逻辑时钟</em></p>
</div>

## TrueTime

逻辑时钟和向量时钟定义了事件之间的偏序关系而非全序关系，仍存在部分无法判断先后顺序的事件，如两个节点之间没有发生
过任何通信，则这两个节点上发生的事件无法进行先后顺序的比较。

TrueTime通过硬件（原子钟+GPS时钟）来解决时钟同步问题。每个数据中心都具有精确的原子钟，同时还可以得到GPS卫星提
供的时钟信息，两种时钟均具有较高的准确性和可靠性。

## 对比

<div style="text-align: center;">
  <img src="assets/img/posts/2024-03-01-distributed_clock/image4.png" alt="对比" style="display: block; margin: 0 auto;">
  <p style="font-size: medium;"><em>对比</em></p>
</div>
