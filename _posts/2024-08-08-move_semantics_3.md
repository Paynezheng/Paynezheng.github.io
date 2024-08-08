---
title: Move Semantics Ⅲ
date: 2024-08-08 02:00:00 +0800
categories: [Tech, C++]
tags: [server, c++]     # TAG names should always be lowercase
description: C++移动语义.
author: Payne
pin: true
math: true
mermaid: true
---

本文是《C++ Move Semantics, the complete guide》第4~5章内容的读书笔记以及部分翻译。

## 如何从移动语义中受益

本章主要内容是普通代码（不包含特殊成员函数）如何从移动语义中获益，并对应介绍若干条款。

### 避免命名对象

根据我们之前所论述的，移动语义用于优化一个后续不再需要的值的使用。如果编译器发现使用的对象已经来到了其生命周期的末尾，将自动切换到移动语义。具体来说就是：
- 该语句使用的临时对象在语句结束后就会销毁；
- 按值返回一个局部对象；

如果生命周期尚未结束，需要使用`std::move`显式指定对象移动。如果需要简单使用移动语义，一个直接的方式是：

> 在不需要重复使用对象时，避免命名变量.
{: .prompt-tip }

比如我需要给函数传值，值的构造以及传值有两种方式，但是使用命名对象一旦忘记了`std::move`，将会使用拷贝语义。

```cpp
MyType x{42, "hello"};
foo(x);                         // copy
foo(std::move(x));              // move
foo(MyType{42, "hello"});       // move
```

这项条款可能代码的可读性和可维护性冲突，需要读者自行权衡是临时对象还是使用`std::move`，是需要简洁还是更好的可读性和可维护性。

### 避免不必要的std::move

根据我们之前所论述的，按值返回局部对象会自动使用移动语义（如果没有其他更优的优化的话），但是也有一些程序员为了保险，强制使用了`std::move`显式指定返回值：

```cpp
std::string foo()
{
    std::string s;
    // ...
    return std::move(s);    // BAD: don’t do this，counterproductive optimization
    // return s;               // best performance(RVO/move)
}
```

`std::move`只是将值强制转化为一个右值引用，然后右值引用和函数的返回值类型不匹配，会导致返回值优化（RVO）被禁用。对于移动语义没有实现的类型，会直接使用拷贝语义拷贝到返回值而不是直接返回对象。

有的情况下`std::move`指定返回值也可能是合理的，比如使用`std::move`指定成员变量，`std::move`指定函数参数作为返回值，这些取决于开发者对返回值预期的行为是直接返回（RVO），移动还是拷贝。

使用`std::move`指定临时变量也是多余的，因为临时对象的使用本身就会触发移动语义。

有的编译器提供了编译选项来警告`std::move`造成的反向优化和冗余使用。比如gcc提供了选项 `-Wpessimizing-move` (包含在`-Wall`中) 检查由于使用 `std::move`而导致性能下降的情况和 `-Wredundant-move` (包含在`-Wextra`中)检查`std::move`不必要的使用。

### 用移动语义初始化成员

以下介绍四种初始化成员的构造函数的传参方式，对比其对参数的要求以及行为和性能上的区别，四种参数分别是：
- `const`左值引用；
- 左值引用；
- 传值；
- 右值引用。

作为构造函数，要求其参数能接受：
1. 能接受右值引用（临时/std::move）;
2. 能接受命名变量；

#### const左值引用

这里举一个包含两个`std::string`成员的例子，传统的构造函数例子如下：

```cpp
#include <string>
class Person {
private:
    std::string first;  // first name
    std::string last;   // last name
public:
    Person(const std::string& f, const std::string& l)
        : first{f}, last{l} {}
};

Person p{"Ben", "Cook"};
```

![const引用](/assets/img/posts/2024-08-08-move_semantics_3/image1.png){: width="570" height="347" .w-50 .right}
调用传了两个`const char*`类型的参数，与`string`类型不匹配，因此运行时会先使用参数生成两个`string`临时变量，然后再将这两个临时对象拷贝到成员*first/last*中，随后两个临时变量就会被销毁。不考虑SSO的情况下，使用`const char*`构造`string`，以及`string`拷贝，一共需要发生四次内存分配。

这里函数调用包括：
- 4次构造（4次内存分配），2个是拷贝构造；
- 析构2个临时对象，析构前对象会被复制；

#### 左值引用

声明参数为左值引用的构造函数不能满足接受参数类型的要求，比如以下代码：
```cpp
class Person {
    // ...
    Person(std::string& f, std::string& l)
        : first{std::move(f)}, last{std::move(l)} {}
    // ...
};

Person p{"Ben", "Cook"}; // ERROR: cannot bind a non-const lvalue reference to a temporary
```

