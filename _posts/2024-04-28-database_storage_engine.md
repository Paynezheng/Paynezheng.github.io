---
title: 数据库存储
date: 2024-02-07 18:52:00 +0800
categories: [Tech, Database]
tags: [database, server]      
description: 数据库存储引擎的底层原理和设计.
---

## 数据库存储

# 存储概览

## 数据库存储的功能

数据库的存储引擎组件扮演数据库SQL语法和底层存储之间媒介的角色，其在存储介质上构建，并向SQL执行器提供接口。存储组件主要负责的功能有：
- [文件组织和页面组织](/posts/CMU_15445_lecture03/)
- 元数据管理
- 日志管理
- [索引管理](/posts/RUM_conjecture/)
- [缓冲区管理](/posts/CMU_15445_project1/)
- 故障恢复
- [并发控制](/posts/distributed_lock/)


## 存储引擎功能模块
- [存储管理](/posts/CMU_15445_lecture03/)。包括管理文件以及页面，[缓冲区管理](/posts/CMU_15445_cache_replacement/)等。
- 日志和故障恢复。
- 事务处理。
- [并发控制](/posts/distributed_lock/)。（分布式场景下的[分布式锁](/posts/distributed_lock/)与[分布式时钟](/posts/distributed_clock/)）
- [索引](/posts/RUM_conjecture/)。