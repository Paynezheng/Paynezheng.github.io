---
title: 数据库总览
date: 2025-03-12 17:10:00 +0800
categories: [Tech, Database]
tags: [database, server]
description: 数据库技术的总览，以及自己之前整理的笔记的索引。
author: Payne
pin: true
math: true
mermaid: true
---

本文主要做数据库技术的总览，并且整理了自己之前写的一些文档和笔记，太零散了，搬运起来比较麻烦（也许以后会来看的时候会搬出来），先写个目录。

## 数据库概述

### 几个概念介绍

主要记录了几个概念，简单介绍数据的类型，数据库的结构，数据库的生态。

> 几个概念：
1. 数据；
2. 数据库，指一个数据集合；
3. 数据库管理系统，指管理数据库的系统；
4. 数据库系统，包含数据库和数据库管理系统的一整个系统。

[文档地址](https://www.yuque.com/payne-pbjor/uhyp15/goyr56bpb1h07v5i?singleDoc# 《1. 数据库概述》)

ps. 语雀的分享只有半年有效期，如果看到失效了可以提醒我更新下链接。

### 数据库设计和使用

1. 关系模型中的各种概念，关系操作定义，关系约束等。[文档地址](https://www.yuque.com/payne-pbjor/uhyp15/qmqbo8g86cg4s8t6?singleDoc# 《2. 关系模型》);
2. 数据库设计，主要是关系型数据库的设计，包括E-R模型，数据库设计范式等，[文档地址](https://www.yuque.com/payne-pbjor/uhyp15/brzu9lp09khcsl53?singleDoc# 《3. 数据库设计》);
3. SQL语言的介绍，[文档地址](https://www.yuque.com/payne-pbjor/uhyp15/kdtwbyioqw190gz4?singleDoc# 《4. SQL》);

## 数据库内核原理以及相关技术

数据库内核主要分为两大部分，一个前端部分包括查询语句的解析，优化，查询执行计划的生成和分发；一个后端部分负责查询执行计划的执行，数据持久化和故障恢复等。

### 存储引擎

数据库存储引擎的功能，设计原理，存储结构，页面组织，文件组织，缓冲区的管理等等。存储引擎是数据库的灵魂。

[文档地址](https://snrixk56e9.feishu.cn/docx/RE4MdWHrXo1ufqxDmvQcmeiDn5e?from=from_copylink)

### 事务管理

[文档](https://snrixk56e9.feishu.cn/docx/OPsJdCNlKo4Hpdxg4a2cllN9nic?from=from_copylink)介绍了
- 数据库事务的特性（ACID），以及各个特性如何实现；
- 数据读写请求的可串行化调度方式；
- 事务的隔离级别；

### 原子性和持久性的实现&&故障恢复

[文档](https://snrixk56e9.feishu.cn/docx/FcdJdsRnVofSbwx30WscmowPnnc?from=from_copylink)介绍了：
- 原子性和持久性实现的方式；
- 数据库的恢复机制；
- 恢复策略和方法；
- 数据库备份技术；

### 并发控制

> **并发控制不仅是数据库，也是后台开发中高性能服务器实现的关键!**

[文档](https://snrixk56e9.feishu.cn/docx/BVrVdYs41oOqMsxHmwkcPYotnpc?from=from_copylink)介绍了：
- 并发控制的目的，方法，以及评估效果的方式；
- 悲观并发控制技术；
- 乐观并发控制技术；
- 多版本机制；

分布式锁和分布式时钟与并发控制强相关，其介绍及其实现分别记录在[分布式锁](https://paynezheng.github.io/posts/distributed_lock/)和[分布式时钟](https://paynezheng.github.io/posts/distributed_clock/)中。

### 索引

[文档](https://www.yuque.com/payne-pbjor/uhyp15/vkmpnzrde2ux9y6s?singleDoc# 《数据库索引》)中介绍了：
- 索引的类型，评价标准；
- B+树索引和LSM的简单介绍；

之前做的LSM-tree的分享: [LSM-tree分享](https://www.yuque.com/payne-pbjor/uhyp15/ffabyqc89kvmlowh?singleDoc# 《LSM-tree分享_入门向》)

### 查询处理，优化和执行

[文档](https://snrixk56e9.feishu.cn/docx/YwDydFSroo3891xQ21bcbj2inYc?from=from_copylink)中包括：
- 查询处理，优化的简单介绍；
- 查询执行的介绍、原理和方式。

在此文档的基础上，笔者研究了Doris的存储引擎代码，并记录了该数据库的查询执行代码的原理和设计思路。[Doris 查询执行](https://snrixk56e9.feishu.cn/docx/LDTddRLOpoovFCxYR5yc9itlnQb?from=from_copylink)

### 数据库安全

[数据库安全](https://paynezheng.github.io/posts/database_security/)在各个方面的考量，从数据库外围设施，数据库访问和数据级几个方面上讨论数据库的安全隐患的防范方式。

## 数据库类型

### 分布式数据库

分布式数据库的起源，架构，事务和查询优化等，记录在[文档](https://paynezheng.github.io/posts/distributed_database/)中。

### OLAP数据库
OLAP数据库的起源，相关技术，记录在[文档](https://www.yuque.com/payne-pbjor/uhyp15/xxarg7zqxucd2ox0?singleDoc# 《OLAP数据库》)中。
