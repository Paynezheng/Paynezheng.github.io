---
title: Move Semantics Ⅳ
date: 2024-08-10 02:00:00 +0800
categories: [Tech, C++]
tags: [server, c++]      
description: C++移动语义.
author: Payne
math: true
mermaid: true
---

本文是《C++ Move Semantics, the complete guide》第5章内容的读书笔记以及部分翻译。

## 重载引用限定符

如果不知道限定符是什么，本节中重载限定符有简单的[限定符介绍](#重载限定符)。

### get方法的返回类型

在实现有较高拷贝成本的成员类型的`get`方法时，C++11之前一般有两种方式：
- 以值返回；
- 以`const`左值引用返回。

这里简要介绍这两种方案。

#### 以值返回

get方法以值返回例子如下（注意：前面的章节提到过，不要返回const值，除非对于返回的值就是不想用移动语义）：

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

代码很安全，但每次调用该方法时，都需要进行一次拷贝。因为这里`name`生命周期和`Person`对象绑定，既不会触发NVO也不会使用移动语义。在很多场景会造成大幅开销增长，比如

```cpp
std::vector<Person> coll;
// ...
for (const auto& person : coll) {
    if (person.getName().empty()) { // OOPS: copies the name
        std::cout << "found empty name\n";
    }
}
```

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

这样实现性能优于以值返回但是稍微不安全，需要调用者注意引用的使用需要在所调用的对象的生命周期内。参考以下例子：

```cpp
for (char c : returnPersonByValue().getName()) { // OOPS: undefined behavior
    if (c == ' ') {
        // ...
    }
}

// 等价于
reference range = returnPersonByValue().getName();
// OOPS: returned temporary object destroyed here
for (auto pos = range.begin(), end = range.end(); pos != end; ++pos) {
    char c = *pos;
    if (c == ' ') {
        // ...
    }
}
```

例子中，`range`引用可以延长被引用对象的生命周期，但是其指向的是临时`Person`对象的成员。初始化语句结束后，临时`Person`对象调用析构函数，引用将使用析构后的字符串对象，产生未定义行为。

#### 使用移动语义

引入移动语义，实现上可以在对象安全时返回引用，而对象可能存在生命周期结束的情况下返回值，例子如下：

```cpp
class Person
{
private:
    std::string name;
public:
    // 这里的返回值标记了std::move，但标记的对象并不是局部对象，与之前的条款并不冲突
    std::string getName() && {      // when we no longer need the value
        return std::move(name);     // we steal and return by value
    }

    const std::string& getName() const & {   // in all other cases
        return name;                        // we give access to the member
    }
};
```

这里通过使用不同的引用限定符重载`get`方法来达到不同场景下调用不同的函数：
- 当使用临时对象或者`std::move`标记的对象调用函数，使用&&限定符的函数；
- 标记&限定符的函数可以应用于所有情况，一般如果不满足&&限定符函数的条件时，该函数可以作为其回退版本调用。

此情况下，`get`方法同时兼顾了性能和安全。参考以下调用的例子：

```cpp
Person p{"Ben"};
std::cout << p.getName();                           // 1) fast (returns reference)
std::cout << returnPersonByValue().getName();       // 2) fast (uses move())
std::vector<Person> coll;

// ...
for (const auto& person : coll) {
    if (person.getName().empty()) {                 // 3) fast (returns reference)
        std::cout << "found empty name\n";
    }
}

for (char c : returnPersonByValue().getName()) {    // 4) safe and fast (uses move())
    if (c == ' ') {
        // ...
    }
}

void foo()
{
    Person p{ ... };
    coll.push_back(p.getName());                // calls getName() const&
    coll.push_back(std::move(p).getName());     // calls getName() && (OK, p no longer used)
}
```

使用`std::move`标记的对象调用函数后，对象进入有效但未指定状态。返回的值可以使用移动语义插入到`coll`向量中。

C++标准库中，`std::optional<>`就使用了移动语义来优化其`get`方法。

### 重载限定符

> *函数的括号后的限定符用于限定一个不通过参数传递的对象，即该成员函数所属的对象本身。*

使用移动语义后，有了更多使用不同限定符的重载函数。以下例子给出所有引用限定符重载函数的例子和使用场景：

```cpp
#include <iostream>
class C {
public:
    void foo() const& {
        std::cout << "foo() const&\n";
    }
    void foo() && {
        std::cout << "foo() &&\n";
    }
    void foo() & {
        std::cout << "foo() &\n";
    }
    void foo() const&& {
        std::cout << "foo() const&&\n";
    }
};

int main()
{
    C x;
    x.foo();        // calls foo() &
    C{}.foo();      // calls foo() &&
    std::move(x).foo();     // calls foo() &&
    const C cx;
    cx.foo();       // calls foo() const&
    std::move(cx).foo();    // calls foo() const&&
}
```

注意！同时重载引用和无引用限定符是非法的！比如这样：

```cpp
class C {
public:
    void foo() &&;
    void foo() const; // ERROR: can’t overload by both reference and value qualifiers
};
```

### 何时使用引用限定符

引用限定符是我们可以根据对象的不同值类型来调用其不同的成员函数实现。

下文将讨论引用限定符使用场景，特别是使用此特性保证*将亡值*不再被修改（将亡值指即将被销毁的对象，因其即将被销毁，大部分对其进行修改的操作无意义）。

#### 赋值操作符的引用限定符

一般的赋值运算符实现赋值给一个临时对象：

```cpp
std::string getString();

getString() = "hello";  // OK
foo(getString() = "");  // passes string instead of bool
```

可以通过添加引用限定符的方式，限制只能赋值给左值，上述的赋值的操作将不再被允许。

```cpp
namespace std {
template<typename charT, ... >
class basic_string {
    public:
    // ...
    constexpr basic_string& operator=(const basic_string& str) &;
    constexpr basic_string& operator=(basic_string&& str) & noexcept( ... );
    constexpr basic_string& operator=(const charT* s) &;
    // ...
};
}
```

以下给出实现类时定义赋值操作运算符的例子，使用&限定之后则会自动禁用对临时对象的赋值（虽然我感觉没什么必要···谁会往临时对象上赋值啊···这么想的话C++标准库拒绝在所有的代码上应用这个修改好像也有道理···）。事实上，引用限定符也应该用于限制每一个*可能修改对象的成员函数*。

```cpp
class MyType {
public:
    // disable assigning value to temporary objects:
    MyType& operator=(const MyType& str) & =default;
    MyType& operator=(MyType&& str) & =default;
    // because this disables the copy/move constructor, also:
    MyType(const MyType&) =default;
    MyType(MyType&&) =default;
    // ...
};
```

#### 其他成员函数的引用限定符

正如第一小节所讨论的，当返回值为引用时，**应该**使用引用限定符。通过引用运算符重载，可以减少访问已销毁对象的成员的风险。当前的`string`就使用了此特性，当使用`[]`，`front()`，`back()`等操作访问对象中元素时，都能保证临时对象的销毁不会影响已获取的元素的使用。（这里代码就不贴了，有点长）