---
title: Storage and Read-Optimized Data Placement Structures for High-Performance Analysis
date: 2024-10-22 10:00:00 +0800
categories: [Tech, 论文泛读]
tags: [Paper]      
description: 2016 年 发表在 INFORMS（运筹学与管理科学学会年会） 上的论文，算是工程系的顶会论文了。
author: Payne
math: true
mermaid: true
---

提出了两种高效的数据放置结构。然后提供了教程，分布示例介绍如何使用Apache Spark 创建、使用和访问由 Parquet 或 ORC（优化行列式）结构化的数据。

数据准备和数据组织是数据挖掘和分析过程中的基础步骤，理想情况下应将处理后的数据存在可以快速高效进行后续重复访问的格式中。传统做法是将数据存储在数据库中，新做法是使用下新的开源格式和数据放置结构，比如：
1. Apache Parquet;
2. Apache ORC ( Optimized Row Columnar ).

高效的数据结构应该：
1. 加速数据加载；
2. 快速查询处理；
3. 高空间利用率；
4. 对不同负载有高度兼容性。

> Ps. 按照 RUM 猜想，这里为了加速读速度和兼容不同内存大小，完全放弃了写入性能（毕竟这个格式也没有很大的这个需求）。

## Apache Parquet

## Apache ORC