# Docker 部署 Overleaf

## 写在前面

### 日期

2025.12.25

在此日期之后的部署，可能受网络、镜像源、系统版本、[[Docker]] 版本等影响，产生不可预料的问题。

### 实现的效果

- 使用 HTTP 协议
- 使用 IP + 端口号 访问
- 正常访问、编辑
- 正常编译

## 步骤

1. [[Git]] clone
2. 修改 Docker Compose 配置文件
3. 启动 [[Docker]] 容器
4. 管理员配置
5. 安装 texlive 和字体

## Git Clone

```bash
git clone https://github.com/overleaf/overleaf.git
cd overleaf
# 我在部署时的 Git 提交头指针
git checkout 0ca1888
```

## 修改 Docker Compose 配置文件

将下面这份文件替换目录中的 `docker-compose.yml`

下面这份文件是我做了修改的，我会将修改的地方以及为什么修改写在注释里

```yaml
# ========== 我部署的宿主机 docker-compose 版本是 1，不加这行会报错 ==========
version: '2.4'
# ====================
services:
    sharelatex:
        restart: always
        # Server Pro users:
        # image: quay.io/sharelatex/sharelatex-pro
        # ========== 固定镜像版本号，以便在若干年后可复现 ==========
        image: sharelatex/sharelatex@sha256:719649cd32f8b45743060958dee42b2a4dbf96cf25e459ef2b904dec2f234938
        # ====================
        # ========== 如果宿主机上还有另一个 Overleaf 容器在运行，会报错，所以改名 ==========
        container_name: sharelatex_overleaf
        # ====================
        depends_on:
            mongo:
                condition: service_healthy
            redis:
                condition: service_started
        ports:
            # ========== 更改端口映射 ==========
            - 8099:80
            # ====================
        stop_grace_period: 60s
        volumes:
            # ========== 更改数据存储位置，以便在 recreate 时数据不丢失 ==========
            - ./data/sharelatex_data:/var/lib/overleaf
            # ====================
            ########################################################################
            ####  Server Pro: Uncomment the following line to mount the docker  ####
            ####             socket, required for Sibling Containers to work    ####
            ########################################################################
            # - /var/run/docker.sock:/var/run/docker.sock
        environment:
            # ========== 一些配置项，是否有效还待验证 ==========
            MAX_UPLOAD_SIZE: 2000000000             # 2000MB
            PROJECT_UPLOAD_TIMEOUT: 600000         # 10分钟
            MAX_ENTITIES_PER_PROJECT: 5000         # 每个项目最大文件数
            # 编译服务配置
            COMPILE_SIZE_LIMIT: 10mb               # 编译请求体大小限制
            COMPILE_CONCURRENCY_LIMIT: 48          # 并发编译数量
            PROCESS_LIFE_SPAN_LIMIT_MS: 172800000  # 2天
            DEFAULT_COMPILE_TIMEOUT: 600           # 最大 LaTeX 编译时间（秒）
            # ====================
            OVERLEAF_APP_NAME: Overleaf Community Edition

            OVERLEAF_MONGO_URL: mongodb://mongo/sharelatex

            # Same property, unfortunately with different names in
            # different locations
            OVERLEAF_REDIS_HOST: redis
            REDIS_HOST: redis

            ENABLED_LINKED_FILE_TYPES: 'project_file,project_output_file'

            # Enables Thumbnail generation using ImageMagick
            ENABLE_CONVERSIONS: 'true'

            # Disables email confirmation requirement
            EMAIL_CONFIRMATION_DISABLED: 'true'

            ## Set for SSL via nginx-proxy
            #VIRTUAL_HOST: 103.112.212.22
            # ========== 按照宿主机的 ip 修改 ==========
            OVERLEAF_SITE_URL: http://58.199.162.151:8099
            # ====================
            # ========== 显示在左上角的名称 ==========
            OVERLEAF_NAV_TITLE: TexLab 604
            # ====================
            # OVERLEAF_HEADER_IMAGE_URL: http://example.com/mylogo.png
            # ========== 显示在界面的管理员邮箱 ==========
            OVERLEAF_ADMIN_EMAIL: 1196062575@shu.edu.cn
            # ====================

            # OVERLEAF_LEFT_FOOTER: '[{"text": "Another page I want to link to can be found <a href=\"here\">here</a>"} ]'
            # ========== 显示在脚注的文字 ==========
            OVERLEAF_RIGHT_FOOTER: '[{"text":"Run by"}, {"text": "@jjc", "url": "mailto:1196062575@shu.edu.cn"}]'
            # ====================

            # ========== 发送邮件的邮箱 ==========
            OVERLEAF_EMAIL_FROM_ADDRESS: "1196062575@shu.edu.cn"
            # ====================

            # OVERLEAF_EMAIL_AWS_SES_ACCESS_KEY_ID:
            # OVERLEAF_EMAIL_AWS_SES_SECRET_KEY:

            # ========== smtp 服务的配置 ==========
            OVERLEAF_EMAIL_SMTP_HOST: smtp.shu.edu.cn
            OVERLEAF_EMAIL_SMTP_PORT: 465
            # ====================
            # OVERLEAF_EMAIL_SMTP_SECURE: false
            # ========== smtp 服务的配置 ==========
            OVERLEAF_EMAIL_SMTP_USER: "1196062575"
            OVERLEAF_EMAIL_SMTP_PASS: "Codeforces1407"
            # ====================
            # OVERLEAF_EMAIL_SMTP_TLS_REJECT_UNAUTH: true
            # OVERLEAF_EMAIL_SMTP_IGNORE_TLS: false
            # OVERLEAF_EMAIL_SMTP_NAME: '127.0.0.1'
            # OVERLEAF_EMAIL_SMTP_LOGGER: true
            # ========== 邮箱的脚注 ==========
            OVERLEAF_CUSTOM_EMAIL_FOOTER: "This system is run by jjc."
            # ====================

            # ENABLE_CRON_RESOURCE_DELETION: true

            ################
            ## Server Pro ##
            ################

            ## The Community Edition is intended for use in environments where all users are trusted and is not appropriate for
            ## scenarios where isolation of users is required. Sandboxed Compiles are not available in the Community Edition,
            ## so the following environment variables must be commented out to avoid compile issues.
            ##
            ## Sandboxed Compiles: https://docs.overleaf.com/on-premises/configuration/overleaf-toolkit/server-pro-only-configuration/sandboxed-compiles
            # ========== 这里不注释掉会报错，因为社区版本没有沙盒机制 ==========
            # SANDBOXED_COMPILES: 'true'
            # ### Bind-mount source for /var/lib/overleaf/data/compiles inside the container.
            # SANDBOXED_COMPILES_HOST_DIR_COMPILES: '/home/user/sharelatex_data/data/compiles'
            # ### Bind-mount source for /var/lib/overleaf/data/output inside the container.
            # SANDBOXED_COMPILES_HOST_DIR_OUTPUT: '/home/user/sharelatex_data/data/output'
            # ### Backwards compatibility (before Server Pro 5.5)
            # DOCKER_RUNNER: 'true'
            # SANDBOXED_COMPILES_SIBLING_CONTAINERS: 'true'
            # ====================

            ## Works with test LDAP server shown at bottom of docker compose
            # OVERLEAF_LDAP_URL: 'ldap://ldap:389'
            # OVERLEAF_LDAP_SEARCH_BASE: 'ou=people,dc=planetexpress,dc=com'
            # OVERLEAF_LDAP_SEARCH_FILTER: '(uid={{username}})'
            # OVERLEAF_LDAP_BIND_DN: 'cn=admin,dc=planetexpress,dc=com'
            # OVERLEAF_LDAP_BIND_CREDENTIALS: 'GoodNewsEveryone'
            # OVERLEAF_LDAP_EMAIL_ATT: 'mail'
            # OVERLEAF_LDAP_NAME_ATT: 'cn'
            # OVERLEAF_LDAP_LAST_NAME_ATT: 'sn'
            # OVERLEAF_LDAP_UPDATE_USER_DETAILS_ON_LOGIN: 'true'

            # OVERLEAF_TEMPLATES_USER_ID: "578773160210479700917ee5"
            # OVERLEAF_NEW_PROJECT_TEMPLATE_LINKS: '[ {"name":"All Templates","url":"/templates/all"}]'


            # OVERLEAF_PROXY_LEARN: "true"

    mongo:
        restart: always
        # ========== 部署的这个 Overleaf 版本要求 8.0 的 MongoDB ==========
        image: mongo:8.0.0
        # ====================
        # ========== 如果宿主机上还有另一个 MongoDB 容器在运行，会报错，所以改名 ==========
        container_name: mongo_overleaf
        # ====================
        # ========== 让 MongoDB 监听所有 ip ==========
        command: ["--replSet","overleaf","--bind_ip_all"]
        # ====================
        volumes:
            # ========== 更改数据存储位置 ==========
            - ./data/mongo_data:/data/db
            # ====================
            - ./bin/shared/mongodb-init-replica-set.js:/docker-entrypoint-initdb.d/mongodb-init-replica-set.js
        environment:
          MONGO_INITDB_DATABASE: sharelatex
        extra_hosts:
          # Required when using the automatic database setup for initializing the replica set.
          # This override is not needed when running the setup after starting up mongo.
          - mongo:127.0.0.1
        healthcheck:
            test: echo 'db.stats().ok' | mongosh localhost:27017/test --quiet
            interval: 10s
            timeout: 10s
            retries: 5

    redis:
        restart: always
        image: redis:6.2
        # ========== 如果宿主机上还有另一个 Redis 容器在运行，会报错，所以改名 ==========
        container_name: redis_overleaf
        # ====================
        volumes:
            # ========== 更改数据存储位置 ==========
            - ./data/redis_data:/data
            # ====================

    # ldap:
    #    restart: always
    #    image: rroemhild/test-openldap
    #    container_name: ldap

    # See https://github.com/jwilder/nginx-proxy for documentation on how to configure the nginx-proxy container,
    # and https://github.com/overleaf/overleaf/wiki/HTTPS-reverse-proxy-using-Nginx for an example of some recommended
    # settings. We recommend using a properly managed nginx instance outside of the Overleaf Server Pro setup,
    # but the example here can be used if you'd prefer to run everything with docker-compose

    # nginx-proxy:
    #     image: jwilder/nginx-proxy
    #     container_name: nginx-proxy
    #     ports:
    #       - "80:80"
    #       - "443:443"
    #     volumes:
    #       - /var/run/docker.sock:/tmp/docker.sock:ro
    #       - /home/overleaf/tmp:/etc/nginx/certs
```

