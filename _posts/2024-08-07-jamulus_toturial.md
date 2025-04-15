---
title: 线上排练(Jamulus)
date: 2024-08-07 20:00:00 +0800
categories: [Music, Tool/Gear]
tags: [music, gear]      
description: 记录安装线上排练软件的过程.
author: Payne
mermaid: true
pin: true
---

## Jamulus

### 介绍
[Jamulus](https://jamulus.io/)是个用来线上排练，演奏或者Jam的开源软件，可以使用普通的带宽提供高品质、低延迟的声音。

[Jamulus的代码仓库](https://github.com/jamulussoftware/jamulus)存放在github上，主要使用C和C++开发。目前Jamulus客户端支持win/mac/linux/ios/android多平台

### 原理背景

#### 实现基础
空气中的音速传播大约是340m/s，所以在排练室内，如果里音源有大概10m的距离，则会有30ms左右的延迟。Jamulus通过有线网络，有线耳机等信号传输，从而保证乐器到耳朵之间的延迟能够小于30ms。实际在使用的时候延迟大概在20~40ms左右，属于是可以接受。

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

setting里面有一个设置自己的输入输出是立体声还是单声道的，一般我设置为单声道输入/立体声输出，因为我的声卡乐器和麦克风是分成两个声道输入的。

这时候查看左侧中间有一个小灯，旁边写着Delay的，用来表示当前延迟大小。如果是绿灯，说明很绿色；如果是黄灯，说明很危；如果是红灯，说明寄了，玩不了。

### 连接服务器

点击左下角connect按钮，然后可以左上角选择频道，选择延迟低的公共频道就可以进去合奏了。

访问未注册服务器参考[这里](#连接)

## 在云主机上部署Jamulus服务器

个人经验向的部署教程。Jamulus是支持将家用PC机设置为服务器的，但是由于家用PC一般都没有固定IP，无法直接提供公网服务，但可以作为局域网的服务器。如果要使用家用PC机来搭建公网服务器，需要DDNS和域名，并需要映射端口号来提供服务。对于偶尔使用的还是购买临时的服务器比较方便（当然如果是富哥或者用的比较多，可以买包年的机器）。

如果公共服务器人太多（一般不会有这样的情况），或者公共服务器无法满足低延迟的需求，这时就需要自行设置服务器。

### 购买服务器

#### 包年包月还是按量计费

按量付费：
- 按量付费机器指的是服务器厂商按照购买的机器配置，使用时间，使用宽带量来实际计算费用，用的少更便宜；
- 按量付费的价格大概是0.2r/h~2r/h之间，2r/h可以买上性能非常不错的机器；
- 按量付费，可以灵活伸缩配置；
- *每次都需要设置服务器*；
- 费用大概是包年包月机器的3~4倍(使用相同时长的平均费用)；

包年包月：
- 包年包月机器指的是购买固定带宽/配置/使用时间的机器;
- 包年包月的机器碰上打折可以买到差不多99一年的，99一年的机器配置大概对应按量付费0.5r/h的机器;
- 固定配置；
- 不需要重复设置；
- 提供24小时服务；

对于临时排练房，只是一时兴起没有固定的计划出来排练，那就购买按量付费更经济（如果不考虑这个每次都要上来重复设置的话）；而且带宽和机器配置的选择也可以更加灵活。

如果是提供给乐团或者提供服务的方式，随时有可能有人会上线使用，那更推荐包年包月机器，更加经济实惠，且不需要每次都设置服务器，更加方便。

如果定期的排练/Jam，就比如一周一次，一次往死里排差不多也是一块多，当然选择按量计费会比包年包月便宜。但是如果每次都设置服务器多少还是有点麻烦，如果不缺这杯瑞幸（或者这杯星巴克）钱还是包年比较舒服一点。

有一个比较吔的点：阿里云如果想购买按量计费的机器，阿里云账号上必须余额大于100，那每次购买机器钱还得检查余额是否大于100······

#### 机器选配

机器配置：
1. 运行软件要求任何服务器都应至少具有 1.6GHz CPU 频率和 1GB RAM，实际上四五个人使用的话基本上吃不了多少计算和内存，2核2G的机器足矣；
2. 购买带宽/流量，公网IP是必须的；
3. 系统可以选择ubuntu(别太旧的版本都行)；
4. 最好是同个地域的机器；
5. 比如专有网络，虚拟交换机这些基本上都默认就可以了；
6. 登陆方式密钥和密码都可以，建议设置个密码就行了（忘了也无所谓，控制台可以重置）。

又一个比较吔的点：只有阿里云有深圳地域的机器，另外两个大厂商最近的都是广州的服务器。

<!-- > todo: 
最低配置是什么？
高IO型/计算型？
最低带宽要求是多少？流量的使用多少？ -->

#### 防火墙设置

一般来说，云厂商会设置防火墙来拦住服务器的大部分端口访问。

以腾讯云为例，还需要开放协议和端口。在腾讯云的控制台中，选择机器实例对应的安全组，腾讯云提供了一键放开，直接一键给放开端口就行。

第一次购买服务器之后设置好安全组的规则，后续如果再此购买按量计费的机器，就不需要再设置安全组了。

> 未注册服务器似乎需要指定22124端口开放？ 设置了但还未验证

### 下载和安装Jamulus-headless


#### 连接服务器

购买成功服务器之后，应该在服务器运营商提供的控制台页面找到机器的公网IP地址，然后在shell工具或者cmd上使用ssh连接：

```shell
ssh username@IP
```

这一步记得在控制台内检查username，有的服务器厂商默认给设置root用户名，有的用户名默认叫ubuntu······

首次连接询问的信息直接yes就行了，然后输入密码，进入连接服务器的shell命令行。


#### 下载，安装和配置
第一步： 下载适用于云服务器的deb文件，选择这种headles安装包，并对应自己的系统选择，我这里是ubuntu，所以选择deb包，目前版本是：jamulus-headless_3.10.0_ubuntu_amd64.deb，目前最新版本可以到[github release](https://github.com/jamulussoftware/jamulus/releases)查看。所以命令行执行：

```shell
wget https://github.com/jamulussoftware/jamulus/releases/download/r3_10_0/jamulus-headless_3.10.0_ubuntu_amd64.deb
```

第二步： 更新ubuntu软件源，为安装deb包做准备：(如果提示输入密码就输入密码)

```shell
sudo apt update
```

第三步：安装Jamulus deb包

安装第一步下载的deb包，注意，如果文件名不一样，注意替换一下：
```shell 
sudo apt install ./jamulus-headless_3.10.0_ubuntu_amd64.deb
```

第四步： 查找当前时区并设置当前时区

```shell
timedatectl list-timezones # 这是查看时区列表的请求，找出自己的时区
```

找到自己的时区之后设置自己的时区，比如：
```shell
sudo timedatectl set-timezone Asia/Hong_Kong ## 这是设置时区的例子
```

第五步：启用Jamulus-headless

```shell
sudo systemctl enable jamulus-headless
```

第六步：设置Jamulus-headless文件

这一步设置Jamulus-headless决定了这一台Jamulus服务器启动的设置，包括是否注册服务等设置都会在这个文件下编辑，更多配置可以参考[官网教程](https://jamulus.io/wiki/Running-a-Server#configuration-options)。

这里，是否注册决定了服务器是否能被所有人看到。已注册的服务器将在Jamulus连接列表中展示，所有人可以连接，未注册的服务器需要连接者已知服务器的地址才能够连接。

```shell
sudo systemctl edit --full jamulus-headless
```

在ExecStart这里，把原来的注释掉（使用#注释），如果需要注册服务器，


如果需要注册服务器，在文件中补充：

```shell
ExecStart=/usr/bin/jamulus-headless -s -n -u 150\
--serverinfo "[name];[city];[country as two-letter ISO country code or Qt5 Locale]"\
--directoryserver "jamulus.fischvolk.de"\
--multithreading\
--fastupdate
```

其中country_id自行替换（China国家ID是44， Hong_Kong是97），房间名和所在地也需要替换。

如果不需要注册服务器，在文件中补充：

```shell
ExecStart=/usr/bin/jamulus-headless --nogui --server \
        --directoryaddress hostname:port \
        --serverinfo "[name];[city];[country as two-letter ISO country code or Qt5 Locale]"
```

其中country_id自行替换（China国家ID是44， Hong_Kong是97），房间名和所在地也需要替换；这里directoryaddress里的hostname自己瞎替换一个就行，port默认是22124.

比如我是这么设置的：

```shell
ExecStart=/usr/bin/jamulus-headless --nogui --server \
        --directoryaddress playground.com:22124 \
        --serverinfo "[Playground];[Shenzhen];[44]"
```

修改完成后，按下 Ctrl + X，接著输入 Y 以保存文件，然后按下 Enter 退出。

第七步： 重启服务系统守护进程和Jamulus

```shell
sudo systemctl daemon-reload && sudo systemctl restart jamulus-headless
```

### 连接

上文中连接已注册服务器的方式和正常使用公共排练室的方式一致。

要连接未注册服务器，需要知道其IP和端口，IP是机器购买时分配的公网IP，端口一般是默认22124。比如购买的机器端口是43.122.23.4，那么则在Jamulus客户端右下角输入
```text
43.122.23.4:22124
```
然后点连接即可。注意！`:`要英文输入法的。


## 最后

如果想出来Jam，但是按上述教程搭建服务器没有成功，可以把问题在邮件(scutrookie@gmail.com)里发给我哦！