# ECO软件功能说明书\-AiKen复古相机\-汉图

- 填写前请阅读 [ECO软件功能说明书通用填写指南V1\.1](https://mi.feishu.cn/docx/AcjjdkVsyouUUOx1MyucxduHnkd) 

- 请联系生态链软件产品经理创建，**勿自行创建。**

# 更新记录

## 版本更新记录\* 

> 提示：初版V1\.0，后续依次为V1\.1……V1\.9，文档内容有调整都需要记录。必填。
> 
> 

|**版本**|**更改内容**|**时间**|**编写人**|**审核人**|**审核意见**|**审核时间**|
|---|---|---|---|---|---|---|
|V1\.0<br>|创建文档|2026\.9\.8|曲歌||||
||||||||
|V1\.1|初稿|2026\.9\.15|盛楠翔||||
||||||||

## OTA计划

> 提示：封样时无法实现，需要后续OTA的需求和功能，请记录在此处。
> 
> 

|**OTA版本和内容**|**预计OTA时间**|**更改人**|
|---|---|---|
||||



# 基础信息

## 产品信息\*

> 提示：Model 仅适用于接入米家的产品。原则上必须要在小米企业组创建（**model:xiaomi\.xxx\.xxx**），请联系对接的生态链软件产品经理创建。必填。
> 
> 

|**产品名称**|小米复古数码相机|
|---|---|
|**产品Model**|待定|
|**生态链公司名称**|上海汉图科技有限公司|



## 项目人员\* 

> 提示：必填。
> 
> 

||**小米**|**生态链公司**|
|---|---|---|
|**软件产品经理**<br>|生态链：曲歌|盛楠翔|
||MIoT：NA||
|**软件项目经理**|李明月|李苏航|
|**交互设计师**|朱修齐|王衎|
|**视觉设计师**|武欣蔚|吴永飞|

## 产品简介

### 产品定义\* 

> 提示：必填。
> 
> 

|**产品关联项**|**详细描述**|
|---|---|
|**产品特点介绍**|一台让年轻人获得胶卷体验的潮玩数码相机。<br>抽拉式过片，无屏幕设计，旁轴光学取景器构图，超焦距免对焦，拿起就拍。<br>模拟一卷36张，拍完传输至手机，选择并套用风格出片。|
|**产品功能概要**|1. 一卷一拍，每卷36张，拍完后需传输至手机并清除相机内文件，方可开始下一卷；<br>2. 按卷选择风格滤镜，在手机端套用风格后出片；<br>3. 提供两种"冲洗"模式：即时模式（传输后立即可查看）和经典模式（传输后模拟若干小时延迟冲洗）；<br>4. 用户可选择多张照片生成拼贴图进行分享；<br>5. 用户可通过完成任务或输入兑换码获得新的风格滤镜。|
|**目标人群**|热爱氛围感的年轻潮人（18\-30岁），追求胶卷质感与拍摄仪式感，不希望承受真实胶卷的技术门槛和经济成本。|
|**需求点/痛点**|1. 手机拍照太“普通”，缺乏仪式感和情绪价值；<br>2. 真实胶卷技术要求高，经济及时间成本太高；<br>3. 希望拥有一台"拿起就拍"的随身相机，操作简单、出片有氛围感。|

### 软件竞争力

- **软件核心卖点**

    > 提示：必填。按重要程度排序。
    > 
    > 

    - **按卷冲洗的仪式体验**

        - 假设观点：按卷拍摄、选风格、冲洗照片的流程设计，让每一卷都有独特的期待感。联动口袋照片打印机，即时获取最后一张，获得社交价值。

        - 基于理由（论据）：富士及一众众筹网红相机已验证冲洗模拟深受用户喜爱，其"揭示"体验创造了持续的惊喜感和社交分享欲。

    - **仿胶卷风格化**

        - 假设观点：目标用户追求仿胶卷、复古等风格化滤镜。

        - 基于理由（论据）：各家手机原生图片App均开始推出类似滤镜，一众第三方滤镜App，用户甚至愿意付费获得。

    - **制作拼贴在社媒分享**

        - 假设观点：目标用户追求通过制作拼贴并在社媒分享来表达个人的审美及生活状态。

        - 基于理由（论据）：小红书等社媒上照片二创后的分享内容是一大主流。



- **关键提升点**

> 提示：如产品有同类老品，需填写；新品可不填写
> 
> 

|**关键功能**|**本产品**|**上一代产品**|**收益变化**|**备注**|
|---|---|---|---|---|
||||||
||||||
||||||

- **竞争力分析**

> 提示：软件功能/性能/用户体验上，怎么竞争
> 
> 

|**产品**|**当前产品**|**Flashback V2**|
|---|---|---|
|开机|抽拉式过片\+1s开机，举起拉开就拍|波轮式过片，开机约需6s|
|传输速度|单图尺寸小，36张需时约70s|DNG大图，27张需时约2分钟|
|冲洗模拟|支持即时/经典双模式<br>经典为3\~24小时随机，更具趣味性|支持即时/经典双模式<br>经典为固定24小时|
|轻量便捷|可选多图进行拼贴二创|不支持|
|影像风格|首发10款（含待解锁款）<br>可通过任务或运营活动解锁获得新风格|首发5款<br>无互动，推新慢（半年2款）|
|即时打印|可配对米家口袋照片打印机<br>按下机身上打印键将即时打印最后一张照片，类拍立得体验|不支持|

### 软件规格表\* 

> 提示：软件规格表可直接从该产品的CDCP文档中复制，并将CDCP文档附在下方。必填。
> 
> 

|**项目**||**内容**|**备注**|
|---|---|---|---|
|接入平台||独立App|小米打印|
|插件类型||其他|不接入米家APP|
|是否有定制云服务||有|1. 风格管理与分发<br>2. 风格解锁体系：行为解锁、兑换码解锁|
|是否涉及算法服务||无||
|联网方式||BLE\+BT\+WiFi 三合一模组|1. BLE用于添加设备<br>2. BT用于与打印机传图<br>3. WiFi\-AP直连，用于与手机传图|
|操作系统|操作系统|Linux|Rockchip的SDK，内核版本是Linux 5\.10|
||首次使用|是|是否该品类第一次使用|
|模组|模组型号/芯片型号|模组：FGN240ASRL\-N1<br>MCU：RV1106B|BLE\+BT\+WiFi 三合一模组|
||米家标准模组|否|不接入米家App|
||首次使用|是||
|特色功能||1. 36张为一组，模拟胶卷导入手机App并套用风格滤镜<br>2. 部分风格滤镜支持开关漏光、颗粒、相框等效果<br>3. 可进行轻量二创生成社媒拼贴图片<br>4. 可配对、连接口袋照片打印机进行单图打印||
|维护|维护方|生态链公司||
||维护周期|3年|指产品EOL之后的的软件运营、迭代、维护周期。|

附\*：该项目的CDCP文档链接。[【飞阅】生态链\-软件概念决策（CDCP）\- 小米复古数码相机（AiKen）\- 汉图](https://mi.feishu.cn/wiki/EKFrwXVGDiGR63kfKzJcxKwintf)

## 硬件信息

### 产品外观ID图\* 

> 提示：必填。
> 
> 

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MmFlYTI4MGI4YjE1ZjkzYWMzMzBmODVlNTQxMWNiMTFfYmU2YzRjODE2NTUyZjc0OTc3ODc5MjY3NzcxMDZiZDVfSUQ6NzY4MzM3ODEwMDk2OTM0NDIwOV8xNzg5NTI2NDAwOjE3ODk2MTI4MDBfVjM)

### 硬件屏幕/按键图\* 

> 提示：必填。
> 
> 

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MzY1NjJmMzcwYjhhYjg4MmUzY2MzOWFjYjFmNTNlNWJfM2IxYjJkNTA0YjM4NzYzYjY3NDAwZTBiYTE0OGIxYTZfSUQ6NzY4NTYzOTk0NTg4OTQwMjAzNF8xNzg5NTI2NDAwOjE3ODk2MTI4MDBfVjM)