## 启动 Docker 镜像

- 由于在容器内部安装 texlive 等，recreate 容器后就会消失
- 有两种方案
    1. 安装后重新打包成一个新的镜像，以后都在新的镜像上启动容器；
    2. 将内部的安装目录挂载到外部
- 这里选择方案 2
- 由于 `-v` 选项或 `volumes` 配置，实际上是将外部的挂载到内部，因此如果一开始就挂载了，会导致挂载空目录进去。而实际上，容器内部本身是有内容的
- 因此
    1. 先启动容器
    2. 然后将容器内的文件复制到外部
    3. 然后在 Docker Compose 文件中挂载到内部

### 启动容器

```bash
docker-compose up -d
```

### 将内部文件复制到宿主机

```bash
sudo docker cp sharelatex_overleaf:/usr/local/texlive ./data/texlive
sudo docker cp sharelatex_overleaf:/usr/share/fonts ./data/fonts
```

### 挂载到内部

向 `docker-compose.yml` 中的 `services/sharelatex/volumes` 添加

```yaml
- ./data/texlive:/usr/local/texlive
- ./data/fonts:/usr/share/fonts
```

#### 最终文件内容

```yaml
# ========== 我部署的宿主机 docker-compose 版本是 1，不加这行会报错 ==========
version: '2.4'
# ====================
services:
    sharelatex:
        restart: always
...
        stop_grace_period: 60s
        volumes:
            # ========== 更改数据存储位置，以便在 recreate 时数据不丢失 ==========
            - ./data/sharelatex_data:/var/lib/overleaf
            - ./data/texlive:/usr/local/texlive
            - ./data/fonts:/usr/share/fonts
            # ====================
            ########################################################################
...
```

