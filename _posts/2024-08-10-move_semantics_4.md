---
title: Move Semantics Ⅳ
date: 2024-08-10 02:00:00 +0800
categories: [Tech, C++]
tags: [server, c++]     # TAG names should always be lowercase
description: C++移动语义.
author: Payne
math: true
mermaid: true
---

本文是《C++ Move Semantics, the complete guide》第5章内容的读书笔记以及部分翻译。

## 重载引用限定符

引用限定符介绍----(原文并没有介绍引用限定符)

### get方法的返回类型

在实现有较高拷贝成本的成员类型的`get`方法时，C++11之前一般有两种方式：
- 以值返回；
- 以`const`左值引用返回。

这里简要介绍这两种方案。

#### 以值返回

get方法以值返回例子如下（注意：不要返回const值，除非对于返回的值就是不想用移动语义）：

```cpp
class Person
{
private:
    std::string name;
public:
    // ...
    std::string getName() const {
        return name;
    }
};
```

代码很安全，但每次调用该方法时，都需要进行一次拷贝。因为这里`name`生命周期和`Person`对象绑定，既不会触发NVO也不会使用移动语义。

#### 以`const`引用返回 

以`const`引用返回的例子如下

```cpp
class Person
{
private:
    std::string name;
public:
    const std::string& getName() const {
        return name;
    }
};
```




### 重载
