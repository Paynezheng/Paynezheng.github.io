---
title: Move Semantics Ⅱ
date: 2024-08-06 02:00:00 +0800
categories: [Tech, C++]
tags: [server, c++]     # TAG names should always be lowercase
description: C++移动语义.
math: true
mermaid: true
---

本文内容包括《C++ Move Semantics, the complete guide》的第3章。

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

line 18中，push_back中使用了Customer的移动构造方法，操作后c成为一个移出对象，进入有效但未指定的状态。第二行输出可能为任何值！只是为了优化内存，实现上常将其`vector`和`string`置为空。

通过显示地实现以下改进，此类可以进一步从移动语义中优化：
- 初始化成员时使用移动语义；
- 使用移动语义来保证get方法更加安全和高性能；

#### 类中自动启用移动语义的场景

根据上文中描述，编译器自动生成普通类的移动语义支持函数。但是并不是对所有的类都可以支持，有一定的限制条件。一条主要的原则是：**编译器需要确认其生成的函数行为是正确的**。移动函数对复制行为做了优化，而不是复制成员，且移动对象后移出对象将不再使用（至少不再使用原值）。

如果类改变了拷贝构造或拷贝赋值的常规行为（比如在拷贝时打印日志/交易数+1/会下个蛋/···），那么在优化这些操作时可能也必须做一些相同的事情（打印日志/交易数+1/···）。因此，当**自行声明**(包括自行实现，`=default`，甚至指定`=delete`)以下至少一个特殊成员函数时，将禁用移动操作的自动生成:
- 复制构造函数；
- 复制赋值运算符；
- 另一个移动操作；
- 析构函数。

