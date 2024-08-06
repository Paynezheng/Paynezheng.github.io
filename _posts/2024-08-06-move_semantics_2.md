---
title: Move Semantics Ⅱ
date: 2024-08-06 02:00:00 +0800
categories: [Tech, C++]
tags: [server, c++]     # TAG names should always be lowercase
description: C++移动语义.
math: true
mermaid: true
---

## 类与移动语义

本节展示类如何受益于移动语义，普通的类如何自动优化，以及怎么在类中显式实现移动语义。

### 普通类中的移动语义

假设有一个普通类，该类中包含可以被移动语义优化的成员变量类型。即成员变量不能全部是不能被移动优化的基本类型。举例如下：

```cpp
#include <string>
#include <vector>
#include <iostream>
#include <cassert>

class Customer {
private:
    std::string name; // name of the customer
    std::vector<int> values; // some values of the customer
public:
    Customer(const std::string& n): name{n} {
        assert(!name.empty());
    }
    std::string getName() const {
        return name;
    }
    void addValue(int val) {
        values.push_back(val);
    }
    friend std::ostream& operator<< (std::ostream& strm, const Customer& cust) {
        strm << '[' << cust.name << ": ";
        for (int val : cust.values) {
            strm << val << ' ';
        }
        strm << ']';
        return strm;
    }
};
```

在这个例子中，两个成员的潜在拷贝开销都是比较大的：
- `name`的拷贝需要为string中字符分配内存，除非name比较短且string实现采用了小字符串优化（*Small string optimization， SSO*）；
- `values`的拷贝需要为向量空间元素分配内存，如果`values`中的类型是其他类型（比如`string`），深拷贝还需要为向量空间每个元素申请内存。

