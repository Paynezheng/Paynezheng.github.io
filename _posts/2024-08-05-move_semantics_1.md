---
title: Move Semantivcs Ⅰ
date: 2024-03-01 20:00:00 +0800
categories: [Tech, C++]
tags: [Server, C++]     # TAG names should always be lowercase
description: C++移动语义.
---


## 基础语义

《C++标准库》的作者 Nicolai M.Josuttis 的几本C++教程都挺好的，可惜只有关于C++11的这本书被侯捷翻译过来。《C++ Move Semantics, the complete guide》英文原版完成于20年，涵盖了从C++11到C++20的移动语义。我没有整本翻译的动力，暂时写点读书笔记吧。

### 移动语义的动机

下文中给出一段代码行为在C++03和C++11两个标准下的不同实现（只是略微不同，不同点在于C++11使用了移动语义的工具）和行为对比，从而简单理解移动语义的用法和优化目的。

#### C++03 样例

以下给出一段C++03标准的代码（不支持移动语义）：
```C++
#include <string>
#include <vector>

std::vector<std::string> createAndInsert() {
    std::vector<std::string> coll;  // 构造vector
    coll.reserve(3);                // 申请空间
    std::string s = "data";         // 创建string对象

    coll.push_back(s);              // 复制string对象，复制得到的对象会插入vector
    coll.push_back(s + s);          // 构造，复制，销毁临时对象
    coll.push_back(s);              // 复制string对象，复制得到的对象会插入vector

    return coll;                    // NVRO/复制
}

int main() {
    std::vector<std::string> v; // 构造vector
    // ...
    v = createAndInsert();       // 复制，销毁临时对象
    // ...
}
```

从内存的分配和回收角度，这段函数的执行步骤包括：
1. 进入main函数，构造vector v；
2. 调用createAndInsert，进入createAndInsert函数，构造vector coll；
3. 申请分配coll空间；
4. 创建字符串对象s；
5. 复制s，并将复制得到的对象插入到了vector空间内，至此C++11尚无可以优化的点；
6. 构造一个s+s的临时对象，并复制临时对象，将复制得到的对象插入到了vector空间内，随后销毁临时对象；
7. 复制s，并将复制得到的对象插入到了vector空间内，在此之后s将不再使用；
8. 返回coll，这里可能需要将coll复制到返回值中，即需要复制一个vector和三个字符串对象，然后再销毁coll；更大的可能是这里发生NRVO（Name Return Value optimization），无需复制直接返回了coll；
9. v接受creatAndInsert()函数返回值的拷贝，creatAndInsert()函数返回值作为临时变量被销毁。

(N)RVO((Named) Return value optimization)，（命名）返回值优化指的是编译器会自行选择，在返回局部命名对象或者临时对象时，是否采用直接返回，而省略从局部命名对象/临时对象(还可能是移动)拷贝到返回的临时对象的过程。该优化由编译器决定，一般不对其做假设。若假定其行为（比如在构造函数中输出之类）结果无法预估。

出去NRVO可以优化的部分，上述的执行中额外的内存开销包括：
1. 步骤6中构造了两个相同临时对象，销毁了一个临时对象，产生浪费；
2. 步骤7中复制一个后续不再使用的对象；
3. 步骤9中接受返回值作为临时对象复制后，销毁了临时对象。

#### C++11 样例

以下给出一段C++11标准的代码（支持移动语义）：
```C++
#include <string>
#include <vector>
#include <utility> // for std::move

std::vector<std::string> createAndInsert() {
    std::vector<std::string> coll;  // 构造vector
    coll.reserve(3);                // 申请空间
    std::string s = "data";         // 创建string对象

    coll.push_back(s);              // 复制string对象，复制得到的对象会插入vector
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
5. 复制s，并将复制得到的对象插入到了vector空间内，至此C++11尚无可以优化的点；
6. 构造一个s+s的临时对象，并**移动临时对象**，将移动得到的对象插入到了vector空间内，随后销毁临时对象；
7. 移动s，并将**移动得到的对象**插入到了vector空间内，在此之后s将不再使用，知道离开作用域调用构造函数；
8. 返回coll，这里可能需要将coll移动到返回值中，然后再销毁coll；更大的可能是这里发生NRVO（Name Return Value optimization），无需复制直接返回了coll；
9. creatAndInsert()**函数返回值移动**到v中，creatAndInsert()函数返回值作为临时变量被销毁。

对比与C++03中行为的不同之处，主要是：
1. 临时对象自行发生了对象移动；
2. 使用std::move标记的对象将其自身移动到了新对象中。

移动对象行为不同于复制将内存部分进行了深拷贝，移动行为将原有对象的内存和状态转移给了新对象，但未销毁原有
对象。按照C++标准规定，原有对象经过移动操作后，后文称之为**移出对象（Move-from Object）**，应处于
**有效但未指定(Valid but unspecifued)**的状态。即该对象的状态是一致的，仍然可以访问值和方法，但是
状态和值处于未指定状态。

std::move直接调用本身并不对原对象做任何操作，仅作标记作用，意思是“我不在需要这个值”，因此可以显式指定支持
移动语义的对象执行移动行为。

后续关于移出对象和std::move都会详细解释。


步骤8中依旧可能调用NRVO，一般来说，函数返回值的来源可能是：
1. 如果编译器实现了NRVO/RVO，则来源于局部命名对象/临时对象；
2. 如果没有实现NRVO/RVO，但是返回值类实现了移动语义，则会将局部命名对象/临时对象移动到返回值中；
3. 以上都没有，那就相当于没有优化，需要复制；
4. 连复制都没有，寄。

### 移动语义的实现

假设有一个非常简易的只有复制语义的vector容器：
```C++
template<typename T>
class vector {
public:
    void push_back(const T& elem);
    // ... 
}
```

### 回退拷贝

### const对象的移动语义

## Core Feature

### 右值引用

### std::move

### 移出对象

### 不同引用参数的重载函数

### 传值函数