声明为左值引用的参数类型，不能接受右值引用（临时/std::move指定的命名对象）作为参数，会直接报错。

#### 传值

有了移动语义之后，可以简单地使用传值来替代传统构造函数方法，然后将值移动到成员中，举例：

```cpp
#include <string>
class Person {
private:
    std::string first;  // first name
    std::string last;   // last name
public:
    Person(std::string f, std::string l)
        : first{std::move(f)}, last{std::move(l)} {}
};

Person p{"Ben", "Cook"};

std::string name1{"Jane"}, name2{"White"};
Person p{name1, name2};             // copy

std::string firstname{"Jane"};
Person p{std::move(firstname),      // OK, move names via parameters to members
        getLastnameAsString()};
```

![传值](/assets/img/posts/2024-08-08-move_semantics_3/image2.png){: width="570" height="347" .w-50 .right}
例子1中类似地也传递了两个`const char*`类型的参数，运行时会先使用参数构造两个`string`临时变量*f/l*。这里传递的如果是对象，会视情况移动/拷贝生成临时对象*f/l*。再将这两个临时对象移动到成员*first/last*中，随后两个临时变量就会被销毁。不考虑SSO的情况下，使用`const char*`构造`string`一共需要发生2次内存分配。

这里函数调用包括：
- 4次构造（2次内存分配），2次移动构造；
- 析构2个临时对象，析构前对象已被移动。

例子2中直接传值，先将对象拷贝到参数，然后再移动到成员，即这里的函数调用包括：
- 4次构造（2次内存分配），2次拷贝构造，2次移动构造；
- 析构2个临时对象，析构前对象已被移动。

例子3中传右值，可以触发`string`类型的移动语义(如果是不支持移动语义的类型，则退化为例子2的执行方式)，这里会将右值引用移动到参数*f/l*，然后*f/l*再移动到成员变量中。这里函数调用包括：
- 4次移动构造（0次内存分配）；
- 析构3个临时对象，析构前对象已被移动，firstname的析构函数暂时还不会被调用。

#### 右值引用

给出使用右值引用定义的构造函数和例子：
```cpp
class Person {
    Person(std::string&& f, std::string&& l)
        : first{std::move(f)}, last{std::move(l)} {}
};

Person p{"Ben", "Cook"};
```

这个例子中，类似地，运行时先生成两个临时变量*f/l*，然后临时变量触发移动语义被使用。这里的函数包括：
- 4次构造（2次内存分配），2次`string`构造，2次移动构造；
- 析构2个临时对象，析构前对象已被移动。

接受参数时，如果接受的是右值引用，则可以直接触发移动语义，这里的函数包括：
- 2次移动构造；
- 如果参数的右值引用是临时变量，则析构之。

但是，定义右值引用参数形式不能直接接受命名变量参数，比如：

```cpp
std::string name1{"Jane"}, name2{"White"};
Person p2{name1, name2};    // ERROR: can’t pass a named object to an rvalue reference
```

因此定义了右值引用的构造函数时，需要重载对应的const左值引用函数作为回退，为了覆盖`string`类型的直接传值，定义例子如下：

```cpp
class Person {

    Person(const std::string& f, const std::string& l)
        : first{f}, last{l} {}
    Person(const std::string& f, std::string&& l)
        : first{f}, last{std::move(l)} {}
    Person(std::string&& f, const std::string& l)
        : first{std::move(f)}, last{l} {}
    Person(std::string&& f, std::string&& l)
        : first{std::move(f)}, last{std::move(l)} {}

};
```

不嫌麻烦地话甚至可以重载对`const char*`类型的支持，一共需要定义9（3*3）个函数：
```cpp
class Person {
private:
    std::string first; // first name
    std::string last; // last name
public:
    Person(const std::string& f, const std::string& l)
        : first{f}, last{l} {}
    Person(const std::string& f, std::string&& l)
        : first{f}, last{std::move(l)} {}
    Person(std::string&& f, const std::string& l)
        : first{std::move(f)}, last{l} {}
    Person(std::string&& f, std::string&& l)
        : first{std::move(f)}, last{std::move(l)} {}
    Person(const char* f, const char* l)
        : first{f}, last{l} {}
    Person(const char* f, const std::string& l)
        : first{f}, last{l} {}
    Person(const char* f, std::string&& l)
        : first{f}, last{std::move(l)} {}
    Person(const std::string& f, const char* l)
        : first{f}, last{l} {}
    Person(std::string&& f, const char* l)
        : first{std::move(f)}, last{l} {}
};
```

#### 行为和性能对比

#### 总结

### 类中使用移动语义

## 引用的重载

### getter的返回类型

### 重载
