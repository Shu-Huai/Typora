# 为什么 Spring 循环依赖需要三级缓存，二级不够吗？ - 面试鸭 | 2026最新Spring 面试题+详细答案解析

## 回答重点

其实，如果仅仅是为了解决循环依赖，二级缓存确实是够用的。只要我们在 Bean 实例化（new）之后，不管它需不需要 AOP，都直接把它的代理对象生成出来，放到二级缓存里，B 就可以拿到了。这样循环依赖就解了。

![image.png](https://pic.code-nav.cn/mianshiya/question_picture/1783388929455529986/8flTu9iA_image_mianshiya.webp)

>

💡 那为什么 Spring 非要搞个三级缓存？

这就涉及到了**Spring 的设计原则和 Bean 的生命周期问题**。

在 Spring 的设计中，Bean 的动态代理（AOP）通常是在 Bean 初始化完成之后（`postProcessAfterInitialization`）才创建的。这是标准流程。

如果我们只用二级缓存，为了解决循环依赖，我们就必须在 **Bean 实例化之后** 就立马去创建代理对象放入缓存。

但这会带来**一个问题**： 我们无法预知这个 Bean 到底会不会产生循环依赖。如果它没有循环依赖，但我们却提前给它创建了代理，这就打破了 Bean 的标准生命周期（本该最后创建代理，结果一开始就创建了）。

所以，Spring 引入了三级缓存（singletonFactories），里面存的不是 Bean，而是一个工厂（Lambda表达式）。

这其实是一种**延迟加载**：

- **A 实例化后**：我先把一个**能创建 A 代理**的工厂放到三级缓存，然后我就不管了，继续按正常流程走。

- **如果没有循环依赖**：这个工厂永远不会被调用，A 就在生命周期的最后一步正常创建代理。完美！

- **如果出现了循环依赖**（B 需要 A）：B 去三级缓存找，触发了那个工厂，这时候工厂才被迫提前把 A 的代理对象创建出来，给 B 用。

![image.png](https://pic.code-nav.cn/mianshiya/question_picture/1783388929455529986/F7hWWwRO_image_mianshiya.webp)

**总结一下**：三级缓存就是为了**在解决循环依赖**和**维持标准生命周期**之间做一个平衡。它让我们可以只在真正发生循环依赖的时候，才去提前创建代理对象；否则，就按兵不动，维持原样。

>

⚠️ 我看到评论区有提到：引入三级缓存，主要是为了解决在循环依赖里，B 给自己注入 A 时能提前拿到 A 的代理对象，而不是原始对象。

实际上，如果仅为了解决这个问题，二级缓存直接放代理对象，即让所有 AOP Bean 无条件提前代理就行了。而之所以不这么做，本质还是为了不破坏 Bean 的生命周期。

引入三级缓存只会**在循环依赖发生时才提前代理**，避免了大范围破坏 Bean 的生命周期。

## 扩展知识

### 进一步理解分析为什么需要三级缓存

很明显，如果仅仅只是为了破解循环依赖，二级缓存够了，压根就不必要三级。

你思考一下，在实例化 Bean A 之后，我在二级 map 里面塞入这个 A，然后继续属性注入，发现 A 依赖 B 所以要创建 Bean B，这时候 B 就能从二级 map 得到 A ，完成 B 的建立之后， A 自然而然能完成。

所以**为什么要搞个三级缓存，且里面存的是创建 Bean 的工厂呢**？

我们来看下调用工厂的 getObject 到底会做什么，实际会调用下面这个方法：

```java
protected Object getEarlyBeanReference(String beanName, RootBeanDefinition mbd, Object bean) {
    Object exposedObject = bean;
    if (!mbd.isSynthetic() && hasInstantiationAwareBeanPostProcessors()) {
        for (SmartInstantiationAwareBeanPostProcessor bp : getBeanPostProcessorCache().smartInstantiationAware) {
            exposedObject = bp.getEarlyBeanReference(exposedObject, beanName);
        }
    }
    return exposedObject;
}
```

重点就在中间的判断，如果 false，返回就是参数传进来的 bean，没任何变化。

如果是 true 说明有 InstantiationAwareBeanPostProcessors ，且循环的 smartInstantiationAware 类型，**如有这个 BeanPostProcessor 说明 Bean 需要被 aop 代理**。

我们都知道如果有代理的话，那么我们想要直接拿到的是代理对象，也就是说如果 A 需要被代理，那么 B 依赖的 A 是已经被代理的 A，所以我们不能返回 A 给 B，而是返回代理的 A 给 B。

这个工厂的作用就是判断这个对象是否需要代理，如果否则直接返回，如果是则返回代理对象。

![](https://pic.code-nav.cn/mianshiya/question_picture/1843904816956411905/Ux2pbznQ_uachKQ1Ob4_mianshiya.webp)

看到这明白的小伙伴肯定会问，那跟三级缓存有什么关系，**我可以在要放到二级缓存的时候判断这个 Bean 是否需要代理，如果要直接放代理的对象不就完事儿了**。

是的，这个思路看起来没任何问题，**问题就出在时机**，这跟 Bean 的生命周期有关系。

正常代理对象的生成是基于后置处理器，是**在被代理的对象初始化后期调用生成的**，**所以如果你提早代理了其实是违背了 Bean 定义的生命周期**。

所以 Spring 先在一个三级缓存放置一个工厂，如果产生循环依赖，那么就调用这个工厂提早得到代理对象，如果没产生依赖，这个工厂根本不会被调用，所以 Bean 的生命周期就是对的。

至此，我想你应该明白为什么会有三级缓存了。

也明白，**其实破坏循环依赖，只有二级缓存就够了，但是碍于生命周期的问题，提前暴露工厂延迟代理对象的生成**。

对了，不用担心三级缓存因为没有循环依赖，数据堆积的问题，最终单例 Bean 创建完毕都会加入一级缓存，此时会清理下面的二、三级缓存。

![](https://pic.code-nav.cn/mianshiya/question_picture/1772087337535152129/oCgImo9n_e567e70b-2376-47f4-b3fd-27cb77fec82f_mianshiya.webp)

### 如果不用 AOP，还需要三级缓存吗

从设计角度来说，如果你的项目完全不用 AOP，理论上二级缓存就够了。但 Spring 是个通用框架，它要考虑所有场景。而且 Spring 内部自己就大量使用 AOP，比如事务管理 `@Transactional`、异步执行 `@Async` 这些都是通过 AOP 实现的。所以三级缓存的设计是必要的。

从另一个角度看，三级缓存的额外开销其实很小，就是多存了一个 Lambda 表达式。如果没有循环依赖，这个 Lambda 压根不会被执行，创建完 Bean 就删了。所以性能影响可以忽略不计。

## 面试官追问

#### 提问：如果 A 被循环依赖了，提前创建了代理，那后面初始化阶段还会再创建代理吗？

回答：不会重复创建。Spring 在 getEarlyBeanReference 里面创建代理的时候，会把这个 Bean 标记一下，放到一个叫 earlyProxyReferences 的 Map 里。后面到了正常的后置处理器阶段，会先检查这个 Map，如果发现已经提前代理过了就跳过，直接用之前创建的代理对象。这样保证了不管有没有循环依赖，最终拿到的都是同一个代理对象。

#### 提问：二级缓存存的是代理对象还是原始对象？

回答：存的是从三级缓存的工厂里拿出来的东西。如果这个 Bean 需要 AOP 代理，那二级缓存存的就是代理对象；如果不需要代理，存的就是原始对象。所以二级缓存的作用是缓存三级缓存工厂的产出物，避免同一个 Bean 被循环依赖多次的时候重复调用工厂。

#### 提问：为什么不在实例化的时候就判断要不要代理，需要就直接放代理到二级缓存？

回答：技术上可行，但会破坏 Bean 生命周期的一致性。正常情况下代理是在初始化后期创建的，那时候 Bean 的所有属性都填充完了，各种后置处理器也跑过了。如果一开始就无条件创建代理，那所有 AOP Bean 的代理时机都提前了，不只是有循环依赖的那些。这会让 Bean 的生命周期变得不可预测，调试和排查问题都会更困难。Spring 选择了一个保守的策略：只在必要的时候才提前代理，其他情况都走标准流程。
...
