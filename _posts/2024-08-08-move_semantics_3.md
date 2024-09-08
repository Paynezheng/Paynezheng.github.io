---
title: Move Semantics Ⅲ
date: 2024-08-08 02:00:00 +0800
categories: [Tech, C++]
tags: [server, c++]      
description: C++移动语义.
author: Payne
pin: true
math: true
mermaid: true
---

本文是《C++ Move Semantics, the complete guide》第4章内容的读书笔记以及部分翻译。

## 如何从移动语义中受益

本章主要内容是普通代码（不包含特殊成员函数）如何从移动语义中获益，并对应介绍若干条款。

### 避免命名对象

根据我们之前所论述的，移动语义用于优化一个后续不再需要的值的使用。如果编译器发现使用的对象已经来到了其生命周期的末尾，将自动切换到移动语义。具体来说就是：
- 该语句使用的临时对象在语句结束后就会销毁；
- 以值返回一个局部对象；

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

根据我们之前所论述的，以值返回局部对象会自动使用移动语义（如果没有其他更优的优化的话），但是也有一些程序员为了保险，强制使用了`std::move`显式指定返回值：

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

本节介绍四种初始化成员的构造函数的传参方式，对比行为和性能上的区别，分别是：
- `const`左值引用；
- 左值引用；
- 传值；
- 右值引用。

节末会对比实现方式的优劣和适合的场景，根据其行为分析提供实现方案的选择。

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

如果是直接传值，那就只包括函数内的2次拷贝构造成员。

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

可以看出，传值函数在直接接受传值时，每个参数需要比定义`const`引用的构造多使用一次移动构造（但在C++11之前是多使用一次拷贝构造！）。例子3中传右值，可以触发`string`类型的移动语义(如果是不支持移动语义的类型，则退化为例子2的执行方式)，这里会将右值引用移动到参数*f/l*，然后*f/l*再移动到成员变量中。这里函数调用包括：
- 4次移动构造（0次内存分配）；
- 析构3个临时对象，析构前对象已被移动，firstname的析构函数暂时还不会被调用。

传值函数在直接接受传值时，每个参数需要比定义右值引用的函数也多使用一次移动构造。

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

明显可以看出，如果参数是可以使用移动语义的对象，这里减少了需要使用的移动构造函数的次数。但是，定义右值引用参数形式不能直接接受命名变量参数，比如：

```cpp
std::string name1{"Jane"}, name2{"White"};
Person p2{name1, name2};    // ERROR: can’t pass a named object to an rvalue reference
```

因此定义了右值引用的构造函数时，需要重载对应的`const`左值引用函数作为回退，为了覆盖`string`类型的直接传值，定义例子如下：

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

一般来说，出于性能的考虑我们都倾向于不去使用简单的定义`const`左值引用的构造函数。下文将测试对比上文中介绍的三种（不包含左值引用）定义构造函数的方式的性能对比，以三种不同的调用方式（临时变量，命名变量，`std::move`）调用构造函数：（为了防止SSO，这里专门用了比较长的字符串）

```cpp
#include <chrono>

// measure num initializations of whatever is currently defined as Person:
std::chrono::nanoseconds measure(int num)
{
    std::chrono::nanoseconds totalDur{0};
    for (int i = 0; i < num; ++i) {
        std::string fname = "a firstname a bit too long for SSO";
        std::string lname = "a lastname a bit too long for SSO";
        
        // measure how long it takes to create 3 Persons in different ways:
        auto t0 = std::chrono::steady_clock::now();
        Person p1{"a firstname too long for SSO", "a lastname too long for SSO"};
        Person p2{fname, lname};
        Person p3{std::move(fname), std::move(lname)};
        auto t1 = std::chrono::steady_clock::now();
        totalDur += t1 - t0;
    }
    return totalDur;
}
```

