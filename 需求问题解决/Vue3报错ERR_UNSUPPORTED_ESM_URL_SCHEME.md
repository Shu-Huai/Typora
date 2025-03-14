# Vue 3 报错 ERR_UNSUPPORTED_ESM_URL_SCHEME

## 报错内容

> \> soybean-admin@1.3.11 dev C:\Users\lvzhi\Desktop\soybean-admin > vite --mode test node:internal/modules/esm/load:208    throw new ERR_UNSUPPORTED_ESM_URL_SCHEME(parsed, schemes);          
>
> ^ Error [ERR_UNSUPPORTED_ESM_URL_SCHEME]: 
>
> Only URLs with a scheme in: file, data, and node are supported by the default ESM loader. On Windows, absolute paths must be valid file:// URLs. Received protocol 'c:'    
>
> at throwIfUnsupportedURLScheme (node:internal/modules/esm/load:208:11)    
>
> at defaultLoad (node:internal/modules/esm/load:103:3)    
>
> at ModuleLoader.load (node:internal/modules/esm/loader:756:12)    
>
> at ModuleLoader.loadAndTranslate (node:internal/modules/esm/loader:536:43)    
>
> at #createModuleJob (node:internal/modules/esm/loader:560:36)    
>
> at #getJobFromResolveResult (node:internal/modules/esm/loader:312:34)    a
>
> t ModuleLoader.getModuleJobForImport (node:internal/modules/esm/loader:280:41)    
>
> at async onImport.tracePromise.__proto__ (node:internal/modules/esm/loader:599:25) 
>
> {  code: 'ERR_UNSUPPORTED_ESM_URL_SCHEME' } 
>
> Node.js v23.9.0 ELIFECYCLE  Command failed with exit code 1.

## 解决问题

降级 Node.js 版本

我的版本是最新的 23.1

降级到官网的 LTS 版本 22.14 解决了这个问题