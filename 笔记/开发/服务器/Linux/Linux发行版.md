# Linux 发行版

Linux 系统并不利于发行，对于一般人来说，使用 Linux 仍然存在困难，于是很多软件公司将自己定制的软件以及安装程序，软件分发平台等等整合进入 Linux 系统，形成一个完整的软件系统包。所以也就做 Linux 发行版，也叫做 Linux 发布商业套件，Linux distribution。

Linux 发行版（也称为 Linux 发行套件）是基于 Linux 内核，集成了各种软件包、工具和应用程序的完整操作系统版本。由于 Linux 的开源特性，全球众多社区和组织开发了多种发行版，以满足不同用户的需求和偏好。

![一张图看懂 主流Linux发行版 家族- Community - Deepin Technology](http://public.file.lvshuhuai.cn/images\202101112228102239_Linux发行版4.png)

**主要的 Linux 发行版及其家族：**

1. **Debian 系：**
    - **Debian**：以稳定性和对自由软件的支持而闻名，许多其他发行版都是基于 Debian 开发的。
    - **Ubuntu**：基于 Debian，注重用户友好性，广受欢迎。
        - **Linux Mint**：基于 Ubuntu，提供更传统的桌面体验。
        - **Kali Linux**：基于 Debian，专注于渗透测试和安全研究。
2. **Red Hat 系：**
    - **Red Hat Enterprise Linux (RHEL)**：面向企业的商业发行版，提供长期支持和服务。
    - **CentOS**：RHEL 的社区版本，提供与 RHEL 相同的功能，但不包含官方支持。
    - **Fedora**：由 Red Hat 赞助的社区发行版，包含最新的技术和功能。
3. **SUSE 系：**
    - **openSUSE**：由社区驱动的发行版，提供稳定和滚动更新两种版本。
    - **SUSE Linux Enterprise**：面向企业的发行版，注重稳定性和支持。
4. **Arch系：**
    - **Arch Linux**：以简洁和用户自定义为特点，采用滚动更新模式。
    - **Manjaro**：基于 Arch，提供更易于安装和使用的体验。
5. **Gentoo 系：**
    - **Gentoo**：强调从源代码编译，提供高度的自定义能力。

## Linux 完整家族树

下图展示了 Linux 发行版的家族树，清晰地描绘了各个发行版之间的关系和演变：

![image-20250213152555345](http://public.file.lvshuhuai.cn/images\image-20250213152555345.png)

## Linux 发行版和 Linux 内核版本关系

Linux 指的是：Linux 内核+各种软件

Linux 发行版：Linux 内核+软件+工具+可安装程序。

简单来说：Linux 发行版是基于某一个 Linux 内核增加发行商自定义的一些特定功能软件等等东西，形成发行版。

所有内核都是 [Linux 内核发布网站](https://www.notion.so/www.kernel.org)所发布，提供的软件都是知名软件包。（分发公司不可能选择一些陌生软件给用户，这只会使得用户放弃）。

## 发行版本规范

为了避免出现各个版本之间对于用户来说使用上的冲突，形成各个版本约束。

举例子：同一个发行版新增目录，定义用途不同，那么对于用户来说完全不可接受。

**LSB 规范（Linux Standard Base）规范**：标准化软件系统结构，包括**文件系统层次结构标准 FHS**

**规范目录结构**：File System Hierachymoshi 规范：是一[个描述类 Unix](https://en.wikipedia.org/wiki/Unix-like) 系统**布局约定的参考**