> 这里记不住也没事，可以往下看到[特殊成员函数](#特殊成员函数)这一小节，合起来一起记。

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
- 成员中使用了引用语义（指针，智能指针，···）；
- 对象没有默认构造。

我的理解/例子：
- 值的限制： 值的限制可能导致移出对象未指定的值非法，导致移出对象进入非一致状态；
- 值相互依赖： 
- 引用语义： 与上面这个可能同时出现，如果指向自身的某些内容，移动后可能指向无效内容。
- 对象没有默认构造： 无法生成一个空的默认构造函数，在这个基础上做移动操作。

原文：(我没理解)
> The problem that can occur is that moved-from objects might no longer be valid: invariants might be broken
or the destructor of the object might even fail. For example, objects of the Customer class in this chapter
might suddenly have an empty name even though we have assertions to avoid that. The chapter about
moved-from states will discuss this in detail.

### 实现复制和移动函数

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

在 *《Effective C++》*条款11/13/14中提到，当资源管理器正确封装时，一般自赋值不会出现问题（虽然那时还没有移动语义）；C++核心指南也表示这是“百万分之一的问题”。看起来在大部分情况下，保证需要遵循和STL一样的标准即可，仍然需要保证自移动后对象处于有效但未定义状态。

原书中提供了[上述例子](#实现复制和移动函数)调用和执行的例子以观察代码行为，建议都搞下来跑一跑看看。测试样例代码：

```cpp
#include "customerimpl.h" // 上面实现的例子
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>

int main()
{
    std::vector<Customer> coll;
    for (int i=0; i<12; ++i) {
        coll.push_back(Customer{"TestCustomer " + std::to_string(i-5)});
    }
    std::cout << "---- sort():\n";
    std::sort(coll.begin(), coll.end(),
        [] (const Customer& c1, const Customer& c2) {
            return c1.getName() < c2.getName();
        });
}
```

### 特殊成员函数的规则

这小节讨论六个特殊成员函数，特别讨论复制和移动成员函数何时以及如何生成（when and how）。

#### 特殊成员函数

C++标准将定义了六个特殊成员函数（*special member functions*）：
- 默认构造
- 拷贝构造
- 拷贝赋值操作符
- 移动构造（since C++11）
- 移动赋值操作符（since C++11）
- 析构

默认构造与其他五个稍有不同，因为其他特殊成员函数没有需要的话一般都不声明且有更多复杂的依赖。编译器生成的默认构造函数为一个没有参数的构造函数。下图给出了何时自动生成特殊成员函数，取决于声明了哪个（其他）构造函数和特殊成员函数。

![special member functions](/assets/img/posts/2024-08-06-move_semantics_2/image1.png){: width="694" height="425" }
_special member functions_

从图里可以总结几个规则：
- 默认构造函数只会在开发者没有声明任何构造函数（包括自定义的默认/拷贝/移动/各种奇怪参数的构造）时自动声明；
- 开发者声明拷贝成员函数（拷贝构造**或**拷贝赋值操作符）**或**析构函数（正如[类中自动启用移动语义的场景](#类中自动启用移动语义的场景)中所讨论的）会禁用移动函数的自动生成，但是仍可以按照移动函数传参的方式调用（除非显式删除），但执行语义上回回退到拷贝语义；
- 开发者声明移动成员函数会禁用拷贝函数和（另一个）移动函数的自动生成，因此调用者只能移动而不能拷贝对象，此时另一个移动函数的拷贝回退也被禁用了（除非主动声明函数）；

以下介绍一些细节和使用场景(当然如果你这里完全懂了，可以不看细节直接跳到[下一小节](#三五法则)，如果只需要一部分细节可以[跳到节尾](#特殊成员函数的准确规则)，否则的话还是根据具体例子理解下)。

#### 默认情况下的拷贝和移动

以下给出例子，例子中不定义任何特殊成员函数。

```cpp
class Person {
    // ...
public:
    // ...
    // NO copy constructor/assignment declared
    // NO move constructor/assignment declared
    // NO destructor declared
};
```

在此情况下，编译器会生成默认的成员函数，实例化的对象可以进行拷贝和移动：

```cpp
std::vector<Person> coll;

Person p{"Tina", "Fox"};        // ? // 这个不是默认构造函数

coll.push_back(p);              // OK, copies p
coll.push_back(std::move(p));   // OK, moves p
```


这里的`Person`实例化用的不是[默认构造函数](https://en.cppreference.com/w/cpp/language/default_constructor)，到底是什么我也不知道。有懂哥可以帮我解释一下。

#### 使用拷贝语义并禁用移动语义

开发者声明拷贝成员函数（拷贝构造**或**拷贝赋值操作符）**或**析构函数会禁用移动函数的自动生成，以下给出一个声明了拷贝函数例子：

```cpp
class Person {
    // ...
public:
    // ...
    // copy constructor/assignment declared:
    Person(const Person&) = default;
    Person& operator=(const Person&) = default;
    // NO move constructor/assignment declared
};
```

在此情况下，移动语义会被禁用，移动操作回回退到拷贝语义，比如下面例子中试图移动对象的例子：

```cpp
std::vector<Person> coll;

Person p{"Tina", "Fox"};
coll.push_back(p);              // OK, copies p
coll.push_back(std::move(p));   // OK, copies p
```

因此，使用`=default`来声明特殊成员函数和不声明它是不一样的！当使用`=default`后，函数被认为是自定义（user-defined）的。自定义的拷贝函数和析构函数会禁用移动函数的自动生成。

将移动函数声明为`=delete`来禁用移动语义并不是一个好选择，因为其会导致回退拷贝机制失效。如果需要禁用移动语义，只需要声明一个拷贝函数（或者两个都声明为默认，因为只声明一个有点令人费解）或者析构函数`=default`即可。

#### 使用移动语义并禁用拷贝语义

由开发者自行声明的（包括自行实现，`=default`，甚至指定`=delete`）移动函数，则会禁用拷贝语义（如果拷贝函数没有声明的话），默认生成的拷贝函数会被删除。参考以下例子：

```cpp
class Person {
    // ...
public:
    // ...
    // NO copy constructor declared
    // move constructor/assignment declared:
    Person(Person&&) = default;
    Person& operator=(Person&&) = default;
};
```

由于拷贝语义被禁用，类型只接受移动对象的操作。注意！这里不能只声明一个函数为`=default`了，因为只声明一个另一个移动函数将被禁用，会造成移动语义的不完整。

```cpp
    std::vector<Person> coll;

    Person p{"Tina", "Fox"};
    coll.push_back(p);                      // ERROR: copying disabled
    coll.push_back(std::move(p));           // OK, moves p
    coll.push_back(Person{"Ben", "Cook"});  // OK, moves temporary person into coll
```

这里又一次可以看出，声明一个特殊成员函数为`=default`与不声明之完全不同，而且这里完全改变了对象的行为：试图使用拷贝语义的行为被拒绝了。

只支持移动语义的（**move-only**）类在需要严格管理对象所有权时是很有意义的。比如C++标准库中就有一些只支持的类，比如`I/O stream`，`std::thread`，`std::unique_ptr<>` 等。后续会在第13章介绍只支持移动语义的类。

#### 删除移动没有意义


同时禁用移动语义和拷贝语义的情况下，如果将移动函数声明为`=delete`（delete一个另一个自动禁用，但建议声明上保持一致），则会禁用默认拷贝函数的生成，对象同时失去移动和拷贝语义。

```cpp
class Person {
public:
    //...
    // NO copy constructor declared
    // move constructor/assignment declared as deleted:
    Person(Person&&) = delete;
    Person& operator=(Person&&) = delete;
    //...
};
Person p{"Tina", "Fox"};
coll.push_back(p);              // ERROR: copying disabled
coll.push_back(std::move(p));   // ERROR: moving **disabled**
```

同样效果可以直接将拷贝函数声明为`=delete`来实现，因为声明拷贝函数的会禁用移动函数生成。

如果只需要拷贝语义而禁用移动语义，如果将移动函数声明为`=delete`，可以达到效果，但是移动函数的拷贝回退将会失效，比如：

```cpp
class Person {
public:
    // ...
    // copy constructor explicitly declared:
    Person(const Person& p) = default;
    Person& operator=(const Person&) = default;
    // move constructor/assignment declared as deleted:
    Person(Person&&) = delete;
    Person& operator=(Person&&) = delete;
    // ...
};
Person p{"Tina", "Fox"};
coll.push_back(p);              // OK: copying enabled
coll.push_back(std::move(p));   // ERROR: moving disabled
```

所以将移动函数声明为`=delete`同样没有意义，尽管行为不完全等于不声明移动函数。需要拷贝语义的时候可以声明拷贝函数（如果不需要修改默认实现声明为`=default`即可），则已经禁用移动函数生成。

所以这里得出一个关键条款：

> 永远不要将移动构造和移动赋值操作符函数声明为`=delete`.
{: .prompt-tip }

如果相同时禁用拷贝和移动语义，将拷贝函数声明为`=delete`即可。

#### 移动包含禁用移动语义成员类型的对象

生成的移动语义执行上在处理成员变量时，如果该类型支持移动，则执行其移动语义，否则创建其一个副本。比如，存在一个不支持移动的类型：

```cpp
class Customer {
public:
    // ...
    Customer(const Customer&) = default;                // copying calls enabled
    Customer& operator=(const Customer&) = default;     // copying calls enabled
    // 根据上文的规则，这里不声明也会禁用移动语义，显式声明= delete在禁用移动语义的同时还失去了回退拷贝的特性
    // Customer(Customer&&) = delete;                      // moving calls disabled
    // Customer& operator=(Customer&&) = delete;           // moving calls disabled
};
```

而另一个类包含该类型作为成员变量：

```cpp
class Invoice {
    std::string id;
    Customer cust;
    public:
        // ... // no special member functions
};

Invoice i;
Invoice i1{std::move(i)}; // OK, moves id, copies cust
```

由于这个类没有定义任何特殊的成员函数，自动生成拷贝和移动语义的成员函数，在执行移动时，`string`成员将被移动，`Customer`成员将被拷贝。

#### 特殊成员函数的准确规则

回到本节的目标，这里解析特殊成员函数生成规则及其行为（when and how）。

- 拷贝构造函数：
  - 以下条件满足时自动生成拷贝构造函数：
    - 没有声明移动构造函数；
    - 没有声明移动赋值运算符；
  - 如果是默认生成的（隐式或者用`=default`声明），拷贝构造有以下行为：
    - 选择基类最匹配的拷贝构造，倾向调用相同声明的（一般声明const&），没有再匹配下一个最匹配的（比如拷贝构造函数模板）；
    - 调用基类的的拷贝构造函数（拷贝构造总是从基类到子类的），然后调用成员变量的拷贝构造；
    - 如果所有的基类以及所有的成员变量的拷贝构造函数都声明了`noexcept`，则该拷贝构造函数也会声明`noexcept`。

```cpp
MyClass(const MyClass& obj) noexcept 
    : Base(obj), value(obj.value) {
}
```

- 移动构造函数：
  - 以下条件满足时自动生成移动构造函数：
    - 没有声明拷贝构造函数；
    - 没有声明拷贝赋值运算符；
    - 没有声明移动赋值运算符；
    - 没有声明析构函数；
  - 如果是默认生成的（隐式或者用`=default`声明），移动构造有以下行为：（其实是类似拷贝构造的）
    - 使用基类和成员移动语义时需要`std::move`标记参数;
    - 选择基类最匹配的移动，倾向调用相同声明的（一般声明&&），没有再匹配下一个最匹配的（比如移动构造函数模板甚至拷贝构造函数）；
    - 调用基类的的移动构造函数（移动构造也是从基类到子类的），然后调用成员变量的移动构造；
    - 如果所有调用的移动/拷贝操作都声明了`noexcept`，则该移动构造函数也会声明`noexcept`。

```cpp
MyClass(MyClass&& obj) noexcept 
    : Base(std::move(obj)), value(std::move(obj.value)) {
}
```

- 拷贝赋值操作符：
  - 以下条件满足时自动生成拷贝赋值操作符：
    - 没有声明移动构造函数；
    - 没有声明移动赋值运算符；
  - 如果是默认生成的（隐式或者用`=default`声明），拷贝赋值操作符有以下行为：
    - 选择基类最匹配的拷贝赋值，倾向调用相同声明的，没有再匹配下一个最匹配的；
    - 调用基类的的拷贝赋值，然后调用成员变量的拷贝赋值；
    - 注意，默认没有检查自赋值！如果有问题需要自行校验；
    - 如果所有的基类以及所有的成员变量的拷贝赋值都声明了`noexcept`，则该拷贝赋值操作符也会声明`noexcept`。

```cpp
MyClass& operator= (const MyClass& obj) noexcept {
    Base::operator=(obj);       // - perform assignments for base class members
    value = obj.value;          // - assign new members
    return *this;
}
```

- 移动赋值操作符
  - 以下条件满足时自动生成移动赋值操作符：
    - 没有声明拷贝构造函数；
    - 没有声明移动构造函数；
    - 没有声明拷贝赋值运算符；
    - 没有声明析构函数；
  - 如果是默认生成的（隐式或者用`=default`声明），移动赋值操作符有以下行为：（其实是类似拷贝赋值操作符的）
    - 使用基类和成员移动语义时需要`std::move`标记参数;
    - 选择基类最匹配的移动赋值，倾向调用相同声明的，没有再匹配下一个最匹配的；
    - 调用基类的的移动赋值，然后调用成员变量的移动赋值；
    - 注意，默认没有检查自赋值，自赋值会使对象进入有效但未指定状态！如果有问题需要自行校验；
    - 如果所有调用的移动/拷贝赋值操作都声明了`noexcept`，则该移动赋值操作符也会声明`noexcept`。

```cpp
MyClass& operator= (MyClass&& obj) noexcept {
    Base::operator=(std::move(obj));    // - perform move assignments for base class members
    value = std::move(obj.value);       // - move assign new members
    return *this;
}
```

有一个比较特别的点是，基类的移动赋值已经使用了参数，该对象已经进入有效但未指定的状态。但是对于基类函数，派生类的成员是不可见的，仍然可以使用该对象的派生类成员变量。

- 其他赋值操作符
  - 析构函数：
    - 除了其声明会禁用移动语义无其他作用；
  - 默认构造函数：
    - 任何构造函数的声明会禁用默认构造函数的生成。

移出对象的状态一般会使默认后遭函数构造的状态，且该状态应该是可析构的。

### 三五法则

由于上述规则中特殊成员函数间依赖之复杂，大多数程序员都没记住。所以需要一些比较好记的法则用以实际应用。

三五法则：
- 三法则（C++11之前）：要么同时声明三个特殊函数（拷贝构造，拷贝赋值，析构），要同时不声明之；
- 五法则（C++11之后）：要么同时声明五个特殊函数（拷贝构造，拷贝赋值，移动构造，移动赋值，析构），要同时不声明之；

其中，声明（declaring）指的是以下任意一种方式：
- 实现（`{...}`）;
- 声明为默认实现（`=default`）；
- 删除实现（`=delete`）。
  
也就是说，当其中一个被声明，则另外四个必须同时被声明（实现/`=default`/`=delete`）。

五法则有个问题，如果只需要拷贝语义的时候，其实只声明拷贝函数即可。但是五法则要求声明五个函数，移动函数声明`=delete`会导致回退拷贝失效，`=default`与实现目标不符合，自行实现则相对非常复杂且行为怪异。

因此，三五法则在使用时应该注意：
- 如果同时声明了五个函数，仔细思考其行为和依赖；
- 如果不熟悉移动语义，建议只实现三个函数（拷贝构造，拷贝赋值，析构），如果不需要移动语义，声明（可以使用`=default`）拷贝函数以禁用移动函数。