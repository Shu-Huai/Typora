# SpringBoot 实现微信登录

## 前言

小程序登录在开发中是最常见的需求，哪怕小程序登录不是你做，你还是要了解一下流程，后续都要使用到 openId 和 unionId，你需要知道这些是干什么的。

## 需求分析

点击登录会弹出弹窗，需要获取用户手机号进行登录。

![图片](http://public.file.lvshuhuai.cn/images\640.png)

微信登录业务逻辑规则

![图片](http://public.file.lvshuhuai.cn/images\640-1759986798069-1.png)

## 思路说明

参考微信官方文档的提供的思路，官方文档：

https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/login.html

微信官方推荐登录流程：

![图片](http://public.file.lvshuhuai.cn/images\640-1759986798069-2.png)

注意点：

- 前端在小程序集成微信相关依赖，调用 `wx.login` 获取临时登录凭证 code，传给后端。
- 后端调用 `auth.code2Session` 接口，换取 `openId` 和 `UnionId`、会话秘钥 `Session_Key`。
- 开发者服务器可以根据用户标识自定义登录状态，用于后续业务逻辑中前后端交互识别用户身份。

## 表结构说明

创建一张表，用于存储用户的信息以及`openId`。

![图片](http://public.file.lvshuhuai.cn/images\640-1759986798069-3.png)

建表语句：

```sql
CREATE TABLE "family_member" (
"id" bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
"phone" varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '手机号',
"name" varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '名称',
"avatar" varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '头像',
"open_id" varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'OpenID',
"gender" int DEFAULT NULL COMMENT '性别(0:男，1:女)',
"create_time" timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
"update_time" timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
"create_by" bigint DEFAULT NULL COMMENT '创建人',
"update_by" bigint DEFAULT NULL COMMENT '更新人',
"remark" varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '备注',
  PRIMARY KEY ("id") USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='老人家属';
```

## 接口说明

接口跟平时的接口略有不同，参考微信开发者平台提供的流程开发。

请求参数：

```json
{
  "code": "0e36jkGa1ercRF0Fu4Ia1V3fPD06jkGW", //临时登录凭证code
  "nickName": "微信用户",
  "phoneCode": "13fe315872a4fb9ed3deee1e5909d5af60dfce7911013436fddcfe13f55ecad3"
}
```

以上三个参数都是前端调用 `wx.login` 获取返回的参数

- **code：**临时登录凭证 code（有效时间 5 分钟）
- **nickName：**微信用户昵称（现在统一返回：微信用户）
- **phoneCode：**详细用户信息 code，后台根据此 code 获取手机号。

响应示例：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiLlpb3mn7_lvIDoirE4OTE1IiwiZXhwIjoxNDY1MjI3MTMyOCwidXNlcmlkIjoxfQ.nB6ElZbUywh-yiHDNMJS8WqUpcLWCszVdvAMfySFxIM",
    "nickName": "好柿开花8915"
  },
  "operationTime": null
}
```

## 小程序环境搭建

### 必要配置

测试阶段使用测试号，在微信小程序后台获取 appId 和小程序秘钥，前端和后端都需要这两个参数。

![图片](http://public.file.lvshuhuai.cn/images\640-1759986798069-4.png)

### 基础环境说明

修改请求路径

![图片](http://public.file.lvshuhuai.cn/images\640-1759986798069-5.png)

本地开发忽略 https 校验

![图片](http://public.file.lvshuhuai.cn/images\640-1759986798069-6.png)

修改小程序环境的 APPID，改为自己申请的测试号 APPID。

![图片](http://public.file.lvshuhuai.cn/images\640-1759986798069-7.png)

## 功能实现

### 实现思路

![图片](http://public.file.lvshuhuai.cn/images\640-1759986798069-8.png)

### 控制层

#### Controller

```java
@PostMapping("/login")
@ApiOperation("小程序登录")
public AjaxResult login(@RequestBody UserLoginRequestDto userLoginRequestDto){
    LoginVo loginVo = familyMemberService.login(userLoginRequestDto);
    return success(loginVo);

}
```

#### UserLoginRequestDTO

```java
package com.zzyl.nursing.dto;
 
import io.swagger.annotations.ApiModelProperty;
import lombok.Data;

/**
 * C端用户登录
 */
@Data
public class UserLoginRequestDto {

    @ApiModelProperty("昵称")
    private String nickName;

    @ApiModelProperty("登录临时凭证")
    private String code;

    @ApiModelProperty("手机号临时凭证")
    private String phoneCode;
}
```

#### LoginVo

```java
package com.zzyl.nursing.vo;
 
import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;
import lombok.Data;

/**
 * LoginVO
 * @author itheima
 */
@Data
@ApiModel(value = "登录对象")
public class LoginVo {

    @ApiModelProperty(value = "JWT token")
    private String token;

    @ApiModelProperty(value = "昵称")
    private String nickName;
}
```

### 业务层【重要】

一般像这种三方接口调用，通常会封装一个单独业务代码，使其更通用。

- 获取用户 openId
- 获取手机号
- 获取 token（获取手机号需要）

### 微信接口调用-单独封装

新增 `WeachatService` 接口：

```java
package com.zzyl.nursing.service;
 
public interface WechatService {

    /**
     * 获取openid
     * @param code
     * @return
     */
    public String getOpenid(String code);

    /**
     * 获取手机号
     * @param detailCode
     * @return
     */
    public String getPhone(String detailCode);
}
```

新增 `WeachatServiceImpl` 实现类：

```java
package com.zzyl.nursing.service.impl;
 
import cn.hutool.core.util.ObjectUtil;
import cn.hutool.http.HttpUtil;
import cn.hutool.json.JSONObject;
import cn.hutool.json.JSONUtil;
import com.zzyl.nursing.service.WechatService;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Service
public class WechatServiceImpl implements WechatService {


    // 登录
    private static final String REQUEST_URL = "https://api.weixin.qq.com/sns/jscode2session?grant_type=authorization_code";

    // 获取token
    private static final String TOKEN_URL = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential";

    // 获取手机号
    private static final String PHONE_REQUEST_URL = "https://api.weixin.qq.com/wxa/business/getuserphonenumber?access_token=";


    @Value("${wechat.appId}")
    private String appid;

    @Value("${wechat.appSecret}")
    private String secret;


    /**
     * 获取openid
     * @param code
     * @return
     */
    @Override
    public String getOpenid(String code) {

        //获取公共参数
        Map<String,Object> paramMap = getAppConfig();
        paramMap.put("js_code",code);

        String result = HttpUtil.get(REQUEST_URL, paramMap);
        //是一个map
        JSONObject jsonObject = JSONUtil.parseObj(result);
        //判断接口响应是否出错
        if(ObjectUtil.isNotEmpty(jsonObject.getInt("errcode"))){
            throw new RuntimeException(jsonObject.getStr("errmsg"));
        }

        String openid = jsonObject.getStr("openid");

        return openid;
    }

    /**
     * 封装公共参数
     * @return
     */
    private Map<String, Object> getAppConfig() {
        Map<String, Object> paramMap = new HashMap<>();
        paramMap.put("appid",appid);
        paramMap.put("secret",secret);
        return paramMap;
    }

    /**
     * 获取手机号
     * @param detailCode
     * @return
     */
    @Override
    public String getPhone(String detailCode) {

        String token = getToken();
        String url = PHONE_REQUEST_URL+token;
        Map<String, Object> paramMap = new HashMap<>();
        paramMap.put("code",detailCode);
        //发起请求
        String result = HttpUtil.post(url, JSONUtil.toJsonStr(paramMap));
        //是一个map
        JSONObject jsonObject = JSONUtil.parseObj(result);
        //判断接口响应是否出错
        if(jsonObject.getInt("errcode") != 0){
            throw new RuntimeException(jsonObject.getStr("errmsg"));
        }

        return jsonObject.getJSONObject("phone_info").getStr("phoneNumber");
    }

    /**
     * 获取token
     * @return
     */
    private String getToken() {

        Map<String, Object> paramMap = getAppConfig();
        //发起请求
        String result = HttpUtil.get(TOKEN_URL, paramMap);
        //是一个map
        JSONObject jsonObject = JSONUtil.parseObj(result);
        //判断接口响应是否出错
        if(ObjectUtil.isNotEmpty(jsonObject.getInt("errcode"))){
            throw new RuntimeException(jsonObject.getStr("errmsg"));
        }

        String token = jsonObject.getStr("access_token");

        return token;

    }
}
```

上面的代码需要读取获取 `appId` 和 `appSecret`，所以我们在 `application.yml` 配置对于配置。

![图片](http://public.file.lvshuhuai.cn/images\640-1759986798069-9.png)

### 微信登录业务开发

```java
/**
 * 微信登录
 * @param userLoginRequestDto
 * @return
 */
LoginVo login(UserLoginRequestDto userLoginRequestDto);
```

实现方法：

```java
@Autowired
private WechatService wechatService;

@Autowired
private TokenService tokenService;

static List<String> DEFAULT_NICKNAME_PREFIX = ListUtil.of("生活更美好",
        "大桔大利",
        "日富一日",
        "好柿开花",
        "柿柿如意",
        "一椰暴富",
        "大柚所为",
        "杨梅吐气",
        "天生荔枝"
);

/**
 * 小程序端登录
 * @param userLoginRequestDto
 * @return
 */
@Override
public LoginVo login(UserLoginRequestDto userLoginRequestDto) {
    //1.调用微信api,根据code获取openId
    String openId = wechatService.getOpenid(userLoginRequestDto.getCode());

    //2.根据openId查询用户
    FamilyMember familyMember = getOne(Wrappers.<FamilyMember>lambdaQuery(FamilyMember.class)
            .eq(FamilyMember::getOpenId, openId));

    //3.如果用户为空，则新增
    if (ObjectUtil.isEmpty(familyMember)) {
        familyMember = FamilyMember.builder().openId(openId).build();
    }

    //4.调用微信api获取用户绑定的手机号
    String phone = wechatService.getPhone(userLoginRequestDto.getPhoneCode());

    //5.保存或修改用户
    saveOrUpdateFamilyMember(familyMember, phone);

    //6.将用户id存入token,返回
    Map<String, Object> claims = new HashMap<>();
    claims.put("userId", familyMember.getId());
    claims.put("userName", familyMember.getName());

    String token = tokenService.createToken(claims);
    LoginVo loginVo = new LoginVo();
    loginVo.setToken(token);
    loginVo.setNickName(familyMember.getName());
    return loginVo;
}

/**
 * 保存或修改客户
 * @param member
 * @param phone
 */
private void saveOrUpdateFamilyMember(FamilyMember member, String phone) {

    //1.判断取到的手机号与数据库中保存的手机号不一样
    if(ObjectUtil.notEqual(phone, member.getPhone())){
        //设置手机号
        member.setPhone(phone);
    }
    //2.判断id存在
    if (ObjectUtil.isNotEmpty(member.getId())) {
        updateById(familyMember);
        return;
    }
    //3.保存新的用户
    //随机组装昵称，词组+手机号后四位
    String nickName = DEFAULT_NICKNAME_PREFIX.get((int) (Math.random() * DEFAULT_NICKNAME_PREFIX.size()))
            + StringUtils.substring(member.getPhone(), 7);

    member.setName(nickName);
    save(member);
}
```

注意：

小程序所有请求不走后台的用户，所以在新增或修改的时候，不需要自动填充创建人和修改人，修改MP的自动填充。

```java
package com.zzyl.framework.interceptor;
 
import com.baomidou.mybatisplus.core.handlers.MetaObjectHandler;
import com.zzyl.common.core.domain.model.LoginUser;
import com.zzyl.common.utils.SecurityUtils;
import lombok.SneakyThrows;
import org.apache.commons.lang3.ObjectUtils;
import org.apache.ibatis.reflection.MetaObject;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import javax.servlet.http.HttpServletRequest;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

@Component
public class MyMetaObjectHandler implements MetaObjectHandler {

    @Autowired
    private HttpServletRequest request;

    @SneakyThrows
    public boolean isExclude() {
        String requestURI = request.getRequestURI();
        if(requestURI.startsWith("/member")){
            returnfalse;
        }
        returntrue;
    }

    @Override
    public void insertFill(MetaObject metaObject) {
        this.strictInsertFill(metaObject, "createTime", Date.class, new Date());
        if(isExclude()){
            this.strictInsertFill(metaObject, "createBy", String.class, loadUserId() + "");
        }

    }

    @Override
    public void updateFill(MetaObject metaObject) {
        this.setFieldValByName("updateTime", new Date(), metaObject);
        if(isExclude()){
            this.setFieldValByName("updateBy", loadUserId() + "", metaObject);
        }

    }

    /**
     * 获取当前登录人的ID
     *
     * @return
     */
    private static Long loadUserId() {

        //获取当前登录人的id
        try {
            LoginUser loginUser = SecurityUtils.getLoginUser();
            if (ObjectUtils.isNotEmpty(loginUser)) {
                return loginUser.getUserId();
            }
            return 1L;
        } catch (Exception e) {
            return 1L;
        }
    }
}
```

## 校验 Toeken

### 思路分析

用户登录成功之后，返回前端一个 token，这个 token 就是用来验证用户信息的，用户点击小程序中的其他操作，就会 token 携带请求头 `header` 中，方便后台去验证获取用户信息，流程如下：

![图片](http://public.file.lvshuhuai.cn/images\640-1759986798070-10.png)

如果要验证用户的 token，我们可以使用拦截器实现。

![图片](http://public.file.lvshuhuai.cn/images\640-1759986798070-11.png)

代码如下

```java
package com.zzyl.framework.interceptor;
 
import cn.hutool.core.map.MapUtil;
import cn.hutool.core.util.ObjectUtil;
import com.zzyl.common.exception.base.BaseException;
import com.zzyl.common.utils.StringUtils;
import com.zzyl.common.utils.UserThreadLocal;
import com.zzyl.framework.web.service.TokenService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.web.method.HandlerMethod;
import org.springframework.web.servlet.HandlerInterceptor;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.util.Map;

@Component
public class MemberInterceptor implements HandlerInterceptor {

    @Autowired
    private TokenService tokenService;

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {

        //判断当前请求是否是handler()
        if(!(handler instanceof HandlerMethod)){
            returntrue;
        }

        //获取token
        String token = request.getHeader("authorization");
        if(StringUtils.isEmpty(token)){
            throw new BaseException("认证失败");
        }
        //解析token
        Map<String, Object> claims =  tokenService.parseToken(token);
        if(ObjectUtil.isEmpty(claims)){
            throw new BaseException("认证失败");
        }
        Long userId = MapUtil.get(claims, "userId", Long.class);
        if(ObjectUtil.isEmpty(userId)){
            throw new BaseException("认证失败");
        }
        //把数据存储到线程中
        UserThreadLocal.set(userId);
        returntrue;

    }

    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler, Exception ex) throws Exception {
        UserThreadLocal.remove();
    }
}
```

使拦截器生效（`WebMvcConfigurer` 实现类）：

```java
/**
 * 自定义拦截规则
 */
@Override
public void addInterceptors(InterceptorRegistry registry)
{
    registry.addInterceptor(repeatSubmitInterceptor).addPathPatterns("/**");
    registry.addInterceptor(membersInterceptor).excludePathPatterns(EXCLUDE_PATH_PATTERNS).addPathPatterns("/member/**");
}
```

