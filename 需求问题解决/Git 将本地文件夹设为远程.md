# Git 将本地文件夹设为远程

## 需求

我有一个 Git 仓库，令其为 `Z:\my_git`，该仓库位于我的 NAS 上。NAS 使用 smb 服务共享存储的文件，本地计算机使用`映射网络驱动器`将文件映射为 `Z:\`。

我现在想在本地计算机做该 Git 仓库的克隆。

如何做？

## 步骤

Git 支持从本地路径克隆仓库，可以直接进行 clone 操作。

在本地计算机上执行命令。

```bash
git clone Z:/my_git
```

命令执行完后，我们就在本地得到了一个 Git 仓库的克隆。

## 那么如何 push 呢？

我们执行

```bash
git remote -v
```

输出如下

```
origin  Z:/my_git (fetch)
origin  Z:/my_git (push)
```

如果我们直接执行 push 操作，大概率会报错

> (base) PS D:\my_git> git push origin master 
> Enumerating objects: 4, done. 
> Counting objects: 100% (4/4), done. 
> Delta compression using up to 20 threads Compressing objects: 100% (2/2), done. 
> Writing objects: 100% (3/3), 271 bytes | 271.00 KiB/s, done.
> Total 3 (delta 0), reused 0 (delta 0), pack-reused 0 (from 0) 
> remote: error: refusing to update checked out branch: refs/heads/master
> remote: error: By default, updating the current branch in a non-bare repository
> remote: is denied, because it will make the index and work tree inconsistent
> remote: with what you pushed, and will require 'git reset --hard' to match
> remote: the work tree to HEAD.
> remote:
> remote: You can set the 'receive.denyCurrentBranch' configuration variable
> remote: to 'ignore' or 'warn' in the remote repository to allow pushing into
> remote: its current branch; however, this is not recommended unless you
> remote: arranged to update its work tree to match what you pushed in some
> remote: other way.
> remote:
> remote: To squelch this message and still keep the default behaviour, set
> remote: 'receive.denyCurrentBranch' configuration variable to 'refuse'.
> to 'Z:/my_git'

### 为什么？

由于 Git 拒绝将更改推送到一个**非裸仓库**（non-bare repository）的当前分支。**裸仓库**是一个没有工作区的 Git 仓库，通常用作远程仓库，而**非裸仓库**是一个包含工作区的 Git 仓库，通常用于本地开发。

### 解决方案

#### 方法 1: 使用 **裸仓库**（推荐）

最常见的做法是将 `Z:/my_git` 转换为一个**裸仓库**，这样它就不再有工作区，可以安全地接收来自其他仓库的推送。

1. **创建裸仓库：** 如果你希望将 `Z:/my_git` 作为裸仓库，你可以删除（或重命名）现有的 `Z:/my_git` 目录，然后重新初始化裸仓库。步骤如下：

    ```bash
    git init --bare Z:/my_git  # 初始化裸仓库
    ```

2. **设置新的远程仓库 URL：** 重新设置远程仓库的 URL，指向新的裸仓库路径：

    ```bash
    git remote set-url origin Z:/my_git
    ```

3. **推送更改：** 现在，使用 `git push` 将更改推送到裸仓库：

    ```bash
    git push origin master
    ```

#### 方法 2: 允许更新当前分支（不推荐）

但在我的使用场景下，需要同时在 `Z:\my_git` 下进行开发，因此需要下面的方法

如果你确实希望将更改推送到非裸仓库并保留当前分支，你可以通过修改 Git 配置来允许更新当前分支。请注意，这种方法不推荐，尤其是对于生产环境，因为它可能导致工作区和仓库状态不一致。

你可以通过以下命令在 `Z:/my_git` 仓库中允许推送到当前分支：

1. 在 `Z:/111111` 仓库中，运行：

    ```my_git
    git config receive.denyCurrentBranch ignore
    ```

2. 然后再尝试推送：

    ```bash
    git push origin master
    ```