---
title: 套接字编程基本函数
date: 2024-10-29 22:00:00 +0800
categories: [Tech, UNIX网络编程]
tags: [server, linux, c++]
description: 套接字编程介绍和基本函数
author: Payne
mermaid: true
---

## 通信层次

OSI模型将网络通信分为7层，TCP/IP将网络通信分为五层，将OSI模型中的上三层合并为应用层（因为三层没有本质区别），即：
- 应用层；
- 传输层；
- 网络层；
- 数据链路层；
- 物理层。

其中，应用层处于用户进行，传输层和网络层的通信由内核执行。应用层使用传输层甚至网络层协议通过使用套接字（socket）编程实现。

