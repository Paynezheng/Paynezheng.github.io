---
title: 线上排练(Jamulus)
date: 2024-08-07 20:00:00 +0800
categories: [Music]
tags: [music, gear]     # TAG names should always be lowercase
description: 记录安装线上排练软件的过程.
mermaid: true
---

## Jamulus

[Jamulus](https://jamulus.io/)是个用来线上排练，演奏或者Jam的开源软件，可以使用普通的带宽提供高品质、低延迟的声音。

[Jamulus的代码仓库](https://github.com/jamulussoftware/jamulus)

空气中的音速传播大约是340m/s，所以在排练室内，如果里音源有大概10m的距离，则会有30ms左右的延迟。Jamulus通过有线网络，有线耳机等信号传输，从而保证乐器到耳朵之间的延迟能够小于30ms。

## 安装和配置

### 硬件/网络/软件需求

硬件要求：
1. 一台电脑/平板/.../甚至手机；
2. 需要有线网络（并关闭wifi），因此上面的手机/平板这些可能效果不大好；
2. 有线耳机（而不是蓝牙或者扬声器）；
3. 一个理的音频设备、声卡和/或麦克风；


软件要求：
1. 操作系统（支持win/mac/linux/ios/android）；
2. ASIO 驱动软件；
3. 



## 部署服务器

[参考教程](https://yaocaptain.com/p/linux-jamulus-on-gcp/#%E5%A6%82%E4%BD%95%E5%9C%A8gcp%E4%B8%8A%E5%BB%BA%E7%AB%8Blinux-server)