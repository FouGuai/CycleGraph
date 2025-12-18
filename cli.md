### **cgql 命令行工具文档（含用户登录）**

`cgql` 是一个与图数据库交互的命令行接口，专注于高效的图查询和数据插入操作。自本版本起，所有会话操作（连接、查询、插入）均要求先完成**用户登录**，以获取并保存访问令牌。

---

## **0. 用户登录与会话**

在任何需要访问服务端的命令之前，必须完成登录。令牌会缓存在本地，会自动随后的请求携带。

**`login`**

使用用户名与密码获取访问令牌，并保存在本地会话配置中。

**语法:**

````bash
cgql login --username <string> --password <string>
````
**返回示例:**

```
{
  "status": "success"
}
```

```
{
  "status“: "error"
  "message": "wrong username or password
}
```
**使用示例:**

````bash
cgql login --username <string> --password <string>
````

**返回示例:**

````text
{
  "status": "success"
}
````

````bash
cgql register 
````

**`logout`**

清除本地保存的令牌与会话配置。

````bash
cgql logout
````

**返回示例:**

````text
Logged out and session cleared.
````

**`whoami`**

查看当前登录用户与会话状态。

````bash
cgql whoami
````

**返回示例:**

````text
{
  "current_user': "alice"
  "status": "success",
  "found": true,
}
````

> 提示：
> - 登录成功后才可执行 `connect`、`query`、`insert` 等需要访问服务端的命令。
> - 如果令牌过期，命令会提示重新登录。

---

## **1. 连接管理**

在使用查询或插入命令前，必须先连接到服务端（且已完成登录）。

**`connect`**

设置并保存服务端 API 的地址，后续所有命令将自动使用此地址。

**语法:**

````bash
cgql connect <host_url>
````

**使用示例:**

````bash
cgql connect http://127.0.0.1:8000
````

**返回示例:**

````text
Successfully connected to http://127.0.0.1:8000. Session configuration saved.
````

---

## **2. 查询 (`query`)**

### **2.1 查询点 (`query vertex`)**

根据一个或多个属性过滤并返回图中的点。

**语法:**

````bash
cgql query vertex [过滤器选项]
````

**过滤器选项:**

* `--vid <integer>`: 按点的唯一 ID 查询。
* `--v-type <integer>...`: 按一个或多个点的类型过滤（用空格分隔）。
* `--min-create-time <integer>`: 按最小创建时间（Unix 时间戳）过滤。
* `--max-create-time <integer>`: 按最大创建时间（Unix 时间戳）过滤。
* `--min-balance <integer>`: 按最小余额过滤。
* `--max-balance <integer>`: 按最大余额过滤。

**使用示例 (过滤多个类型):**

````bash
cgql query vertex --v-type 1 3 --min-balance 1000000
````

---

### **2.2 查询边 (`query edge`)**

根据一个或多个属性过滤并返回图中的边。

**语法:**

````bash
cgql query edge [过滤器选项]
````

**过滤器选项:**

* `--eid <integer>`: 按边的唯一 ID 查询。
* `--src-vid <integer>`: 按边的源点 ID 过滤。
* `--dst-vid <integer>`: 按边的目标点 ID 过滤。
* `--e-type <integer>...`: 按一个或多个边的类型过滤（用空格分隔）。
* `--min-amount <integer>`: 按最小交易金额过滤。
* `--max-amount <integer>`: 按最大交易金额过滤。
* `--min-occur-time <integer>`: 按最小发生时间（Unix 时间戳）过滤。
* `--max-occur-time <integer>`: 按最大发生时间（Unix 时间戳）过滤。

**使用示例:**

````bash
cgql query edge --src-vid 1001 --min-amount 10000
````

---

### **2.3 查询环路 (`query cycle`)**

检测并返回满足所有指定条件的资金环路，包括构成环路的所有点和边的详细属性。

**语法:**

````bash
cgql query cycle --start-vid <integer> --max-depth <integer> [选项]
````

**核心参数:**

* `--start-vid <integer>`: **（必需）** 环路检测的起始点 `vid`。
* `--max-depth <integer>`: **（必需）** 搜索的最大深度（环路的最大长度）。
* `--direction <string>`: （可选）环路中边的时序方向。可选值为：
  * `forward`: 要求环路中所有边的 `occur_time` 必须严格递增（经典资金环路）。**（默认）**
  * `any`: 对边的时序无要求，只查找结构上的环。

**过滤器选项 (可对环路上的点和边进行过滤):**

