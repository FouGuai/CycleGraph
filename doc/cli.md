# cgql 命令行工具完整文档

`cgql` 是图数据库命令行工具,提供用户认证、数据查询和插入功能。

---

## 目录
1. [用户认证](#1-用户认证)
2. [连接管理](#2-连接管理)
3. [查询操作](#3-查询操作)
4. [插入操作](#4-插入操作)
5. [错误处理](#5-错误处理)

---

## 1. 用户认证

### 1.1 注册 (`register`)

创建新用户账号。

**语法:**
```bash
cgql register -u <username> -p <password>
```

**参数:**
- `-u, --username`: 用户名 (必需)
- `-p, --password`: 密码 (必需)

**示例:**
```bash
cgql register -u alice -p pass123
```

**成功响应:**
```json
{
  "status": "success"
}
```

**错误响应:**
```json
{
  "status": "error",
  "message": "Username already exists"
}
```

---

### 1.2 登录 (`login`)

使用用户名和密码登录,获取访问令牌。

**语法:**
```bash
cgql login -u <username> -p <password>
```

**参数:**
- `-u, --username`: 用户名 (必需)
- `-p, --password`: 密码 (必需)

**示例:**
```bash
cgql login -u alice -p pass123
```

**成功响应:**
```json
{
  "status": "success"
}
```

**错误响应:**
```json
{
  "status": "error",
  "message": "Invalid username or password"
}
```

---

### 1.3 登出 (`logout`)

清除本地令牌和会话。

**语法:**
```bash
cgql logout
```

**响应:**
```json
{
  "status": "success",
  "message": "Logged out and session cleared."
}
```

---

### 1.4 当前用户 (`whoami`)

查看当前登录状态和用户信息。

**语法:**
```bash
cgql whoami
```

**成功响应 (已登录):**
```json
{
  "status": "success",
  "found": true,
  "current_user": "alice"
}
```

**错误响应 (未登录):**
```json
{
  "status": "error",
  "message": "Not logged in"
}
```

---

## 2. 连接管理

### 2.1 连接服务器 (`connect`)

设置服务端地址。**注意:** 执行此命令前必须先登录。

**语法:**
```bash
cgql connect <host_url>
```

**参数:**
- `host_url`: 服务器地址 (必需),例如 `http://127.0.0.1:8000`

**示例:**
```bash
cgql connect http://127.0.0.1:8000
```

**成功响应:**
```json
{
  "status": "success",
  "message": "Successfully connected to http://127.0.0.1:8000. Session configuration saved."
}
```

---

## 3. 查询操作

所有查询操作都需要先完成登录和连接。

### 3.1 查询点 (`query vertex`)

根据条件过滤并返回图中的点。

**语法:**
```bash
cgql query vertex [选项]
```

**选项:**
- `--vid <int>`: 按点ID查询
- `--vt, --v-type <str>...`: 按点类型过滤 (可多个)
- `--min-time <int>`: 最小创建时间 (Unix时间戳)
- `--max-time <int>`: 最大创建时间 (Unix时间戳)
- `--min-bal <int>`: 最小余额
- `--max-bal <int>`: 最大余额

**示例 1: 查询所有点**
```bash
cgql query vertex
```

**示例 2: 按ID查询**
```bash
cgql query vertex --vid 12345
```

**示例 3: 按类型和余额过滤**
```bash
cgql query vertex --vt account company --min-bal 100000
```

**成功响应:**
```json
{
  "status": "success",
  "found": true,
  "count": 2,
  "data": [
    {
      "vid": 12345,
      "v_type": "account",
      "create_time": 1672531200,
      "balance": 500000
    },
    {
      "vid": 54321,
      "v_type": "company",
      "create_time": 1672617600,
      "balance": 120000
    }
  ]
}
```

**未找到响应:**
```json
{
  "status": "success",
  "found": false,
  "count": 0,
  "data": []
}
```

---

### 3.2 查询边 (`query edge`)

根据条件过滤并返回图中的边。

**语法:**
```bash
cgql query edge [选项]
```

**选项:**
- `--eid <int>`: 按边ID查询
- `--src <int>`: 按源点ID过滤
- `--dst <int>`: 按目标点ID过滤
- `--et, --e-type <str>...`: 按边类型过滤 (可多个)
- `--min-amt <int>`: 最小交易金额
- `--max-amt <int>`: 最大交易金额
- `--min-time <int>`: 最小发生时间 (Unix时间戳)
- `--max-time <int>`: 最大发生时间 (Unix时间戳)

**示例 1: 查询所有边**
```bash
cgql query edge
```

**示例 2: 查询指定源点的所有边**
```bash
cgql query edge --src 12345
```

**示例 3: 金额范围查询**
```bash
cgql query edge --src 12345 --min-amt 10000 --max-amt 50000
```

**成功响应:**
```json
{
  "status": "success",
  "found": true,
  "count": 1,
  "data": [
    {
      "eid": 8001,
      "src_vid": 12345,
      "dst_vid": 54321,
      "amount": 25000,
      "occur_time": 1678881000,
      "e_type": "transfer"
    }
  ]
}
```

---

### 3.3 查询环路 (`query cycle`)

检测并返回满足条件的资金环路,包含环路上所有点和边的完整信息。

**语法:**
```bash
cgql query cycle --start <vid> --depth <int> [选项]
```

**核心参数 (必需):**
- `--start <int>`: 环路起始点ID
- `--depth <int>`: 最大搜索深度 (环路最大长度)

**方向控制:**
- `--dir <forward|any>`: 边的时序方向
  - `forward`: 要求边的 `occur_time` 严格递增 (默认)
  - `any`: 无时序要求

**点过滤选项:**
- `--vt, --v-type <str>...`: 环路上所有点必须属于指定类型
- `--min-bal <int>`: 环路上所有点的余额 >= 此值

**边过滤选项:**
- `--et, --e-type <str>...`: 环路上所有边必须属于指定类型
- `--min-amt <int>`: 环路上所有边的金额 >= 此值
- `--max-amt <int>`: 环路上所有边的金额 <= 此值

**结果控制:**
- `--limit <int>`: 最多返回的环路数量 (默认 10)
- `--allow-dup-v`: 允许环路中重复访问同一个点
- `--allow-dup-e`: 允许环路中重复使用同一条边

**示例 1: 基本环路查询**
```bash
cgql query cycle --start 12345 --depth 8
```

**示例 2: 查询时间递增的环路**
```bash
cgql query cycle --start 12345 --depth 8 --dir forward
```

**示例 3: 带点类型过滤**
```bash
cgql query cycle --start 12345 --depth 8 --vt account company
```

**示例 4: 带边金额过滤**
```bash
cgql query cycle --start 12345 --depth 8 --min-amt 5000 --max-amt 100000
```

**示例 5: 组合过滤查询**
```bash
cgql query cycle --start 12345 --depth 10 --dir forward \
  --vt account --min-bal 50000 \
  --et transfer --min-amt 10000 \
  --limit 20
```

**成功响应 (找到环路):**
```json
{
  "status": "success",
  "found": true,
  "count": 2,
  "data": [
    {
      "vertices": [
        {
          "vid": 12345,
          "v_type": "account",
          "create_time": 1672531200,
          "balance": 500000
        },
        {
          "vid": 54321,
          "v_type": "account",
          "create_time": 1672617600,
          "balance": 120000
        },
        {
          "vid": 67890,
          "v_type": "company",
          "create_time": 1672704000,
          "balance": 300000
        }
      ],
      "edges": [
        {
          "eid": 8001,
          "src_vid": 12345,
          "dst_vid": 54321,
          "amount": 15000,
          "occur_time": 1678881000,
          "e_type": "transfer"
        },
        {
          "eid": 8002,
          "src_vid": 54321,
          "dst_vid": 67890,
          "amount": 12000,
          "occur_time": 1678882000,
          "e_type": "transfer"
        },
        {
          "eid": 8003,
          "src_vid": 67890,
          "dst_vid": 12345,
          "amount": 10000,
          "occur_time": 1678883000,
          "e_type": "transfer"
        }
      ]
    }
  ],
  "meta": {
    "execution_time_ms": 150
  }
}
```

**未找到环路响应:**
```json
{
  "status": "success",
  "found": false,
  "count": 0,
  "data": [],
  "meta": {
    "execution_time_ms": 50
  }
}
```

**错误响应 (起始点不存在):**
```json
{
  "status": "error",
  "message": "Start vertex 999999 does not exist"
}
```

**错误响应 (参数无效):**
```json
{
  "status": "error",
  "message": "Invalid depth: must be positive integer"
}
```

---

## 4. DML

所有插入操作都需要先完成登录和连接。

### 4.1 插入点 (`insert vertex`)

创建新的点。

**语法:**
```bash
cgql insert vertex --vt <type> [选项]
```

**参数:**
- `--vt, --v-type <str>`: 点类型 (必需)
- `--vid <int>`: 点ID (可选,默认自动生成)
- `--time <int>`: 创建时间 Unix时间戳 (可选,默认当前时间)
- `--bal <int>`: 初始余额 (可选,默认 0)

**示例 1: 自动生成ID**
```bash
cgql insert vertex --vt account --bal 100000
```

**示例 2: 指定ID**
```bash
cgql insert vertex --vt company --vid 999999 --bal 500000
```

**成功响应:**
```json
{
  "status": "success",
  "message": "Vertex 999999 created successfully.",
  "data": {
    "vid": 999999,
    "v_type": "company",
    "create_time": 1765987200,
    "balance": 500000
  }
}
```

**错误响应 (ID重复):**
```json
{
  "status": "error",
  "message": "Vertex 999999 already exists"
}
```

---

### 4.2 插入边 (`insert edge`)

创建新的边。

**语法:**
```bash
cgql insert edge --eid <id> --src <vid> --dst <vid> --amt <amount> [选项]
```

**参数 (必需):**
- `--eid <int>`: 边ID
- `--src <int>`: 源点ID
- `--dst <int>`: 目标点ID
- `--amt <int>`: 交易金额

**参数 (可选):**
- `--time <int>`: 发生时间 Unix时间戳 (默认当前时间)
- `--et, --e-type <str>`: 边类型 (默认 `"+"`)
- `--create-v`: 自动创建不存在的源点和目标点

**示例 1: 基本插入**
```bash
cgql insert edge --eid 8888 --src 12345 --dst 54321 --amt 25000
```

**示例 2: 指定类型和时间**
```bash
cgql insert edge --eid 8889 --src 12345 --dst 54321 \
  --amt 30000 --et transfer --time 1678881000
```

**示例 3: 自动创建点**
```bash
cgql insert edge --eid 8890 --src 111111 --dst 222222 \
  --amt 15000 --create-v
```

**成功响应:**
```json
{
  "status": "success",
  "message": "Edge 8888 created successfully.",
  "data": {
    "eid": 8888,
    "src_vid": 12345,
    "dst_vid": 54321,
    "amount": 25000,
    "occur_time": 1765987200,
    "e_type": "+"
  }
}
```

**错误响应 (ID重复):**
```json
{
  "status": "error",
  "message": "Edge 8888 already exists"
}
```

**错误响应 (点不存在):**
```json
{
  "status": "error",
  "message": "Source vertex 12345 does not exist"
}
```

---

### 4.3 删除点 (`delete vertex`)

根据点ID删除点。**注意:** 删除点会同时删除所有与该点相关的边。

**语法:**
```bash
cgql delete vertex --vid <id>
```

**参数:**
- `--vid <int>`: 要删除的点ID (必需)

**示例:**
```bash
cgql delete vertex --vid 12345
```

**成功响应:**
```json
{
  "status": "success",
  "message": "Vertex 12345 deleted successfully. 3 related edges also deleted.",
  "data": {
    "vid": 12345,
    "edges_deleted": 3
  }
}
```

**错误响应 (点不存在):**
```json
{
  "status": "error",
  "message": "Vertex 12345 does not exist"
}
```

---

### 4.4 删除边 (`delete edge`)

根据边ID删除边。

**语法:**
```bash
cgql delete edge --eid <id>
```

**参数:**
- `--eid <int>`: 要删除的边ID (必需)

**示例:**
```bash
cgql delete edge --eid 8888
```

**成功响应:**
```json
{
  "status": "success",
  "message": "Edge 8888 deleted successfully.",
  "data": {
    "eid": 8888
  }
}
```

**错误响应 (边不存在):**
```json
{
  "status": "error",
  "message": "Edge 8888 does not exist"
}
```

---

## 5. 错误处理

### 5.1 通用错误

**未登录:**
```json
{
  "status": "error",
  "message": "Please login first"
}
```

**未连接服务器:**
```json
{
  "status": "error",
  "message": "Not connected to server. Use 'cgql connect <host>' first"
}
```

**令牌过期:**
```json
{
  "status": "error",
  "message": "Token expired. Please login again"
}
```

**网络错误:**
```json
{
  "status": "error",
  "message": "Connection failed: Unable to reach server"
}
```

### 5.2 参数错误

**缺少必需参数:**
```json
{
  "status": "error",
  "message": "Missing required argument: --start"
}
```

**参数类型错误:**
```json
{
  "status": "error",
  "message": "Invalid argument type: --depth must be integer"
}
```

**参数值无效:**
```json
{
  "status": "error",
  "message": "Invalid depth: must be positive i
  nteger"
}
```

### 5.3 数据错误

**资源不存在:**
```json
{
  "status": "error",
  "message": "Vertex 999999 does not exist"
}
```

**资源已存在:**
```json
{
  "status": "error",
  "message": "Edge 8888 already exists"
}
```

**数据库错误:**
```json
{
  "status": "error",
  "message": "Database error: Connection timeout"
}
```

---

## 6. 使用流程

**典型工作流程:**

1. **注册账号**
   ```bash
   cgql register -u alice -p pass123
   ```

2. **登录**
   ```bash
   cgql login -u alice -p pass123
   ```

3. **连接服务器**
   ```bash
   cgql connect http://127.0.0.1:8000
   ```

4. **插入数据**
   ```bash
   cgql insert vertex --vt account --vid 1001 --bal 100000
   cgql insert vertex --vt account --vid 1002 --bal 200000
   cgql insert edge --eid 2001 --src 1001 --dst 1002 --amt 50000
   ```

5. **查询数据**
   ```bash
   cgql query vertex --min-bal 50000
   cgql query edge --src 1001
   cgql query cycle --start 1001 --depth 5
   ```

6. **登出**
   ```bash
   cgql logout
   ```

---

## 7. 命令速查表

| 命令 | 简写 | 说明 |
|------|------|------|
| `register -u <user> -p <pass>` | - | 注册用户 |
| `login -u <user> -p <pass>` | - | 登录 |
| `logout` | - | 登出 |
| `whoami` | - | 查看当前用户 |
| `connect <host>` | - | 连接服务器 |
| `query vertex` | `q v` | 查询点 |
| `query edge` | `q e` | 查询边 |
| `query cycle` | `q c` | 查询环路 |
| `insert vertex` | `i v` | 插入点 |
| `insert edge` | `i e` | 插入边 |
| `delete vertex` | `d v` | 删除点 |
| `delete edge` | `d e` | 删除边 |
**常用选项简写:**

| 选项 | 简写 | 说明 |
|------|------|------|
| `--username` | `-u` | 用户名 |
| `--password` | `-p` | 密码 |
| `--v-type` | `--vt` | 点类型 |
| `--e-type` | `--et` | 边类型 |
| `--balance` | `--bal` | 余额 |
| `--amount` | `--amt` | 金额 |
| `--src-vid` | `--src` | 源点ID |
| `--dst-vid` | `--dst` | 目标点ID |
| `--start-vid` | `--start` | 起始点ID |
| `--max-depth` | `--depth` | 最大深度 |
| `--direction` | `--dir` | 方向 |
| `--min-balance` | `--min-bal` | 最小余额 |
| `--max-balance` | `--max-bal` | 最大余额 |
| `--min-amount` | `--min-amt` | 最小金额 |
| `--max-amount` | `--max-amt` | 最大金额 |
| `--min-time` | - | 最小时间 |
| `--max-time` | - | 最大时间 |
| `--create-vertices` | `--create-v` | 自动创建点 |
| `--allow-duplicate-vertices` | `--allow-dup-v` | 允许重复点 |
| `--allow-duplicate-edges` | `--allow-dup-e` | 允许重复边 |

---

## 8. 注意事项

1. **执行顺序:** 必须先 `register/login` → `connect` → 才能执行查询/插入操作
2. **时间格式:** 所有时间参数使用 Unix 时间戳 (秒级)
3. **类型参数:** 点类型和边类型支持多个值,用空格分隔
4. **ID生成:** 点ID可以自动生成,边ID必须手动指定
5. **环路查询:** 默认要求时间递增,使用 `--dir any` 可忽略时序
6. **性能考虑:** 环路查询深度建议不超过 10,使用 `--limit` 控制返回数量
7. **会话管理:** 令牌保存在本地,使用 `logout` 清除

---

## 9. FAQ

**Q: 为什么查询返回空结果?**
A: 检查过滤条件是否过严,或数据库中是否有匹配数据。

**Q: 环路查询很慢怎么办?**
A: 减小 `--depth` 参数,或添加更多过滤条件减少搜索空间。

**Q: 如何查看详细错误信息?**
A: 所有错误都会在 `message` 字段中返回详细描述。

**Q: 可以在脚本中使用吗?**
A: 可以,所有命令都返回 JSON 格式,便于解析。

**Q: 令牌会过期吗?**
A: 会,过期后需要重新登录。