# HPD用户端需求文档

## 桌面详情

![image-20230411130418957](C:\Users\lvzhi\AppData\Roaming\Typora\typora-user-images\image-20230411130418957.png)

### 桌面列表

桌面详情以列表形式展示用户使用中的云桌面列表

云桌面列表信息包含

- 桌面名称
- 桌面类型（个人云桌面、高性能云桌面）
- 系统——当前桌面操作系统
- 开机状态（运行中、已关机）
- 当前开机时长（关机显示0）
- 连接状态（已连接、未连接）
- 桌面登录——按钮
- 更多——弹出菜单

![image-20230411130806568](C:\Users\lvzhi\AppData\Roaming\Typora\typora-user-images\image-20230411130806568.png)

### 桌面操作

1. 申请新桌面

   点击弹出菜单申请个人云桌面或高性能云桌面，点击跳转同济EKP申请链接

2. 桌面操作

   - 开机、关机、重启、释放
   - 高性能云桌面不支持开机、关机、重启；在勾选高性能云桌面时开机，关机，重启按钮灰显不支持操作
   - 用户点击关机、重启、释放时，弹出对话框提示用户确认，确认后执行相关操作。

![image-20230411131250398](C:\Users\lvzhi\AppData\Roaming\Typora\typora-user-images\image-20230411131250398.png)

### 桌面使用详情

- 选择需要查看的桌面名称

  初始默认显示个人云桌面

- 下方显示当前选择桌面的各项性能指标

  - CPU
  - 内存
  - GPU
  - 显存
  - 硬盘

  以可视化形式表达，下图仅为示意，可按实际情况优化

![image-20230411131353660](C:\Users\lvzhi\AppData\Roaming\Typora\typora-user-images\image-20230411131353660.png)

## 计量详情

![image-20230411131413850](C:\Users\lvzhi\AppData\Roaming\Typora\typora-user-images\image-20230411131413850.png)

### 个人云桌面

- 上方选择个人云桌面

  通常用户仅有1个个人云桌面，则锁定不能选择

![image-20230411131924625](C:\Users\lvzhi\AppData\Roaming\Typora\typora-user-images\image-20230411131924625.png)

- 左侧显示会话状态

![image-20230411131919881](C:\Users\lvzhi\AppData\Roaming\Typora\typora-user-images\image-20230411131919881.png)

- 右侧显示信息

  - 使用时长

  - 登录比例

  - 峰谷比例

  - 使用健康度

    暂时默认正常，后期补充逻辑

  - 我的部门

    用户信息自动读取

  以可视化形式表达，下图仅为示意，可按实际情况优化

![image-20230411132127305](C:\Users\lvzhi\AppData\Roaming\Typora\typora-user-images\image-20230411132127305.png)

### 高性能云桌面

- 上方选择高性能云桌面

  当只有1个高性能云桌面时则锁定不能选择

  ![image-20230411132238412](C:\Users\lvzhi\AppData\Roaming\Typora\typora-user-images\image-20230411132238412.png)

- 左侧显示当前会话状态

  ![image-20230411132258893](C:\Users\lvzhi\AppData\Roaming\Typora\typora-user-images\image-20230411132258893.png)

- 右侧显示信息

  - 使用时长

  - 登录比例

  - 峰谷比例

  - 使用健康度

    暂时默认正常，后期补充逻辑

  - 我的项目

    申请HPD时填写，从EKP申请信息获得

  以可视化形式表达，下图仅为示意，可按实际情况优化

  ![image-20230411132409655](C:\Users\lvzhi\AppData\Roaming\Typora\typora-user-images\image-20230411132409655.png)

## 资源调度

用户申请高性能算力资源成功时，需要由后台进行资源分配，当前版本直接将用户添加到DDC中的交付组，初次分配时有剩余容量就分配，当用户再次申请时查看历史分配记录，优先添加到上次的交付组。

![image-20230412154725088](C:\Users\lvzhi\AppData\Roaming\Typora\typora-user-images\image-20230412154725088.png)

![image-20230412154749112](C:\Users\lvzhi\AppData\Roaming\Typora\typora-user-images\image-20230412154749112.png)

DDC操作可通过REST API或SDK实现，参考资料https://developer.cloud.com/citrixworkspace/citrix-daas-rest-apis/docs/overview

把用户添加到交付组时，参考POWERSHELL命令 Get-BrokerAccessPolicyRule -DesktopGroupName "62SHAHPD-WS03" | Set-BrokerAccessPolicyRule -IncludedUsers "tjadri\poc-u-user09"。这个方式需要把交付组内的用户先全部读取再拼接上要添加的用户，然后添加到交付组内。否则原有的用户数据会丢失。

把用户从交付组移除时，待研究。