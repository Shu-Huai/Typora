# Hpd测试文档

## 初始条件

初始情况下，三维建模的资源已经全部占满

## 正常申请-测试正常

在数据库中新建一个名为3D-Single的单用户三维建模交付组

| resource\_type\_id | resource\_type\_name | code | description                     | resource\_type\_enable | delivery\_group\_id | delivery\_group\_name | os              | session\_type | max\_sessions | delivery\_group\_enable |
| :----------------- | :------------------- | :--- | :------------------------------ | :--------------------- | :------------------ | :-------------------- | :-------------- | :------------ | :------------ | :---------------------- |
| 7                  | 三维建模             | 3D   | 适合类型:Revit/Rhino/Sketchup等 | 1                      | 14                  | 3D-Single             | Windows Desktop | single        | 1             | 1                       |

此时，前端页面显示“还可以分配1人”，点击申请按钮，提示申请成功

回到数据库查看，在resource_application表中有相应数据

| id         | account    | name | mail | phone | department | major | project\_name | request\_type | start\_time | end\_time | resource\_type\_id | resource\_name | delivery\_group\_os | create\_time        |
| :--------- | :--------- | :--- | :--- | :---- | :--------- | :---- | :------------ | :------------ | :---------- | :-------- | :----------------- | :------------- | :------------------ | :------------------ |
| -286838782 | sacguser01 | null | null | null  | null       | null  | null          | 0             | null        | null      | 7                  | 三维建模       | Windows Desktop     | 2023-04-27 03:13:35 |

在resource_allocation表中有相应数据

| id   | account    | form\_id   | resource\_type\_id | delivery\_group\_id | status | allocate\_time      | release\_time |
| :--- | :--------- | :--------- | :----------------- | :------------------ | :----- | :------------------ | :------------ |
| 14   | sacguser01 | -286838782 | 7                  | 14                  | 0      | 2023-04-27 03:13:35 | null          |

- 其中， create_time和allocate\_time的数据不正确，可能与服务器时间、时区设置有关

此时前端页面显示6人正在使用、还可以分配0人，如下图所示

![image-20230427152230837](Z:\Typora\图片\Hpd测试文档\image-20230427152230837.png)

在主页的资源列表中出现3个三维建模的资源（申请前为2个）

![image-20230427152419489](Z:\Typora\图片\Hpd测试文档\image-20230427152419489.png)

## 资源不足、等待队列

### 排队

现在尝试再次申请一个三维建模的单用户交付组

提示申请成功

在数据库的resource_application中有相应数据

| id         | account    | name | mail | phone | department | major | project\_name | request\_type | start\_time | end\_time | resource\_type\_id | resource\_name | delivery\_group\_os | create\_time        |
| :--------- | :--------- | :--- | :--- | :---- | :--------- | :---- | :------------ | :------------ | :---------- | :-------- | :----------------- | :------------- | :------------------ | :------------------ |
| -911790078 | sacguser01 | null | null | null  | null       | null  | null          | 0             | null        | null      | 7                  | 三维建模       | Windows Desktop     | 2023-04-27 03:38:34 |

前端页面显示当前排队1人

![image-20230427154751111](Z:\Typora\图片\Hpd测试文档\image-20230427154751111.png)

### 释放