> [*Small String Optimization*](https://cppdepend.com/blog/understanding-small-string-optimization-sso-in-stdstring/)
> : 一种通过始终为一定数量的字符保留内存来节省短字符串内存分配的方法。标准库实现中的典型值是始终保留 16 或 24 字节内存，以便字符串可以有 15 或 23 个字符（加上 1 个字节用于空终止符）而无需分配内存。这会使所有字符串对象变大（因为一两个字符的也会占 16/24 个字节），但通常会节省大量运行时间，因为在实践中，字符串通常短于 16 或 24 个字符，并且在堆上分配内存是一项非常昂贵的操作。
> : 简而言之，该方法使得短字符串在栈上操作而无需分配堆上内存。

好消息是，自C++11后，这样的普通类会自动支持移动语义。编译器一般会生成移动构造和移动赋值操作符的重载（类似于编译器自动生成拷贝构造和拷贝赋值操作符的重载）。在上述的例子中，该优化有以下效果：
- 按值返回的函数内，返回局部命名变量`Customer`会使用移动语义（假设没有其他优化，比如RVO）；
- 按值返回的函数内，返回临时变量`Customer`会使用移动语义（假设没有其他优化，比如RVO）；
- 传值函数，接受临时变量`Customer`作为参数，会使用移动语义（假设没有其他优化）；
- 传值函数，接受`std::move`指定的局部命名变量`Customer`作为参数，会使用移动语义（假设没有其他优化）；

使用上述例子中的`Customer`为例，以下给出使用其的场景，并解释其中如何使用移动语义进行了优化。

```cpp
#include "customer.hpp"
#include <iostream>
#include <random>
#include <utility> // for std::move()

int main()
{
    // create a customer with some initial values:
    Customer c{"Wolfgang Amadeus Mozart" };
    for (int val : {0, 8, 15}) {
        c.addValue(val);
    }
    std::cout << "c: " << c << '\n';        // print value of initialized c

    // insert the customer twice into a collection of customers:
    std::vector<Customer> customers;
    customers.push_back(c);                 // copy into the vector
    customers.push_back(std::move(c));      // move into the vector
    std::cout << "c: " << c << '\n';        // print value of moved-from c

    // print all customers in the collection:
    std::cout << "customers:\n";
    for (const Customer& cust : customers) {
        std::cout << " " << cust << '\n';
    }
}
```
这里的字符串使用了长字符串，是为了防止SSO优化。SSO优化发生后函数的行为可能不一致（string的移动变成了直接复制了）。

第一行输出将正常输出`Customer`的内容：

```text
c: [Wolfgang Amadeus Mozart: 0 8 15 ]
```

line 18中，push_back中使用了Customer的移动构造方法，操作后c成为一个移出对象，进入有效但未指定的状态。第二行输出可能为：

```text
c: [: ]
```
注意！此时第二行输出可能为任何值！只是为了优化内存，实现上常将其`vector`和`string`置为空。

通过显示地实现以下改进，此类可以进一步从移动语义中优化：
- 初始化成员时使用移动语义；
- 使用移动语义来保证get方法更加安全和高性能；

#### 类中自动启用移动语义的场景

根据上文中描述，编译器自动生成普通类的移动语义支持函数。但是并不是对所有的类都可以支持，有一定的限制条件。一条主要的原则是：编译器需要确认其生成的函数行为是正确的，移动函数对复制行为做了优化，而不是复制成员，且移动对象后移出对象将不再使用（至少不再使用原值）。

如果类改变了复制或赋值的常规行为，那么在优化这些操作时可能也必须做一些不同的事情。因此，当**用户声明**以下至少一个特殊成员函数时，将禁用移动操作的自动生成:
- 复制构造函数；
- 复制赋值运算符；
- 另一个移动操作；
- 析构函数。

任何形式的复制构造函数、复制赋值操作符或析构函数的显式声明都禁用移动语义。例如，如果实现了一个什么也不做的析构函数，就禁用了移动语义:
```cpp
class Customer {
    // automatic move semantics is disabled
    ~Customer() {}
};
```

甚至以下声明也可以禁用移动语义：
```cpp
class Customer {
    ~Customer() = default; // automatic move semantics is disabled
};
```

显示指定了析构函数会禁用移动语义，而在禁用移动语义的情况下，拷贝语义会作为默认行为而被执行。

由于上述原因，**如果没有特定的需要，就不要实现或声明析构函数**。（大部分程序员都会忽略的法则！）

这也意味着默认情况下，多态基类禁用了移动语义:
```cpp
class Base {
    // automatic move semantics is disabled
    virtual ~Base() {}
};
```

但是对派生类的成员，移动语义仍会自动生成 (如果派生类没有显式声明特殊的成员函数)。指的注意的是，派生类生成的移动语义只会移动属于派生类的部分，属于基类的部分仍然会执行基类的拷贝语义。后续[类中使用移动语义](#类中使用移动语义)会继续解释.

#### 生成不可用的移动函数

即使保证了生成的拷贝操作是正确的，生成的移动函数也可能会导致一些问题。特别需要注意以下问题：
- 成员变量有限制：
  - 值的限制；
  - 值相互依赖；
- 成员中使用了引用语义（指针，智能指针,···）；
- 对象没有默认构造。

我的理解/例子：
- 值得限制： 值的限制可能导致移出对象未指定的值非法，导致移出对象进入非一致状态；
- 值相互依赖： 
- 引用语义： 与上面这个可能同时出现，如果指向自身的某些内容，移动后可能指向无效内容。
- 对象没有默认构造： 无法生成一个空的默认构造函数，在这个基础上做移动操作。

原文：(我没理解)
> The problem that can occur is that moved-from objects might no longer be valid: invariants might be broken
or the destructor of the object might even fail. For example, objects of the Customer class in this chapter
might suddenly have an empty name even though we have assertions to avoid that. The chapter about
moved-from states will discuss this in detail.

### 实现复制/移动函数

可以自行实现移动成员函数，与实现复制构造和复制赋值操作符的方式类似，仅参数需要声明为非const右值引用，且内部需要优化复制操作。

以下给出自行实现复制和移动成员函数的例子：
```cpp
#include <string>
#include <vector>
#include <iostream>
#include <cassert>

class Customer {
private:
    std::string name; // name of the customer
    std::vector<int> values; // some values of the customer
public:
    Customer(const std::string& n): name{n} {
        assert(!name.empty());
    }
    std::string getName() const {
        return name;
    }
    void addValue(int val) {
        values.push_back(val);
    }
    friend std::ostream& operator<< (std::ostream& strm, const Customer& cust) {
        strm << '[' << cust.name << ": ";
        for (int val : cust.values) {
            strm << val << ' ';
        }
        strm << ']';
        return strm;
    }
    
    // 记住了：构造函数没引用返回值，赋值操作符有引用返回值。

    // copy constructor (copy all members): // noexcept declaration missing
    Customer(const Customer& cust): name{cust.name}, values{cust.values} {
        std::cout << "COPY " << cust.name << '\n';
    }
    
    // move constructor (move all members): // noexcept declaration missing
    Customer(Customer&& cust): name{std::move(cust.name)}, values{std::move(cust.values)} {
        std::cout << "MOVE " << name << '\n';   // 这里也不能用 cust.name
    }

    // copy assignment (assign all members):
    Customer& operator= (const Customer& cust) {    // noexcept declaration missing
        std::cout << "COPYASSIGN " << cust.name << '\n';
        name = cust.name;
        values = cust.values;
        return *this;
    }
    // move assignment (move all members):
    Customer& operator= (Customer&& cust) {         // noexcept declaration missing
        std::cout << "MOVEASSIGN " << cust.name << '\n';
        name = std::move(cust.name);
        values = std::move(cust.values);
        return *this;
    }

    // 记住这四个函数长啥样了吗？参数形式/函数声明样式/返回值？没记住回去再记一次
};
```

手动实现移动构造函数和移动赋值操作符时，通常都应该有`noexcept`声明。关于移动语义和`noexcept`在第七章中讨论。以下继续展开上面这个例子。

#### 拷贝构造

例子中实现的拷贝构造只相当于在默认的拷贝构造的基础上加了一行输出。

#### 移动构造

例子中实现的移动构造只相当于在默认的移动构造的基础上加了一行输出，与拷贝构造几乎仅参数声明上的区别。

需要特别注意的一个点是：**移动语义不会传递**。这里的不会传递的意思是：比如我使用`std::move`显式指定传递的参数执行移动语义，到了函数内部，在哪一步需要执行移动语义需要重新使用`std::move`指定。否则在进入函数的作用域后，第一个处理参数的地方直接触发移动语义，直接丢失该值，但在很多场景中，函数内会多次需要该值。因此函数内需要由函数设计者自行决定在哪里执行移动语义。

因此，移动构造函数的初值列需要用`std::move()`，否则就只能复制它们。

注意应该始终使用`noexcept`规范来实现移动构造函数，以提高对象重新分配时的性能。

#### 拷贝（复制）赋值操作符

例子中实现的拷贝赋值操作符只相当于在默认的拷贝赋值操作符的基础上加了一行输出。实现赋值操作符时，可以（也应该）检查对象对自身的复制，虽然默认的不会这么做。这里需要用引用限定符（即引用返回值）声明此函数。

#### 移动赋值操作符

类似拷贝赋值操作符，这里不同的在于将对函数体中的成员执行的时移动成员。这里需要用引用限定符（即引用返回值）声明此函数。

#### 自移动

前面的章节提到自移动会导致对象进入有效但未定义状态，甚至会出现一些诸如成员的值相互依赖导致地更严重的问题。如果需要避免可以简单地在移动赋值操作符实现做一个检查：

```cpp
Customer& operator= (Customer&& cust) { // noexcept declaration missing
    std::cout << "MOVEASSIGN " << cust.name << '\n';
    if (this != &cust) { // move assignment to myself?
        name = std::move(cust.name);
        values = std::move(cust.values);
    }
    return *this;
}
```

此外，如果需要遵循和STL一样的标准，仍然需要保证自移动后对象处于有效但未定义状态。

#### 使用自定拷贝/移动函数




### 特殊成员函数的规则

### 三五法则

## 如何从移动语义中受益

### 避免命名对象

### 避免不必要的std::move

### 用移动语义初始化成员

### 类中使用移动语义

## 引用的重载

### getter的返回类型

### 重载
