### 1. 项目文件树结构

```text
aml_cycle_detection/
├── server/                              # 服务端代码（部署在数据库宿主机或旁路服务器）
│   ├── sql/
│   │   └── init_schema.sql              # 数据库初始化脚本（点边表定义与核心索引）
│   ├── core/
│   │   ├── db_driver.py                 # 数据库连接、事务管理与原子执行器
│   │   └── sql_generator.py             # 核心：SQL 语句构造器（负责拼装 GraphGen 逻辑）
│   ├── algo/
│   │   └── bidirectional_bfs.py         # 核心：双向 BFS 流程编排与剪枝逻辑实现（已合并）
│   ├── api/
│   │   └── endpoints.py                 # HTTP 接口定义（Flask/FastAPI 视图函数）
│   ├── main.py                          # 服务端启动入口
│   └── config.py                        # 数据库连接配置与全局常量
├── client/                              # 客户端代码（可运行在任意机器）
│   ├── remote_caller.py                 # 封装 HTTP 请求
│   └── cli.py                           # 命令行交互入口
└── docs/
    └── api_spec.md                      # 接口规范文档
```

---

### 2. 详细接口设计规划

#### A. 模块：`server/sql/init_schema.sql`
**描述**：OpenGauss 数据库的 DDL 初始化脚本。定义不可变的点边表结构，并建立对时序剪枝至关重要的物理索引。
**内容**：
* **SQL语句块**：
    1.  **Vertex 表**：包含 `vid` (BigInt, PK), `v_type` (TinyInt), `create_time` (BigInt), `balance` (BigInt)。
    2.  **Edge 表**：包含 `eid` (BigInt, PK), `src_vid` (BigInt), `dst_vid` (BigInt), `amount` (BigInt), `occur_time` (BigInt), `e_type` (TinyInt)。
    3.  **核心索引（必须创建）**：
        * `idx_edge_src_time`: `ON Edge(src_vid, occur_time)` —— 加速正向遍历与时序过滤。
        * `idx_edge_dst_time`: `ON Edge(dst_vid, occur_time)` —— 加速反向遍历与时序过滤。

---

#### B. 模块：`server/core/sql_generator.py`
**描述**：纯函数模块，负责生成所有发往 OpenGauss 的 SQL 字符串。所有的图算法逻辑（如时序比较、金额比较）在此处转化为 SQL `WHERE` 子句。
**接口列表**：

1.  **`gen_create_temp_table_sql(table_name: str) -> str`**
    * **功能**：生成创建 `UNLOGGED` 临时表的 SQL。
    * **逻辑**：表结构必须包含 `vid`, `parent_vid` (用于回溯), `occur_time` (记录到达时间), `path_id`。指定 `WITH (ORIENTATION = ROW)`。

2.  **`gen_create_index_sql(table_name: str, column: str) -> str`**
    * **功能**：生成为临时表的 `vid` 列创建 B-Tree 或 Hash 索引的 SQL。这是多层 Join 性能不衰减的关键。

3.  **`gen_expand_forward_sql(src_table: str, target_table: str, min_amount: int) -> str`**
    * **功能**：生成正向 BFS 扩展的 `INSERT INTO ... SELECT` 语句。
    * **逻辑**：
        * `JOIN`: `src_table` 与 `Edge` 在 `src_table.vid = Edge.src_vid` 上连接。
        * **剪枝逻辑转化**：
            * `WHERE Edge.occur_time > src_table.occur_time` (时序递增)。
            * `AND Edge.amount >= min_amount` (金额阈值)。
            * `AND Edge.dst_vid` 的类型不在黑名单中。

4.  **`gen_expand_backward_sql(src_table: str, target_table: str, min_amount: int) -> str`**
    * **功能**：生成反向 BFS 扩展的 SQL。
    * **逻辑**：
        * `JOIN`: `src_table` 与 `Edge` 在 `src_table.vid = Edge.dst_vid` 上连接（反向查找入边）。
        * **剪枝逻辑转化**：
            * `WHERE Edge.occur_time < src_table.occur_time` (**注意：**反向搜索时，需寻找时间更早的交易)。

5.  **`gen_intersection_check_sql(fwd_table: str, bwd_table: str) -> str`**
    * **功能**：生成检测碰撞的查询 SQL。
    * **逻辑**：`SELECT ... FROM fwd_table f JOIN bwd_table b ON f.vid = b.vid WHERE f.occur_time < b.occur_time`。

6.  **`gen_drop_table_sql(table_name: str) -> str`**
    * **功能**：生成 `DROP TABLE IF EXISTS` 语句。

---

#### C. 模块：`server/core/db_driver.py`
**描述**：负责与 OpenGauss 的物理连接交互，执行 SQL 并处理返回结果。
**接口列表**：

1.  **`get_db_connection() -> Connection`**
    * **功能**：建立并返回 psycopg2 (或兼容 OpenGauss) 的数据库连接对象。

2.  **`execute_ddl(conn: Connection, sql: str) -> None`**
    * **功能**：执行无返回值的 SQL（建表、删表、索引），并自动 Commit。