按键图

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=YTE2OWRlYTVmYjQ5YmU1ZmE0N2U3NTE5NDU1MjQ2OTBfZmRjYzU2NGU1OTg3MWVmOWQ1NmM0MTBmNmRlM2I5NGNfSUQ6NzY4NTYzOTk4MjQ2OTI3MDUwNl8xNzg5NTI2NDAwOjE3ODk2MTI4MDBfVjM)

屏幕图



### 硬件规格表\* 

> 提示：可以直接引用硬件团队的相关产品说明文档。必填。
> 
> 

[规格书：小米复古数码相机（AiKen）](https://mi-p.feishu.cn/docx/Hs8udahZpoZgKBxODq6clOZ4n2c)

# 开发方式和 IoT 能力\* 

> 提示：必填。
> 
> 

||**信息填写**|**备注（示例）**|
|---|---|---|
|**协议类型**|汉图自定义<br>|Spec开发、Profile开发<br>**注意：使用标准Spec的产品企业必须将SN传回，如无法支持需与生态链软件产品经理提前说明**|
|**SN回传**|不涉及|支持SN传回，场测数据与生产数据需要隔离区分<br>[生态链设备SN上报规范 V1\.0](https://mi.feishu.cn/docx/GSved3lwwodab3xVFbHcHJXJnXg)|
|**插件类型**|Flutter类型|自定义扩展程序（自行开发的插件）、标准扩展程序（米家标准插件）、标准\+自定义扩展程序|
|**独立App**|小米打印App|小米打印App，搭载米家SDK，是米系App（如果支持请填写独立App名称，标注是否搭载米家SDK，标注是否米系App）|
|**联网方式**<br>|BLE\+BT\+WiFi<br>BEL用于添加设备；<br>BT 用于与打印机传图；<br>WiFi直连用于与手机传图；|联网方式指产品接入互联网的方式，用于设备与小米IoT平台进行通信。仅支持 WiFi、WiFi\+BLE、BLE、Zigbee、BLE\-Mesh、本地AP、蜂窝网、PLC、仅网线。|
|**配网方式**|BLE添加设备|配网方式指通过米家APP帮助设备配网以接入小米IoT平台的方式，只在米家APP添加设备时会用到，设备添加成功后与小米IoT平台的通信使用的是联网方式。**不同的联网方式对应不同的配网方式，具体每个联网方式对应哪些配网方式详见创建产品的弹框选择联网方式后出现的配网方式选项。**|
|**操作系统**|Linux（Rockchip的SDK，内核版本是Linux 5\.10）|RTOS、Android、Linux、其他（请补充填写）|
|**固件开发模式**<br>|MCU\+外置通讯模组<br>|小米标准模组\+MCU、基于小米模组二次开发\+MCU、小米模组二次开发（RTOS）；外置通信模块\+MCU\(Andorid 或 Linux系统\)|
|**模组型号/芯片型号**<br>|FGN240ASRL\-N1|[小米模组考文档](https://iot.mi.com/new/doc/tools-and-resources/module)|
|**MCU**|RV1106B|如：MR133（根据自己所选MCU型号填写）|
|**通过蓝牙网关上报**|不支持|支持/不支持，蓝牙子设备需要填写此项|
|**OTA能力及升级途径**<br>|支持，通过自有平台升级|必须支持<br>通过米家平台升级 或 通过自有平台升级|
|**静默OTA**<br>|不支持|中国大陆销售的WiFi联网产品必须支持，海外产品暂不支持<br>[静默OTA参考文档](https://iot.mi.com/new/doc/accesses/direct-access/productcenter/develop-firmware?keywords=%E8%87%AA%E5%8A%A8ota)|
|**畅快连**<br>|不支持|无特殊原因必须支持以下三个能力，三个都支持才是支持畅快连<br>1. 支持靠近配网<br>2. 支持一键配网<br>3. 支持改密同步<br>参考文档[小米畅快连™外发资料](https://mi.feishu.cn/docx/OigWd5d9Uo3tQ3xhc9YcqSdlnkc) |
|**插件大屏适配**|不支持<br>|[米家响应式布局\-适配大屏需求通知](https://mi.feishu.cn/docx/M9NnditluoFj0ExA31ZcogmYnpc) <br>无特殊原因必须支持<br>支持在pad、折叠屏等大屏幕设备上使用插件的操控体验<br>1、Android<br>A\.圆角矩形容器20dp<br>B\.高：屏幕的短边\*0\.85（短边指的是：屏幕显示区域长、宽中最短的那个边）<br>C\.宽：根据高度按照高宽比18:9计算<br>2、IOS<br>A\.圆角矩形容器20pt<br>B\.高：屏幕的短边\*0\.85（短边指的是：屏幕显示区域长、宽中最短的那个边）<br>C\.宽：375pt<br>3、处理逻辑<br>A\.出现：点击插件出现（无快捷卡片情况），从宫格位置逐渐放大展开，展示插件首页<br>B\.小窗口内插件布局、样式同手机，需无异常；需能正常点击、滑动、跳转等交互，UI没有异常（文案图标重叠、锯齿等）<br>C\.退出插件：<br>插件第一页情况下点击左上角返回button（同手机）<br>点击插件以外的蒙层插件关闭|
|**深色模式**|不支持|无特殊原因必须支持[参考文档](https://iot.mi.com/new/doc/accesses/direct-access/extension-development/topics/mode?keywords=%E6%B7%B1%E8%89%B2%E6%A8%A1%E5%BC%8F)|
|**无感配网**<br>|不支持|根据工厂产线能力评估是否支持<br>参考文档[无感配网开放接入资料](https://mi.feishu.cn/docx/IYCNdXiJhocE5yxiwgpcKOBtnVh) |
|**电机及电机驱动**|不涉及<br>|- 风险结论：「高、中、低、无」<br>- 电机：是否为首次应用<br>- 电机驱动：是否有逻辑或代码变更<br>> 重点评估原则：重点评估该电机及驱动方案，是否已经过市场<br>> <br>> 量产及用户充分验证、无存量质量问题<br>> <br>> <br>- 参考品类<br>> 风险等级P0：空气净化器、加湿器、风扇、电暖器、除湿机、烟灶、洗碗机、浴霸、香氛机、扫地机器人、滑板车\&踏板车<br>> <br>> 风险等级P1：洗地机、吸尘器、电动牙刷、投影仪、智能窗帘、晾衣机、智能宠物、筋膜枪、健身大件、按摩小件、按摩大件、摄像机<br>> <br>> 注：上述不包含品类，根据电机是否为核心器件评估，如不涉及核心器件，写不涉及。<br>> <br>> |

# 功能定义

## 名词解释



> 提示：为了方便阅读者理解，如有相关专有名词请添加相关解释。
> 
> 

|**名词**|**解释**|**备注**|
|---|---|---|
|过片|此设备为仿胶卷数码相机，有刻意不支持连拍，每拍一张需要用户在硬件进行一次抽拉后模拟胶卷相机的过片行为。||
|冲洗|此处的冲洗可以理解为将相机端的照片传输到手机端后，在App端再将预先选择的风格套用到该卷所有照片上的行为。||



## 设备端功能

### **功能逻辑图\* **

> 提示：填写设备端的主要功能点，给出设备端主要功能的层级和归属关系图，功能的层级可以根据实际产品增减。必填。
> 
> 



### **交互设计\* **

> 提示：对于有视觉交互（例如屏幕、特殊的灯带）的设备，这里放设备的交互图。机身指示灯的设计，必须遵循小米IoT设备UED规范：https://iot\.mi\.com/new/doc/tools\-and\-resources/design/device\-ued?keywords=UED。必填。
> 
> 

[【Aiken】小米复古数码相机 对接设计信息表 ](https://mi-p.feishu.cn/docx/JfVZdNWAYoGynxx2u1Ucs9KfnHf)





### **重置WiFi和恢复出厂设置\***

> 提示：设备重置作为最基础功能，请单独列出该功能的操作方式、重置内容等。必填。
> 
> 

|**前置****状态**|**操作**|**结果**|**重置功能**|**重置结果**|
|---|---|---|---|---|
|开机待机态。<br>> 非报错状态、操作执行、传输中、固件升级中等瞬态。<br>> <br>> <br>|长按“打印”键7秒：<br>> 长按3s关机与长按7s重置的时间区间：3s关机时不松手，继续按到4s以上记入重置计时（累计需7s）。3\~4s间松手=关机，4s后松手=进入重置计时。<br>> <br>> <br>|橙灯闪烁2s后白灯常亮。<br>设备恢复出厂设置成功。|App用户绑定关系|清除APP用户绑定关系|
||||绑定的口袋打印机|清除已绑定的口袋打印机|
||||||
||||设备设置选项（日期戳、默认冲洗方式）|重置为默认值|
||||设备内照片文件|删除设备内照片文件|



### **功能详细设计\* **

> 提示：详细描述设备端的功能，可以根据需求增加功能层级。必填。
> 
> 



|**一级功能**|**二级功能**|**功能描述、参数与逻辑**|**备注**|
|---|---|---|---|
|APP配对||- 拉开设备开机；<br>- 若设备未被任何账户添加，则开始广播，允许App端发起添加配对；<br>- App端发起添加后，根据插件UI提示，短按“打印”键一次；|- 硬件仅三个按键：快门键、打印键与复位键。复位键需工具，快门键在不配对状态下即可用于拍照，若复用快门键触发配对会造成功能冲突。只能退而求其次使用“打印”键来进行配对，也能因此确保用户开闸进入开机状态。|
|设备控制<br>|开机|- 关机状态下，拉开设备则自动开机；<br>- 开机后显示屏显示；||
||关机|- 正常待机状态下（拉开或关闭），无操作开始自动关机计时，无操作60秒后自动关机；<br>- 长按“打印”键3s后关机；<br>- 传输数据、OTA及重置过程不计入自动关机计时；|- 无操作自动关机计时后续将根据实际情况尝试优化调整。|
||过片、拍摄|- 过片：一次开合设备完成一次过片，过片后可拍摄一张照片；<br>- 拍摄：可拍摄状态下，按下快门拍摄一张照片。拍摄完成后剩余可拍数量 \-1；|- 用户过片后不拍，直接再抽拉过片，计数器不变，直到按下快门时 \-1。也就是用户可以抽拉若干次，按下快门才完成一次拍摄，计数 \-1，实际存储多一张照片。|
||屏幕显示|- 显示剩余可拍数量及设备状态；<br>- 具体参见[【Aiken】小米复古数码相机 对接设计信息表 ](https://mi-p.feishu.cn/docx/JfVZdNWAYoGynxx2u1Ucs9KfnHf)|详情见设计信息表中88屏部分|
||Type\-C USB|- 仅用于充电|- 与电脑连接后，不可见，防止用户作为U盘占用存储影响正常拍照。|
|固件OTA|/|- 插件端有新固件提示升级；<br>- 通过插件中进行固件升级；|- 升级过程中，短按或长按电源键（打印键）均无效。|
|恢复出厂设置|恢复到默认出厂设置|- [参见“重置WiFi和恢复出厂设置”交互设计](https://mi.feishu.cn/wiki/L5bEwMQvki32AVkHfvLc5fYFnxb#share-DKP0dvNoiofkihx0Gk6cZZO1nbf)||

### **其他**

> 提示：根据生态链软件质量团队要求，涉及「电机专项」的品类，需要明确说明
> 
> - 电机是否为首次应用、电机驱动是否有逻辑/代码变更，并清晰列明对应差异点；
> 
> - 若电机驱动逻辑未变，但存在工程重构、代码重写，均视为发生变更，需要完整梳理并明确电机驱动逻辑；
> 
> - 涉及品类包括
> 
>     - 风险等级P0：空气净化器、加湿器、风扇、电暖器、除湿机、烟灶、洗碗机、浴霸、香氛机、扫地机器人、滑板车\&踏板车
> 
>     - 风险等级P1：洗地机、吸尘器、电动牙刷、投影仪、智能窗帘、晾衣机、智能宠物、筋膜枪、健身大件、按摩小件、按摩大件、摄像机
> 
> 

暂无



## 小米打印APP内该设备功能

### 适配小米打印APP版本\* 

> 提示：这里是支持的米家App最低版本。必填。
> 
> 

不接入米家App。

仅适配（小米打印版本号5\.0及以上版本），前序版本无法添加使用此产品。

### 插件首页功能

#### **功能逻辑图\* **

> 提示：这里列出插件的功能逻辑图，功能的层级可以根据实际产品增减。必填。
> 
> 



#### 功能详细设计\* 

> 提示：详细描述插件端的功能，可以根据需求增加功能层级。**如果插件类型是“标准\+自定义扩展程序”，自定义实现的功能，请务必在备注栏添加文案“自定义实现”。**必填。
> 
> 

|**一级功能**|**二级功能**|**功能描述、参数与逻辑**|**备注**|
|---|---|---|---|
|首页<br>|结构|1. 设备连接状态<br>2. 电量信息<br>3. 剩余可拍数量信息<br>4. 风格选择<br>5. 取出命令|- 电量信息需要显示百分比|
||设备未连接|- 尝试自动回连，超时候提供“连接”按钮手动连接设备；<br>- 提示打开相机开机；|![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ZTM2Nzk3MjQ0MDYyZWU3MTY3MzU4MDJjMGQyNjJmNTdfMmM0MDg1Zjk3MmM2MjBkOWI1NzcyOWMyNWFhZjU0YjlfSUQ6NzY4NTU5MDI0MjI4ODMyMzU1NF8xNzg5NTI2NDAwOjE3ODk2MTI4MDBfVjM)<br><br>![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=YTFkOGY3ZTBkMGRhZmNiNjczM2ZlMTU2ODhlNTg1NDRfOTA3ZDJjMWFhODk0OGY5MjFlZWVmOTQ0MWRkYTA5NTdfSUQ6NzY4NTU5MDMwNDYzNTk0ODAxNV8xNzg5NTI2NDAwOjE3ODk2MTI4MDBfVjM)<br>|
||设备已连接|- 显示剩余电量信息；<br>![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ZmIyNjViMTllYzBjNjMwNjhjZDZlODAyZDlkYjk5ZjJfMTk2N2M4MGU4MjU5YWQ5NDQyMzZkNjNjNzZkY2U2MDRfSUQ6NzY4NTY4MzIxNjY0MTEzMzc5OF8xNzg5NTI2NDAwOjE3ODk2MTI4MDBfVjM)<br>- 与硬件同步，显示已选风格及剩余可拍数量信息；<br>|![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ZWQyYjE3MDQ3YzU3NDUwNmJiMWNkMzAyY2VhMWFjOTJfMjZiZjQyZmNmMzk4NjI4NGJlZTQyMjQ4MjU3NTFjMWRfSUQ6NzY4NTU5MjA3NDEyOTEzMjc3NF8xNzg5NTI2NDAwOjE3ODk2MTI4MDBfVjM)<br><br>|
||选择风格|- 未选择风格时提示“选择风格”；<br>- 选择风格后显示风格名；<br>- 点击进入风格列表可选择/更换风格；|- 每次重置为一卷开始时，可拍36张，**风格为“未选择”**；<br>- 决定取出前均可更换风格；|
||风格列表<br>|- 陈列风格分为已解锁和待解锁；<br>- 风格卡片提供以下信息：<br>    - 样图；<br>    - 风格名称；<br>    - 风格标签；<br>    - 已拍摄卷数；<br>    - 待解锁状态<br>- 排序按风格名称排序；<br>- 点击风格卡片进入风格详情；<br>- 点击底部解锁新风格弹出兑换码输入弹窗<br><br>- ~~提供“全部”和标签作为列表筛选；~~<br>- ~~点击“选择”则选中风格；~~<br>- 待解锁风格：<br>    - 提供信息与可用风格相同；<br>    - “选择”按钮 变为 “解锁”字样；<br>    - 未达标时点击“解锁”后弹框提供解锁所需要求，当前完成度；<br>    - 达标时点击“解锁”后，动画🎉解锁成功，随后该风格变为可用风格，按钮变为“选择”，再次点击为选中该风格；<br>|![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ZDc3NDY4NGIwMTlkODMzODQ3YWVkN2YyMzk1YjgxZjBfMWIyOThhNjExMjNlN2QyYzc1MmYzNDZiOWQzOTk4N2FfSUQ6NzY4NTYwNTY0NDc5NjAyMTcxNl8xNzg5NTI2NDAwOjE3ODk2MTI4MDBfVjM)<br><br>![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NGE4ZWNkMzdlMWJhN2FjZDk3ZTU3MmJhYWEzNjAwYWVfZmVhODUxYzEyMDMxNjA1NTU2NjI2NTcyMDFkMDYxODRfSUQ6NzY4NTYwNzg1MTI4MDI3MjU5OF8xNzg5NTI2NDAwOjE3ODk2MTI4MDBfVjM)<br><br>|
||风格详情|- 显示以下内容：<br>    - 风格名称；<br>    - 风格介绍；<br>    - 风格标签；<br>    - 样片大图（不可点击再进入单图预览模式）；<br>    - 以下特效开关，打开后样图需要实时展示效果：<br>        - 相框<br>        - 漏光效果；<br>        - 暗角效果；<br>- 底部命令首先判断是否已解锁，其次判断是否已下载：<br>    - 待解锁风格底部显示：<br>        - 未满足不可解锁时：解锁指引文案；<br>        - 已满足可解锁时：“解锁风格”；<br>    - 已解锁风格底部：<br>        - 未下载时：下载此风格；<br>        - 已下载时：选用此风格；|![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=Zjc5ZTlmODg2NjQ2MzA2MGUyZTNhYjkwZTViNjRmNTlfYzk0MDY1MmQyY2YyODE1MDk4MWYxOTJkMjlhYWUyZDNfSUQ6NzY4NTYwODYzODM4NzQ3MzM1NV8xNzg5NTI2NDAwOjE3ODk2MTI4MDBfVjM)<br><br>![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=YTBhNWYwMDlhZTQ1OTU1ZTYyNTBiZmY2MDU0NzJiYTJfODUyYTcxZjA2NmVjNmM1ZDIyMDY5YTU2NDZkNDQ1NzhfSUQ6NzY4NTYwODc1MzQwMzgyNTEyMF8xNzg5NTI2NDAwOjE3ODk2MTI4MDBfVjM)<br><br>![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=OTNmZDE2M2Q0ZWIxYmMyOTRiODc5YjJjNzc5Yjg1NDVfNGZkOTUzYmFhY2M4ZTBiYjcxMGFkYjEzYzZkNTE1MGZfSUQ6NzY4NTYxMDQyMTU2MjU3NTg0NV8xNzg5NTI2NDAwOjE3ODk2MTI4MDBfVjM)<br><br>![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MjdkYTFhNDE1MDYwZjY3NjNlNzA3MWRlMGNhNjM3NWFfMzg5N2U1MzBmZTlkMDEwYjM5MWY0NmZhNDIzYTJjYzVfSUQ6NzY4NTYxMDQ1NDMxOTk3NTM5N18xNzg5NTI2NDAwOjE3ODk2MTI4MDBfVjM)<br>|
||取出（传图）|- 未拍照时，命令为不可用状态；<br>- 已拍照但未满36张时，显示为“提前取出”，用户可开始传图；<br>- 拍满36张一卷后，显示为“取出并冲洗”，开始传图；<br>- 点击“取出”后，弹框询问冲洗方式（当设置为“每次询问”时）；<br>- 取出传图后，并确认传输成功后删除相机内照片；<br>|- 若传输过程被打断（如用户离开米家等），不能删除相机内原图，用户可在插件中重新点击“取出”开始重新传图。若部分图片已被保存到手机，新流程中同名覆盖；<br>- 传图成功后：<br>    - 删除相机内原图；<br>    - 相机复位到一卷初始状态（可拍数量重置为36张）；<br>    - 风格为“未选择”；|
|暗房<br>|结构|1. 胶卷列表及操作<br>2. 卷内照片列表及操作<br>3. 单图浏览模式及操作||
||胶卷列表|- 列表为空时：<br>    - 空列表设计，提示还没有“取出”冲洗的胶卷；<br>- 列表非空时：<br>    - 列表时显示已取出的胶卷；<br>    - 最新的在列表最上；<br>    - 已冲洗胶卷项显示：<br>        - 名称；<br>        - 选用的风格；<br>        - 包含的相片数量；<br>        - 取出的日期\+时间；<br>        - 封面图：<br>            - 冲洗中为图标\+底片图示；<br>            - 已冲洗默认为首图，用户可进入更改；<br>    - 冲洗中胶卷显示冲洗倒计时（HH:mm格式），可不显示以上已冲洗显示项；<br>        - 点击冲洗中胶卷后弹框提示仍在冲洗中；<br>    - ~~提供“全部”及已使用风格标签用于筛选列表显示内容（如点击“温暖午后”则只显示应用该风格的胶卷）；~~|![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=YzcyNzI5YmJkNGEwZTZjY2RlZmUxNjVjYTg4ZGM2NGRfNmQ3MDBmMzE3OWY0ZWQzNzNjOWJhZjdiNTliMWZkMDdfSUQ6NzY4NTYxMDk2MzYwNTI2MTI2OV8xNzg5NTI2NDAwOjE3ODk2MTI4MDBfVjM)<br><br>![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NzA0ZjRmMzM4YzIyZmMyNDY0NjkyNTJmMjVjM2ZkZGRfYjI5NjM5ZjE4MWEwYzkyN2YzMGU4NmMyYzI1N2Y3YjdfSUQ6NzY4NTYxMDk5NDY4NDk1NTkwN18xNzg5NTI2NDAwOjE3ODk2MTI4MDBfVjM)<br>|
||胶卷列表操作|- 点击列表中一个胶卷项目，进入卷内多图浏览页面；<br>- 从右向左滑动一个胶卷项，呼出“删除”操作；<br>    - 点击“删除”后，弹框要求用户确认，确认后删除该胶卷及内含所有照片；<br>- 冲洗中的胶卷不可删除（滑动抖动）|![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=OGZhZGQzNDU5OTkzNjQxMGQyMjFhYWU4ZTBmMjJlY2NfZWQ4NWY4NTkyZjQ2NTU2ZWZkZDM2NDY4MDM1MTZiYzRfSUQ6NzY4NTYxMTkzNjkyMjM0MDI5N18xNzg5NTI2NDAwOjE3ODk2MTI4MDBfVjM)<br><br>![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=YjFlOTk1NDJjNzA5YTM1YmM1NDA2NjNlODBmMzZlMDJfZGU5YWM0MWI0YmM1ZWRmMjU5MjJmMzIyYmE4ZTdjNTFfSUQ6NzY4NTYxMjQyODMwMjAxMTY5MF8xNzg5NTI2NDAwOjE3ODk2MTI4MDBfVjM)<br>|
||卷内多图浏览|- 重命名：点击“编辑”图标可更改胶卷名；<br>- 点击“保存全部”将保存卷内所有图片至手机图库默认文件夹（如 DCIM/Camera）<br>- 点击“选择”进入多选模式；<br>- 点击“创作”进入创作模式；<br>|![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=OTg5ZTBlYjVjZGU1MTc2MWMyOTQ1MTFmYTQ0ZDdjYjZfNWUwYTg4MWRiMWRlNTI1ZjM0MGEzZGZmMzk3ZWExMzBfSUQ6NzY4NTYxMjc0MDI0NDg1MTkzOF8xNzg5NTI2NDAwOjE3ODk2MTI4MDBfVjM)<br><br>|
||多选模式|- 多选模式中，选择至少一张照片后，用户可以：<br>    - 保存：保存选中的图片到设备图库默认位置；<br>    - 删除：删除选中的照片，有弹框确认；|![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ZTdiNzI5NWNiYzkwM2M5OGNhNDQ0NWQxMjk0MTI4YTlfMWFmNWY3ZTNiMjIwYjdjNzE4MWZhNGNjMDAwMTYwMTZfSUQ6NzY4NTYxMzY5NjQ1NDIxNjY0Nl8xNzg5NTI2NDAwOjE3ODk2MTI4MDBfVjM)<br><br>|
||创作|- 选择模板：点击模板缩略图；<br>- 添加图片到拼贴图：<br>    - 点击“添加图片”；<br>    - 可选1、2、3、4张，最多4张。多选有次序；<br>    - 根据选择照片数量，选用模板中对应的预设layout，按序填入图片；<br>- 添加拼贴图：点击右侧虚框添加一个拼贴图；<br>- 保存：点击“保存”，将所有有图片的拼贴图保存到手机相册默认位置；<br>- 有添加图片后，点击返回，需要清空提示弹窗；<br>|![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MDdkZmY2YjJlNjZhYjEzNTliMjcyY2EyZjVjZTJmMjFfNzllMzQwYTE5MGEwOTFlNzEyZDA5ZTkyYTliNWJkZGNfSUQ6NzY4NTYxNDY4Njc0NTg1Njk2NF8xNzg5NTI2NDAwOjE3ODk2MTI4MDBfVjM)<br><br>![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=YTYyMzA4YTA0MThkN2Y4YjI0YTM4NTU2ODJlNGQzODZfYmNjNWE5Yjc5MzYzMmVlMmVlODIxNDIyYjkxMGM2YTJfSUQ6NzY4NTYxNDkyMjY5NjM5NTk4OF8xNzg5NTI2NDAwOjE3ODk2MTI4MDBfVjM)<br><br>![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ZDVkMWNhOTEwYjAwNjY4MWIwMWJlMzRjZGVjZmYxNjNfYmFiNWEwOTBkNGNmZTQzYzQxMWRkMDRjNjg0MWQ3YjdfSUQ6NzY4NTYxNTgzMDIzOTEyMDM0Nl8xNzg5NTI2NDAwOjE3ODk2MTI4MDBfVjM)<br><br>|
||单图浏览|- 在多图预览非多选模式下，点击某图进入该图单图浏览模式；<br>- 用户左右滑动浏览上一张、下一张图片；<br>- 不支持旋转，支持双指放大缩小，最小为自适应填满宽度；<br>- 不提供裁切、编辑功能；<br>- 提供“设为封面”、“打印”、“保存”、和“删除”功能；||
||单图操作|- 点击“设为封面”将该照片设置为该胶卷在胶卷列表中的封面缩略图；<br>- 点击“保存”将该照片保存到手机相册对应胶卷文件夹中，若已有则自动重命名（文件名末尾添加（01）之类）；<br>- 点击“打印”开始单图打印流程；<br>- 点击“删除”，弹框确认，确认后删除该照片。删除后，在胶卷内不再可见，但不删除用户保存到手机相册的对应照片；||
||单图打印<br>|- 点击“打印”；<br>- 上拉面板提供同米家账号已配对照片打印机列表；<br>- 用户选择一款打印机：<br>    - 与打印机进行蓝牙连接：<br>        - 连接失败：弹窗提示；<br>        - 连接成功：继续；<br>    - 连接成功后，将所选图片带入打印机，跳过“打印预览”直接开始打印；<br>    - 打印过程：<br>        - 异常、失败按正常打印机已有逻辑提示处理；<br>        - 成功后继续；<br>    - 打印成功后，提示完成，提供“完成”按钮，点击缩回上拉面板；|- 是不是需要跳出App到米家中？@崔道攀|
|设置|结构|1. 冲洗方式<br>2. 可用风格<br>3. 日期戳<br>4. 口袋照片打印机（配对）<br>5. 设备名称<br>6. 固件版本<br>7. 帮助与反馈<br>8. 关于设备<br>9. 删除设备|![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=YTMwNTA4MzkzNDM4ZmM1ZTY2OGE3YjA4ZGFhYTdkNWRfMzljYTYyOWQwYzAzZTg0Y2E1ZmRhZjg2YWRjOTZkZmJfSUQ6NzY4NTYyNTEzMTM4NDkxNjkzOV8xNzg5NTI2NDAwOjE3ODk2MTI4MDBfVjM)<br><br>|
||可用风格|- 点击进入风格列表页；<br>- 此处进入风格列表与从相机页进入唯一且关键的区别是，设置中进入无法下载和选择风格。但是可以查看详情、尝试开关特效，了解解锁任务和去解锁已满足风格。||
||冲洗方式|- 提供三个选项：<br>    - 每次询问；<br>    - 即时冲洗：立等可取；<br>    - 经典冲洗：须等待3\~24小时；<br>- 出厂默认项为：每次询问；|- 即时冲洗模式为点击“取出”后，立刻可进入该卷浏览拍摄的照片；<br>- 经典冲洗模式：<br>    - 不立刻对用户显示拍摄的照片，点击“取出”后，进入胶卷列表；<br>    - 该卷被随机赋予一个3\~24小时之间的小时数作为倒计时。<br>    - 倒计时结束后，用户可进入该卷浏览拍摄的照片；|
||~~自动保存所有~~|- ~~开、关选项~~<br>- ~~出厂默认项为：关闭~~|- ~~用户选择打开后，从相机传输照片到手机端后，将自动保存该卷所有照片到手机相册下的文件夹中；~~|
||日期戳|- 开、关选项<br>- 出厂默认项为：打开|- 日期戳格式为：'YY MM DD<br>- 例如：'26 08 03<br>- 日期戳字体设计参考如下<br>![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MWUyNzA5M2I5MTk1MDU4NzczODc3NmMzMmNmMDYyYjRfOTAzMDlhMjVhNjM0MDhhMjZhYjIwYjNjNTdiMTc5NGNfSUQ6NzY4MzQwMDEyODc3ODYzNjUwOF8xNzg5NTI2NDAwOjE3ODk2MTI4MDBfVjM)|
||口袋照片打印机|- 图文说明：<br>    - 支持的口袋打印机：1代、1s和Pro；<br>    - 确保米家中已添加打印机；<br>    - 按下相机上的“打印”键可发起打印；<br>- 用户已在米家添加的打印机列表；<br>    - 未配对：点击进行配对；<br>    - 已配对：点击解绑；<br>- 每台相机只能绑定配对一台口袋照片打印机；|![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NzA0Nzg4ZWU4Y2U3OTQ1NDBkYzY0NWJjMmU5YmFlODJfNGIwMzQ1NGI1ZmVjNWE2YTNlYzM0NWMyNzY5MDMxMGJfSUQ6NzY4NTYyNjA2MzAxOTM5NjA2Nl8xNzg5NTI2NDAwOjE3ODk2MTI4MDBfVjM)<br><br>![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MzM2MDQxMzI5MWUzZDZmMDA2ZmNiZGYxN2IxNzg2YjBfMjA5Nzc4NDFjMWUzN2ZmMTk1Mjg5OGM4OTc3MTM0YzFfSUQ6NzY4NTYyNjA4OTg0MjEzNDIyOV8xNzg5NTI2NDAwOjE3ODk2MTI4MDBfVjM)<br>|
||固件版本|- 进入查看当前固件版本;<br>- 有新固件更新时，提供提醒；<br>- 有新固件时，提供“更新”按钮：<br>    - 点击“更新”后，首先检查电量是否满足电量要求；|- 具体电量要求需要后期研发阶段实测决定。|



#### 特殊情况处理

> 提示：根据实际情况填写，没有可以写“无”。
> 
> 

暂无



### 插件设置页功能

> 提示：插件右上角“更多”按钮内设置页的功能逻辑，分为自定义设置项和米家通用设置项。
> 
> 

暂无，不接入米家App。



#### **自定义设置项\* **

> 提示：这些设置项由厂商自行开发，通常配置一些不常用的功能。必填。
> 
> 

暂无，不接入米家App。

|**一级功能**|**二级功能**|**功能关键参数或逻辑**|**备注**|
|---|---|---|---|
|尾灯常亮|开关尾灯灯常亮功能<br>|开启：车辆通电尾灯常亮<br>关闭：尾灯随前照灯亮灭||
|||||
|||||



#### **米家通用设置项\* **

> 提示：这些设置项是米家通用设置项，不需要开发，只需要选择“支持”或“不支持”。必填。
> 
> 

不接入米家App。

|**序号**|**设置项**|**是否支持**|**备注**|
|---|---|---|---|
|1|设备名称|支持|必选|
|2|按键设置|不支持|多键开关必选|
|3|位置管理|支持|必选|
|4|设备共享|支持|可选，非特殊情况需要支持|
|5|智能场景|支持|可选，非特殊情况需要支持|
|6|产品百科|支持|在中国大陆销售的产品必须支持，在海外销售的产品暂不支持|
|7|固件升级|支持|必选|
|8|帮助与反馈|支持|必选|
|9|更多设置|支持|必选|
|10|米家首页显示|支持|必选，默认开启，用户可以关闭|



### **插件交互设计\* **

> 提示：这里放完整插件交互设计图或链接。必填。
> 
> 

https://www\.figma\.com/design/HQ3E1d6JH94VyWgogfvHwK/Aiken?node\-id=0\-1\&t=Y6YRVGspHqLQEHub\-1

## 小米打印APP改造需求

### 小米打印APP修改需求

[独立APP：小米打印 APP 功能说明书](https://mi-p.feishu.cn/docx/Aczqd8hRvoTt9NxgIdycJpnFnM1)

### 改造交互

@王衎小米打印App的交互figma有了吗？

## 数据统计\*

> 提示：
> 
> - 产品经理主要负责定义到「事件类型」（如曝光 view、点击 click），埋点需求从核心指标出发牵引，避免盲目全埋；
> 
> - 同一品类不同生态链公司的相同功能，需使用统一的埋点事件名称，确保看板数据可统一统计。
> 
> - 埋点文档需要请联系生态链软件产品经理创建，**勿自行创建。**
> 
> - 必填，如不涉及，需要写明不涉及原因。
> 
> 

埋点模版：[埋点需求模版](https://mi.feishu.cn/wiki/L5CgwbAeziry7NkHbYScaWwFnA2)

参考流程文档：[ECO\-核心数据指标制定\+落地全流程指导手册\-2026版](https://mi.feishu.cn/wiki/RtHswDbIRiScLhkHZ2jc2obZnHh)



埋点需求文档：[埋点需求\-复古相机](https://mi.feishu.cn/wiki/IiQYww4BJiIv0WkdDFgcOZ3unfh?sheet=Yh46c8)

### 

## Spec功能定义\*

> 提示：
> 
> 1、在提交初版软件功能说明书时，请同时提供初版的Spec功能定义。必填。
> 
> 2、使用米家标准Spec定义的功能，必须检查标准Spec对应的通用能力是否支持，小爱语控、自动化 均需要验证。
> 
> 3、如果有问题，提交米家工单，联系米家确认。
> 
> 

示例：[【这里替换成产品名称】新增标准spec 定义](https://mi.feishu.cn/docx/BafqdBYEOoI52TxJnZJcfaLqndh)

非米家标准模组产品，不适用Spec通讯

## 米家平台功能

### 米家通用能力\* 

> 提示：必填。
> 
> 

不接入米家App

|**功能**|**信息填写**|**备注**|
|---|---|---|
|**推送消息**|不支持|推送消息的介绍和配置方案请参考：[推送消息配置](https://iot.mi.com/new/doc/accesses/direct-access/productcenter/advance-configure?keywords=%E6%B6%88%E6%81%AF#%E7%AC%AC5%E6%AD%A5%20-%20%E9%85%8D%E7%BD%AE%E6%B6%88%E6%81%AF%E6%8E%A8%E9%80%81)|
|**电视米家推送消息**|不支持||
|**快捷卡片**|不支持|Spec接入产品已支持快捷卡片样式请参考：[快捷卡片](https://iot.mi.com/new/doc/tools-and-resources/design/spec/shortcut)<br>注：额外需求请补充对应的展现样式。|
|**App耗材展示**|不支持|请参考：[耗材配置](https://iot.mi.com/new/doc/accesses/direct-access/productcenter/consumable_material?keywords=%E8%80%97%E6%9D%90)|
|**插件离线提醒**|不支持|建议：BLE不支持、Wi\-Fi设备插件中离线提醒支持|
|**设备离线插件可使用**|否|是/否|



### 耗材配置

> 提示：
> 
> 1、如果不支持米家APP耗材展示，请删除下方表格。
> 
> 2、如果支持米家APP耗材展示耗材，需要填写所有耗材的详细信息，标记\*的是必填项，参考小米IoT平台文档[耗材配置](https://iot.mi.com/v2/new/doc/configuration/advance-configure/consumable-material) 。下表中耗材数量可以根据需要自行增加。
> 
> 

无耗材，不适用。

||**耗材1**|**耗材2**|\.\.\.|**备注**|
|---|---|---|---|---|
|耗材名称\*|示例：全效复合滤芯|示例：碳素阵列|||
|不足状态定义\*|示例：≤5%|示例：≤5%|||
|耗尽状态定义|示例：≤0%|示例：≤0%|||
|建议更换周期|示例：/|示例：/|||
|耗材型号\*|示例：全效复合滤芯|示例：碳素阵列|||
|功能介绍|示例：/|示例：/|||
|是否支持重置\*|示例：否|示例：否|||
|耗材图片\*|![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NmEwN2RmZDA3Zjk4MmFiZmQxODdiNmIzM2VjNDEwYjBfZTc2MWM3NzQ3YzM4MDUzOWUxZTRhOGUzN2RjM2Y4NmNfSUQ6NzY4MzA5NjIwNzExMTY1NDM1NF8xNzg5NTI2NDAwOjE3ODk2MTI4MDBfVjM)|![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ODdjMWIwNzMxNzUwOTJhMjkyYmIyZDYyZWEwZWE1YThfODdlYmUxMzMzMzE5OTcxZWVlZTRkZjM3NmFhNjJkNTFfSUQ6NzY4MzA5NjIwNzMyNTU4MDIxOV8xNzg5NTI2NDAwOjE3ODk2MTI4MDBfVjM)|||
|耗材链接\*<br>|https://m\.xiaomiyoupin\.com/detail?gid=168559\&pid=469219|https://m\.xiaomiyoupin\.com/detail?gid=168559\&pid=469219||产品上市后补充小米有品的耗材链接|
|更换教学|示例：/|示例：/|||

### 小爱语控\* 

> 提示：部分Spec标准功能已默认支持小爱语控，请查看已支持功能列表[小爱语控](https://iot.mi.com/v2/new/doc/resources-and-services/design/feature-define/language-control)后填写。必填。
> 
> 

不支持小爱语控。

**已支持的**

|**控制类需求**|**查询类需求**|
|---|---|
|1. 破壁料理机停止烹饪/停止榨汁|1. 查询当前破壁料理机剩余时间|
|2. 破壁料理机打开豆浆/米糊模式||

**如有额外语控需求，请填写下表：**

|**控制类需求**|**查询类需求**|
|---|---|
|1. 破壁料理机打开快浆/果蔬模式开始榨汁||
|3. 预约xx模式xx时间开始烹饪<br>4. xx时间开始xx模式||
|5. 破壁料理机暂停烹饪||

### 自动化\* 

> 提示：智能场景if、then的配置和描述，请参考MIoT平台文档[智能场景](https://iot.mi.com/new/doc/accesses/direct-access/extension-development/topics/automation-develop?keywords=%E6%99%BA%E8%83%BD%E5%9C%BA%E6%99%AF)。必填。
> 
> 

不支持。

|**if配置**|**then配置**|**备注**|
|---|---|---|
||||
||||
||||
||||



## 隐私与安全

### 预研阶段隐私风险自查表\* 

> 提示：在预研阶段，厂商需要按照此表对产品进行隐私风险自查，并如实填写结果。必填。
> 
> 

|**序号**|**检查项**||**示例**|**检查结果（是/否）**|
|---|---|---|---|---|
|**1**|新品类||/||
|**2**|涉及敏感个人信息<br>[敏感个人信息的定义和示例](https://mi.feishu.cn/docx/A0Y1diRkrowk8exHr1accQzfnRg) |人脸、指纹等生物识别信息|门铃、门锁、摄像机<br>|否|
|||精准地理位置信息|扫地机器人、行车记录仪|否|
|||生理健康信息|智能手表|否|
|||儿童信息|卡片学习机|否|
|||其他敏感个人信息（参考所附文档）|/|否|
|**3**|功能相对复杂<br>||带屏幕、接入除小爱外的其他语控功能、接小爱语控如符合固定要求则不属于复杂功能|否|
|**4**|涉及向第三方提供数据||/|否|
|**5**|涉及数据跨境||/|否|
|**6**|接入第三方独立App、小程序、PC端App、web端||/|是|

### 隐私功能

产品隐私合入独立App隐私中，不再独立提供隐私说明。

#### **隐私概要\* **

> 提示：正常情况下接入米家平台的产品都涉及隐私功能，必填。
> 
> 

|**涉及隐私**|**需求描述**||**备注**|
|---|---|---|---|
|否|不收集任何个人信息，产品不涉及隐私|||
|是|隐私文稿|示例<br>1. 《隐私政策》<br>2. 《用户协议》<br>3. 《儿童信息保护规则》<br>4. 《第三方共享信息清单》|1. 这里需要说明支持的所有隐私文稿类型，常用文稿类型包括<br>《隐私政策》<br>《用户协议》<br>《用户体验改进计划》<br>《儿童信息保护规则》<br>《第三方共享信息清单》<br>2. 如有“其他”，请详细说明|
||隐私功能|示例<br>1. 隐私弹窗<br>2. 隐私更新弹窗<br>3. 撤销授权<br>4. 隐私下载<br>5. 数据存储服务器<br>6. 数据清除<br>|1. 这里需要说明支持的隐私功能，常见隐私功能包括<br>- 隐私弹窗<br>- 隐私更新弹窗<br>- 敏感信息提醒弹窗<br>- 权限管理<br>- 撤销授权<br>- 隐私下载<br>- 数据清除<br>- 用户体验改进计划开关<br>2. 如有“其他”，请详细说明<br>|
||数据收集|示例<br>1. 存放在云端的数据<br>- PM2\.5数值<br>- 甲醛数值<br>2. 存放在本地的数据<br>- 定时开关时间|这里需要说明数据收集存储情况，包括存放在云端和本地的数据，明确到具体字段，例如PM2\.5。需要根据产品实际情况全部列出来。<br>|

#### **隐私功能详细设计\* **

1. 禁止欺骗误导用户：严禁以欺骗、诱骗等不正当的方式误导用户授权同意隐私、打开收集个人信息的权限、同意提供个人信息

2. 禁止频繁自启动：严禁频繁自启动或关联启动第三方应用

3. 禁止频繁获取个人信息：收集个人信息的频度不超出业务功能实际需要

> 提示：上方3\.7\.2\.1“隐私概要”中列举的隐私功能，都需要进行详细说明，示例给出了通用做法。必填。
> 
> 

|**隐私功能**|**功能逻辑\&描述**|**备注**|
|---|---|---|
|隐私弹窗<br>|示例：<br>1. 绑定设备，进入插件首页，弹出隐私弹窗<br>    1. 弹窗文案：xxx<br>    2. 同意前：不得收集插件相关的个人信息或打开可收集个人信息的权限，不可收集任何插件数据（包括用户数据、非用户数据和打点数据）<br>    3. 同意后：<br>        1. 进入插件首页<br>        2. 云端需生成一条同意日志，记录App version，手机系统版本，UID，DID，隐私政策version，时间戳。<br>    4. 拒绝同意，则回到“米家”页面<br>    5. 相关隐私文稿为超链接，点击链接跳转到对应页面<br>2. 撤回隐私同意和删除设备后，再次绑定设备，弹出隐私弹窗|如产品涉及隐私，必须支持此功能。<br>示例<br>![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ZTRkYzA0NzM4ZWY1ZTU0YjgyZDc3ZTJlMGRkMjI1MjFfNGE0ZGJkNjQyZWIzYzkyMjYxMGVlMjAzYWM0MDA4NDVfSUQ6NzY4MzA5NjIwOTg3NTQwNTc1NV8xNzg5NTI2NDAwOjE3ODk2MTI4MDBfVjM)<br>|
|隐私更新弹窗|示例：<br>产品上线后，隐私文稿内容发生变更（隐私内容版本A\-更新为版本B）<br>1. 新用户/已撤回产品隐私同意的老用户，不弹出隐私更新弹窗<br>2. 已同意历史版本隐私或隐私A，且未同意过隐私B的老用户，弹出隐私更新弹窗<br>    1. 更新弹窗文案：xxx  <br>    2. 同意前：不得收集插件相关的个人信息或打开可收集个人信息的权限，不可收集任何插件数据（包括用户数据、非用户数据和打点数据）<br>    3. 同意后：<br>        1. 进入插件首页<br>        2. 云端需生成一条同意日志，记录App version，手机系统版本，UID，DID，隐私政策version，时间戳。<br>    4. 拒绝同意，则回到“米家”页面<br>    5. 相关隐私文稿为超链接，点击链接跳转到对应新版隐私页面<br>|1. 产品上线前，隐私文稿内容发生变更，不弹出隐私更新弹窗<br>2. 产品上线后，隐私文稿内容发生变更，必须支持此功能。更新弹窗文案可参考：[隐私政策更新弹窗文案指引](https://mi.feishu.cn/docx/BlJodBPJNo0SEyxWrWscCMKsnDd) <br>|
|敏感信息权限提醒弹窗<br>|示例：<br>使用收集敏感数据功能时，弹出敏感信息权限提醒弹窗，告知用户申请权限的目的等<br>1. 收集的敏感信息<br>- 定位<br>2. 敏感信息弹窗<br>    1. 敏感信息弹窗文案：xxx<br>    2. 同意前，不得使用对应功能和收集敏感数据<br>    3. 同意后，才能使用对应功能和进行敏感数据收集，且云端需生成一条同意日志，记录App version，手机系统版本，UID，DID，时间戳。<br>|1. 如产品涉及收集用户敏感数据的功能，必须支持此功能。[敏感个人信息的定义和示例](https://mi.feishu.cn/docx/A0Y1diRkrowk8exHr1accQzfnRg) <br>2. 注意：收集年满14周岁未成年人的个人信息前，应征得未成年或其监护人的明示同意；不满十四周岁的，应征得其监护人的明示同意。<br>3. 敏感信息弹窗文案示例<br>    *为向您提供XXX功能，XXX有限公司（联系方式：XXX）将收集您的XXX信息，用于XXX。【请您放心，您的XXX信息将仅用于上述目的。在完成XXX后，我们将删除您的XXX信息，您可以通过XXX路径删除上述信息。】若您拒绝授权，您将无法使用上述功能。*<br>    【】里的内容根据实际情况判断，如果用于其他目的（比如模型训练），不支持单独删除，不包含这几句话也可以。<br>示例<br>![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MjY1NzE2MDBjYWRmMTA0NmFjNTQ2NjBmNWM0MTM1MjRfNTY4NDJjOTJlM2ZkNGY2OGE3NzU5ZGY2ZWFkZWI4NzNfSUQ6NzY4MzA5NjIwNzY0MDU2MjYxOF8xNzg5NTI2NDAwOjE3ODk2MTI4MDBfVjM)|
|敏感信息权限申请弹窗<br>|示例<br>根据不同的手机系统，展示索取权限弹窗<br>1. 弹窗文案：xxxx<br>2. 用户授权选项<br>    1. 不允许：不得使用对应功能和收集敏感数据<br>    2. 允许一次<br>    3. 使用APP时允许|如产品涉及获取设备权限，必须支持此功能<br>示例<br>![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NTcwNTRlMGY5ZTA3MjAxM2IyNDU3OTM5NWViNGY4YmVfMDM5YmQ0YjljNDgwMGNiNmI2NjZjYmVmODJlMDU0NzFfSUQ6NzY4MzA5NjIxMDk2MTU1MDI5NV8xNzg5NTI2NDAwOjE3ODk2MTI4MDBfVjM)|
|撤销授权<br>|示例：<br>1. 用户同意隐私后，支持撤销授权，点击“撤销授权”，弹出撤销授权弹窗<br>    1. 撤销授权文案：xxx<br>    2. 撤回后果应同文案相符。<br>2. 从米家App首页开始计算，进入撤销授权页面的步骤不得超过4步|如产品涉及隐私，必须支持此功能。<br>示例<br>![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MTU0OTk4ZWFiNzM4Zjc3ZTU0NTAwNzE3OTIyOTU0NDVfZTU2ZjkwYmY5ZTM5YThjODMxZWY5NjQxOWE0OWY2NzRfSUQ6NzY4MzA5NjIxMTIxMzg0NzUyNl8xNzg5NTI2NDAwOjE3ODk2MTI4MDBfVjM)|
|隐私下载|示例：<br>1. 所有隐私文稿支持下载为PDF格式<br>2. 下载后的文件内容正常显示|如产品涉及隐私，必须支持此功能。<br>![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=OWQ5MjlmY2Y3YWExMzZhNmVkMmU0MTBjMDcwZDdjN2ZfMmRjMzlhZDk4YmIxZjk2Zjk1NWY5MDRmNjk2ZjU2MDlfSUQ6NzY4MzA5NjIxMjI2NjMzOTI3Nl8xNzg5NTI2NDAwOjE3ODk2MTI4MDBfVjM)|
|数据清除<br>|示例：<br>所有用户数据都支持清除<br>1. 本地数据清除：通过重置设备或恢复物理出厂<br>2. 云端数据清除：通过撤销授权、删除设备、注销账号|如产品涉及隐私，必须支持此功能<br>|
|用户体验改进计划开关<br>|示例：<br>支持用户体验改进计划<br>1. 用户同意隐私后，弹出用户体验改进计划弹窗<br>    1. 弹窗文案：xxx<br>    2. 同意前：不得收集相关信息，拒绝同意后不得影响其正常使用产品或服务<br>    3. 同意后，才能收集相关信息<br>2. 支持用户体验改进计划开关，开关默认关闭。|如产品支持用户体验改进计划，必须支持此功能。<br>示例<br>![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NzlmOGNiZGUxOThjMzJmZjZhZjU0MmE3MDVhNDY3MmFfNDk1NDZkYTRiYTI0YTAwZjg2M2YxODVkYjgzYjg2ZGRfSUQ6NzY4MzA5NjIxMzMwMTk1NTUyNF8xNzg5NTI2NDAwOjE3ODk2MTI4MDBfVjM)<br>|

# 米家服务端和云平台需求\* 

> 提示：这里填写上文“功能定义”中，需要服务端或云平台支持的功能。必填。
> 
> 

|**服务类型**|**是否需要**|**需求说明**|
|---|---|---|
|**云端数据统计服务**|否|例：温湿度变化曲线、插座电量统计|
|**音视频播放功能**|否|例：网络收音机播放电台|
|**大文件存储服务**|否|例：打印机传输图片|
|**其他云端接口及云端服务功能**|否|例：云端定时开关机|



# 国际化

## 语言和地区\* 

这里填写国际化相关的信息。必填。

> 仅在中国大陆地区销售也需要填写该表，通常填写为：
> 
> 销售地区：中国大陆
> 
> 插件语言：简体中文、英文
> 
> 隐私多语言：简体中文、英文
> 
> 设备名称语言：简体中文、英文
> 
> model上线服务器：大陆服务器
> 
> 

|**维度**|**内容**|**备注**|
|---|---|---|
|**销售地区**|中国大陆<br>|1、请按《定制需求表》填写所有销售地区。<br>2、销售地区需要在 [《隐私可选国家》](https://wiki.n.miui.com/pages/viewpage.action?pageId=220432404)清单中。|
|**插件语言**<br>|简体中文、英文|1、请按《定制需求表》填写需要支持的插件语言。<br>2、不得超出米家App已支持语言列表，请参考：[多语言](https://iot.mi.com/v2/new/doc/plugin/basic/i18n#%E6%94%AF%E6%8C%81%E7%9A%84%E5%A4%9A%E8%AF%AD%E8%A8%80)。请注意目前尚未支持阿拉伯语和希伯来语。|
|**固件语言**|英文|若固件有显示文字的功能，列出支持的语言。|
|**隐私多语言**|简体中文、英文|因法律要求，法律信息文件需要支持当地语言，隐私语言需与[插件内多语言隐私语言配置规则示例](https://mi.feishu.cn/sheets/IvjTspasuhnStptlCCScwQ0un3c)相同。<br>|
|**设备名称语言**|简体中文、英文||
|**model上线服务器**<br>|大陆服务器|目前服务器部署：<br>- 大陆服务器<br>- 新加坡服务器<br>- 欧洲服务器<br>- 美国服务器<br>- 俄罗斯服务器<br>- 印度服务器<br><br>服务器和国家/地区对应关系参考 [国际化配置](https://iot.mi.com/v2/new/doc/configuration/globalization?keywords=%E5%9B%BD%E9%99%85%E5%8C%96&rank=1)|

## 海外生态接入功能支持\* 

需要支持海外语控的model，请填写该表格。必填。

不支持

> 说明：
> 
> 1. MIoT进行海外语控适配时将以此表信息为准，**请务必认真填写**，避免遗漏。
> 
> 2. Works with与Compatible with的区别：Works with是认证标准，要求更严格，MIoT语控适配后厂商可向Amazon/Google申请认证贴标（认证周期4\-6周，Amazon需寄送样品，Google线上提交）；Compatible with是适配标准，要求较宽松，MIoT语控适配后，用户可以通过Amazon Alexa语控设备，无法认证贴标（Google生态后续不再支持Compatible接入方式）。
> 
> 3. 设备封样提测后，即启动海外语控适配工作。
> 
> 

|**Alexa**<br>|支持/不支持|||
|---|---|---|---|
||Works with/Compatible with|||
||期望语音服务上线地区及需要的支持语言|||
||支持的语言 <br>（国家和语言不要求必须一 一对应）|地区/国家 <br>（如同时包含国家地区，可将此列分为两列填写，左侧地区，右侧对应该地区国家）<br>|无语控功能支持会受到影响的预计销售数量（万台）<br>|
||**示例：**<br>英语<br>法语<br>德语<br>\.\.\.\.\.\.|**示例：**<br>英国|**示例：**<br>0\.5|
|||法国|1\.8|
|||\.\.\.\.\.\.|\.\.\.\.\.\.|
||功能支持需求：<br>（仅描述清楚功能需求即可，注意不要增加其他额外的内容）<br>1. 开关<br>2. 调节XX<br>3. \.\.\.\.\.\.|||
|**Google Assistant**<br>|支持/不支持|||
||Works with|||
||期望语音服务上线地区及需要的支持语言|||
||支持的语言 <br>（国家和语言不要求必须一 一对应）|地区/国家 <br>（如同时包含国家地区，可将此列分为两列填写，左侧地区，右侧对应该地区国家）|无语控功能支持会受到影响的预计销售数量（万台）|
||**示例：**<br>英语<br>法语<br>德语<br>\.\.\.\.\.\.|**示例：**<br>英国|**示例：**<br>0\.5|
|||法国|1\.8|
|||\.\.\.\.\.\.|\.\.\.\.\.\.|
||功能支持需求：<br>（仅描述清楚功能需求即可，注意不要增加其他额外的内容）<br>1. 开关<br>2. 调节XX<br>3. \.\.\.\.\.\.|||



