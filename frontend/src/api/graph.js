import request from './request'

/**
 * 执行图查询
 * @param {Object} params - 查询参数
 * @param {string} params.startId - 起始节点ID
 * @param {string} params.endId - 目标节点ID
 * @param {number} params.maxDepth - 最大深度
 * @param {string} params.queryType - 查询类型
 */
export function queryGraph(params) {
  return request({
    url: '/graph/query',
    method: 'post',
    data: params
  })
}

/**
 * 获取节点信息
 * @param {string} nodeId - 节点ID
 */
export function getNode(nodeId) {
  return request({
    url: `/graph/node/${nodeId}`,
    method: 'get'
  })
}

/**
 * 获取图统计信息
 */
export function getGraphStats() {
  return request({
    url: '/graph/stats',
    method: 'get'
  })
}

/**
 * 执行BiBFS查询
 * @param {Object} params - 查询参数
 */
export function executeBiBFS(params) {
  return request({
    url: '/bibfs/query',
    method: 'post',
    data: params
  })
}

/**
 * 执行内存BiBFS查询
 * @param {Object} params - 查询参数
 */
export function executeMemBiBFS(params) {
  return request({
    url: '/membibfs/query',
    method: 'post',
    data: params
  })
}

/**
 * 执行命令 - 通用接口
 * @param {Array} command - 命令数组，例如 ['query', 'vertex', '--vid', '123']
 * @returns {Promise}
 */
export function executeCommand(command) {
  return request({
    url: '/execute',
    method: 'post',
    data: {
      command
    }
  })
}

/**
 * 用户注册
 * @param {string} username - 用户名
 * @param {string} password - 密码
 * @returns {Promise}
 */
export function register(username, password) {
  return executeCommand(['register', '-u', username, '-p', password])
}

/**
 * 用户登录
 * @param {string} username - 用户名
 * @param {string} password - 密码
 * @returns {Promise}
 */
export function login(username, password) {
  return executeCommand(['login', '-u', username, '-p', password])
}

/**
 * 用户登出
 * @returns {Promise}
 */
export function logout() {
  return executeCommand(['logout'])
}

/**
 * 查询当前用户
 * @returns {Promise}
 */
export function whoami() {
  return executeCommand(['whoami'])
}

/**
 * 查询点
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function queryVertices(params = {}) {
  const command = ['query', 'vertex']
  
  if (params.vid) command.push('--vid', params.vid)
  if (params.vType) command.push('--vt', ...params.vType)
  if (params.minTime) command.push('--min-time', params.minTime)
  if (params.maxTime) command.push('--max-time', params.maxTime)
  if (params.minBalance) command.push('--min-bal', params.minBalance)
  if (params.maxBalance) command.push('--max-bal', params.maxBalance)
  
  return executeCommand(command)
}

/**
 * 查询边
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function queryEdges(params = {}) {
  const command = ['query', 'edge']
  
  if (params.eid) command.push('--eid', params.eid)
  if (params.src) command.push('--src', params.src)
  if (params.dst) command.push('--dst', params.dst)
  if (params.eType) command.push('--et', ...params.eType)
  if (params.minAmount) command.push('--min-amt', params.minAmount)
  if (params.maxAmount) command.push('--max-amt', params.maxAmount)
  if (params.minTime) command.push('--min-time', params.minTime)
  if (params.maxTime) command.push('--max-time', params.maxTime)
  
  return executeCommand(command)
}

/**
 * 查询环路
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function queryCycles(params) {
  const command = ['query', 'cycle', '--start', params.start, '--depth', params.depth]
  
  if (params.direction) command.push('--dir', params.direction)
  if (params.vType) command.push('--vt', ...params.vType)
  if (params.minBalance) command.push('--min-bal', params.minBalance)
  if (params.eType) command.push('--et', ...params.eType)
  if (params.minAmount) command.push('--min-amt', params.minAmount)
  if (params.maxAmount) command.push('--max-amt', params.maxAmount)
  if (params.limit) command.push('--limit', params.limit)
  if (params.allowDupV) command.push('--allow-dup-v')
  if (params.allowDupE) command.push('--allow-dup-e')
  
  return executeCommand(command)
}

/**
 * 插入点
 * @param {Object} data - 点数据
 * @returns {Promise}
 */
export function insertVertex(data) {
  const command = ['insert', 'vertex', '--vt', data.vType]
  
  if (data.vid) command.push('--vid', data.vid)
  if (data.time) command.push('--time', data.time)
  if (data.balance !== undefined) command.push('--bal', data.balance)
  
  return executeCommand(command)
}

/**
 * 插入边
 * @param {Object} data - 边数据
 * @returns {Promise}
 */
export function insertEdge(data) {
  const command = [
    'insert', 'edge',
    '--src', data.src,
    '--dst', data.dst
  ]
  
  if (data.eid) command.push('--eid', data.eid)
  if (data.amount !== undefined) command.push('--amt', data.amount)
  if (data.time) command.push('--time', data.time)
  if (data.eType) command.push('--et', data.eType)
  if (data.createV) command.push('--create-v')
  
  return executeCommand(command)
}

/**
 * 删除点
 * @param {number} vid - 点ID
 * @returns {Promise}
 */
export function deleteVertex(vid) {
  return executeCommand(['delete', 'vertex', '--vid', vid])
}

/**
 * 删除边
 * @param {number} eid - 边ID
 * @returns {Promise}
 */
export function deleteEdge(eid) {
  return executeCommand(['delete', 'edge', '--eid', eid])
}
