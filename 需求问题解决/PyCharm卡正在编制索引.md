# PyCharm 卡正在编制索引

## 问题

这应该是 PyCharm 的一个祖传 BUG，问题表现为，打开一个项目，然后右下角一直提示“正在编制索引”。在这个过程中，“文件”和“代码”选项不可用。

且我打开的这个项目是一个空项目，也是新建的干净的 Python 解释器。

但是很奇怪，我打开另一个全是文件的项目，就能正常。

重启之后也不管用。

## 解决方案

根据 https://stackoverflow.com/questions/29030682/pycharm-hangs-on-scanning-files-to-index-background-task 所说，

> I just tried the following:
>
> In PyCharm, go to the "File" on the left top, then select "invalidate caches/restart...", and press "Invalidate and restart".
>
> After that, it can finish scanning in a short period without hanging anymore.

也就是说

<img src="Z:\Public\images\image-20250522202245911.png" alt="image-20250522202245911" style="zoom:50%;" />

<img src="Z:\Public\images\image-20250522202257074.png" alt="image-20250522202257074" style="zoom:50%;" />

全选后失效并重启，重启后就正常了。

