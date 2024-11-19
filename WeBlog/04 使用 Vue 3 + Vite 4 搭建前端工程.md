# 04 使用 Vue 3 + Vite 4 搭建前端工程

## Vue 3 环境安装& Weblog 项目搭建

本章节中，我们将正式进入 `weblog` 前端的开发工作。因为目前国内企业级项目开发中，前端比较主流的技术栈是 `Vue`，在技术选型上，小哈也是贴近企业实战，使用 `Vue 3` 来开发 `weblog` 前端。

![img](http://public.file.lvshuhuai.cn/图床\168078282470912.png)

本小节中，我们的目标是将开发 `Vue 3` 项目所需的环境安装好。

### 什么是 Vue ?

Vue (发音为 /vjuː/，类似 **view**) 是一款用于构建用户界面的 JavaScript **渐进式框架**。它基于标准 HTML、CSS 和 JavaScript 构建，并提供了一套**声明式**的、**响应式**的、**组件化**的编程模型，帮助你高效地开发用户界面。无论是简单还是复杂的界面，Vue 都可以轻松搞定。

### 安装 Node.js

要想学习 Vue ，首先需要安装好 Vue 的环境。

#### 第一步：安装 Node.js 环境

访问 Node.js 官网：https://nodejs.org/en ，点击左侧的下载按钮，下载 Node.js LTS 版本的安装包：

> ⚠️ 注意：**学习 Vue 3, 你需要安装 Node.js 16.0 版本或者更高**, LTS 表示该安装包是一个被长期支持的版本，可以理解成是一个稳定版本。

![下载 Node.js 安装包](http://public.file.lvshuhuai.cn/图床\168077273062539.jpeg)

下载完成后，双击开始安装：

![Node.js 安装文件](http://public.file.lvshuhuai.cn/图床\168077281275327.jpeg)Node.js 安装文件

无脑点击下一步【Next】按钮即可，其中，需要勾选接受协议，以及自选选择安装路径，小哈这里直接使用的默认安装路径 `C`盘：

![安装 Node.js](http://public.file.lvshuhuai.cn/图床\168078003737925.jpeg)

继续点击【Next】按钮, 然后进入安装：

![安装 Node.js](http://public.file.lvshuhuai.cn/图床\168078029137335.jpeg)

等待其安装成功：

![Node.js 正在安装中](http://public.file.lvshuhuai.cn/图床\168078045795714.jpeg)

然后点击【Finish】按钮，到这里 Node.js 就安装成功了：

![Node.js 安装完成](http://public.file.lvshuhuai.cn/图床\168078086463568.jpeg)

#### 第二步：验证是否真的安装成功了

按住快捷键 `win + R` 输入 `cmd` 打开命令行，或者使用 PowerShell 等其他命令行工具，执行如下命令：

```undefined
node -v
npm -v
```

如果能够正确输出版本号，则表示 Vue 的环境搭建成功：

![确认 Node.js 环境是否安装成功](http://public.file.lvshuhuai.cn/图床\168078100007722.jpeg)

### 创建 Weblog 前端工程

打开 `cmd` 命令工具，进入到 `weblog` 目录中：

```bash
cd D:\IDEA_Projects\weblog
```

> PS : 实际需要根据你之前创建的 `weblog` 工程具体路径来修改以上命令。

然后，执行创建 Vue 项目命令：

```sql
npm create vue@latest
```

> TIP: 该命令会安装并执行 `create-vue`, 它是 Vue 官方的项目脚手架工具。

![img](http://public.file.lvshuhuai.cn/图床\169231968101828.jpeg)

执行过程中，会提示你命名新项目，我们命名为 `weblog-vue3`，以及是否需要开启一些诸如 TypeScript 和测试支持之类的可选功能，这里统一敲击回车键选择 `No` 即可。当你看到命令行中提示 `Done` ， 表示你已经创建好了 `weblog` 前端项目。

![img](http://public.file.lvshuhuai.cn/图床\169231994777870.jpeg)

#### 项目目录说明

创建好了 `weblog` 前端工程后，进入该文件夹，看下目录结构：

![img](http://public.file.lvshuhuai.cn/图床\169231999718537.jpeg)

解释一下目录结构以及相关文件的作用：

- `node_modules` : 项目依赖包文件夹，比如通过 `npm install 包名` 安装的包都会放在这个目录下，*因为现在还没有执行 npm install 命令，所以还未生成该文件夹*；
- `public` : 公共资源目录，用于存放公共资源，如 `favicon.ico` 图标等；
- `index.html` : 首页；
- `package.json` : 项目描述以及依赖；
- `package-lock.json` : 版本管理使用的文件；
- `README.md` : 用于项目描述的 markdown 文档；
- `src` : 核心文件目录，源码都放在这里面；

进入 `src` 文件夹，目录如下：

![img](http://public.file.lvshuhuai.cn/图床\169232021843334.jpeg)

- `assets` : 静态资源目录，用于存放样式、图片、字体等；
- `components`: 组件文件夹，通用的组件存放目录；
- `App.vue`: 主组件，也是页面的入口文件，所有页面都是在 App.vue 下进行路由切换的；
- `main.js` : 入口 Javascript 文件；

### 启动项目

进入到想要启动的项目文件夹中，执行如下命令，为项目安装依赖并启动项目：

```bash
## 进入项目文件夹
cd weblog-vue3
## 安装项目所需依赖
npm install
## 启动项目
npm run dev
```

启动成功后，会提示项目的访问地址，如 `http://localhost:5173/`:

![img](http://public.file.lvshuhuai.cn/图床\169232042870672.jpeg)

在浏览器地址栏中访问该地址，即可访问此 Vue 项目啦，整个过程还是非常简单的。

![Vue 启动页面展示](http://public.file.lvshuhuai.cn/图床\168077411830485.jpeg)

### 结语

本小节中，我们正式进入了 `weblog` 的前端开发领域，了解了 什么是 `Vue`, 以及安装好了 `Vue 3` 所需的环境，最后，我们搭建了 `weblog` 前端项目，并启动了它，也能够在浏览器中正常访问该项目。

## 安装 VSCode 开发工具 & 打开 Weblog 项目

![img](http://public.file.lvshuhuai.cn/图床\169232586036528.jpeg)

为了更高效率的开发 Vue 3 项目，我们需要有个趁手的兵器，也就是开发工具。比较常见的如 VSCode 、Webstorm 等，但是官方推荐使用 VSCode， 那我们就通过 VSCode 来开发 Vue 3。

### VSCode 简介

VSCode 全称 Visual Studio Code，是微软出的一款轻量级代码编辑器，它具有如下特点：

- 开源且免费；
- 代码智能提示、自动补全功能；
- 可自定义配置；
- 支持丰富的文件格式；
- 代码调试功能强大；
- 各种方便的快捷键；
- 强大的插件拓展功能；

### 下载安装包

前往 VSCode 官网：https://code.visualstudio.com/ 下载对应系统的安装包，小哈这里用 Windows 系统来演示：

![官网下载 VSCode 安装包](http://public.file.lvshuhuai.cn/图床\168136203997815.jpeg)

### 开始安装

下载成功后，双击安装包开始安装 VSCode:

![VSCode 安装包](http://public.file.lvshuhuai.cn/图床\168128659782959.jpeg)VSCode 安装包

勾选【我同意此协议】，点击下一步按钮：

![同意安装协议](http://public.file.lvshuhuai.cn/图床\168128669924897.jpeg)

自定义安装路径，小哈这里安装在了 `D` 盘，可自行选择安装位置，继续点击下一步按钮：

![自定义 VSCode 安装路径](http://public.file.lvshuhuai.cn/图床\168128682307134.jpeg)

继续点击下一步按钮:

![img](http://public.file.lvshuhuai.cn/图床\168128697450593.jpeg)

勾选【创建桌面快捷方式】，点击下一步：

![创建 VSCode 桌面快捷启动方式](http://public.file.lvshuhuai.cn/图床\168128704365752.jpeg)

点击【安装】：

![开始安装 VSCode](http://public.file.lvshuhuai.cn/图床\168128715711838.jpeg)

等待一分钟左右，即可安装成功，然后点击【完成】按钮：

![VSCode 安装完成](http://public.file.lvshuhuai.cn/图床\168128726605058.jpeg)

### 使用界面

启动成功后，即可看到如下界面，至此，VSCode 就安装成功啦~

![VSCode 界面](https://img.quanxiaoha.com/quanxiaoha/168128771855058)

### VSCdoe 设置中文

> TIP: **汉化是可选项**，针对初学者来说，全英文化的 VSCode 可能不太友好，所以，根据自己的需要来确定是否需要汉化。

#### 开始设置

在 VSCode 的左侧栏，可以看到插件市场选项，如下图所示：

![VSCode 插件市场](http://public.file.lvshuhuai.cn/图床\168129097931891.jpeg)

打开插件市场，搜索关键词【中文】，即可看到中文汉化插件，点击【Install】安装：

![VSCode 安装中文插件](https://img.quanxiaoha.com/quanxiaoha/168129108399620)

安装成功后，右下角会提示是否需要立刻重启 VSCode 来使汉化生效，点击重启：

![重启 VSCode](http://public.file.lvshuhuai.cn/图床\168129114707120.jpeg)

#### 汉化后的界面

重启 VSCode 后，你就可以看到所有菜单均已被设置成中文了：

![中文汉化后的 VSCode](http://public.file.lvshuhuai.cn/图床\168129122315365.jpeg)

### 安装 Vue 相关插件

想要在 VSCode 中开发 Vue 3 项目，还需要安装几个必备插件。

#### 一、Vue - Official 插件

简介：这是一款专用于构建 Vue 的拓展，想要在 VSCode 上开发 Vue 3 应用，这款插件必不可少。

![Vue - Official 插件](http://public.file.lvshuhuai.cn/图床\170952129977853.jpeg)

#### 二、Vue 3 Snippets 插件

简介：HTML 代码自动提示和代码补全插件，提升编码效率。

![Vue 3 Snippets 插件](http://public.file.lvshuhuai.cn/图床\168130580421245.jpeg)

#### 三、别名路径跳转

简介：别名路径跳转插件，支持任何项目，可以自由配置映射规则，自由配置可缺省后缀名列表

![别名路径跳转](http://public.file.lvshuhuai.cn/图床\169604699649078.jpeg)

#### 四、Auto Rename Tag

简介：当我们修改 HTML/XML 某个节点标签时，能够自动重命名结束标签的命名。

![Auto Rename Tag](http://public.file.lvshuhuai.cn/图床\169604728658288.jpeg)

#### 五、Auto Close Tag

简介：自动添加 HTML/XML 结束标签，比如当输入 `<p>` 标签，则自动添加 `</p>` 结尾标签。

![Auto Close Tag](http://public.file.lvshuhuai.cn/图床\169604745275475.jpeg)

#### 六、CSS Navigation

简介：允许你通过点击 `HTML` 中的类名，直接跳转至对应的样式代码。

![CSS Navigation](http://public.file.lvshuhuai.cn/图床\169642374818915.jpeg)

#### 七、Path Intellisense

简介：当你通过 `.` 的方式导入某个文件时，可自动提示文件路径。

![Path Intellisense](http://public.file.lvshuhuai.cn/图床\169642398689292.jpeg)

#### 八、Moonlight 主题插件（可选）

简介：原生的 VSCode 主题样式看腻了？不妨安装一下此主题插件，效果图如下：

![Moonlight 主题插件](http://public.file.lvshuhuai.cn/图床\169642417400739.jpeg)

#### 九、IntelliJ IDEA Keybindings 插件 (可选)

简介：将 VSCode 默认的快捷键变更为 IntellJ IDEA 、Webstorm、PyCharm、PHP Storm 等 IDE 的快捷键。

![IntelliJ IDEA Keybindings 插件](http://public.file.lvshuhuai.cn/图床\169534559070046.jpeg)

#### 如何安装插件？

可参考前面的安装中文汉化插件。

### 通过 VSCode 打开 Weblog 项目

前面小节中已经通过命令行创建了第一个 Vue 应用，现在，我们将通过 VSCode 来打开它。

#### 打开项目

点击 VSCode 左上角菜单：*文件 -> 打开文件夹*，导入之前创建好的 `weblog-vue3` 项目：

> TIP : 或者你也可以将项目文件夹直接拖入 VSCode 来打开项目。

![打开 Vue 项目](http://public.file.lvshuhuai.cn/图床\168134998776626.jpeg)

导入成功后，视图如下：

![img](http://public.file.lvshuhuai.cn/图床\169232404812493.jpeg)

#### 核心文件说明

在前面创建项目小节中，我们已经了解了各个文件夹，以及文件的大致用途。这里小哈针对最核心的 3 个文件再详细说明一下，分别是：

- `index.html` ： 首页；
- `main.js` ： 主 js 文件；
- `App.vue` : 主组件；

这 3 者之间的关系如下：

![依赖关系](http://public.file.lvshuhuai.cn/图床\168135293123532.jpeg)

当打开一个 Vue 3 应用，首先先看 `index.html` 文件，它是首页，代码如下，这里小哈已经添加好注释说明：

```php-template
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <link rel="icon" href="/favicon.ico">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vite App</title>
  </head>
  <body>
    <!-- 指定挂载点，用于渲染组件 -->
    <div id="app"></div>
    <!-- 引入主 js 文件 -->
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
```

再来看 `main.js` 文件：

```javascript
import { createApp } from 'vue' // 引入 createApp 方法
import App from './App.vue'     // 引入 App.vue 组件

import './assets/main.css'      // 引入 main.css 样式文件

// 创建应用，并将 App 根组件挂载到 <div id="#app"></div> 中
createApp(App).mount('#app')
```

再看 `app.vue` 组件代码：

```php-template
<script setup>
// 引入自定义组件
import HelloWorld from './components/HelloWorld.vue'
import TheWelcome from './components/TheWelcome.vue'
</script>

<template>
  <header>
    <img alt="Vue logo" class="logo" src="./assets/logo.svg" width="125" height="125" />

    <div class="wrapper">
      <HelloWorld msg="You did it!" />
    </div>
  </header>

  <main>
    <TheWelcome />
  </main>
</template>

<style scoped>
header {
  line-height: 1.5;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
}
</style>
```

作为初学者，为了更方便的学习，我们先将多余的代码删除掉，只保留结构，如下图所示：

![img](http://public.file.lvshuhuai.cn/图床\169232435241764.jpeg)

结构分为 3 个部分：

- `script` : 节点中间用于放置 `javascript` 代码；
- `template` : 节点中间用于放置 `html` 代码；
- `style` : 节点中间用于放置 `css` 样式代码；

```php-template
<template>
	<!-- html 代码 -->
</template>

<script setup>
	<!-- js 代码, setup 标识通常和组合式 API 搭配使用, 用于告诉 Vue 需要在编译时进行一些处理，让我们可以更简洁地使用组合式 API -->
</script>

<style scoped>
	<!-- css 代码， scoped 表示节点内 css 样式只针对此组件有效，不影响其他组件 -->
</style>
```

然后，我们在 `<template>` 标签下添加一个 `<h1>` 标题：

```php-template
<template>
   <h1>Hello, Vue 3 !</h1>
</template>

<script setup>
 
</script>

<style scoped>

</style>
```

打开 `main.js` 文件，注释掉模板工程的自带的样式文件 `main.css`：

![img](http://public.file.lvshuhuai.cn/图床\169232479386589.jpeg)

**保存代码**, 并直接通过 VSCode 打开命令行，来执行启动命令 `npm run dev`：

![img](http://public.file.lvshuhuai.cn/图床\169232451983078.jpeg)

![img](http://public.file.lvshuhuai.cn/图床\169232457637166.jpeg)

启动成功后，浏览器访问 `http://localhost:5173` ，效果如下:

![img](http://public.file.lvshuhuai.cn/图床\169232498542474.jpeg)

### 结语

本小节中，我们安装好了前端的开发工具 VSCode ，并打开了之前创建好的 `weblog-vue3` 项目，同时了解到项目中几个核心文件的作用，最后，在 `App.vue` 中添加了 `<h1>` 标签，重启了项目，看到了修改内容已生效。

## 整合 vue-router 路由管理器

![img](http://public.file.lvshuhuai.cn/图床\169234498473045.jpeg)

### 什么是 Vue Router？

Vue Router 是 Vue.js 官方提供路由管理器。它与 Vue.js 核心深度集成，让构建单页面应用（Single Page Applications，SPA）变得轻而易举。

### 为什么需要 Vue Router？

在一个标准的单页面应用中，仅有一个 HTML 页面被服务器发送到客户端。随后的页面内容都是通过 JavaScript 动态替换生成的。这时候，就需要 Vue Router 来管理这些页面的导航和组织。

### 开始设置

#### 安装 vue-router

在命令行中，执行如下命令，安装 `vue-router`:

```undefined
npm install vue-router
```

![img](http://public.file.lvshuhuai.cn/图床\169234028054770.jpeg)

#### 配置 Router

##### 创建首页

在 `src` 目录下，创建 `/pages` 文件夹，此文件夹中统一存放*页面*相关代码，然后 `/pages` 文件夹下，再创建两个文件夹, 分别是：

- `/admin` : 存放管理后台相关页面；
- `/frontend` ：存放前台展示相关页面，如首页、博客详情页等；

![img](http://public.file.lvshuhuai.cn/图床\169234072120068.jpeg)

在 `/frontend` 文件夹下，创建 `index.vue` 首页文件，代码如下：

```php-template
<template>
    <h1>首页</h1>
</template>
```

##### 设置路由配置

在 `/src` 目录下，新建 `/router` 路由文件夹，用于存放路由相关代码，并在此文件夹下，新建 `index.js` 文件, 代码如下：

```javascript
import Index from '../pages/frontend/index.vue'
import { createRouter, createWebHashHistory } from 'vue-router'

// 统一在这里声明所有路由
const routes = [
    {
        path: '/', // 路由地址
        component: Index, // 对应组件
        meta: { // meta 信息
            title: 'Weblog 首页' // 页面标题
        }
    }
]

// 创建路由
const router = createRouter({
    // 指定路由的历史管理方式，hash 模式指的是 URL 的路径是通过 hash 符号（#）进行标识
    history: createWebHashHistory(),
    // routes: routes 的缩写
    routes, 
})

// ES6 模块导出语句，它用于将 router 对象导出，以便其他文件可以导入和使用这个对象
export default router
```

上述代码中，我们先通过 `import` 关键词导入了 `index.vue` 组件，以及 `vue-router` 路由中的相关方法。然后，我们定义一个 `routes` 数组，用于统一声明所有路由。最后，我们创建了路由，并使用 `export default` 关键字导出了 `router` 对象。

##### 使用 router-view 组件

`<router-view>` 是 Vue Router 的一个核心组件，它是一个功能性组件（functional component）。其主要作用是根据当前的路由（URL）动态地渲染对应的组件，相当于是一个“占位符”，它会自动渲染与当前路径匹配的组件。

###### 作用：

- 1、**动态渲染组件**： `<router-view>` 根据当前的 URL，自动渲染与当前路径匹配的组件。
- 2、**嵌套路由**： 在有嵌套路由的情况下，`<router-view>` 可以用于渲染嵌套的子路由组件。

接下来，我们需要在 `app.vue` 中添加该组件，**用于动态渲染路由对应的组件**：

```php-template
<template>
   <router-view></router-view>
</template>

<script setup>
 
</script>

<style scoped>

</style>
```

##### 将 Router 添加到 Vue 实例

最后，要想路由生效，还需要打开 `src/main.js` 文件，将 `router` 导入并添加到 Vue `app` 实例中，应用刚刚声明的路由, 最终代码如下:

```javascript
// import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
// 导入路由
import router from './router'

const app = createApp(App)

// 应用路由
app.use(router)
app.mount('#app')
```

### 启动项目看看效果

如果你的项目已经启动了，则直接浏览器访问 `http://localhost:5173/`，无需重启，前端所有新修改的代码都会实时的被动态加载。如果未启动项目，则控制台执行 `npm run dev` 启动项目后再查看，效果图如下：

![img](http://public.file.lvshuhuai.cn/图床\169234382999074.jpeg)

可以看到，路由生效了，且能够正常渲染出 `index.vue` 组件。

### 本小节对应源码

https://t.zsxq.com/11Zq9548U

### 结语

本小节中，小哈带着大家在 `weblog-vue3` 前端项目中，添加了路由管理器，并创建了一个首页文件，使得它能够根据 URL 动态被渲染出来。

## Vite 配置路径别名：更方便的引用文件

![img](http://public.file.lvshuhuai.cn/images\169235017424476.jpeg)

在本小节中，我们来说说 Vite 的一个重要配置选项：`alias`。

### 什么是 alias？

`alias` 是一个用于定义路径别名的配置选项。当你的项目结构变得复杂时，路径别名可以帮助你简化 `import` 或 `require` 语句中的路径，让代码更干净、更可维护。

### 为什么需要 Alias？

上小节中，我们在 `/router/index.js` 文件中引入了 `index.vue` 组件，格式是下面这样的：

```javascript
import Index from '../pages/frontend/index.vue'
```

通过 `..` 来指定上一级目录，然后再定位具体路径下。考虑一个大型项目中，我们经常需要这样的引用，当文件层级很深，那么代码可能会像下面这样：

```javascript
import Button from '../../../components/Button.vue';
```

这种相对路径不易于管理和阅读。使用 `alias`，我们可以将路径简化为：

```javascript
import Button from '@/components/Button.vue';
```

这样一来，不仅路径更短、更明确，而且移动文件时无需改动 `import` 路径。

### 如何在 Vite 中配置 Alias

以下是如何在 Vite 项目中设置 `alias` 的步骤:

#### 修改 Vite 配置

在项目的根目录中，找到 Vite 的配置文件 `vite.config.js`，编辑它，添加`alias` 配置，代码如下：

```javascript
import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      // 定义一个别名 '@'，该别名对应于当前 JavaScript 模块文件所在目录下的 'src' 目录的绝对文件路径。
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
```

上述代码中，我们定义一个别名 `@`，该别名对应于当前 JavaScript 模块文件所在目录下的 `src` 目录的绝对文件路径。

### 如何使用别名 Alias？

定义好了别名以后，我们将之前的 `/router/index.js` 文件中的路径引用改进一下，如下：

![img](http://public.file.lvshuhuai.cn/images\169235000751676.jpeg)

另外，`main.js` 中的路径引用同样也可以改进一波：

![img](http://public.file.lvshuhuai.cn/images\169235007436915.jpeg)

### 小结

`alias` 是一个非常有用的 Vite 配置选项，它可以让你的导入语句更加清晰和易于管理。在大型项目中，使用 `alias` 可以极大地提高代码的可维护性。

## 整合 Tailwind CSS

![img](http://public.file.lvshuhuai.cn/images\169241660365359.jpeg)

### 什么是 Tailwind CSS ？

Tailwind CSS 是一个高度可定制的、实用工具优先的 CSS 框架，它使你能够通过组合小型、单一用途的类来构建现代网站界面，而无需写任何 CSS。

### 为什么选择 Tailwind CSS？

- 1、 **高度可定制**：Tailwind CSS 提供了一整套预设样式，但所有这些都是完全可配置的。
- 2、 **实用工具优先**：它允许你通过在 HTML 中组合类，而不是自定义 CSS，来迅速构建响应式页面。
- 3、 **优化生产环境**：Tailwind CSS 在生产环境中会自动移除未使用的样式，这有助于保持 CSS 文件大小最小。

### 开始安装

执行如下命令，开始安装 Tailwind CSS :

```undefined
npm install -D tailwindcss postcss autoprefixer
```

此命令会在你的项目中安装三个依赖，它们分别是：

- 1、`tailwindcss`：Tailwind CSS 框架本身。
- 2、`postcss`：一个用于转换 CSS 的工具。
- 3、`autoprefixer`：一个 PostCSS 插件，用于自动添加浏览器供应商前缀到 CSS 规则中，确保跨浏览器的兼容性。

然后，再执行如下命令：

```csharp
npx tailwindcss init -p
```

此命令用于生成 `tailwind.config.js` 和 `postcss.config.js` 配置文件。

![img](http://public.file.lvshuhuai.cn/images\169241447768964.jpeg)

### 配置模板路径

在 `tailwind.config.js` 文件中添加所有模板文件的路径:

```java
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
  
}
```

### 将 Tailwind 指令添加到 CSS 文件中

修改 `main.js` 文件，引入 `main.css` :

![img](http://public.file.lvshuhuai.cn/images\169241470626053.jpeg)

然后编辑 `main.css` 文件，*清空*里面初始化项目时自动生成的 `css` 代码，添加如下代码：

```less
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### 重新构建工程

执行 `npm run dev` 命令，重新构建工程。

### 在项目中使用 Tailwind CSS

编辑 `/frontend/index.vue` 文件，内容如下：

```php-template
<template>
    <div class="bg-green-300 inline">绿色</div>
    <div class="bg-yellow-300 ml-2 inline">黄色</div>
    <div class="bg-blue-300 ml-2 inline">蓝色</div>
</template>
```

我们在 `div` 标签上添加了一些 Tailwind CSS 库中的样式类：

- `bg-green-300` : 绿色背景；
- `bg-yellow-300` : 黄色背景；
- `bg-blue-300` : 蓝色背景；
- `inline` : 相当于 `display: inline;`
- `ml-2` : 相当于 `margin-left`;

效果如下：

![img](http://public.file.lvshuhuai.cn/images\169241528294166.jpeg)

#### 响应式设计

通过在 Tailwind 类名前添加前缀，你可以轻松地应用不同的样式于不同屏幕尺寸：

```php-template
<div class="text-xs sm:text-lg md:text-xl lg:text-2xl">
  响应式字体
</div>
```

更多样式类，小伙伴们可查询官网：https://tailwindcss.com/docs/installation ，应有尽有。

![img](http://public.file.lvshuhuai.cn/images\169241617042832.jpeg)

### 本小节对应源码

https://t.zsxq.com/11MRrMEiA

### 结语

本小节中，小哈带着大家在 `weblog` 前端项目中安装了 Tailwind CSS 库，它在后面设计页面时，会被频繁被用到。这里只是简单介绍下，等涉及到具体功能开发时，我们再慢慢体会。

## 整合 Tailwind CSS 组件库：Flowbite

![img](http://public.file.lvshuhuai.cn/images\169245338993861.jpeg)

市面上有很多基于 Tailwind CSS 开源的组件库，小哈综合选择下来，觉得 Flowbite 的 UI 更好看些，组件也较为丰富，所以在 `weblog` 的前台展示中决定选择再整个框架。

### 什么是 Flowbite？

Flowbite 是一个基于 Tailwind CSS 创建的组件库，旨在帮助开发者快速构建现代、响应式的 Web 应用界面。在本小节中，小哈将的带着大家在 `weblog` 项目中集成和使用 Flowbite。

### 开始整合

Flowbite 是基于 Tailwind CSS 构建，因此我们需要先安装 Tailwind CSS、PostCSS 和 Autoprefixer，这项工作在上一小节已经完成了。这里，我们只需要安装 Flowbite 本身就行了。

#### 安装 Flowbite

执行如下命令安装 Flowbit :

```bash
npm install flowbite
```

在 `tailwind.config.js` 文件添加 Flowbit 插件：

```java
module.exports = {
	省略...
    plugins: [
        require('flowbite/plugin')
    ]

}
```

另外, 还需要在 `tailwind.config.js` 文件中，添加 `js` 相关的文件，因为页面交互需要 `js`：

```java
module.exports = {

    content: [
        "./node_modules/flowbite/**/*.js"
    ]

}
```

重新执行 `npm run dev` 命令使之生效。

### 使用 Flowbite

Flowbit 支持的组件列表，大家可以去官网：https://flowbite.com/docs/components/accordion/ 查看:

![img](http://public.file.lvshuhuai.cn/images\169243871192362.jpeg)

这里我们在 `/frontend/index.vue` 首页文件中添加 `Navbar` 导航栏头的源码，并将几处跳转的地方改为中文，代码如下：

```php-template
<template>
    <nav class="bg-white border-gray-200 border-b dark:bg-gray-900">
        <div class="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4">
            <a href="/" class="flex items-center">
                <img src="https://flowbite.com/docs/images/logo.svg" class="h-8 mr-3" alt="Flowbite Logo" />
                <span class="self-center text-2xl font-semibold whitespace-nowrap dark:text-white">犬小哈的博客</span>
            </a>
            <div class="flex md:order-2">
                <button type="button" data-collapse-toggle="navbar-search" aria-controls="navbar-search"
                    aria-expanded="false"
                    class="md:hidden text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-4 focus:ring-gray-200 dark:focus:ring-gray-700 rounded-lg text-sm p-2.5 mr-1">
                    <svg class="w-5 h-5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none"
                        viewBox="0 0 20 20">
                        <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="m19 19-4-4m0-7A7 7 0 1 1 1 8a7 7 0 0 1 14 0Z" />
                    </svg>
                    <span class="sr-only">Search</span>
                </button>
                <div class="relative hidden md:block">
                    <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                        <svg class="w-4 h-4 text-gray-500 dark:text-gray-400" aria-hidden="true"
                            xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 20">
                            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="m19 19-4-4m0-7A7 7 0 1 1 1 8a7 7 0 0 1 14 0Z" />
                        </svg>
                        <span class="sr-only">Search icon</span>
                    </div>
                    <input type="text" id="search-navbar"
                        class="block w-full p-2 pl-10 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                        placeholder="请输入关键词...">
                </div>
                <button data-collapse-toggle="navbar-search" type="button"
                    class="inline-flex items-center p-2 w-10 h-10 justify-center text-sm text-gray-500 rounded-lg md:hidden hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200 dark:text-gray-400 dark:hover:bg-gray-700 dark:focus:ring-gray-600"
                    aria-controls="navbar-search" aria-expanded="false">
                    <span class="sr-only">Open main menu</span>
                    <svg class="w-5 h-5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none"
                        viewBox="0 0 17 14">
                        <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M1 1h15M1 7h15M1 13h15" />
                    </svg>
                </button>
            </div>
            <div class="items-center justify-between hidden w-full md:flex md:w-auto md:order-1" id="navbar-search">
                <div class="relative mt-3 md:hidden">
                    <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                        <svg class="w-4 h-4 text-gray-500 dark:text-gray-400" aria-hidden="true"
                            xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 20">
                            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="m19 19-4-4m0-7A7 7 0 1 1 1 8a7 7 0 0 1 14 0Z" />
                        </svg>
                    </div>
                    <input type="text" id="search-navbar"
                        class="block w-full p-2 pl-10 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                        placeholder="Search...">
                </div>
                <ul
                    class="flex flex-col p-4 md:p-0 mt-4 font-medium border border-gray-100 rounded-lg bg-gray-50 md:flex-row md:space-x-8 md:mt-0 md:border-0 md:bg-white dark:bg-gray-800 md:dark:bg-gray-900 dark:border-gray-700">
                    <li>
                        <a href="#"
                            class="block py-2 pl-3 pr-4 text-white bg-blue-700 rounded md:bg-transparent md:text-blue-700 md:p-0 md:dark:text-blue-500"
                            aria-current="page">首页</a>
                    </li>
                <li>
                    <a href="#"
                        class="block py-2 pl-3 pr-4 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:hover:text-blue-700 md:p-0 md:dark:hover:text-blue-500 dark:text-white dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent dark:border-gray-700">分类</a>
                </li>
                <li>
                    <a href="#"
                        class="block py-2 pl-3 pr-4 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent dark:border-gray-700">标签</a>
                </li>
                <li>
                    <a href="#"
                        class="block py-2 pl-3 pr-4 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent dark:border-gray-700">归档</a>
                </li>
            </ul>
        </div>
    </div>
</nav>
</template>

<script setup>
import { onMounted } from 'vue'
import { initCollapses } from 'flowbite'

// 初始化 flowbit 相关组件
onMounted(() => {
    initCollapses();
})
</script>
```

解释一下 `<script>` 中的代码：

- `onMounted` 是一个生命周期钩子（lifecycle hook）。生命周期钩子是 Vue 组件在其生命周期的不同阶段可以调用的函数。`onMounted` 钩子在组件被挂载到 DOM 之后立即调用。这意味着，当此钩子被触发时，你可以安全地访问和操作组件的 DOM 元素；

- `initCollapses()` 用于初始化 `flowbite` 的 `collapse` 组件，有了它，当页面在移动端展示时，点击菜单收缩按钮，可查看隐藏的菜单选项，如下图所示：

  ![img](http://public.file.lvshuhuai.cn/images\169245232719523.jpeg)

然后，在 `main.css` 中添加 `<body>` 标签的基本样式：

```\
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  font-family: -apple-system-font,BlinkMacSystemFont,Helvetica Neue,PingFang SC,Hiragino Sans GB,Microsoft YaHei UI,Microsoft YaHei,Arial,sans-serif;
  color: #4c4e4d;
  font-size: 16px;
  background: #f4f4f4;
  line-height: 1.6;
}
```

保存后，查看效果，如下图所示：

![img](http://public.file.lvshuhuai.cn/images\169245069397951.jpeg)

怎么样，UI 还是很好看的，有木有。

### 添加【登录】超链接

接下来，我们要完成的第一个完整页面就是*登录页*，这就需要在导航栏中的搜索框后面，添加一个跳转超链接，代码如下：

```php-template
<!-- 登录 -->
<div class="text-gray-900 ml-1 mr-1 hover:text-blue-700">登录</div>
```

![img](http://public.file.lvshuhuai.cn/images\169245267602057.jpeg)

注意，为了让登录超链接垂直居中，还需要在父级 `<div>` 中添加样式 `items-center`, 以及边距调整。最终效果如下：

![img](http://public.file.lvshuhuai.cn/images\169245280867723.jpeg)

### 本小节对应源码

https://t.zsxq.com/11d6AiKoP

### 结语

本小节中，小哈带着大家在 `weblog` 项目中整合了 `Flowbite` 组件库，并将首页的头部导航栏完成了。注意，我们暂时只完成首页的导航栏部分，下小节我们先将登录页搞定，在后续小节中，再回来将首页开发完成。

## 整合饿了么 Element Plus 组件库

![img](http://public.file.lvshuhuai.cn/images\169252793201139.jpeg)

### Element Plus 是什么？

Element Plus 是一个专为 Vue 3 设计的 UI 组件库。与 Vue 2 的 Element UI 相似，它提供了一整套丰富且高质量的组件，从基本的按钮和输入框到复杂的日期选择器和数据表格。这些组件不仅样式美观，而且具有广泛的定制选项。*同时，它也是目前企业级 Admin 管理后台中，使用广度非常高的一个组件框架，所以，针对 `weblog` 后台相关页面，小哈决定使用它作为技术栈，更加贴合实际企业场景。*

### 为什么使用 Element Plus？

- **为 Vue 3 量身打造**：尽管存在许多 UI 组件库，但 Element Plus 是专门为 Vue 3 设计的，确保最大的兼容性和性能。
- **高效开发**：使用预制的 UI 组件可以大大提高开发速度，减少从零开始编写 UI 代码的时间。
- **一致性和专业性**：Element Plus 提供的组件在设计上保持了一致性，使得你的应用看起来更为专业。
- **广泛的社区支持**：由于 Element UI 和 Vue 的广泛使用，Element Plus 也有一个日益增长的社区，这意味着丰富的资源、插件和持续的更新。
- **企业项目中使用频次非常多**：它是目前国内企业级后台项目中，使用频率非常高的一个组件库，为了贴合企业级开发，也是小哈将它作为技术选型的重要依据。

### 整合 Element Plus

#### 安装

打开命令行，通过 `npm` 执行如下命令来安装 Element Plus:

```css
npm install element-plus --save
```

#### 自动导入

Element Plus 有很多组件，而我们实际项目中，并不是每个组件都会被用到。所以，在生产级项目中，比较推荐按需导入组件，而不是在打包的时候，一次性将所以组件都打包进去，导致相关包非常大，页面初次加载很慢的情况发生。

要想实现按需导入组件，你需要安装`unplugin-vue-components` 和 `unplugin-auto-import`这两款插件：

```cpp
npm install -D unplugin-vue-components unplugin-auto-import
```

然后把下列代码插入到你的 `Vite` 配置文件 `vite.config.js` 中:

```javascript
import { defineConfig } from 'vite'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export default defineConfig({
  // ...
  plugins: [
    // ...
    AutoImport({
      resolvers: [ElementPlusResolver()],
    }),
    Components({
      resolvers: [ElementPlusResolver()],
    }),
  ],
})
```

完成上面工作后，在控制台 执行 `npm run dev` 重新构建一下项目。

### 开始使用

#### 新建一个登录页

为了测试一下目前项目是否正确整合了 `Elment Plus` 组件库，先来新建一个登录页，等下在该页面中，添加一些 Element Plus 组件，看看能够正确被展示。另外，刚好下面一章进入登录模块的开发，提前建好。在 `/pages/admin/` 中新建一个 `login.vue` 登录页面。

![img](http://public.file.lvshuhuai.cn/images\169448423235312.jpeg)

#### 添加登录页路由

页面新建好了后，还需要在 `/router/index.js` 中添加对应的路由：

```javascript
import Login from '@/pages/admin/login.vue'

// 统一在这里声明所有路由
const routes = [
    // 省略...
    {
        path: '/login', // 登录页
        component: Login,
        meta: {
            title: 'Weblog 登录页'
        }
    },
]
    // 省略...
```

路由添加好了后，编辑 `/pages/frontend/index.vue` 首页文件，为登录按钮添加点击事件，实现跳转功能：

```php-template
<!-- 登录 -->
<div class="text-gray-900 ml-1 mr-1 hover:text-blue-700" @click="$router.push('/login')">登录</div>
```

![img](http://public.file.lvshuhuai.cn/images\169448473287871.jpeg)

#### 在登录页中引入组件

Element Plus 提供了非常多的组件以供选择，小伙们可访问官网查看：https://element-plus.org/zh-CN/component/button.html

![img](http://public.file.lvshuhuai.cn/images\169252723167953.jpeg)

我们将按钮相关的组件代码，通过*右下角查看源码*， 即可看到每个组件对应的源码。复制它们到登录页 `/pages/admin/login.vue` 中, 完整代码如下：

```php-template
<template>
    <div class="p-2">
        <h1>登录页</h1>
        <el-row class="mb-4">
            <el-button>Default</el-button>
            <el-button type="primary">Primary</el-button>
            <el-button type="success">Success</el-button>
            <el-button type="info">Info</el-button>
            <el-button type="warning">Warning</el-button>
            <el-button type="danger">Danger</el-button>
        </el-row>

        <el-row class="mb-4">
            <el-button plain>Plain</el-button>
            <el-button type="primary" plain>Primary</el-button>
            <el-button type="success" plain>Success</el-button>
            <el-button type="info" plain>Info</el-button>
            <el-button type="warning" plain>Warning</el-button>
            <el-button type="danger" plain>Danger</el-button>
        </el-row>

        <el-row class="mb-4">
            <el-button round>Round</el-button>
            <el-button type="primary" round>Primary</el-button>
            <el-button type="success" round>Success</el-button>
            <el-button type="info" round>Info</el-button>
            <el-button type="warning" round>Warning</el-button>
            <el-button type="danger" round>Danger</el-button>
        </el-row>

    </div>
</template>
```

访问登录页，看下效果：

![img](http://public.file.lvshuhuai.cn/images\169252750521210.jpeg)

可以看到，按钮样式正确展示，这说明我们整合 Element Plus 成功了，后面按自己需要，在官网选择自己想要的组件代码，贴到项目中，按需修改就行了。

### 本小节对应源码

https://t.zsxq.com/11GVIgjTB

### 结语

在日益繁忙和要求即时交付的前端开发领域中，有效利用现有的工具和资源显得尤为重要。Element Plus 为 Vue 3 开发者提供了这样一个强大的工具，不仅节省了手动编写和调整 UI 的时间，还确保了应用在各种设备和场景下都能提供一致和高质量的用户体验。另外一个重要的原因就是，国内的 `Admin` 前端管理后台大部分都是选择的它作为的技术栈，小哈选择它，也是为了更好的贴合实际企业开发场景。