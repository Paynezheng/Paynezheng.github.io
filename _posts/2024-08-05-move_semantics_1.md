---
title: Move Semantics Ⅰ
date: 2024-08-05 20:00:00 +0800
categories: [Tech, C++]
tags: [server, c++]     # TAG names should always be lowercase
description: C++移动语义.
math: true
mermaid: true
---

《C++标准库》的作者 Nicolai M.Josuttis 的几本C++教程都挺好的，可惜只有关于C++11的这本书被侯捷翻译过来。《[C++ Move Semantics, the complete guide](https://www.cppmove.com/)》英文原版涵盖了从C++11到C++20的移动语义，我读的版本时2020-12-19，读后收益良多。这里本想写的是读书笔记，但是看上去大部分还是按照原文翻译的，英文功底有限，技术上的语言上的都欢迎指正（拉到最底下有评论区）。

书中的例子讲述的例子其实知识点重复冗余较多，但是这样也更好的使得每一节的知识点能更少地依赖上文。如果只是不清楚某个点可以直接按照目录查阅，而不需要从头阅读，从头阅读的话后续遇到一些重复叙述的点也能较快理解。有些词我翻译了会随便用，比如拷贝和复制我会混着用···emmmmmm····也懒得改了。（不过这个复制听起来跟赋值有点像，记成拷贝就好多了）

本文内容包括《C++ Move Semantics, the complete guide》的第1~2章。

## 基础语义

### 移动语义的动机

下文中给出一段代码行为在C++03和C++11两个标准下的不同实现（只是略微不同，不同点在于C++11使用了移动语义的工具）和行为对比，从而简单理解移动语义的用法和优化目的。

#### C++03 样例

以下给出一段C++03标准的代码（不支持移动语义）：
```cpp
#include <string>
#include <vector>

std::vector<std::string> createAndInsert() {
    std::vector<std::string> coll;  // 构造vector
    coll.reserve(3);                // 申请空间
    std::string s = "data";         // 创建string对象

    coll.push_back(s);              // 拷贝string对象，拷贝得到的对象会插入vector
    coll.push_back(s + s);          // 构造，拷贝，销毁临时对象
    coll.push_back(s);              // 拷贝string对象，拷贝得到的对象会插入vector

    return coll;                    // NVRO/拷贝
}

int main() {
    std::vector<std::string> v;     // 构造vector
    // ...
    v = createAndInsert();          // 拷贝，销毁临时对象
    // ...
}
```

从内存的分配和回收角度，这段函数的执行步骤包括：
1. 进入main函数，构造vector v；
2. 调用createAndInsert，进入createAndInsert函数，构造vector coll；
3. 申请分配coll容量，这里申请了三个对象的容量；
4. 创建字符串对象s；
5. 拷贝s，并将拷贝得到的对象插入到了vector空间内，至此C++11尚无可以优化的点；
6. 构造一个s+s的临时对象，并拷贝临时对象，将拷贝得到的对象插入到了vector空间内，随后销毁临时对象；
7. 拷贝s，并将拷贝得到的对象插入到了vector空间内，在此之后s将不再使用；
8. 返回coll，这里可能需要将coll拷贝到返回值中，即需要拷贝一个vector和三个字符串对象，然后再销毁coll；但编译器普遍的实现是这里执行NRVO（*Name Return Value optimization*），无需拷贝直接返回了coll；
9. v接受creatAndInsert()函数返回值的拷贝，creatAndInsert()函数返回值作为临时变量被销毁。

[(N)RVO(*(Named) Return value optimization*)](https://en.cppreference.com/w/cpp/language/copy_elision)，即（命名）返回值优化，指的是编译器会自行选择，在返回命名对象或者临时对象时，是否采用直接返回，而省略从命名对象/临时对象(还可能是移动)拷贝到返回的临时对象的过程。该优化由编译器决定，一般不对其做假设。若假定其行为则执行结果无法预估。比如构造函数中包含输出，无法预期该输出是否执行。

除去NRVO可以优化的部分，上述的执行中额外的内存开销包括：
1. 步骤6中构造了两个相同临时对象，销毁了一个临时对象，产生浪费；
2. 步骤7中拷贝一个后续不再使用的对象；
3. 步骤9中接受返回值作为临时对象拷贝后，销毁了临时对象。

#### C++11 样例

以下给出一段C++11标准的代码（支持移动语义）：
```cpp
#include <string>
#include <vector>

std::vector<std::string> createAndInsert() {
    std::vector<std::string> coll;  // 构造vector
    coll.reserve(3);                // 申请空间
    std::string s = "data";         // 创建string对象

    coll.push_back(s);              // 拷贝string对象，拷贝得到的对象会插入vector
    coll.push_back(s + s);          // 构造，移动，销毁临时对象
    coll.push_back(std::move(s));   // 移动string对象

    return coll;                    // NVRO/移动
}

int main() {
    std::vector<std::string> v; // 构造vector
    // ...
    v = createAndInsert();      // 移动临时对象，而后销毁临时对象
    // ...
}
```

从内存的分配和回收角度，这段函数的执行步骤包括：
1. 进入main函数，构造vector v；
2. 调用createAndInsert，进入createAndInsert函数，构造vector coll；
3. 申请分配coll空间；
4. 创建字符串对象s；
5. 拷贝s，并将拷贝得到的对象插入到了vector空间内，至此C++11尚无可以优化的点；
6. 构造一个s+s的临时对象，并**移动临时对象**，将移动得到的对象插入到了vector空间内，随后销毁临时对象；
7. 移动s，并将**移动得到的对象**插入到了vector空间内，在此之后s将不再使用，知道离开作用域调用构造函数；
8. 返回coll，这里可能需要将coll移动到返回值中，然后再销毁coll；更大的可能是这里发生NRVO（*Name Return Value optimization*），无需拷贝直接返回了coll；
9. creatAndInsert()**函数返回值移动**到v中，creatAndInsert()函数返回值作为临时变量被销毁。

对比与C++03中行为的不同之处，主要是：
1. 临时对象自行发生了对象移动；
2. 使用`std::move`标记的对象将其自身移动到了新对象中。

移动对象行为不同于拷贝将内存部分进行了**深拷贝**，移动行为将原有对象的内存和状态转移给了新对象，但未销毁原有对象。按照C++标准规定，原有对象经过移动操作后，后文称之为**移出对象（Move-from Object）**，应处于**有效但未指定(Valid but unspecifued)**的状态。即该对象的状态是一致的，仍然可以访问值和方法，但是状态和值处于未指定状态。

`std::move`直接调用本身并不对原对象做任何操作，仅作标记作用，意思是“我不在需要这个值”，因此可以显式指定支持移动语义的对象执行移动行为。

后续关于移出对象和`std::move`都会详细解释。

步骤8中依旧可能调用NRVO，一般来说，函数返回值的来源可能是：
1. 如果编译器实现了NRVO/RVO，则来源于命名对象/临时对象；
2. 如果没有实现NRVO/RVO，但是返回值类实现了移动语义，则会将命名对象/临时对象移动到返回值中；
3. 以上都没有，那就相当于没有优化，需要拷贝；
4. 连拷贝都没有，寄。

### 移动语义的实现

移动语义实现前，`std::vector`只有拷贝语义：
```cpp
template<typename T>
class vector {
public:
    void push_back(const T& elem);
    // ... 
}
```
push_back调用会将参数绑定到const引用上，随后在函数内部对参数进行拷贝。函数内部const引用是只读的。

C++11开始，新增了push_back的一个函数重载：
```cpp
template<typename T>
class vector {
public:
    //...
    // insert a copy of elem:
    void push_back (const T& elem);
    // insert elem when the value of elem is no longer needed:
    void push_back (T&& elem);
    //...
};
```

带有两个&的类型被称为右值引用，一般只有一个&的被称为左值引用，两个函数区别在于：
1. `push_back(const T&)`承诺不修改引用内容，函数调用后引用对象可继续正常使用；
2. `push_back (T&& elem)`可以修改引用内容（因此不是`const`），函数调用后引用对象有效但未指定。

在使用`std::vector`时，当调用者不再需要所传的值时会调用函数重载2。有两种情况编译器会认为调用者不再需要所传的值：
1. 临时对象；
2. `std::move`指定的非`const`命名对象。

使用了push_back的移动语义之后，实际的移动行为（或者是否定义移动行为）定义在模板T中，以下以`string`为例，简单了解拷贝和移动语义实现代码上的区别。(emmm... 实际的`string`代码当然不会这么简单)

#### 拷贝构造代码实现

拷贝构造拷贝对象内存空间（不是拷贝指针），以及对象状态。
```cpp
class string {
private:
    int len;        // current number of characters
    char* data;     // dynamic array of characters
public:
    // copy constructor: create a full copy of s:
    string (const string& s) : len{s.len} { // copy number of characters
        if (len > 0) { // if not empty
            data = new char[len+1]; // - allocate new memory
            memcpy(data, s.data, len+1); // - and copy the characters
        }
    }
    //...
};
```

#### 移动构造代码实现

移动构造函数获取移出对象的内存空间和状态，并将后者的状态和内存空间设为未指定状态。（移出对象未销毁，仍需要析构）
```cpp
class string {
private:
    int len; // current number of characters
    char* data; // dynamic array of characters
public:
    //...
    // move constructor: initialize the new string from s (stealing the value):
    string (string&& s) : len{s.len}, data{s.data} { // copy number of characters and pointer to memory
        s.data = nullptr; // release the memory for the source value
        s.len = 0; // and adjust number of characters accordingly
    }
    //...
};
```

### 回退拷贝

假设有一个容器类，只实现了拷贝语义，如：
```cpp
template<typename T>
class MyVector {
public:
    void push_back(const T& elem);
    // ... 
}
```

如下的代码中，push_back函数仍然可以接受临时对象和`std::move`指定的非`const`命名变量。这样的场景下编译器优先选择参数定义了右值引用的函数，如果没有这样的函数再选择实现拷贝语义的函数。

```cpp
MyVector<std::string> coll;
std::string s{"data"};
...
coll.push_back(std::move(s)); // OK, uses copy semantics
```

一般来说，指定了`std::move`来传递函数参数但是没有获得移动语义的优化有两个目的：
1. 该函数/类型未支持移动语义；
2. 没有可优化的空间（比如基础类型int/long之类的移动）。

### const对象的移动语义

#### 试图移动const对象
[上文中提到](#移动构造代码实现)，移动语义可能对移出对象进行修改，因此`const`对象无法实现移动语义，因为无法修改`const`对象。如果`std::move`指定`const`对象，函数会回退到拷贝语义版本。（所以这里的`std::move`啥都没干）

```cpp
std::vector<std::string> coll;
const std::string s{"data"};
...
coll.push_back(std::move(s)); // OK, calls push_back(const std::string&)
```

原则上，可以定义一个接受const右值引用参数的函数，但是const右值引用一般来说没有什么意义。（有这个东西，但没卵用）

#### const返回值

如果将返回值定义为`const`，返回值则无法使用移动语义。因此C++11之后将返回值定义为`const`不是一个好习惯。比如以下场景，会导致回退到拷贝语义：

```cpp
const std::string getValue();
std::vector<std::string> coll;
// ...
coll.push_back(getValue());     // copies (because the return value is const)
```

推荐的风格是，如果要限制对象的读写权限，可以使用const声明部分返回值，而不要声明整个返回值，比如：

```cpp
const std::string getValue();   // BAD: disables move semantics for return values
const std::string& getRef();    // OK
const std::string* getPtr();    // OK
```

## Core Feature

在了解了移动语义的例子之后，本章讨论移动语义中几个基本概念。

### 右值引用

右值引用使用两个&号声明，根据其语义，其只能引用临时对象和使用`std::move`标记的非`const`命名变量。与普通引用类似的是，右值引用也可以延长命名变量的生命周期，直到右值引用的生命周期结束。参考以下例子：

```cpp
std::string returnStringByValue();          // forward declaration
std::string s{"hello"};
// ...
std::string&& r1{s};                        // ERROR
std::string&& r2{std::move(s)};             // OK
std::string&& r3{returnStringByValue()};    // OK, extends lifetime of return value
```

右值引用同样也能接受多种初始化方式，比如等号/大括号/括号：

```cpp
std::string s{"hello"};
// ...
std::string&& r1 = std::move(s);    // OK, rvalue reference to s
std::string&& r2{std::move(s)};     // OK, rvalue reference to s
std::string&& r3(std::move(s));     // OK, rvalue reference to s
```

#### 使用右值引用参数

参数声明右值引用的，只能接受右值引用参数或可以初始化右值引用的参数，如：

```cpp
void foo(std::string&& rv); // takes only objects where we no longer need the value
std::string s{"hello"};
// ...
foo(s);                     // ERROR
foo(std::move(s));          // OK, value of s might change
foo(returnStringByValue()); // OK
```

在该函数使用过右值后，移出对象进入有效但未指定状态，状态一致，但是内容和值可能为指定。其行为可以参考以下例子

```cpp
std::cout << s << '\n';     // OOPS, you don’t know which value is printed
foo(std::move(s));          // OOPS, you don’t know which value is passed
s = "hello again";          // OK, but rarely done
foo(std::move(s));          // OK, value of s might change
```

代码均可正常执行，但是前两行输出内容无法预测。由于该对象处于一致的状态，如果后续进行重新的拷贝，可以重复使用。

### std::move

`std::move`用以标记一个对象，表示“**我不在需要该值**”。这不代表原值的生命周期已经结束，已经销毁或者已经移动，事实上啥也没干。以下介绍`std::move`在不同场景中的使用效果。

在实现移动和拷贝语义重载的函数中，调用者借助`std::move`可以显式指定移动语义。

```cpp
void foo1(const std::string& lr); // binds to the passed object without modifying it
void foo1(std::string&& rv); // binds to the passed object and might steal/modify the value
...
std::string s{"hello"};
...
foo1(s); // calls the first foo1(), s keeps its value
foo1(std::move(s)); // calls the second foo1(), s might lose its value
```

只有拷贝语义（const引用）重载的函数在被调用时，使用`std::move`指定参数，函数的行为会回退到拷贝语义。

```cpp
void foo2(const std::string& lr); // binds to the passed object without modifying it
... // no other overload of foo2()
std::string s{"hello"};
...
foo2(s); // calls foo2(), s keeps its value
foo2(std::move(s)); // also calls foo2(), s keeps its value
```

接受非const左值引用参数的函数，无法匹配`std::move`的参数。

```cpp
void foo3(std::string&); // modifies the passed argument
...
std::string s{"hello"};
...
foo3(s); // OK, calls foo3()
foo3(std::move(s)); // ERROR: no matching foo3() declared
```

另外，临时对象在语义上会自动触发移动语义，无需标记为`std::move`。事实上，使用`std::move`标记临时对象可能会是一种**反向优化**。

#### 头文件
`std::move`定义在头文件`<utility>`中。

基本上所有的标准库中都包含`<utility>`，因此大部分使用了标准库组件的场景都无需显示指定头文件`<utility>`（比如[上文](#c11-样例)中使用了`std::move`，但只有`vector`头文件），但如果不使用标准库，记得带上`<utility>`。

#### std::move的实现

`std::move`使用`static_cast`，执行了源对象到右值引用的类型转换，所有使用`std::move`的地方也可以被替代为：

```cpp
foo(static_cast<decltype(obj)&&>(obj)); // same effect as foo(std::move(obj))
```

`static_cast`实现和`std::move`有一点点细微的区别，在 _值的类别_ 相关章节中进行介绍。


### 移出对象

使用移动语义之后，移出对象仍未（完全）被销毁，至少析构函数尚未被调用，其处于一个有效但未指定（Valid but unspecified）的状态，所有的值可状态均可访问，只是不知道其值指定的是什么。

#### 有效但未指定状态

上文中以做多次解释，此处仅给出例子理解：

```cpp
foo(std::move(s));                  // keeps s in a valid but unclear state
std::cout << s << '\n';             // OK (don’t know which value is written)
std::cout << s.size() << '\n';      // OK (writes current number of characters)
std::cout << s[0] << '\n';          // ERROR (potentially undefined behavior)
std::cout << s.front() << '\n';     // ERROR (potentially undefined behavior)
s = "new value";                    // OK

foo(std::move(s));                  // keeps s in a valid but unclear state
for (int i = 0; i < s.size(); ++i) {
    std::cout << s[i];              // OK
}
```

#### 移出对象复用

由于移出对象并未真正析构，在一些场景可以复用移出对象，以减少对象的重复构造。比如：

```cpp
std::vector<std::string> allRows;
std::string row;
while (std::getline(myStream, row)) {   // read next line into row
    allRows.push_back(std::move(row));  // and move it to somewhere
}
```

例子中，重复使用row对象获取输入，并将结果移动到向量空间内。

移出对象复用有一个非常实用的场景，参考以下一个实现了swap功能的泛型函数：

```cpp
template<typename T>
void swap(T& a, T& b)
{
    T tmp{std::move(a)};
    a = std::move(b);       // assign new value to moved-from a
    b = std::move(tmp);     // assign new value to moved-from b
}
```

类似于这样的移动swap实现，被广泛应用在stl的排序算法中。

#### 自移动

直接或者间接的自移动操作会导致对象进入有效但未指定状态。比如：

```cpp
x = std::move(x); // afterwards x is valid but has an unclear value
```

以上，C++标准库保证其实现满足上述标准，若自定类型需要实现移动语义，亦需满足以上特征。

### 不同引用参数的重载函数

这里总结一下，有三种传引用的参数类型：
- `void foo(const std::string& arg)`： 参数声明为const引用，意味着函数内只有读取权限，可以传所有类型匹配的参数：
  - 可修改的命名对象；
  - const命名对象；
  - 无名临时对象；
  - 使用`std::move`标记的对象。

该语义意味着我们赋予`foo`函数访问`arg`的读取权限，换言之，`arg`参数是函数的输入（*in*）参数。

- `void foo(std::string& arg)`： 参数声明为非const左值引用，意味着函数内有写入权限，这里即使类型匹配也不一定能匹配参数，类型匹配的情况下，此处仅能接受的参数为：
  - 可修改的命名对象。

该语义意味着我们赋予`foo`函数访问`arg`的写入权限，换言之，`arg`参数是函数的输出（*out*）或者输入输出（*in/out*）参数。

- `void foo(std::string&& arg)`： 参数声明为非const右值引用，意味着函数内有写入权限，同时限制了传入的内容，此处仅能接受的参数为：
  - 无名临时对象；
  - 使用`std::move`标记的对象。

该语义意味着我们赋予`foo`函数访问`arg`的写入权限以窃取（steal）其值。`arg`参数是函数的输入（*in*）参数，且后续调用者不在需要该值。

#### const 右值引用

技术上来看其实还有第四种传参数的引用类型：
- `void foo(const std::string&& arg)`： 参数声明为const右值引用，意味着函数内只有读取权限，同时限制了传入的内容，此处仅能接受的参数为：
  - 无名临时对象；
  - 使用`std::move`标记的对象。

移动语义中允许窃取右值引用参数的值，但是const又限制参数无法被修改值，产生了自身矛盾。因此const右值引用基本上没有或者很少使用（std::optional<>使用了），一般来说都直接使用const左值引用函数。

### 传值函数

定义传值的函数，移动语义也可能会自动使用。例子如下：
```cpp
void foo(std::string str);      // takes the object by value
std::string s{"hello"};
foo(s);                         // calls foo(), str becomes a copy of s
foo(std::move(s));              // calls foo(), s is moved to str
foo(returnStringByValue());     // calls foo(), return value is moved to str
```

实际上，该移动语义发生主要取决于参数类的实现。发生的行为类似于：
```cpp
std::string str
str = s;                        // copy
s = std::move(s);               // move
s = returnStringByValue();      // move
```

因此，在参数类型实现了移动语义的情况下，传值函数可以显式指定对象移动（指定了就一定移动），而使用右值引用参数则表示该函数体“可能移动对象”。