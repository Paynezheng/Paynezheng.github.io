---
title: 线上排练(Jamulus)
date: 2024-08-07 20:00:00 +0800
categories: [Music, Tool/Gear]
tags: [music, gear]     # TAG names should always be lowercase
description: 记录安装线上排练软件的过程.
author: Payne
mermaid: true
---

## Jamulus

[Jamulus](https://jamulus.io/)是个用来线上排练，演奏或者Jam的开源软件，可以使用普通的带宽提供高品质、低延迟的声音。

[Jamulus的代码仓库](https://github.com/jamulussoftware/jamulus)存放在github上，主要使用C和C++开发。目前Jamulus客户端支持win/mac/linux/ios/android多平台

空气中的音速传播大约是340m/s，所以在排练室内，如果里音源有大概10m的距离，则会有30ms左右的延迟。Jamulus通过有线网络，有线耳机等信号传输，从而保证乐器到耳朵之间的延迟能够小于30ms。实际在使用的时候延迟大概在38ms左右，属于是可以接受。

## 安装和配置

### 硬件/网络/软件需求

硬件要求：
1. 一台电脑/平板/.../甚至手机；
2. 需要有线网络（并关闭wifi）；
2. 有线耳机（而不是蓝牙或者扬声器）；
3. 一个合理的音频设备、声卡和/或麦克风；

硬件上不推荐使用手机/平板，延迟会比有线的台式机高20~40ms。这点延迟很关键，因为原本的延迟其实已经很大了属于是刚刚好能合奏，再大的话延迟的感觉就很明显了。蓝牙需要蓝牙传输信号有协议的传输和解码延迟，扬声器有空气传播的延迟，这些都或多或少对体验产生着最后一点的关键影响。

软件要求：
1. 操作系统（支持win/mac/linux/ios/android）；
2. 音频驱动软件（win：ASIO/Jack，Mac：Core Audio， Linux： Jack）;
3. 到官网或者[github](https://github.com/jamulussoftware/jamulus/releases/tag/r3_10_0)（链接更新于24-08-08）下载稳定版的安装包，对应自己的操作系统;

网络需求：
1. 有线网络；
2. 带宽当然是越大越好；
3. 最好一起合奏的朋友在同一个地域。

### 安装软件

参考官网教程，注意找对应自己系统版本的安装包。

### 配置

进入主窗口，点击左下角setting设置个人信息，名称（Name/Alias）必填，其他随意。

连接自己的乐器到声卡上，此时弹奏乐器，Jamulus左侧这个Input栏的Input有反应则说明有输入，否则需要检查乐器/声卡/声卡驱动等。如果声卡驱动已正常安装，进入Jamulus时无需其他配置。

这时候查看左侧中间有一个小灯，旁边写着Delay的，用来表示当前延迟大小。如果是绿灯，说明很绿色；如果是黄灯，说明很危；如果是红灯，说明寄了，玩不了。

### 连接服务器

点击左下角connect按钮，然后可以左上角选择频道，选择延迟低的公共频道就可以进去合奏了。

> todo: 如何访问未注册服务器？（私有排练室）

## 部署服务器

如果公共服务器人太多（一般不会有这样的情况），或者公共服务器无法满足低延迟的需求，这时就需要自行设置服务器。

大部分用户在第三方/云主机上部署服务器，也可以使用自己的主机部署服务器。但是国内运营商一般都不给固定IP，需要映射端口后还要绑定DNS，太麻烦了。建议还是在云主机上部署。如果是富哥可以购买包年包月的机器一直挂着，如果临时想找朋友玩一下但是没有合适的公共服务器，买个按量付费的机器也不会很贵（一小时大概1.5人民币左右）。

### 在云主机上部署Jamulus服务器

#### 购买服务器

机器配置：
1. 运行软件要求任何服务器都应至少具有 1.6GHz CPU 频率和 1GB RAM
2. 购买带宽/流量，公网IP是必须的；
3. 系统可以选择ubuntu；

> todo: 
最低配置是什么？
高IO型/计算型？
最低带宽要求是多少？流量的使用多少？



以腾讯云为例，还需要开放协议和端口。在腾讯云的控制台中，选择机器实例对应的安全组，腾讯云提供了一键放开，直接一键给放开端口就行。

#### 下载和安装Jamulus

[参考教程](https://yaocaptain.com/p/linux-jamulus-on-gcp/#%E5%A6%82%E4%BD%95%E5%9C%A8gcp%E4%B8%8A%E5%BB%BA%E7%AB%8Blinux-server)

> todo: 给一个一键安装的脚本

第一步： 下载适用于云服务器的deb文件，选择这种headles安装包，并对应自己的系统选择，我这里是ubuntu，所以选择deb包，目前版本是：jamulus-headless_3.10.0_ubuntu_amd64.deb，目前最新版本可以到[github release](https://github.com/jamulussoftware/jamulus/releases)查看。所以命令行执行：

```shell
wget https://github.com/jamulussoftware/jamulus/releases/download/r3_10_0/jamulus-headless_3.10.0_ubuntu_amd64.deb
```

第二步： 更新ubuntu软件源，为安装deb包做准备：(如果提示输入密码就输入密码)

```shell
sudo apt update
```

第三步：安装Jamulus deb包

```shell 
sudo apt install ./jamulus-headless_3.10.0_ubuntu_amd64.deb
```

第四步： 查找当前时区并设置当前时区
```shell
timedatectl list-timezones # 这是查看时区列表的请求，找出自己的时区
 
sudo timedatectl set-timezone Asia/Hong_Kong ## 这是设置时区的例子
```

第五步：启用Jamulus-headless

```shell
sudo systemctl enable jamulus-headless
```

第六步：设置Jamulus-headless文件

```shell
sudo systemctl edit --full jamulus-headless
```

在ExecStart这里，把原来的注释掉（使用#注释），换成：

```shell
ExecStart=/usr/bin/jamulus-headless -s -n -u 150\
--serverinfo "自定義房間名稱;你的所在地;[country ID]"\
--directoryserver "jamulus.fischvolk.de"\
--multithreading\
--fastupdate
```

其中country_id自行替换（China国家ID是44， Hong_Kong是97），房间名和所在地也需要替换。
修改完成后，按下 Ctrl + X，接著输入 Y 以保存文件，然后按下 Enter 退出。

> todo: 这里未注册服务器（私有排练室）是怎么设置的？

第七步： 重启服务系统守护进程和Jamulus

```shell
sudo systemctl daemon-reload
sudo systemctl restart jamulus-headless
```

然后就可以在桌面Jamulus客户端中点击connect看到刚刚设置的服务器啦！