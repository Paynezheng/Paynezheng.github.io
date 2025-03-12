---
title: C++ Polymorphism
date: 2023-12-12 02:00:00 +0800
categories: [Tech, C++]
tags: [server, c++]      
description: C++多态，虚函数机制.
author: Payne
mermaid: true
---

C++的多态是老八股了，虽然翻来覆去的说，但是网上文章一大抄，对关键原理讲解清晰的反倒不多。这里记录对C++多态的理解，不过也许也就要问八股的时候会翻出来看看。

## 多态的定义

多态是面向对象编程中的一个重要概念，它指的是**同一个接口或方法可以在不同的类中有不同的实现方式**。具体来说，多态允许我们使用父类的引用来调用子类的方法，从而实现代码的灵活性和可扩展性。

参考：
- [1](https://zhuanlan.zhihu.com/p/365765942)
- [2](https://zhuanlan.zhihu.com/p/563418849)

## 编译时多态/静态多态

静态多态是指在编译时就已经确定了调用哪个方法。它通常通过函数重载（Overloading）和模板（在C++中）来实现。函数重载允许在同一作用域内定义多个同名函数，只要它们的参数列表不同即可。编译器**根据函数调用时提供的参数类型和数量**来决定具体调用哪个函数。

## 运行时多态/动态多态

动态多态是指在程序运行时才能确定调用哪个方法。它通常通过继承和虚函数来实现。动态多态允许子类重写父类的方法，当**通过父类的引用或指针调用该方法时，实际执行的是子类重写后的方法**。

虚函数的实现需要虚表指针，类的对象通过虚表指针访问虚函数表，虚函数表中有指向函数实现代码的指针，而虚表属于C++内存布局中的一部分。

## 子类的内存布局

### 没有重写虚函数的派生类

```cpp
class Base1 {
public:
    int base1_1, base1_2;

    virtual void base1_fun1() {}  //  定义虚函数
    virtual void base1_fun2() {}
};
 
class Derive1 : public Base1 { // Derive1 中不存在虚函数
public:
    int derive1_1, derive1_2;
};
```
在这个例子中，虚函数没有被重写，对象指针指向的虚函数表中的虚函数实现都是父类中实现的。如果子类有自己的虚函数（不是从父类继承的），则从这个虚函数表后添加一个函数指针。

![没有虚函数的派生类](/assets/img/posts/2023-12-12-polymorphism/image1.png)

> 如果继承了多个父类，每个父类的内存区域都有一个虚函数表指针，派生类的虚函数（不论是否重写）放在第一个父类的虚函数表中。

### 重写父类虚函数的派生类

```cpp
class Base1 {
public:
    int base1_1, base1_2;
 
    virtual void base1_fun1() {}
    virtual void base1_fun2() {}
};
 
class Derive1 : public Base1 {
public:
    int derive1_1, derive1_2;

    virtual void base1_fun1() {} // 派生类函数覆盖基类中同名函数
}
```

![重写父类虚函数的派生类](/assets/img/posts/2023-12-12-polymorphism/image2.png)

### 几个概念

- 对象指针；
- 虚表指针；
- 虚函数表；
- 虚指针，其实就是具体虚函数实现的代码段的指针；

![调用过程](/assets/img/posts/2023-12-12-polymorphism/image3.png)