## 管理员配置

### 创建管理员帐户

1. 在浏览器中，打开 `http://<ip>:<port>/launchpad`。应该会看到一个包含电子邮件和密码字段的表单。用想用作管理员帐户的凭据填写这些凭据，然后单击“注册”。
2. 然后单击链接进入登录页面（`http://<ip>:port/login`）。输入凭据。登录后，将被带到欢迎页面。
3. 单击页面底部的绿色按钮开始使用。

![img](http://public.file.lvshuhuai.cn/images\21350faa7c6f4dd5988e0595c0237e66.png)

### 创建第一个项目

在 `http://<ip>:<port>/project`页面上，将看到一个按钮，提示创建第一个项目。单击按钮并按照说明进行操作。

![img](http://public.file.lvshuhuai.cn/images\bfcc7c3806c44a0eab95958ba2b0941f.png)

然后，你应该被带到新项目，在那里将看到一个文本编辑器和一个 PDF 预览。

### 创建其他账户

![img](http://public.file.lvshuhuai.cn/images\d14020b024554e3ca725f2a6ab7a75ae-1766645923453-68.png)

![img](http://public.file.lvshuhuai.cn/images\b2f98427220f4f7fbbff1fec89641151.png)

## 安装 texlive 和字体

### 安装 texlive

#### 配置代理

如果不配置代理的话，下载速度会很慢。

推荐在宿主机上配置好 Clash，并开启 `Allow LAN` 配置，在容器里连接到外部代理。

```bash
docker exec -it sharelatex bash 
export HTTP_PROXY="<宿主机代理>"
export HTTPS_PROXY="<宿主机代理>"
export http_proxy="<宿主机代理>"
export https_proxy="<宿主机代理>"
```

#### 安装

```bash
docker exec -it sharelatex bash 
cd /usr/local/texlive
wget http://mirror.ctan.org/systems/texlive/tlnet/update-tlmgr-latest.sh --no-check-certificate
tlmgr option repository https://mirrors.tuna.tsinghua.edu.cn/CTAN/systems/texlive/tlnet/
sh update-tlmgr-latest.sh -- --upgrade
tlmgr option repository ctan
tlmgr update --self --all
luaotfload-tool -fu
tlmgr install scheme-full
```

### 安装字体

```bash
apt update
apt install ttf-mscorefonts-installer
apt install -y latex-cjk-all texlive-lang-chinese texlive-lang-english
fc-cache -fv
```