如果想自己跑一下测试，可以直接下载[代码文件*initperf.cpp*](https://cppmove.com/code/basics/initperf.cpp.html)跑一下所有的三个实现，包括测试SSO对性能的影响，了解对应不同实现的性能对比。

三个不同实现运行效果区别：
- `const`左值引用构造明显慢于其他构造（有时甚至是2倍的时间差距？）；
- 传值构造和右值引用重载构造没有明显的性能差异，两者速度不相上下；
- 如果使用了SSO，则移动构造和拷贝构造没有明显区别，几种方式的性能会更接近。

```text
# initperf.cpp的一次执行结果
  a: classic:       0.04503ms
  b: all:           0.02425ms
  c: valmove:       0.02814ms
  d: classicSSO:    0.02472ms
  e: allSSO:        0.01732ms
  f: valmoveSSO:    0.01959ms
```

但是如果类型中包含一个无法用移动语义优化的，拷贝开销还非常大的类型，传值函数将面临甚至两倍的开销，比如对于以下类型：

```cpp
class Person {
private:
    std::string name;
    std::array<double, 10000> values; // move can’t optimize here
    public:
    // ...
};
```

每次移动和拷贝都无法避免需要拷贝values中这10000个基本类型。具体性能表现可以下载[*initbigperf.cpp*](https://cppmove.com/code/basics/initbigperf.cpp.html)进行测试。

```text
# initbigperf.cpp的一次执行结果
  a: bigclassic:    5.50814ms
  b: bigall:        5.44619ms
  c: bigmove:       10.6304ms
  d: bigclassicSSO: 5.30286ms
  e: bigallSSO:     5.27824ms
  f: bigmoveSSO:    10.5696ms
```

#### 总结

> 想要使用移动语义优化类型（包括支持移动语义的成员）的构造，有两个可选方案：
1. 使用传值的函数，并将所传的值move到成员中，所传的值来源于移动还是拷贝由使用者决定；
2. 移动构造开销较大的情况下，重载构造函数，使得每一个参数都包含支持右值引用和const左值引用两个版本。
{: .prompt-tip }

使用传值的函数定义简单，但是会导致多余的移动操作。如果移动操作也有巨大开销，那最好还是选择重载所有构造函数。

除了构造函数，传值并移动参数值并不适合所有场景。这*取决于成员是否已经有值，如果已有值*，这样实现可能导致反向优化。比如，以下有一个set方法采取了类似的实现，并按照其中的例子调用接口：

```cpp
class Person {
private:
    std::string first;  // first name
    std::string last;   // last name
    public:
    Person(std::string f, std::string l)
        : first{std::move(f)}, last{std::move(l)} {}

    void setFirstname(std::string s) {      // take by value
        first = std::move(s);               // and move
    }

    // 传统实现，这个函数确实可以和上面这个函数一起定义，但是最好不要这么做，
    // 调起接口非常地狱，编译器会常常不知道你想调什么接口
    void setFirstname(const std::string& s) { // take by reference
        first = s; // and assign
    }
};

Person p{"Ben", "Cook"};
std::string name1{"Ann"};
std::string name2{"Constantin Alexander"};

p.setFirstname(name1);
p.setFirstname(name2);
p.setFirstname(name1);
p.setFirstname(name2);
```

假设没有SSO，每次调用set方法：
- 传值函数都会拷贝创建临时对象，并将其移动到成员内，四次调用分配了四次内存；
- 传const引用，每次只会在原成员长度小于新长度时需要分配内存。

因此，如果成员已经包含了值，传值并移动的实现可能是反向优化。

构造函数之外，重载右值引用函数也不一定适合所有场景，也可能导致反向优化。因为移动语义收缩成员的内存容量，使得如果穿插调用传左值引用，不得不有多余的分配内存，比如：

```cpp
class Person {
private:
    std::string first;  // first name
    std::string last;   // last name
public:
    Person(std::string f, std::string l)
        : first{std::move(f)}, last{std::move(l)} {}
    // ...
    void setFirstname(const std::string& s) {   // take by lvalue reference
        first = s; // and assign
    }
    void setFirstname(std::string&& s) {        // take by rvalue reference
        first = std::move(s);                   // and move assign
    }
    // ...
};
Person p{"Ben", "Cook"};
p.setFirstname("Constantin Alexander");     // would allocate enough memory
p.setFirstname("Ann");                      // would reduce capacity
p.setFirstname("Constantin Alexander");     // would have to allocate again

```

综上，如果是更新或者是修改一个已初始化的成员，传统的定义`const`引用的方式更合适。如果是初始化成员，或者新增值，或者给容器新增成员等情况，可以考虑传值移动和重载右值引用函数两种实现方式。

### 继承关系中的移动语义

声明拷贝构造函数和析构函数会禁用移动语义的自动生成，这同样作用于多态基类。但在继承关系中，移动语义的实现还有一些其他方面需要考虑。

#### 实现多态基类

声明析构函数的时候必然禁用移动语义，如果基类中包含需要使用移动语义的成员，则需要显式声明移动成员函数。但是显式声明移动成员函数会禁用拷贝语义，如果需要保留拷贝语义，还需要声明拷贝函数。

如果上述这些特殊成员函数均被声明，可能导致出现切片（*slicing*）问题。

> 切片问题（Slicing Problem）是指当通过值传递或赋值操作将派生类对象赋值给基类对象时，派生类对象的特定部分（即派生类新增的成员变量和方法）被“切掉”或丢失，只保留基类部分。这会导致对象的多态性失效，并且可能引发未定义行为。

参考以下例子：

```cpp
Circle c1{1}, c2{2};

GeoObj& geoRef{c1};
geoRef = c2;            // OOPS: uses GeoObj::operator=() and assigns no Circle members
```

因为基类的赋值操作运算符没有声明`virtual`，所以只会使用指针类型对应的定义，导致其没有操作派生类的部分。即使指定了`virtual`也于事无补，因为派生类中的赋值操作运算符的参数类型与基类不同，无法`override`。为了避免切片问题，将基类定义为：

```cpp
class GeoObj {
protected:
    std::string name;                 // name of the geometric object

    GeoObj(std::string n)
        :name{std::move(n)} {}  
public:
    std::string getName() const {
        return name;
    }

    virtual void draw() const = 0;    // pure virtual function (introducing the API)
    virtual ~GeoObj() = default;      // would disable move semantics for name
protected:
    // enable copy and move semantics (callable only for derived classes):
    GeoObj(const GeoObj&) = default;
    GeoObj(GeoObj&&) = default;
    // disable assignment operator (due to the problem of slicing):
    GeoObj& operator= (GeoObj&&) = delete;
    GeoObj& operator= (const GeoObj&) = delete;
    //...
};
```

ps.虽然这样确实避免了切片问题···但是现在赋值运算符也用不了了，也不是什么好的解决办法···

更多参考:
- 《C++ Core Guideline》 [C.35](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#Rc-dtor-virtual) and C.67
- [compiler_explorer](https://github.com/nglee/compiler_explorer/blob/master/220329_move_in_class_hierarchy.cpp)

#### 实现派生类

一般来说，不需要在派生类中声明特殊成员函数。特别是没有需要实现的时候，不需要声明析构函数，否则又需要自行声明以启用移动语义。

如果声明了移动构造，要谨慎处理正确的`noexcept`条件。