3.  **`execute_batch_insert(conn: Connection, sql: str) -> int`**
    * **功能**：执行 `INSERT INTO ... SELECT`，并返回受影响的行数（`rowcount`）。此返回值用于判断 BFS 是否走进死胡同。

4.  **`fetch_query_results(conn: Connection, sql: str) -> List[Tuple]`**
    * **功能**：执行 `SELECT` 语句并提取所有结果行，用于获取碰撞的节点信息。

---

#### D. 模块：`server/algo/bidirectional_bfs.py` (已合并剪枝逻辑)
**描述**：核心调度器。负责管理 BFS 的生命周期、计算每一层的剪枝参数（原 `pruning.py` 的功能），并编排 SQL 的执行顺序。
**接口列表**：

1.  **`_calculate_pruning_params(depth: int, initial_amount: int) -> Dict`**
    * **功能**：**（原 Pruning 逻辑）** 根据当前深度和起始金额，计算当前层所需的过滤参数。
    * **逻辑**：例如，虽然去掉了 0.9 的强制系数，但此处可保留接口以支持“最小交易额限制”（如 `min_amount = 100` 分），防止零钱干扰。

2.  **`init_search_session(conn: Connection, start_vid: int) -> str`**
    * **功能**：生成 UUID 作为 Session ID。创建初始表 `fwd_0` 和 `bwd_0`，将起点 `start_vid` 写入两表。

3.  **`step_forward(conn: Connection, session_id: str, depth: int, pruning_params: Dict) -> str`**
    * **功能**：执行正向推演。
        1.  调用 `sql_generator.gen_expand_forward_sql`，传入 `pruning_params`。
        2.  执行 SQL，若插入行数为 0，返回空字符串。
        3.  若有数据，建立索引，返回新表名。

4.  **`step_backward(conn: Connection, session_id: str, depth: int, pruning_params: Dict) -> str`**
    * **功能**：执行反向推演。逻辑同上，但调用 `gen_expand_backward_sql`。

5.  **`detect_cycles(conn: Connection, fwd_table: str, bwd_table: str) -> List[Dict]`**
    * **功能**：执行碰撞检测。若发现碰撞，调用内部辅助函数重组路径，返回环的完整 ID 链条。

6.  **`garbage_collection(conn: Connection, session_id: str, max_depth: int) -> None`**
    * **功能**：根据 Session ID 和最大深度，批量删除所有遗留的临时表。

7.  **`execute_search_workflow(start_vid: int, max_depth: int) -> Dict`**
    * **功能**：**主入口**。
        1.  获取连接。
        2.  初始化 Session。
        3.  循环 `k` 从 1 到 `max_depth / 2`：
            * 计算剪枝参数 `_calculate_pruning_params`。
            * 执行 `step_forward`。
            * 执行 `step_backward`。
            * 执行 `detect_cycles`，若命中则立即返回。
            * 检查前沿表是否为空，若空则提前 `break`。
        4.  确保 `finally` 中执行 `garbage_collection`。
        5.  返回结果字典。

---

#### E. 模块：`server/api/endpoints.py`
**描述**：HTTP 接口层，将 HTTP 请求参数解包并传递给算法模块。
**接口列表**：

1.  **`handle_health_check() -> Dict`**
    * **功能**：返回服务状态及数据库连接测试结果。

2.  **`handle_detect_cycle_request(payload: Dict) -> Dict`**
    * **功能**：
        * 输入：`{"target_vid": 12345, "max_depth": 20}`。
        * 调用 `algo.bidirectional_bfs.execute_search_workflow`。
        * 输出：`{"found": True, "path": [1, 5, 9, 1], "meta": {...}}`。

---

#### F. 模块：`server/main.py`
**描述**：服务端启动脚本。
**接口列表**：

1.  **`start_server(host: str, port: int) -> None`**
    * **功能**：初始化 Web 服务器（如 Uvicorn/Gunicorn），加载配置，暴露 `endpoints` 中的路由。

---

#### G. 模块：`client/remote_caller.py`
**描述**：客户端网络通信模块。
**接口列表**：

1.  **`post_detection_task(server_url: str, vid: int, depth: int) -> Dict`**
    * **功能**：构建 JSON Payload，发送 POST 请求。处理超时（Timeout）和 HTTP 错误（500/404），返回解析后的字典。

---

#### H. 模块：`client/cli.py`
**描述**：命令行入口，负责用户交互。
**接口列表**：

1.  **`parse_arguments() -> Namespace`**
    * **功能**：使用 `argparse` 处理命令行参数 `--vid`, `--depth`, `--host`。

2.  **`display_results(result: Dict) -> None`**
    * **功能**：
        * 若 `result['found']` 为 True，以红色高亮打印 "CYCLE DETECTED"，并按顺序打印链路中的 `vid` 和时间。
        * 若为 False，打印 "No cycle found"。

3.  **`main() -> None`**
    * **功能**：程序执行入口。串联参数解析、远程调用和结果展示。