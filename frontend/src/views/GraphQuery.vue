<template>
  <div class="graph-query">
    <el-row :gutter="20">
      <!-- 左侧操作面板 -->
      <el-col :span="8">
        <el-card class="operation-panel">
          <template #header>
            <div class="panel-header">
              <el-icon>
                <Operation />
              </el-icon>
              <span>操作面板</span>
            </div>
          </template>

          <el-tabs v-model="mainTab" class="main-tabs">
            <!-- 查询选项卡 -->
            <el-tab-pane label="查询" name="query">
              <el-tabs v-model="activeTab" class="query-tabs">
                <!-- 全图选项卡 -->
                <el-tab-pane label="全图" name="fullGraph">
                  <div style="text-align: center; padding: 40px 20px;">
                    <el-icon :size="60" color="#667eea">
                      <PieChart />
                    </el-icon>
                    <p style="margin-top: 20px; color: #666; font-size: 14px;">
                      显示数据库中所有的点和边
                    </p>
                    <el-button type="primary" @click="queryFullGraph" :loading="loading" size="large"
                      style="margin-top: 20px;">
                      <el-icon>
                        <RefreshRight />
                      </el-icon>
                      <span>刷新全图</span>
                    </el-button>
                  </div>
                </el-tab-pane>

                <!-- 查点选项卡 -->
                <el-tab-pane label="查点" name="vertex">
                  <el-form :model="vertexForm" label-width="100px" size="default">
                    <el-form-item label="点ID">
                      <el-input v-model.number="vertexForm.vid" placeholder="输入点ID" clearable />
                    </el-form-item>
                    <el-form-item label="点类型">
                      <el-input v-model="vertexForm.vTypes" placeholder="输入类型，多个用空格分隔" clearable />
                    </el-form-item>
                    <el-form-item label="最小余额">
                      <el-input-number v-model="vertexForm.minBalance" :min="0" controls-position="right"
                        style="width: 100%" />
                    </el-form-item>
                    <el-form-item label="最大余额">
                      <el-input-number v-model="vertexForm.maxBalance" :min="0" controls-position="right"
                        style="width: 100%" />
                    </el-form-item>
                    <el-form-item>
                      <el-button type="primary" @click="queryVertex" :loading="loading" style="width: 100%">
                        <el-icon>
                          <Search />
                        </el-icon>
                        <span>查询</span>
                      </el-button>
                    </el-form-item>
                  </el-form>
                </el-tab-pane>

                <!-- 查边选项卡 -->
                <el-tab-pane label="查边" name="edge">
                  <el-form :model="edgeForm" label-width="100px" size="default">
                    <el-form-item label="边ID">
                      <el-input v-model.number="edgeForm.eid" placeholder="输入边ID" clearable />
                    </el-form-item>
                    <el-form-item label="源点ID">
                      <el-input v-model.number="edgeForm.srcVid" placeholder="输入源点ID" clearable />
                    </el-form-item>
                    <el-form-item label="目标点ID">
                      <el-input v-model.number="edgeForm.dstVid" placeholder="输入目标点ID" clearable />
                    </el-form-item>
                    <el-form-item label="边类型">
                      <el-input v-model="edgeForm.eTypes" placeholder="输入类型，多个用空格分隔" clearable />
                    </el-form-item>
                    <el-form-item label="最小金额">
                      <el-input-number v-model="edgeForm.minAmount" :min="0" controls-position="right"
                        style="width: 100%" />
                    </el-form-item>
                    <el-form-item label="最大金额">
                      <el-input-number v-model="edgeForm.maxAmount" :min="0" controls-position="right"
                        style="width: 100%" />
                    </el-form-item>
                    <el-form-item>
                      <el-button type="primary" @click="queryEdge" :loading="loading" style="width: 100%">
                        <el-icon>
                          <Search />
                        </el-icon>
                        <span>查询</span>
                      </el-button>
                    </el-form-item>
                  </el-form>
                </el-tab-pane>

                <!-- 查环选项卡 -->
                <el-tab-pane label="查环" name="cycle">
                  <el-form :model="cycleForm" label-width="100px" size="default">
                    <el-form-item label="起始点ID" required>
                      <el-input v-model.number="cycleForm.startVid" placeholder="输入起始点ID" clearable />
                    </el-form-item>
                    <el-form-item label="最大深度" required>
                      <el-input-number v-model="cycleForm.maxDepth" :min="1" :max="20" controls-position="right"
                        style="width: 100%" />
                    </el-form-item>
                    <el-form-item label="方向">
                      <el-select v-model="cycleForm.direction" style="width: 100%">
                        <el-option label="时间递增" value="forward" />
                        <el-option label="任意方向" value="any" />
                      </el-select>
                    </el-form-item>
                    <el-form-item label="点类型">
                      <el-input v-model="cycleForm.vTypes" placeholder="输入类型，多个用空格分隔" clearable />
                    </el-form-item>
                    <el-form-item label="最小余额">
                      <el-input-number v-model="cycleForm.minBalance" :min="0" controls-position="right"
                        style="width: 100%" />
                    </el-form-item>
                    <el-form-item label="边类型">
                      <el-input v-model="cycleForm.eTypes" placeholder="输入类型，多个用空格分隔" clearable />
                    </el-form-item>
                    <el-form-item label="最小金额">
                      <el-input-number v-model="cycleForm.minAmount" :min="0" controls-position="right"
                        style="width: 100%" />
                    </el-form-item>
                    <el-form-item label="返回数量">
                      <el-input-number v-model="cycleForm.limit" :min="1" :max="100" controls-position="right"
                        style="width: 100%" />
                    </el-form-item>
                    <el-form-item>
                      <el-button type="primary" @click="queryCycle" :loading="loading" style="width: 100%">
                        <el-icon>
                          <Search />
                        </el-icon>
                        <span>查询</span>
                      </el-button>
                    </el-form-item>
                  </el-form>
                </el-tab-pane>
              </el-tabs>
            </el-tab-pane>

            <!-- 插入/删除选项卡 -->
            <el-tab-pane label="插入/删除" name="modify">
              <el-tabs v-model="modifyTab" class="modify-tabs">
                <!-- 插入点 -->
                <el-tab-pane label="插入点" name="insertVertex">
                  <el-form :model="insertVertexForm" label-width="100px" size="default">
                    <el-form-item label="点类型" required>
                      <el-input v-model="insertVertexForm.vType" placeholder="例如: account, company" clearable />
                    </el-form-item>
                    <el-form-item label="点ID">
                      <el-input-number v-model="insertVertexForm.vid" :min="1" controls-position="right"
                        style="width: 100%" placeholder="留空自动生成" />
                    </el-form-item>
                    <el-form-item label="初始余额">
                      <el-input-number v-model="insertVertexForm.balance" :min="0" controls-position="right"
                        style="width: 100%" />
                    </el-form-item>
                    <el-form-item label="创建时间">
                      <el-date-picker v-model="insertVertexForm.createTime" type="datetime" placeholder="留空使用当前时间"
                        style="width: 100%" />
                    </el-form-item>
                    <el-form-item>
                      <el-button type="success" @click="insertVertex" :loading="loading" style="width: 100%">
                        <el-icon>
                          <Plus />
                        </el-icon>
                        <span>插入</span>
                      </el-button>
                    </el-form-item>
                  </el-form>
                </el-tab-pane>

                <!-- 插入边 -->
                <el-tab-pane label="插入边" name="insertEdge">
                  <el-form :model="insertEdgeForm" label-width="100px" size="default">
                    <el-form-item label="边ID">
                      <el-input-number v-model="insertEdgeForm.eid" :min="1" controls-position="right"
                        style="width: 100%" placeholder="留空自动生成" />
                    </el-form-item>
                    <el-form-item label="源点ID" required>
                      <el-input-number v-model="insertEdgeForm.srcVid" :min="1" controls-position="right"
                        style="width: 100%" />
                    </el-form-item>
                    <el-form-item label="目标点ID" required>
                      <el-input-number v-model="insertEdgeForm.dstVid" :min="1" controls-position="right"
                        style="width: 100%" />
                    </el-form-item>
                    <el-form-item label="交易金额" required>
                      <el-input-number v-model="insertEdgeForm.amount" :min="0" controls-position="right"
                        style="width: 100%" />
                    </el-form-item>
                    <el-form-item label="边类型">
                      <el-input v-model="insertEdgeForm.eType" placeholder="例如: transfer, 留空默认为 +" clearable />
                    </el-form-item>
                    <el-form-item label="发生时间">
                      <el-date-picker v-model="insertEdgeForm.occurTime" type="datetime" placeholder="留空使用当前时间"
                        style="width: 100%" />
                    </el-form-item>
                    <el-form-item>
                      <el-checkbox v-model="insertEdgeForm.createVertices">自动创建不存在的点</el-checkbox>
                    </el-form-item>
                    <el-form-item>
                      <el-button type="success" @click="insertEdge" :loading="loading" style="width: 100%">
                        <el-icon>
                          <Plus />
                        </el-icon>
                        <span>插入</span>
                      </el-button>
                    </el-form-item>
                  </el-form>
                </el-tab-pane>

                <!-- 删除点 -->
                <el-tab-pane label="删除点" name="deleteVertex">
                  <el-form :model="deleteVertexForm" label-width="100px" size="default">
                    <el-form-item label="点ID" required>
                      <el-input-number v-model="deleteVertexForm.vid" :min="1" controls-position="right"
                        style="width: 100%" />
                    </el-form-item>
                    <el-alert title="警告" type="warning" description="删除点会同时删除所有与该点相关的边" show-icon :closable="false"
                      style="margin-bottom: 20px" />
                    <el-form-item>
                      <el-button type="danger" @click="deleteVertex" :loading="loading" style="width: 100%">
                        <el-icon>
                          <Delete />
                        </el-icon>
                        <span>删除</span>
                      </el-button>
                    </el-form-item>
                  </el-form>
                </el-tab-pane>

                <!-- 删除边 -->
                <el-tab-pane label="删除边" name="deleteEdge">
                  <el-form :model="deleteEdgeForm" label-width="100px" size="default">
                    <el-form-item label="边ID" required>
                      <el-input-number v-model="deleteEdgeForm.eid" :min="1" controls-position="right"
                        style="width: 100%" />
                    </el-form-item>
                    <el-form-item>
                      <el-button type="danger" @click="deleteEdge" :loading="loading" style="width: 100%">
                        <el-icon>
                          <Delete />
                        </el-icon>
                        <span>删除</span>
                      </el-button>
                    </el-form-item>
                  </el-form>
                </el-tab-pane>
              </el-tabs>
            </el-tab-pane>
          </el-tabs>
        </el-card>

         <!-- 操作结果统计 -->
        <el-card class="result-stats" v-if="queryResult" style="margin-bottom: 20px;">
          <template #header>
            <div class="panel-header">
              <el-icon>
                <DataAnalysis />
              </el-icon>
              <span>查询结果</span>
            </div>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="状态">
              <el-tag :type="queryResult.status === 'success' ? 'success' : 'danger'">
                {{ queryResult.status === 'success' ? '成功' : '失败' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="结果数量">
              <span v-if="activeTab === 'fullGraph' && queryResult.vertexCount !== undefined">
                {{ queryResult.vertexCount }} 个点，{{ queryResult.edgeCount }} 条边
              </span>
              <span v-else>
                {{ queryResult.count || 0 }}
              </span>
            </el-descriptions-item>
            <el-descriptions-item label="执行时间" v-if="queryResult.meta">
              {{ queryResult.meta.execution_time_ms }}ms
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

      </el-col>

      <!-- 右侧可视化区域 -->
      <el-col :span="16">
       
        <!-- 图可视化 -->
        <el-card class="visualization-panel">
          <template #header>
            <div class="panel-header">
              <div>
                <el-icon>
                  <PieChart />
                </el-icon>
                <span>图可视化</span>
              </div>
              <div class="header-actions">
                <el-button size="small" @click="resetZoom" :disabled="!hasGraphData">
                  <el-icon>
                    <RefreshRight />
                  </el-icon>
                  重置视图
                </el-button>
                <el-button size="small" @click="exportData" :disabled="!hasGraphData">
                  <el-icon>
                    <Download />
                  </el-icon>
                  导出数据
                </el-button>
              </div>
            </div>
          </template>

          <div v-if="!hasGraphData" class="empty-state">
            <el-empty description="暂无数据，请执行查询操作">
              <el-icon :size="100" color="#909399">
                <Box />
              </el-icon>
            </el-empty>
          </div>

          <div v-else>
            <div ref="chartContainer" class="chart-container"></div>

            <!-- 右键菜单 -->
            <teleport to="body">
              <div
                v-if="contextMenuVisible"
                class="context-menu"
                :style="{
                  left: contextMenuPosition.x + 'px',
                  top: contextMenuPosition.y + 'px'
                }"
                @click.stop
              >
                <div v-if="contextMenuTarget?.type === 'node'" class="menu-item" @click="deleteNodeFromMenu">
                  <el-icon><Delete /></el-icon>
                  <span>删除节点 {{ contextMenuTarget.data.id }}</span>
                </div>
                <div v-if="contextMenuTarget?.type === 'edge'" class="menu-item" @click="deleteEdgeFromMenu">
                  <el-icon><Delete /></el-icon>
                  <span>删除边 {{ contextMenuTarget.data.rawData?.eid }}</span>
                </div>
              </div>
            </teleport>

            <!-- 快速插入节点对话框 -->
            <el-dialog
              v-model="quickInsertDialogVisible"
              title="快速插入节点"
              width="400px"
              :close-on-click-modal="false"
            >
              <el-form :model="quickInsertVertexForm" label-width="80px">
                <el-form-item label="点类型" required>
                  <el-input v-model="quickInsertVertexForm.vType" placeholder="例如: account, company" />
                </el-form-item>
                <el-form-item label="初始余额">
                  <el-input-number v-model="quickInsertVertexForm.balance" :min="0" style="width: 100%" />
                </el-form-item>
              </el-form>
              <template #footer>
                <el-button @click="quickInsertDialogVisible = false">取消</el-button>
                <el-button type="primary" @click="quickInsertNode" :loading="loading">插入</el-button>
              </template>
            </el-dialog>

            <!-- Shift+点击提示 -->
            <div v-if="selectedNodesForEdge.length > 0" class="selection-hint">
              <el-tag type="danger" size="large" effect="dark">
                <el-icon><Connection /></el-icon>
                已选中 {{ selectedNodesForEdge.length }} 个节点: {{ selectedNodesForEdge.join(', ') }}
                <span v-if="selectedNodesForEdge.length < 2"> - 再选择一个节点以创建边</span>
                <el-button
                  text
                  size="small"
                  @click="selectedNodesForEdge = []; updateNodeSelection()"
                  style="margin-left: 10px; color: white;"
                >
                  清除
                </el-button>
              </el-tag>
            </div>

            <!-- 环路列表 -->
            <div v-if="activeTab === 'cycle' && cycleList.length > 0" class="cycle-list">
              <el-divider>环路详情 (共 {{ cycleList.length }} 个)</el-divider>
              <el-collapse v-model="activeCycle">
                <el-collapse-item v-for="(cycle, index) in cycleList" :key="index" :name="index">
                  <template #title>
                    <div class="cycle-title">
                      <el-tag :type="displayedCycles.includes(index) ? 'success' : 'primary'" size="small">
                        环路 {{ index + 1 }}
                        <span v-if="displayedCycles.includes(index)">✓</span>
                      </el-tag>
                      <span class="cycle-info">长度: {{ cycle.vertices?.length || cycle.length }}</span>
                      <el-tag v-if="displayedCycles.includes(index)" size="small" type="success" effect="plain">
                        当前显示
                      </el-tag>
                    </div>
                  </template>
                  <div class="cycle-content">
                    <div class="path-section">
                      <strong>路径:</strong>
                      <div class="path-nodes">
                        <template v-if="cycle.vertices">
                          <el-tag v-for="(vertex, idx) in cycle.vertices" :key="idx" size="small" class="path-tag">
                            {{ vertex.vid }}
                          </el-tag>
                        </template>
                        <template v-else-if="cycle.path">
                          <el-tag v-for="(vid, idx) in cycle.path" :key="idx" size="small" class="path-tag">
                            {{ vid }}
                          </el-tag>
                        </template>
                      </div>
                    </div>
                    <el-button 
                      size="small" 
                      :type="displayedCycles.length === 1 && displayedCycles[0] === index ? 'success' : 'primary'" 
                      @click="highlightCycle(index)"
                      style="margin-top: 10px"
                    >
                      {{ displayedCycles.length === 1 && displayedCycles[0] === index ? '✓ 已显示此环路' : '单独显示此环路' }}
                    </el-button>
                    <el-button 
                      v-if="displayedCycles.length === 1 && displayedCycles[0] === index"
                      size="small" 
                      type="info" 
                      plain
                      @click="buildGraphFromCycles(cycleList)"
                      style="margin-top: 10px; margin-left: 10px"
                    >
                      显示所有环路
                    </el-button>
                  </div>
                </el-collapse-item>
              </el-collapse>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, DataAnalysis, PieChart, RefreshRight, Download, Box, Operation, Plus, Delete, Connection
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { executeCommand } from '@/api/graph'

// 主选项卡
const mainTab = ref('query')
const modifyTab = ref('insertVertex')

// 查询相关
const activeTab = ref('fullGraph')
const loading = ref(false)
const queryResult = ref(null)
const hasGraphData = ref(false)

// 表单数据
const vertexForm = reactive({
  vid: null,
  vTypes: '',
  minBalance: null,
  maxBalance: null
})

const edgeForm = reactive({
  eid: null,
  srcVid: null,
  dstVid: null,
  eTypes: '',
  minAmount: null,
  maxAmount: null
})

const cycleForm = reactive({
  startVid: null,
  maxDepth: 8,
  direction: 'forward',
  vTypes: '',
  minBalance: null,
  eTypes: '',
  minAmount: null,
  limit: 10
})

// 插入表单数据
const insertVertexForm = reactive({
  vid: null,
  vType: '',
  balance: 0,
  createTime: null
})

const insertEdgeForm = reactive({
  eid: null,
  srcVid: null,
  dstVid: null,
  amount: null,
  eType: '',
  occurTime: null,
  createVertices: false
})

// 删除表单数据
const deleteVertexForm = reactive({
  vid: null
})

const deleteEdgeForm = reactive({
  eid: null
})

// 图表相关
const chartContainer = ref(null)
let chartInstance = null
const graphData = reactive({
  nodes: [],
  links: []
})

// 环路相关
const cycleList = ref([])
const activeCycle = ref([0])
const displayedCycles = ref([]) // 当前显示的环路索引列表
const maxDisplayCycles = 5 // 最多同时显示的环路数量

// 交互相关状态
const contextMenuVisible = ref(false)
const contextMenuPosition = ref({ x: 0, y: 0 })
const contextMenuTarget = ref(null) // { type: 'node'|'edge', data: ... }
const quickInsertDialogVisible = ref(false)
const quickInsertPosition = ref({ x: 0, y: 0 })
const selectedNodesForEdge = ref([]) // 用于Shift+点击选择两个节点连边
const quickInsertVertexForm = reactive({
  vType: 'account',
  balance: 0
})
const quickInsertEdgeForm = reactive({
  amount: 1000,
  eType: '+'
})

// 时间格式化辅助函数
const formatTimestamp = (timestamp) => {
  if (!timestamp) return '未知'
  const date = new Date(timestamp * 1000) // Unix时间戳转毫秒
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 查询全图
const queryFullGraph = async () => {
  loading.value = true
  try {
    // 先查询所有边
    const edgeResponse = await executeCommand(['query', 'edge'])
    // 再查询所有点
    const vertexResponse = await executeCommand(['query', 'vertex'])

    // 检查数据有效性
    const hasVertices = vertexResponse.status === 'success' && vertexResponse.data && vertexResponse.data.length > 0
    const hasEdges = edgeResponse.status === 'success' && edgeResponse.data && edgeResponse.data.length > 0

    if (!hasVertices && !hasEdges) {
      ElMessage.warning('数据库为空，未找到任何点或边')
      clearGraph()
      loading.value = false
      return
    }

    // 构建图数据
    graphData.nodes = hasVertices ? vertexResponse.data.map(v => ({
      id: v.vid.toString(),
      name: `V${v.vid}`,
      value: v.balance,
      category: v.v_type,
      symbolSize: Math.max(30, Math.min(80, v.balance / 1000)),
      rawData: v // 保留原始数据用于tooltip显示
    })) : []

    graphData.links = hasEdges ? edgeResponse.data.map(e => ({
      source: e.src_vid.toString(),
      target: e.dst_vid.toString(),
      value: e.amount,
      label: e.e_type,
      lineStyle: {
        width: Math.max(1, Math.min(5, e.amount / 5000))
      },
      rawData: e // 保留原始数据用于tooltip显示
    })) : []

    queryResult.value = {
      status: 'success',
      count: (vertexResponse.count || 0) + (edgeResponse.count || 0),
      meta: {
        execution_time_ms: (vertexResponse.meta?.execution_time_ms || 0) + (edgeResponse.meta?.execution_time_ms || 0)
      },
      vertexCount: vertexResponse.count || 0,
      edgeCount: edgeResponse.count || 0
    }

    hasGraphData.value = true
    renderGraph()
    ElMessage.success(`加载成功：${vertexResponse.count || 0} 个点，${edgeResponse.count || 0} 条边`)
  } catch (error) {
    ElMessage.error('加载全图失败: ' + error.message)
    clearGraph()
  } finally {
    loading.value = false
  }
}

// 查询点
const queryVertex = async () => {
  loading.value = true
  try {
    const command = ['query', 'vertex']

    if (vertexForm.vid) command.push('--vid', vertexForm.vid.toString())
    if (vertexForm.vTypes && vertexForm.vTypes.trim()) {
      const types = vertexForm.vTypes.trim().split(/\s+/)
      command.push('--vt', ...types)
    }
    if (vertexForm.minBalance) command.push('--min-bal', vertexForm.minBalance.toString())
    if (vertexForm.maxBalance) command.push('--max-bal', vertexForm.maxBalance.toString())

    const response = await executeCommand(command)
    queryResult.value = response

    if (response.status === 'success' && response.data) {
      buildGraphFromVertices(response.data)
      ElMessage.success(`查询成功，找到 ${response.count} 个点`)
    } else {
      ElMessage.warning('未找到匹配的点')
      clearGraph()
    }
  } catch (error) {
    ElMessage.error('查询失败: ' + error.message)
    clearGraph()
  } finally {
    loading.value = false
  }
}

// 查询边
const queryEdge = async () => {
  loading.value = true
  try {
    const command = ['query', 'edge']

    if (edgeForm.eid) command.push('--eid', edgeForm.eid.toString())
    if (edgeForm.srcVid) command.push('--src', edgeForm.srcVid.toString())
    if (edgeForm.dstVid) command.push('--dst', edgeForm.dstVid.toString())
    if (edgeForm.eTypes && edgeForm.eTypes.trim()) {
      const types = edgeForm.eTypes.trim().split(/\s+/)
      command.push('--et', ...types)
    }
    if (edgeForm.minAmount) command.push('--min-amt', edgeForm.minAmount.toString())
    if (edgeForm.maxAmount) command.push('--max-amt', edgeForm.maxAmount.toString())

    const response = await executeCommand(command)
    queryResult.value = response

    if (response.status === 'success' && response.data) {
      await buildGraphFromEdges(response.data)
      ElMessage.success(`查询成功，找到 ${response.count} 条边`)
    } else {
      ElMessage.warning('未找到匹配的边')
      clearGraph()
    }
  } catch (error) {
    ElMessage.error('查询失败: ' + error.message)
    clearGraph()
  } finally {
    loading.value = false
  }
}

// 查询环
const queryCycle = async () => {
  if (!cycleForm.startVid) {
    ElMessage.warning('请输入起始点ID')
    return
  }

  loading.value = true
  try {
    const command = [
      'query', 'cycle',
      '--start', cycleForm.startVid.toString(),
      '--depth', cycleForm.maxDepth.toString(),
      '--dir', cycleForm.direction,
      '--limit', cycleForm.limit.toString()
    ]

    if (cycleForm.vTypes && cycleForm.vTypes.trim()) {
      const types = cycleForm.vTypes.trim().split(/\s+/)
      command.push('--vt', ...types)
    }
    if (cycleForm.minBalance) command.push('--min-bal', cycleForm.minBalance.toString())
    if (cycleForm.eTypes && cycleForm.eTypes.trim()) {
      const types = cycleForm.eTypes.trim().split(/\s+/)
      command.push('--et', ...types)
    }
    if (cycleForm.minAmount) command.push('--min-amt', cycleForm.minAmount.toString())

    const response = await executeCommand(command)
    queryResult.value = response

    if (response.status === 'success' && response.data && response.data.length > 0) {
      cycleList.value = response.data
      buildGraphFromCycles(response.data)
      ElMessage.success(`查询成功，找到 ${response.count} 个环路`)
    } else {
      ElMessage.warning('未找到匹配的环路')
      cycleList.value = []
      clearGraph()
    }
  } catch (error) {
    ElMessage.error('查询失败: ' + error.message)
    cycleList.value = []
    clearGraph()
  } finally {
    loading.value = false
  }
}

// 插入点
const insertVertex = async () => {
  if (!insertVertexForm.vType || !insertVertexForm.vType.trim()) {
    ElMessage.warning('请输入点类型')
    return
  }

  loading.value = true
  try {
    const command = ['insert', 'vertex', '--vt', insertVertexForm.vType.trim()]

    if (insertVertexForm.vid) command.push('--vid', insertVertexForm.vid.toString())
    if (insertVertexForm.balance) command.push('--bal', insertVertexForm.balance.toString())
    if (insertVertexForm.createTime) {
      const timestamp = Math.floor(insertVertexForm.createTime.getTime() / 1000)
      command.push('--time', timestamp.toString())
    }

    const response = await executeCommand(command)

    if (response.status === 'success') {
      ElMessage.success(`点插入成功: ID=${response.data?.vid || '自动生成'}`)
      // 重置表单
      insertVertexForm.vid = null
      insertVertexForm.vType = ''
      insertVertexForm.balance = 0
      insertVertexForm.createTime = null
      // 刷新全图
      await queryFullGraph()
    } else {
      ElMessage.error('插入失败: ' + response.message)
    }
  } catch (error) {
    ElMessage.error('插入失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 插入边
const insertEdge = async () => {
  if (!insertEdgeForm.srcVid || !insertEdgeForm.dstVid) {
    ElMessage.warning('请输入源点ID和目标点ID')
    return
  }
  if (insertEdgeForm.amount === null || insertEdgeForm.amount === undefined) {
    ElMessage.warning('请输入交易金额')
    return
  }

  loading.value = true
  try {
    const command = [
      'insert', 'edge',
      '--src', insertEdgeForm.srcVid.toString(),
      '--dst', insertEdgeForm.dstVid.toString(),
      '--amt', insertEdgeForm.amount.toString()
    ]

    if (insertEdgeForm.eid) command.push('--eid', insertEdgeForm.eid.toString())
    if (insertEdgeForm.eType && insertEdgeForm.eType.trim()) {
      command.push('--et', insertEdgeForm.eType.trim())
    }
    if (insertEdgeForm.occurTime) {
      const timestamp = Math.floor(insertEdgeForm.occurTime.getTime() / 1000)
      command.push('--time', timestamp.toString())
    }
    if (insertEdgeForm.createVertices) {
      command.push('--create-v')
    }

    const response = await executeCommand(command)

    if (response.status === 'success') {
      ElMessage.success(`边插入成功: ID=${response.data?.eid || '自动生成'}`)
      // 重置表单
      insertEdgeForm.eid = null
      insertEdgeForm.srcVid = null
      insertEdgeForm.dstVid = null
      insertEdgeForm.amount = null
      insertEdgeForm.eType = ''
      insertEdgeForm.occurTime = null
      insertEdgeForm.createVertices = false
      // 刷新全图
      await queryFullGraph()
    } else {
      ElMessage.error('插入失败: ' + response.message)
    }
  } catch (error) {
    ElMessage.error('插入失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 删除点
const deleteVertex = async () => {
  if (!deleteVertexForm.vid) {
    ElMessage.warning('请输入点ID')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除点 ${deleteVertexForm.vid} 吗？这将同时删除所有相关的边。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    loading.value = true
    const command = ['delete', 'vertex', '--vid', deleteVertexForm.vid.toString()]
    const response = await executeCommand(command)

    if (response.status === 'success') {
      const edgesDeleted = response.data?.edges_deleted || 0
      ElMessage.success(`点删除成功，同时删除了 ${edgesDeleted} 条相关的边`)
      // 重置表单
      deleteVertexForm.vid = null
      // 刷新全图
      await queryFullGraph()
    } else {
      ElMessage.error('删除失败: ' + response.message)
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + error.message)
    }
  } finally {
    loading.value = false
  }
}

// 删除边
const deleteEdge = async () => {
  if (!deleteEdgeForm.eid) {
    ElMessage.warning('请输入边ID')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除边 ${deleteEdgeForm.eid} 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    loading.value = true
    const command = ['delete', 'edge', '--eid', deleteEdgeForm.eid.toString()]
    const response = await executeCommand(command)

    if (response.status === 'success') {
      ElMessage.success('边删除成功')
      // 重置表单
      deleteEdgeForm.eid = null
      // 刷新全图
      await queryFullGraph()
    } else {
      ElMessage.error('删除失败: ' + response.message)
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + error.message)
    }
  } finally {
    loading.value = false
  }
}

// 从点数据构建图
const buildGraphFromVertices = (vertices) => {
  graphData.nodes = vertices.map(v => ({
    id: v.vid.toString(),
    name: `V${v.vid}`,
    value: v.balance,
    category: v.v_type,
    symbolSize: Math.max(30, Math.min(80, v.balance / 1000)),
    rawData: v // 保留原始数据
  }))
  graphData.links = []
  hasGraphData.value = true
  renderGraph()
}

// 从边数据构建图
const buildGraphFromEdges = async (edges) => {
  // 收集所有涉及的点ID
  const vidSet = new Set()
  edges.forEach(e => {
    vidSet.add(e.src_vid)
    vidSet.add(e.dst_vid)
  })

  // 查询这些点的详细信息
  const nodes = []
  for (const vid of vidSet) {
    try {
      const response = await executeCommand(['query', 'vertex', '--vid', vid.toString()])
      if (response.status === 'success' && response.data && response.data.length > 0) {
        const v = response.data[0]
        nodes.push({
          id: v.vid.toString(),
          name: `V${v.vid}`,
          value: v.balance,
          category: v.v_type,
          symbolSize: Math.max(30, Math.min(80, v.balance / 1000)),
          rawData: v // 保留原始数据
        })
      }
    } catch (error) {
      // 如果查询失败，创建默认节点
      nodes.push({
        id: vid.toString(),
        name: `V${vid}`,
        value: 0,
        category: 'unknown',
        symbolSize: 40,
        rawData: { vid, v_type: 'unknown', balance: 0, create_time: null } // 默认数据
      })
    }
  }

  graphData.nodes = nodes
  graphData.links = edges.map(e => ({
    source: e.src_vid.toString(),
    target: e.dst_vid.toString(),
    value: e.amount,
    label: e.e_type,
    lineStyle: {
      width: Math.max(1, Math.min(5, e.amount / 5000))
    },
    rawData: e // 保留原始数据
  }))

  hasGraphData.value = true
  renderGraph()
}

// 从环路数据构建图
const buildGraphFromCycles = (cycles) => {
  const nodeMap = new Map()
  const edgeMap = new Map()
  
  // 确定要显示的环路数量
  const cyclesToDisplay = Math.min(cycles.length, maxDisplayCycles)
  displayedCycles.value = Array.from({ length: cyclesToDisplay }, (_, i) => i)

  // 合并前N个环的数据
  for (let i = 0; i < cyclesToDisplay; i++) {
    const cycle = cycles[i]
    
    // 添加点
    cycle.vertices.forEach(v => {
      nodeMap.set(v.vid.toString(), {
        id: v.vid.toString(),
        name: `V${v.vid}`,
        value: v.balance,
        category: v.v_type,
        symbolSize: Math.max(30, Math.min(80, v.balance / 1000)),
        rawData: v // 保留原始数据
      })
    })
    
    // 添加边
    cycle.edges.forEach(e => {
      const key = `${e.src_vid}-${e.dst_vid}`
      edgeMap.set(key, {
        source: e.src_vid.toString(),
        target: e.dst_vid.toString(),
        value: e.amount,
        label: e.e_type,
        lineStyle: {
          width: Math.max(1, Math.min(5, e.amount / 5000))
        },
        rawData: e // 保留原始数据
      })
    })
  }

  graphData.nodes = Array.from(nodeMap.values())
  graphData.links = Array.from(edgeMap.values())

  hasGraphData.value = true
  renderGraph()
  
  // 如果有未显示的环路，提示用户
  if (cycles.length > maxDisplayCycles) {
    ElMessage.info(`图中显示前 ${maxDisplayCycles} 个环路，点击列表中的环路可查看其他环路`)
  }
}

// 渲染图表
const renderGraph = () => {
  nextTick(() => {
    if (!chartContainer.value) return

    // 如果图表实例不存在或已被销毁，重新创建
    if (!chartInstance || chartInstance.isDisposed()) {
      chartInstance = echarts.init(chartContainer.value)
    }

    // 获取所有类型用于图例
    const categories = [...new Set(graphData.nodes.map(n => n.category))]
    const legendData = categories.length > 0 ? categories : ['account', 'company', 'unknown']

    // 如果只有一个或少数节点，添加初始位置
    const processedNodes = graphData.nodes.map((node, index) => {
      if (graphData.nodes.length <= 3) {
        const angle = (2 * Math.PI * index) / Math.max(graphData.nodes.length, 1)
        const radius = 100
        return {
          ...node,
          x: Math.cos(angle) * radius,
          y: Math.sin(angle) * radius,
          fixed: false
        }
      }
      return node
    })

    const option = {
      tooltip: {
        formatter: function (params) {
          if (params.dataType === 'node') {
            const node = params.data
            const raw = node.rawData || {}
            return `
              <div style="padding: 10px; max-width: 350px;">
                <strong style="font-size: 15px; color: #409eff;">📍 点信息</strong><br/>
                <div style="margin-top: 10px; line-height: 1.8; font-size: 13px;">
                  <div><span style="color: #909399;">点ID (vid):</span> <strong style="color: #303133;">${raw.vid || node.id}</strong></div>
                  <div><span style="color: #909399;">类型 (v_type):</span> <strong style="color: #303133;">${raw.v_type || node.category}</strong></div>
                  <div><span style="color: #909399;">余额 (balance):</span> <strong style="color: #303133;">${(raw.balance !== undefined ? raw.balance : node.value).toLocaleString()}</strong></div>
                  <div><span style="color: #909399;">创建时间 (create_time):</span> <strong style="color: #303133;">${formatTimestamp(raw.create_time)}</strong></div>
                  <div style="margin-top: 4px; padding-top: 4px; border-top: 1px dashed #dcdfe6;">
                    <span style="color: #909399; font-size: 11px;">时间戳: ${raw.create_time || '未知'}</span>
                  </div>
                </div>
              </div>
            `
          } else if (params.dataType === 'edge') {
            const edge = params.data
            const raw = edge.rawData || {}
            return `
              <div style="padding: 10px; max-width: 350px;">
                <strong style="font-size: 15px; color: #67c23a;">🔗 边信息</strong><br/>
                <div style="margin-top: 10px; line-height: 1.8; font-size: 13px;">
                  <div><span style="color: #909399;">边ID (eid):</span> <strong style="color: #303133;">${raw.eid || '未知'}</strong></div>
                  <div><span style="color: #909399;">源点ID (src_vid):</span> <strong style="color: #303133;">${raw.src_vid || edge.source}</strong></div>
                  <div><span style="color: #909399;">目标点ID (dst_vid):</span> <strong style="color: #303133;">${raw.dst_vid || edge.target}</strong></div>
                  <div><span style="color: #909399;">边类型 (e_type):</span> <strong style="color: #303133;">${raw.e_type || edge.label}</strong></div>
                  <div><span style="color: #909399;">金额 (amount):</span> <strong style="color: #303133;">${(raw.amount !== undefined ? raw.amount : edge.value).toLocaleString()}</strong></div>
                  <div><span style="color: #909399;">发生时间 (occur_time):</span> <strong style="color: #303133;">${formatTimestamp(raw.occur_time)}</strong></div>
                  <div style="margin-top: 4px; padding-top: 4px; border-top: 1px dashed #dcdfe6;">
                    <span style="color: #909399; font-size: 11px;">时间戳: ${raw.occur_time || '未知'}</span>
                  </div>
                </div>
              </div>
            `
          }
        }
      },
      legend: {
        data: legendData,
        top: 10,
        textStyle: {
          color: '#666'
        }
      },
      series: [{
        type: 'graph',
        layout: graphData.nodes.length <= 3 ? 'none' : 'force',
        data: processedNodes,
        links: graphData.links,
        categories: legendData.map(name => ({ name })),
        roam: true,
        draggable: true,
        label: {
          show: true,
          position: 'right',
          formatter: (params) => {
            // 显示点ID
            return params.data.id
          },
          fontSize: 14,
          fontWeight: 'bold',
          color: '#333'
        },
        labelLayout: {
          hideOverlap: true
        },
        edgeLabel: {
          show: graphData.links.length > 0 && graphData.links.length <= 20,
          fontSize: 10,
          formatter: '{c}'
        },
        force: {
          repulsion: 500,
          gravity: 0.1,
          edgeLength: [100, 200],
          layoutAnimation: true
        },
        emphasis: {
          focus: 'adjacency',
          label: {
            show: true
          },
          lineStyle: {
            width: 5
          }
        },
        itemStyle: {
          borderColor: '#fff',
          borderWidth: 2,
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.3)'
        },
        lineStyle: {
          color: 'source',
          curveness: 0.2,
          opacity: 0.7
        },
        edgeSymbol: ['none', 'arrow'],
        edgeSymbolSize: [0, 10]
      }]
    }

    chartInstance.setOption(option, true)

    // 移除旧的事件监听器
    chartInstance.off('dblclick')
    chartInstance.off('click')
    
    // 添加双击事件监听
    chartInstance.on('dblclick', handleChartDblClick)
    
    // 添加点击事件监听（用于Shift+点击）
    chartInstance.on('click', handleNodeClick)

    // 确保图表自适应容器大小
    setTimeout(() => {
      if (chartInstance) {
        chartInstance.resize()
      }
    }, 100)
  })
}

// 高亮显示环路
const highlightCycle = (index) => {
  if (!cycleList.value[index]) return
  
  const cycle = cycleList.value[index]
  
  // 重新构建图数据，只显示这个环路
  const nodeMap = new Map()
  const edgeMap = new Map()
  
  // 添加这个环的点
  cycle.vertices.forEach(v => {
    nodeMap.set(v.vid.toString(), {
      id: v.vid.toString(),
      name: `V${v.vid}`,
      value: v.balance,
      category: v.v_type,
      symbolSize: Math.max(30, Math.min(80, v.balance / 1000)),
      rawData: v // 保留原始数据
    })
  })
  
  // 添加这个环的边
  cycle.edges.forEach(e => {
    const key = `${e.src_vid}-${e.dst_vid}`
    edgeMap.set(key, {
      source: e.src_vid.toString(),
      target: e.dst_vid.toString(),
      value: e.amount,
      label: e.e_type,
      lineStyle: {
        width: Math.max(1, Math.min(5, e.amount / 5000))
      },
      rawData: e // 保留原始数据
    })
  })
  
  graphData.nodes = Array.from(nodeMap.values())
  graphData.links = Array.from(edgeMap.values())
  displayedCycles.value = [index]
  
  renderGraph()
  ElMessage.success(`已切换显示环路 ${index + 1}`)
}

// 重置视图
const resetZoom = () => {
  if (chartInstance) {
    chartInstance.dispatchAction({
      type: 'restore'
    })
    renderGraph()
  }
}

// 导出数据
const exportData = () => {
  const data = {
    queryType: activeTab.value,
    result: queryResult.value,
    graph: {
      nodes: graphData.nodes,
      links: graphData.links
    }
  }

  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `graph-query-${Date.now()}.json`
  a.click()
  URL.revokeObjectURL(url)

  ElMessage.success('数据已导出')
}

// 清空图表
const clearGraph = () => {
  graphData.nodes = []
  graphData.links = []
  displayedCycles.value = []
  selectedNodesForEdge.value = []
  if (chartInstance && !chartInstance.isDisposed()) {
    chartInstance.clear()
  }
}

// 处理图表双击事件
const handleChartDblClick = (params) => {
  if (params.componentType === 'series') {
    if (params.dataType === 'node') {
      // 双击节点，显示删除菜单
      contextMenuTarget.value = {
        type: 'node',
        data: params.data
      }
      showContextMenu(params.event.event)
    } else if (params.dataType === 'edge') {
      // 双击边，显示删除菜单
      contextMenuTarget.value = {
        type: 'edge',
        data: params.data
      }
      showContextMenu(params.event.event)
    }
  } else {
    // 双击空白处，显示插入节点对话框
    quickInsertDialogVisible.value = true
    quickInsertVertexForm.vType = 'account'
    quickInsertVertexForm.balance = 0
  }
}

// 显示右键菜单
const showContextMenu = (event) => {
  contextMenuVisible.value = true
  contextMenuPosition.value = {
    x: event.clientX,
    y: event.clientY
  }
}

// 隐藏右键菜单
const hideContextMenu = () => {
  contextMenuVisible.value = false
  contextMenuTarget.value = null
}

// 从右键菜单删除节点
const deleteNodeFromMenu = async () => {
  if (!contextMenuTarget.value || contextMenuTarget.value.type !== 'node') return
  
  const nodeData = contextMenuTarget.value.data
  const vid = nodeData.rawData?.vid || nodeData.id
  
  hideContextMenu()
  
  try {
    await ElMessageBox.confirm(
      `确定要删除点 ${vid} 吗？这将同时删除所有相关的边。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    loading.value = true
    const command = ['delete', 'vertex', '--vid', vid.toString()]
    const response = await executeCommand(command)

    if (response.status === 'success') {
      const edgesDeleted = response.data?.edges_deleted || 0
      ElMessage.success(`点删除成功，同时删除了 ${edgesDeleted} 条相关的边`)
      // 刷新当前视图
      if (activeTab.value === 'fullGraph') {
        await queryFullGraph()
      } else if (activeTab.value === 'vertex') {
        await queryVertex()
      } else if (activeTab.value === 'edge') {
        await queryEdge()
      } else if (activeTab.value === 'cycle' && cycleList.value.length > 0) {
        await queryCycle()
      }
    } else {
      ElMessage.error('删除失败: ' + response.message)
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + error.message)
    }
  } finally {
    loading.value = false
  }
}

// 从右键菜单删除边
const deleteEdgeFromMenu = async () => {
  if (!contextMenuTarget.value || contextMenuTarget.value.type !== 'edge') return
  
  const edgeData = contextMenuTarget.value.data
  const eid = edgeData.rawData?.eid
  
  if (!eid) {
    ElMessage.error('无法获取边ID')
    hideContextMenu()
    return
  }
  
  hideContextMenu()
  
  try {
    await ElMessageBox.confirm(
      `确定要删除边 ${eid} 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    loading.value = true
    const command = ['delete', 'edge', '--eid', eid.toString()]
    const response = await executeCommand(command)

    if (response.status === 'success') {
      ElMessage.success('边删除成功')
      // 刷新当前视图
      if (activeTab.value === 'fullGraph') {
        await queryFullGraph()
      } else if (activeTab.value === 'edge') {
        await queryEdge()
      } else if (activeTab.value === 'vertex') {
        await queryVertex()
      } else if (activeTab.value === 'cycle' && cycleList.value.length > 0) {
        await queryCycle()
      }
    } else {
      ElMessage.error('删除失败: ' + response.message)
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + error.message)
    }
  } finally {
    loading.value = false
  }
}

// 快速插入节点
const quickInsertNode = async () => {
  if (!quickInsertVertexForm.vType || !quickInsertVertexForm.vType.trim()) {
    ElMessage.warning('请输入点类型')
    return
  }

  loading.value = true
  try {
    const command = [
      'insert', 'vertex',
      '--vt', quickInsertVertexForm.vType.trim(),
      '--bal', quickInsertVertexForm.balance.toString()
    ]

    const response = await executeCommand(command)

    if (response.status === 'success') {
      ElMessage.success(`点插入成功: ID=${response.data?.vid || '自动生成'}`)
      quickInsertDialogVisible.value = false
      // 刷新全图
      await queryFullGraph()
    } else {
      ElMessage.error('插入失败: ' + response.message)
    }
  } catch (error) {
    ElMessage.error('插入失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 处理Shift+点击选择节点
const handleNodeClick = (params, event) => {
  if (event.event.shiftKey && params.dataType === 'node') {
    const nodeId = params.data.id
    
    // 如果已经选中这个节点，取消选中
    const index = selectedNodesForEdge.value.indexOf(nodeId)
    if (index > -1) {
      selectedNodesForEdge.value.splice(index, 1)
      ElMessage.info(`取消选中节点 ${nodeId}`)
      updateNodeSelection()
      return
    }
    
    // 如果已经选中了2个节点，先清空
    if (selectedNodesForEdge.value.length >= 2) {
      selectedNodesForEdge.value = []
    }
    
    // 添加选中的节点
    selectedNodesForEdge.value.push(nodeId)
    ElMessage.success(`已选中节点 ${nodeId} (${selectedNodesForEdge.value.length}/2)`)
    
    // 如果选中了2个节点，显示连边对话框
    if (selectedNodesForEdge.value.length === 2) {
      showQuickEdgeDialog()
    }
    
    updateNodeSelection()
  }
}

// 更新节点选中状态的视觉效果
const updateNodeSelection = () => {
  if (!chartInstance) return
  
  const option = chartInstance.getOption()
  if (!option.series || !option.series[0]) return
  
  // 更新节点样式以显示选中状态
  const nodes = option.series[0].data.map(node => {
    const isSelected = selectedNodesForEdge.value.includes(node.id)
    return {
      ...node,
      itemStyle: {
        ...node.itemStyle,
        borderColor: isSelected ? '#f56c6c' : '#fff',
        borderWidth: isSelected ? 4 : 2,
        shadowBlur: isSelected ? 20 : 10,
        shadowColor: isSelected ? 'rgba(245, 108, 108, 0.8)' : 'rgba(0, 0, 0, 0.3)'
      }
    }
  })
  
  chartInstance.setOption({
    series: [{
      data: nodes
    }]
  })
}

// 显示快速连边对话框
const showQuickEdgeDialog = () => {
  // 使用对话框而不是直接执行
  ElMessageBox.prompt(
    `在节点 ${selectedNodesForEdge.value[0]} 和 ${selectedNodesForEdge.value[1]} 之间创建边\n\n请输入金额:`,
    '创建边',
    {
      confirmButtonText: '创建',
      cancelButtonText: '取消',
      inputPattern: /^\d+$/,
      inputErrorMessage: '请输入有效的数字',
      inputValue: '1000',
      inputPlaceholder: '输入金额'
    }
  ).then(async ({ value }) => {
    await quickInsertEdgeBetweenNodes(parseInt(value))
  }).catch(() => {
    ElMessage.info('已取消')
    selectedNodesForEdge.value = []
    updateNodeSelection()
  })
}

// 快速在两个节点之间插入边
const quickInsertEdgeBetweenNodes = async (amount) => {
  if (selectedNodesForEdge.value.length !== 2) {
    ElMessage.warning('请先选择两个节点')
    return
  }

  loading.value = true
  try {
    const command = [
      'insert', 'edge',
      '--src', selectedNodesForEdge.value[0].toString(),
      '--dst', selectedNodesForEdge.value[1].toString(),
      '--amt', amount.toString(),
      '--et', '+'
    ]

    const response = await executeCommand(command)

    if (response.status === 'success') {
      ElMessage.success(`边创建成功: ${selectedNodesForEdge.value[0]} → ${selectedNodesForEdge.value[1]}`)
      selectedNodesForEdge.value = []
      // 刷新全图
      await queryFullGraph()
    } else {
      ElMessage.error('创建边失败: ' + response.message)
      selectedNodesForEdge.value = []
      updateNodeSelection()
    }
  } catch (error) {
    ElMessage.error('创建边失败: ' + error.message)
    selectedNodesForEdge.value = []
    updateNodeSelection()
  } finally {
    loading.value = false
  }
}

// 生命周期
onMounted(() => {
  window.addEventListener('resize', () => {
    if (chartInstance) {
      chartInstance.resize()
    }
  })
  
  // 添加全局点击事件来隐藏右键菜单
  window.addEventListener('click', (e) => {
    if (contextMenuVisible.value) {
      hideContextMenu()
    }
  })

  // 默认加载全图
  queryFullGraph()
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
  }
})
</script>

<style scoped>
.graph-query {
  padding: 20px;
  min-height: calc(100vh - 140px);
}

.operation-panel {
  margin-bottom: 20px;
  border-radius: 12px;
  max-height: calc(100vh - 160px);
  overflow-y: auto;
}

.visualization-panel {
  border-radius: 12px;
  height: auto;
}

.result-stats {
  border-radius: 12px;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
  font-size: 16px;
  color: #333;
}

.panel-header>div {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.main-tabs {
  margin-top: -10px;
}

.main-tabs :deep(.el-tabs__item) {
  font-weight: 600;
  font-size: 15px;
}

.main-tabs :deep(.el-tabs__item.is-active) {
  color: #667eea;
}

.main-tabs :deep(.el-tabs__active-bar) {
  background-color: #667eea;
  height: 3px;
}

.query-tabs,
.modify-tabs {
  margin-top: 10px;
}

.query-tabs :deep(.el-tabs__item),
.modify-tabs :deep(.el-tabs__item) {
  font-weight: 500;
}

.query-tabs :deep(.el-tabs__item.is-active),
.modify-tabs :deep(.el-tabs__item.is-active) {
  color: #667eea;
}

.query-tabs :deep(.el-tabs__active-bar),
.modify-tabs :deep(.el-tabs__active-bar) {
  background-color: #667eea;
}

.query-tabs :deep(.el-form-item),
.modify-tabs :deep(.el-form-item) {
  margin-bottom: 18px;
}

.chart-container {
  width: 100%;
  height: 600px;
  min-height: 400px;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: calc(100vh - 300px);
  min-height: 500px;
}

.cycle-list {
  margin-top: 20px;
  max-height: 300px;
  overflow-y: auto;
}

.cycle-title {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.cycle-info {
  color: #666;
  font-size: 14px;
  flex: 1;
}

.cycle-content {
  padding: 10px 0;
}

.path-section {
  margin-bottom: 10px;
}

.path-nodes {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.path-tag {
  font-family: 'Courier New', monospace;
}

/* 右键菜单样式 */
.context-menu {
  position: fixed;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  padding: 6px 0;
  z-index: 9999;
  min-width: 160px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  cursor: pointer;
  transition: background-color 0.2s;
  font-size: 14px;
  color: #606266;
}

.menu-item:hover {
  background-color: #f5f7fa;
  color: #f56c6c;
}

.menu-item .el-icon {
  font-size: 16px;
}

/* 选择提示样式 */
.selection-hint {
  position: fixed;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    bottom: 0;
    opacity: 0;
  }
  to {
    bottom: 30px;
    opacity: 1;
  }
}

.selection-hint .el-tag {
  padding: 12px 20px;
  font-size: 14px;
}
</style>