* `--vertex-filter-v-type <integer>...`: 环路上所有点的类型必须属于指定类型之一。
* `--vertex-filter-min-balance <integer>`: 环路上所有点的余额必须大于等于此值。
* `--edge-filter-e-type <integer>...`: 环路上所有边的类型必须属于指定类型之一。
* `--edge-filter-min-amount <integer>`: 环路上所有边的金额必须大于等于此值。
* `--edge-filter-max-amount <integer>`: 环路上所有边的金额必须小于等于此值。

**使用示例 (复杂查询):**

查找从点 `12345` 出发，长度不超过 `8`，时间递增，且环上所有交易金额都大于 `5000`，并且所有途径点的类型都是 `1` 的环路。

````bash
cgql query cycle --start-vid 12345 --max-depth 8 --direction forward --edge-filter-min-amount 5000 --vertex-filter-v-type 1
````

**返回示例 (找到环路):**

````json
{
  "status": "success",
  "found": true,
  "data": {
    "vertices": [
      { "vid": 12345, "v_type": 1, "create_time": 1672531200, "balance": 500000 },
      { "vid": 54321, "v_type": 1, "create_time": 1672617600, "balance": 120000 }
    ],
    "edges": [
      { "eid": 8001, "src_vid": 12345, "dst_vid": 54321, "amount": 6000, "occur_time": 1678881000, "e_type": 0 },
      { "eid": 8003, "src_vid": 54321, "dst_vid": 12345, "amount": 5500, "occur_time": 1678883000, "e_type": 0 }
    ]
  },
  "meta": { "execution_time_ms": 150 }
}
````

---

## **3. 插入 (`insert`)**

### **3.1 插入点 (`insert vertex`)**

在图中创建一个新的点。

**语法:**

````bash
cgql insert vertex --v-type <integer> [选项]
````

**参数:**

* `--v-type <integer>`: **（必需）** 点的类型。
* `--vid <integer>`: （可选）新点的唯一 ID。如果省略，则由服务端**自动生成**。
* `--create-time <integer>`: （可选）创建时间的 Unix 时间戳。如果省略，则由服务端设置为**当前时间**。
* `--balance <integer>`: （可选）初始余额。如果省略，默认为 `0`。

**使用示例 (自动生成ID):**

````bash
cgql insert vertex --v-type 1
````

**返回示例 (JSON):**

````json
{
  "status": "success",
  "message": "Vertex 18446744073709551615 created successfully.",
  "data": {
    "vid": 18446744073709551615, // 服务端生成的唯一ID
    "v_type": 1,
    "create_time": 1765987200,
    "balance": 0
  }
}
````

---

### **3.2 插入边 (`insert edge`)**

在图中创建一条新的边。

**语法:**

````bash
cgql insert edge --eid <integer> --src-vid <integer> --dst-vid <integer> --amount <integer> [选项]
````

**参数:**

* `--eid <integer>`: **（必需）** 新边的唯一 ID。
* `--src-vid <integer>`: **（必需）** 源点 ID。
* `--dst-vid <integer>`: **（必需）** 目标点 ID。
* `--amount <integer>`: **（必需）** 交易金额。
* `--occur-time <integer>`: （可选）交易发生时间的 Unix 时间戳。如果省略，则由服务端设置为**当前时间**。
* `--e-type <integer>`: （可选）边的类型。如果省略，默认为 `0`。
* `--create-vertices`: （可选标志）如果提供此标志，当源点或目标点不存在时，会自动创建它们。

**使用示例:**

````bash
cgql insert edge --eid 7777 --src-vid 1001 --dst-vid 9999 --amount 5000
````

---

## **4. 常见问题与说明**

1. **为何需要先登录再连接？**  
   登录获取令牌，连接保存目标主机地址，后续所有命令会自动带上令牌与主机信息。

2. **令牌存储在哪里？是否加密？**  
   默认保存在用户主目录下的配置文件中（实现因平台而异）。请确保本机安全；如需彻底清除，请执行 `cgql logout`。

3. **令牌过期怎么办？**  
   重新执行 `cgql login`，成功后再重试原命令。

4. **是否支持非交互式使用？**  
   支持。可以在 CI 或脚本中使用 `cgql login --username ... --password ...` 获取令牌后继续执行。

5. **连接与登录的顺序要求？**  
   推荐顺序：先 `login`，再 `connect`。如果先连接后登录，也能正常工作，但在执行需要鉴权的命令前必须已登录。

6. **未登录执行查询/插入会怎样？**  
   会返回未认证错误，提示先执行 `cgql login`。