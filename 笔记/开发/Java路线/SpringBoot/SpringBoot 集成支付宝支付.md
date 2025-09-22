# SpringBoot 集成支付宝支付

## 网页操作步骤

### 进入支付宝开发平台——沙箱环境

使用开发者账号登录开放平台控制平台

### 点击沙箱进入沙箱环境

![img](http://public.file.lvshuhuai.cn/images\640.jpeg)图片

说明：沙箱环境支持的产品，可以在沙箱控制台 沙箱应用 > 产品列表 中查看。

### 进入沙箱，配置接口加签方式

![img](http://public.file.lvshuhuai.cn/images\640-1758010138317-5.jpeg)图片

在沙箱进行调试前需要确保已经配置密钥/证书用于加签，支付宝提供了 系统默认密钥 及 自定义密钥 两种方式进行配置。这里我采取的是默认方式：

开发者如需使用系统默认密钥/证书，可在开发信息中选择系统默认密钥。注意:使用API在线调试工具调试OpenAPI必须使用系统默认密钥。

### 配置应用网关

![img](http://public.file.lvshuhuai.cn/images\640-1758010138317-6.jpeg)图片

应用网关用于接收支付宝沙箱环境的异步通知（对接 From 蚂蚁消息），如创建门店的被动通知。

注意：仅 HTTP 订阅模式的 From 蚂蚁消息才需要配置应用网关，WebSocket 订阅模式的 From 蚂蚁消息无需配置应用网关。

### 生成自己的密钥

![img](http://public.file.lvshuhuai.cn/images\640-1758010138317-7.jpeg)图片

至此，网页操作完成

## idea 操作步骤

### 导入依赖

```xml
<dependency>
   <groupId>com.alipay.sdk</groupId>
   <artifactId>alipay-sdk-java</artifactId>
   <version>4.22.110.ALL</version>
</dependency>
```

### 在 application.yml 里面进行配置

```yaml
alipay:
  appId: 
  appPrivateKey: 
  alipayPublicKey: 
  notifyUrl: （回调接口）
```

### alipay的JAVA配置：AlipayConfig.java

读取yml中的配置信息，自动填充到对应的属性

```java
@Data
@Component
@ConfigurationProperties(prefix = "alipay")
public class AliPayConfig {
    private String appId;
    private String appPrivateKey;
    private String alipayPublicKey;
    private String notifyUrl;

}
```

### 支付接口：新建一个 AliPayController.java

1. 在 Controller 中配置 gateway_url（调用支付宝 url 的一个网关地址）、format（JSON形式）、charset（UTF-8）、sign_type（签名方式 rsa2）
2. 编写一个 Get 请求，（方法参数是一个 AliPay 的配置类里面包括自己生成的订单号、总金额、支付的名称、支付宝交易凭证号和 HttpServletResponse）
3. 创建 Client（他是由通用 SDK 提供的 Client，负责调用支付宝的 API，设置参数包含网关地址、appid、密钥、公钥、format、charset、签名方式）
4. 创建 AlipayTradePagePayRequest，配置 notifyUrl 并设置 Request 参数（参数包含订单号、总金额、支付的名称）（格式：JSON 格式）
5. 通过 AlipayClient 执行 request 调用 SDK 生成表单，用 HttpServletResponse（浏览器响应的一个流）写表单的内容，创建一个 html 的网页）

```java
@Data
publicclass AliPay {
    private String traceNo;
    privatedouble totalAmount;
    private String subject;
    private String alipayTraceNo;
}
privatestaticfinal String GATEWAY_URL = "https://openapi.alipaydev.com/gateway.do";
privatestaticfinal String FORMAT = "JSON";
privatestaticfinal String CHARSET = "UTF-8";
    //签名方式
    privatestaticfinal String SIGN_TYPE = "RSA2";
@Resource
private AliPayConfig aliPayConfig;

@Resource
private OrdersMapper ordersMapper;

@GetMapping("/pay") // &subject=xxx&traceNo=xxx&totalAmount=xxx
public void pay(AliPay aliPay, HttpServletResponse httpResponse) throws Exception {
    // 1. 创建Client，通用SDK提供的Client，负责调用支付宝的API
    AlipayClient alipayClient = new DefaultAlipayClient(GATEWAY_URL, aliPayConfig.getAppId(),
            aliPayConfig.getAppPrivateKey(), FORMAT, CHARSET, aliPayConfig.getAlipayPublicKey(), SIGN_TYPE);

    // 2. 创建 Request并设置Request参数
    AlipayTradePagePayRequest request = new AlipayTradePagePayRequest();  // 发送请求的 Request类
    request.setNotifyUrl(aliPayConfig.getNotifyUrl());
    JSONObject bizContent = new JSONObject();
    bizContent.set("out_trade_no", aliPay.getTraceNo());  // 我们自己生成的订单编号
    bizContent.set("total_amount", aliPay.getTotalAmount()); // 订单的总金额
    bizContent.set("subject", aliPay.getSubject());   // 支付的名称
    bizContent.set("product_code", "FAST_INSTANT_TRADE_PAY");  // 固定配置
    request.setBizContent(bizContent.toString());

    // 执行请求，拿到响应的结果，返回给浏览器
    String form = "";
    try {
        form = alipayClient.pageExecute(request).getBody(); // 调用SDK生成表单
    } catch (AlipayApiException e) {
        e.printStackTrace();
    }
    httpResponse.setContentType("text/html;charset=" + CHARSET);
    httpResponse.getWriter().write(form);// 直接将完整的表单html输出到页面
    httpResponse.getWriter().flush();
    httpResponse.getWriter().close();
}
```

### 在拦截器里面加上：忽略 alipay 接口的配置

遇到的坑：

1. url 中有中文字符报错，更换依赖
2. 官网提供有 easy 版和正式版
3. easy-sdk 好像不太支持中文的 subject，否则 biz_content 就会乱码，那我索性就用了 alipay-sdk 正式版的

### 回调接口

1. 使用的 Post 接口，首先验证交易状态是否成功，获取 request 里面的信息
2. 支付宝验签（使用的是 AlipaySignature（通用 SDK 提供的类）获取一个 String 字符串将其与 sign 签名验证），通过后，使用 OrderMapper 更新到数据库）

使用的 Post 接口，因为官方建议处理付款成功后的操作在异步调用方法中，异步调用为 post 请求，异步回调方法必须为公网 IP，因为支付宝是基于公网访问，访问不了 localhost，需要代理，设置公网IP有两种方案，1、内网穿透，2、将项目部署到服务器，我们项目使用的是内网穿透，使用的是 natapp，配置一条免费的隧道，在 idea 中配置 notifyurl 接口

```java
@PostMapping("/notify")  // 注意这里必须是POST接口
public String payNotify(HttpServletRequest request) throws Exception {
    if (request.getParameter("trade_status").equals("TRADE_SUCCESS")) {
        System.out.println("=========支付宝异步回调========");        
  Map<String, String> params = new HashMap<>();
        Map<String, String[]> requestParams = request.getParameterMap();
        for (String name : requestParams.keySet()) {
            params.put(name, request.getParameter(name));
            // System.out.println(name + " = " + request.getParameter(name));
        }

        String tradeNo = params.get("out_trade_no");
        String gmtPayment = params.get("gmt_payment");
        String alipayTradeNo = params.get("trade_no");

        String sign = params.get("sign");
        String content = AlipaySignature.getSignCheckContentV1(params);
        boolean checkSignature = AlipaySignature.rsa256CheckContent(content, sign, aliPayConfig.getAlipayPublicKey(), "UTF-8"); // 验证签名
        // 支付宝验签
        if (checkSignature) {
            // 验签通过
            System.out.println("交易名称: " + params.get("subject"));
            System.out.println("交易状态: " + params.get("trade_status"));
            System.out.println("支付宝交易凭证号: " + params.get("trade_no"));
            System.out.println("商户订单号: " + params.get("out_trade_no"));
            System.out.println("交易金额: " + params.get("total_amount"));
            System.out.println("买家在支付宝唯一id: " + params.get("buyer_id"));
            System.out.println("买家付款时间: " + params.get("gmt_payment"));
            System.out.println("买家付款金额: " + params.get("buyer_pay_amount"));

            // 更新订单未已支付
            ordersMapper.updateState(tradeNo, "已支付", gmtPayment, alipayTradeNo);
        }
    }
    return"success";
}
```

## 退款流程

1. 创建 Client（他是由通用 SDK 提供的 Client，负责调用支付宝的 API）（参数包含网关地址、appid、密钥、公钥、format、charset、签名方式）
2. 创建 AlipayTradePagePayRequest，设置 Request 参数（参数包含支付宝回调的订单流水号、总金额、我的订单编号）（格式：JSON 格式）
3. 通过 AlipayClient 执行 request 获取 response，通过 isSuccess 判断是否成功，成功后更新数据库状态

```java
@GetMapping("/return")
public Result returnPay(AliPay aliPay) throws AlipayApiException {
        // 7天无理由退款
        String now = DateUtil.now();
        Orders orders = ordersMapper.getByNo(aliPay.getTraceNo());
        if (orders != null) {
            // hutool工具类，判断时间间隔
            long between = DateUtil.between(DateUtil.parseDateTime(orders.getPaymentTime()), DateUtil.parseDateTime(now), DateUnit.DAY);
            if (between > 7) {
                return Result.error("-1", "该订单已超过7天，不支持退款");
            }
        }
    // 1. 创建Client，通用SDK提供的Client，负责调用支付宝的API
    AlipayClient alipayClient = new DefaultAlipayClient(GATEWAY_URL,
            aliPayConfig.getAppId(), aliPayConfig.getAppPrivateKey(), FORMAT, CHARSET,
            aliPayConfig.getAlipayPublicKey(), SIGN_TYPE);
    // 2. 创建 Request，设置参数
    AlipayTradeRefundRequest request = new AlipayTradeRefundRequest();
    JSONObject bizContent = new JSONObject();
    bizContent.set("trade_no", aliPay.getAlipayTraceNo());  // 支付宝回调的订单流水号
    bizContent.set("refund_amount", aliPay.getTotalAmount());  // 订单的总金额
    bizContent.set("out_request_no", aliPay.getTraceNo());   //  我的订单编号

    // 返回参数选项，按需传入
    //JSONArray queryOptions = new JSONArray();
    //queryOptions.add("refund_detail_item_list");
    //bizContent.put("query_options", queryOptions);

    request.setBizContent(bizContent.toString());

    // 3. 执行请求
    AlipayTradeRefundResponse response = alipayClient.execute(request);
    if (response.isSuccess()) {  // 退款成功，isSuccess 为true
        System.out.println("调用成功");

        // 4. 更新数据库状态
        ordersMapper.updatePayState(aliPay.getTraceNo(), "已退款", now);
        return Result.success();
    } else {   // 退款失败，isSuccess 为false
        System.out.println(response.getBody());
        return Result.error(response.getCode(), response.getBody());
    }

}
```

### 订单三十分钟未支付自动取消

#### 使用消息队列

我们可以采用 rabbitMQ 的延时队列。RabbitMQ 具有以下两个特性，可以实现延迟队列

RabbitMQ 可以针对 Queue 和 Message 设置 x-message-tt，来控制消息的生存时间，如果超时，则消息变为 dead letter

RabbitMQ 的 Queue 可以配置 x-dead-letter-exchange 和 x-dead-letter-routing-key（可选）两个参数，用来控制队列内出现了 deadletter，则按照这两个参数重新路由。结合以上两个特性，就可以模拟出延迟消息的功能

#### 优缺点

- **优点：** 高效,可以利用 rabbitmq 的分布式特性轻易的进行横向扩展,消息支持持久化增加了可靠性。
- **缺点：** 本身的易用度要依赖于 rabbitMq 的运维。因为要引用 rabbitMq，所以复杂度和成本变高。

用户下单之后，投递一个 msg 消息存放在 msg 服务器 daunt，该消息 msg 消息过期时间为 30 分钟，一直未被订单消费者消费，消息会转移到死信交换机路由到死信队列中，被我们的死信消费者 30 分钟后消息。

死信消费者在根据订单号码查询支付订单状态，如果是未支付情况下，则将该订单设置未超时。

对筛选出来的订单号码进行核对校验:

1. 订单中是否存在
2. 携带订单号码调用支付宝查询订单支付状态是否为待支付
3. 更新该订单号码状态