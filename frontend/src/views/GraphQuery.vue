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
        <el-card class="result-stats" v-if="queryResult" style="margin-bottom: 0px;">
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
        <div style="position: relative; height: 100%; display: flex; flex-direction: column;">
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

            <div v-else style="position: relative; width: 100%; height: 600px;">
              <div ref="chartContainer" class="chart-container"></div>

            <!-- 右键菜单浮动窗口 -->
            <teleport to="body">
              <transition name="context-menu-fade">
                <el-card v-if="contextMenuVisible" class="context-menu-card" :style="{
                  left: contextMenuPosition.x + 'px',
                  top: contextMenuPosition.y + 'px'
                }" shadow="always" @click.stop>
                  <template #header>
                    <div class="context-menu-header">
                      <span v-if="contextMenuTarget?.type === 'node'">节点操作</span>
                      <span v-else-if="contextMenuTarget?.type === 'edge'">边操作</span>
                      <span v-else>快捷操作</span>
                    </div>
                  </template>
                  <div class="context-menu-content">
                    <div v-if="contextMenuTarget?.type === 'node'">
                      <div class="menu-item" @click="openEditDialog('vertex')">
                        <el-icon color="#409eff">
                          <Edit />
                        </el-icon>
                        <span>编辑属性</span>
                      </div>
                      <div class="menu-item" @click="deleteNodeFromMenu">
                        <el-icon color="#f56c6c">
                          <Delete />
                        </el-icon>
                        <span>删除节点 {{ contextMenuTarget.data.id }}</span>
                      </div>
                    </div>
                    <div v-if="contextMenuTarget?.type === 'edge'">
                      <div class="menu-item" @click="openEditDialog('edge')">
                        <el-icon color="#409eff">
                          <Edit />
                        </el-icon>
                        <span>编辑属性</span>
                      </div>
                      <div class="menu-item" @click="deleteEdgeFromMenu">
                        <el-icon color="#f56c6c">
                          <Delete />
                        </el-icon>
                        <span>删除边 {{ contextMenuTarget.data.rawData?.eid }}</span>
                      </div>
                    </div>
                    <div v-if="contextMenuTarget?.type === 'blank'" class="menu-item" @click="showQuickInsertDialog">
                      <el-icon color="#67c23a">
                        <Plus />
                      </el-icon>
                      <span>插入节点</span>
                    </div>
                  </div>
                </el-card>
              </transition>
            </teleport>

            <!-- 快速插入节点对话框 -->
            <el-dialog v-model="quickInsertDialogVisible" title="快速插入节点" width="400px" :close-on-click-modal="false">
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

            <!-- 快速连边对话框 -->
            <el-dialog v-model="quickEdgeDialogVisible" title="快速创建边" width="500px" :close-on-click-modal="false">
              <el-form :model="quickInsertEdgeForm" label-width="100px">
                <el-form-item label="源点ID">
                  <el-input-number v-model="quickInsertEdgeForm.srcVid" :min="1" controls-position="right"
                    style="width: 100%" disabled />
                </el-form-item>
                <el-form-item label="目标点ID">
                  <el-input-number v-model="quickInsertEdgeForm.dstVid" :min="1" controls-position="right"
                    style="width: 100%" disabled />
                </el-form-item>
                <el-form-item label="边ID">
                  <el-input-number v-model="quickInsertEdgeForm.eid" :min="1" controls-position="right"
                    style="width: 100%" placeholder="留空自动生成" />
                </el-form-item>
                <el-form-item label="交易金额" required>
                  <el-input-number v-model="quickInsertEdgeForm.amount" :min="0" controls-position="right"
                    style="width: 100%" />
                </el-form-item>
                <el-form-item label="边类型">
                  <el-input v-model="quickInsertEdgeForm.eType" placeholder="例如: transfer, 留空默认为 +" clearable />
                </el-form-item>
                <el-form-item label="发生时间">
                  <el-date-picker v-model="quickInsertEdgeForm.occurTime" type="datetime" placeholder="留空使用当前时间"
                    style="width: 100%" />
                </el-form-item>
              </el-form>
              <template #footer>
                <el-button @click="cancelQuickEdge">取消</el-button>
                <el-button type="primary" @click="confirmQuickEdge" :loading="loading">创建</el-button>
              </template>
            </el-dialog>

            <!-- 编辑属性对话框 -->
            <el-dialog 
              v-model="editDialogVisible" 
              :title="editType === 'vertex' ? '编辑节点属性' : '编辑边属性'" 
              width="500px"
              :close-on-click-modal="false"
              @close="resetEditForm"
            >
              <!-- 编辑节点 -->
              <el-form v-if="editType === 'vertex'" :model="editForm" label-width="100px">
                <el-form-item label="点ID">
                  <el-input v-model="editForm.vid" disabled />
                </el-form-item>
                <el-form-item label="点类型">
                  <el-input v-model="editForm.vType" placeholder="输入点类型" clearable />
                </el-form-item>
                <el-form-item label="余额">
                  <el-input v-model="editForm.balance" placeholder="输入余额" clearable />
                </el-form-item>
              </el-form>

              <!-- 编辑边 -->
              <el-form v-if="editType === 'edge'" :model="editForm" label-width="100px">
                <el-form-item label="边ID">
                  <el-input v-model="editForm.eid" disabled />
                </el-form-item>
                <el-form-item label="源点ID">
                  <el-input v-model="editForm.srcVid" disabled />
                </el-form-item>
                <el-form-item label="目标点ID">
                  <el-input v-model="editForm.dstVid" disabled />
                </el-form-item>
                <el-form-item label="边类型">
                  <el-input v-model="editForm.eType" placeholder="输入边类型" clearable />
                </el-form-item>
                <el-form-item label="金额">
                  <el-input v-model="editForm.amount" placeholder="输入金额" clearable />
                </el-form-item>
                <el-form-item label="发生时间">
                  <el-date-picker
                    v-model="editForm.occurTime"
                    type="datetime"
                    placeholder="选择时间"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-form>

              <template #footer>
                <span class="dialog-footer">
                  <el-button @click="editDialogVisible = false">取消</el-button>
                  <el-button type="primary" @click="handleUpdate" :loading="loading">更新</el-button>
                </span>
              </template>
            </el-dialog>

            <!-- Shift+点击提示 -->
            <div v-if="selectedNodesForEdge.length > 0" class="selection-hint">
              <el-tag type="danger" size="large" effect="dark">
                <el-icon>
                  <Connection />
                </el-icon>
                已选中 {{ selectedNodesForEdge.length }} 个节点: {{ selectedNodesForEdge.join(', ') }}
                <span v-if="selectedNodesForEdge.length < 2"> - 再选择一个节点以创建边</span>
                <el-button text size="small" @click="selectedNodesForEdge = []; updateNodeSelection()"
                  style="margin-left: 10px; color: white;">
                  清除
                </el-button>
              </el-tag>
            </div>
          </div>
        </el-card>

        <!-- 底部环路面板 -->
        <div v-if="activeTab === 'cycle' && cycleList.length > 0" 
             class="cycle-bottom-panel" 
             :class="{ collapsed: cycleDrawerCollapsed }"
             :style="{ height: cycleDrawerCollapsed ? '32px' : cycleDrawerHeight + 'px' }">
          <div class="cycle-panel-header" @click="cycleDrawerCollapsed = !cycleDrawerCollapsed">
            <div class="cycle-panel-resizer" @mousedown.stop="startResizeCycleDrawer"></div>
            <div style="display: flex; align-items: center; gap: 10px; flex: 1;">
              <el-icon><DataAnalysis /></el-icon>
              <span style="font-weight: 600;">环路列表 (共 {{ cycleList.length }} 个)</span>
            </div>
            <el-icon style="transition: transform 0.3s;" :style="{ transform: cycleDrawerCollapsed ? 'rotate(0deg)' : 'rotate(180deg)' }">
              <ArrowDown />
            </el-icon>
          </div>
          <div v-show="!cycleDrawerCollapsed" class="cycle-panel-content">
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
                  <el-button size="small"
                    :type="displayedCycles.length === 1 && displayedCycles[0] === index ? 'success' : 'primary'"
                    @click="highlightCycle(index)" style="margin-top: 10px">
                    {{ displayedCycles.length === 1 && displayedCycles[0] === index ? '✓ 已显示此环路' : '单独显示此环路' }}
                  </el-button>
                  <el-button v-if="displayedCycles.length === 1 && displayedCycles[0] === index" size="small"
                    type="info" plain @click="buildGraphFromCycles(cycleList)"
                    style="margin-top: 10px; margin-left: 10px">
                    显示所有环路
                  </el-button>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </div>
      </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, DataAnalysis, PieChart, RefreshRight, Download, Box, Operation, Plus, Delete, Connection, Edit, ArrowDown
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
const contextMenuTarget = ref(null) // { type: 'node'|'edge'|'blank', data: ... }
const quickInsertDialogVisible = ref(false)
const quickEdgeDialogVisible = ref(false)
const quickInsertPosition = ref({ x: 0, y: 0 })
const selectedNodesForEdge = ref([]) // 用于Shift+点击选择两个节点连边
const isShiftKeyPressed = ref(false) // 跟踪Shift键状态
const cycleDrawerHeight = ref(250) // 环路面板高度
const cycleDrawerCollapsed = ref(false) // 环路面板是否折叠
const quickInsertVertexForm = reactive({
  vType: 'account',
  balance: 0
})
const quickInsertEdgeForm = reactive({
  srcVid: null,
  dstVid: null,
  eid: null,
  amount: 1000,
  eType: '+',
  occurTime: null
})

// 编辑对话框相关状态
const editDialogVisible = ref(false)
const editType = ref('') // 'vertex' or 'edge'
const editForm = reactive({
  // 节点编辑字段
  vid: '',
  vType: '',
  balance: '',
  // 边编辑字段
  eid: '',
  srcVid: '',
  dstVid: '',
  eType: '',
  amount: '',
  occurTime: null // Date对象（毫秒时间戳）
})
const originalEditData = ref(null) // 保存原始数据用于对比

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
  if (!edges || edges.length === 0) {
    ElMessage.warning('没有找到匹配的边')
    clearGraph()
    return
  }

  // 收集所有涉及的点ID
  const vidSet = new Set()
  edges.forEach(e => {
    vidSet.add(e.src_vid)
    vidSet.add(e.dst_vid)
  })

  ElMessage.info(`正在查询 ${vidSet.size} 个相关节点...`)

  // 批量查询这些点的详细信息
  const nodes = []
  let successCount = 0
  
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
          rawData: v
        })
        successCount++
      } else {
        // 点不存在，创建占位节点
        nodes.push({
          id: vid.toString(),
          name: `V${vid}`,
          value: 0,
          category: 'unknown',
          symbolSize: 40,
          rawData: { vid, v_type: 'unknown', balance: 0, create_time: null }
        })
      }
    } catch (error) {
      console.error(`查询点 ${vid} 失败:`, error)
      // 创建默认节点
      nodes.push({
        id: vid.toString(),
        name: `V${vid}`,
        value: 0,
        category: 'unknown',
        symbolSize: 40,
        rawData: { vid, v_type: 'unknown', balance: 0, create_time: null }
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
      width: Math.max(1, Math.min(5, e.amount / 5000)),
      color: 'source'
    },
    rawData: e
  }))

  hasGraphData.value = true
  renderGraph()
  
  ElMessage.success(`显示 ${edges.length} 条边，${successCount} 个节点`)
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
        trigger: 'item',
        triggerOn: 'click', // 改为点击触发
        formatter: function (params) {
          // 如果按住Shift键，不显示tooltip
          if (isShiftKeyPressed.value) {
            return ''
          }
          
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
        edgeLabel: {
          show: graphData.links.length > 0 && graphData.links.length <= 50,
          fontSize: 11,
          position: 'middle',
          formatter: (params) => {
            const amount = params.data.value || params.data.rawData?.amount || 0
            return amount.toLocaleString()
          },
          color: '#666',
          backgroundColor: 'rgba(255, 255, 255, 0.8)',
          padding: [2, 4],
          borderRadius: 2
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
    chartInstance.off('contextmenu')

    // 添加双击事件监听（空白处插入节点）
    chartInstance.on('dblclick', handleChartDblClick)

    // 添加右键菜单事件监听
    chartInstance.on('contextmenu', handleChartRightClick)

    // 添加点击事件监听（用于Shift+点击选择节点）
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

// 拖拽调整环路面板大小
const startResizeCycleDrawer = (e) => {
  e.preventDefault()
  e.stopPropagation()
  
  const startY = e.clientY
  const startHeight = cycleDrawerHeight.value

  const onMouseMove = (moveEvent) => {
    const deltaY = startY - moveEvent.clientY // 注意：向上拖动增加高度
    const newHeight = Math.max(32, Math.min(600, startHeight + deltaY))
    cycleDrawerHeight.value = newHeight
    
    // 如果高度小于50px，自动折叠
    if (newHeight < 50) {
      cycleDrawerCollapsed.value = true
    } else {
      cycleDrawerCollapsed.value = false
    }
  }

  const onMouseUp = () => {
    document.removeEventListener('mousemove', onMouseMove)
    document.removeEventListener('mouseup', onMouseUp)
  }

  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
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
  console.log('双击事件:', params)
  
  // 双击空白处，显示插入节点对话框
  if (!params.componentType || params.componentType !== 'series') {
    console.log('双击空白处，显示插入对话框')
    quickInsertDialogVisible.value = true
    quickInsertVertexForm.vType = 'account'
    quickInsertVertexForm.balance = 0
  }
}

// 处理图表右键菜单事件
const handleChartRightClick = (params) => {
  console.log('右键事件:', params)
  
  // 阻止浏览器默认右键菜单
  if (params.event && params.event.event) {
    params.event.event.preventDefault()
  }

  if (params.componentType === 'series') {
    if (params.dataType === 'node') {
      // 右键节点，显示删除菜单
      console.log('右键节点:', params.data)
      contextMenuTarget.value = {
        type: 'node',
        data: params.data
      }
      showContextMenu(params.event.event)
    } else if (params.dataType === 'edge') {
      // 右键边，显示删除菜单
      console.log('右键边:', params.data)
      contextMenuTarget.value = {
        type: 'edge',
        data: params.data
      }
      showContextMenu(params.event.event)
    }
  } else {
    // 右键空白处，显示插入节点菜单
    console.log('右键空白处')
    contextMenuTarget.value = {
      type: 'blank',
      data: null
    }
    showContextMenu(params.event.event)
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

// 打开编辑对话框
const openEditDialog = (type) => {
  if (!contextMenuTarget.value) return

  editType.value = type
  const data = contextMenuTarget.value.data

  if (type === 'vertex') {
    // 编辑节点
    const raw = data.rawData || {}
    editForm.vid = (raw.vid || data.id).toString()
    editForm.vType = raw.v_type || data.category || ''
    editForm.balance = (raw.balance !== undefined ? raw.balance : data.value).toString()
    
    // 保存原始数据
    originalEditData.value = {
      vType: editForm.vType,
      balance: editForm.balance
    }
  } else if (type === 'edge') {
    // 编辑边
    const raw = data.rawData || {}
    editForm.eid = (raw.eid || '').toString()
    editForm.srcVid = (raw.src_vid || data.source || '').toString()
    editForm.dstVid = (raw.dst_vid || data.target || '').toString()
    editForm.eType = raw.e_type || data.label || ''
    editForm.amount = (raw.amount !== undefined ? raw.amount : data.value || '').toString()
    // 将时间戳转换为毫秒（如果是秒级时间戳）
    const timestamp = raw.occur_time || 0
    editForm.occurTime = timestamp ? (timestamp < 10000000000 ? timestamp * 1000 : timestamp) : null
    
    // 保存原始数据
    originalEditData.value = {
      eType: editForm.eType,
      amount: editForm.amount,
      occurTime: editForm.occurTime
    }
  }

  hideContextMenu()
  editDialogVisible.value = true
}

// 重置编辑表单
const resetEditForm = () => {
  editForm.vid = ''
  editForm.vType = ''
  editForm.balance = ''
  editForm.eid = ''
  editForm.srcVid = ''
  editForm.dstVid = ''
  editForm.eType = ''
  editForm.amount = ''
  editForm.occurTime = null
  originalEditData.value = null
}

// 处理更新操作
const handleUpdate = async () => {
  if (editType.value === 'vertex') {
    await updateVertex()
  } else if (editType.value === 'edge') {
    await updateEdge()
  }
}

// 更新节点
const updateVertex = async () => {
  const vid = editForm.vid
  if (!vid) {
    ElMessage.warning('点ID不能为空')
    return
  }

  // 检测哪些字段被修改了
  const changes = []
  const command = ['update', 'vertex', '--vid', vid]

  if (editForm.vType !== originalEditData.value.vType && editForm.vType.trim()) {
    command.push('--vt', editForm.vType.trim())
    changes.push('点类型')
  }

  if (editForm.balance !== originalEditData.value.balance && editForm.balance.trim()) {
    const balance = parseFloat(editForm.balance)
    if (isNaN(balance) || balance < 0) {
      ElMessage.warning('余额必须是非负数')
      return
    }
    command.push('--bal', balance.toString())
    changes.push('余额')
  }

  if (changes.length === 0) {
    ElMessage.info('没有检测到任何修改')
    return
  }

  loading.value = true
  try {
    console.log('执行更新命令:', command)
    const response = await executeCommand(command)
    console.log('更新响应:', response)

    if (response.status === 'success') {
      ElMessage.success(`节点更新成功，已更新: ${changes.join('、')}`)
      editDialogVisible.value = false
      resetEditForm()

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
      ElMessage.error('更新失败: ' + (response.message || '未知错误'))
    }
  } catch (error) {
    console.error('更新节点错误:', error)
    ElMessage.error('更新失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

// 更新边
const updateEdge = async () => {
  const eid = editForm.eid
  if (!eid) {
    ElMessage.warning('边ID不能为空')
    return
  }

  // 检测哪些字段被修改了
  const changes = []
  const command = ['update', 'edge', '--eid', eid]

  if (editForm.eType !== originalEditData.value.eType && editForm.eType.trim()) {
    command.push('--et', editForm.eType.trim())
    changes.push('边类型')
  }

  if (editForm.amount !== originalEditData.value.amount && editForm.amount.trim()) {
    const amount = parseFloat(editForm.amount)
    if (isNaN(amount) || amount < 0) {
      ElMessage.warning('金额必须是非负数')
      return
    }
    command.push('--amt', amount.toString())
    changes.push('金额')
  }

  if (editForm.occurTime !== originalEditData.value.occurTime && editForm.occurTime) {
    // 将毫秒时间戳转换为秒级时间戳
    const timestamp = Math.floor(editForm.occurTime / 1000)
    command.push('--time', timestamp.toString())
    changes.push('发生时间')
  }

  if (changes.length === 0) {
    ElMessage.info('没有检测到任何修改')
    return
  }

  loading.value = true
  try {
    console.log('执行更新命令:', command)
    const response = await executeCommand(command)
    console.log('更新响应:', response)

    if (response.status === 'success') {
      ElMessage.success(`边更新成功，已更新: ${changes.join('、')}`)
      editDialogVisible.value = false
      resetEditForm()

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
      ElMessage.error('更新失败: ' + (response.message || '未知错误'))
    }
  } catch (error) {
    console.error('更新边错误:', error)
    ElMessage.error('更新失败: ' + (error.message || '未知错误'))
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

    console.log('执行快速插入命令:', command)
    const response = await executeCommand(command)
    console.log('插入响应:', response)

    if (response.status === 'success') {
      ElMessage.success(`点插入成功: ID=${response.data?.vid || '自动生成'}`)
      quickInsertDialogVisible.value = false

      // 重置表单
      quickInsertVertexForm.vType = 'account'
      quickInsertVertexForm.balance = 0

      // 刷新当前视图
      if (activeTab.value === 'fullGraph') {
        await queryFullGraph()
      } else {
        // 如果不在全图视图，也刷新全图以确保数据最新
        await queryFullGraph()
      }
    } else {
      ElMessage.error('插入失败: ' + (response.message || '未知错误'))
    }
  } catch (error) {
    console.error('快速插入节点错误:', error)
    ElMessage.error('插入失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

// 处理左键点击显示tooltip和自动填充ID
const handleNodeClick = (params) => {
  console.log('点击事件:', params)
  console.log('是否按住Shift:', params.event?.shiftKey)
  console.log('数据类型:', params.dataType)
  
  // ECharts click 事件: params.event.event 是原始DOM事件
  const isShiftPressed = params.event?.event?.shiftKey || params.event?.shiftKey
  
  if (isShiftPressed && params.dataType === 'node') {
    // Shift+点击节点：选择节点用于连边，不显示tooltip
    console.log('Shift+点击节点:', params.data)
    
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
  } else if (!isShiftPressed && (params.dataType === 'node' || params.dataType === 'edge')) {
    // 普通左键点击：显示tooltip并自动填充ID
    console.log('左键点击显示tooltip:', params.data)
    
    // 自动填充左侧表单的ID字段
    autoFillFormIds(params)
  }
}

// 自动填充左侧表单的ID字段
const autoFillFormIds = (params) => {
  if (params.dataType === 'node') {
    const vid = parseInt(params.data.rawData?.vid || params.data.id)
    
    // 根据当前激活的tab自动填充
    if (mainTab.value === 'query') {
      if (activeTab.value === 'vertex' && !vertexForm.vid) {
        vertexForm.vid = vid
        ElMessage.success(`已自动填充点ID: ${vid}`)
      } else if (activeTab.value === 'edge') {
        if (!edgeForm.srcVid) {
          edgeForm.srcVid = vid
          ElMessage.success(`已自动填充源点ID: ${vid}`)
        } else if (!edgeForm.dstVid) {
          edgeForm.dstVid = vid
          ElMessage.success(`已自动填充目标点ID: ${vid}`)
        }
      } else if (activeTab.value === 'cycle' && !cycleForm.startVid) {
        cycleForm.startVid = vid
        ElMessage.success(`已自动填充起始点ID: ${vid}`)
      }
    } else if (mainTab.value === 'modify') {
      if (modifyTab.value === 'insertEdge') {
        if (!insertEdgeForm.srcVid) {
          insertEdgeForm.srcVid = vid
          ElMessage.success(`已自动填充源点ID: ${vid}`)
        } else if (!insertEdgeForm.dstVid) {
          insertEdgeForm.dstVid = vid
          ElMessage.success(`已自动填充目标点ID: ${vid}`)
        }
      } else if (modifyTab.value === 'deleteVertex' && !deleteVertexForm.vid) {
        deleteVertexForm.vid = vid
        ElMessage.success(`已自动填充点ID: ${vid}`)
      }
    }
  } else if (params.dataType === 'edge') {
    const eid = params.data.rawData?.eid
    
    if (eid) {
      // 根据当前激活的tab自动填充
      if (mainTab.value === 'query' && activeTab.value === 'edge' && !edgeForm.eid) {
        edgeForm.eid = eid
        ElMessage.success(`已自动填充边ID: ${eid}`)
      } else if (mainTab.value === 'modify' && modifyTab.value === 'deleteEdge' && !deleteEdgeForm.eid) {
        deleteEdgeForm.eid = eid
        ElMessage.success(`已自动填充边ID: ${eid}`)
      }
    }
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

// 显示快速插入节点对话框
const showQuickInsertDialog = () => {
  hideContextMenu()
  quickInsertDialogVisible.value = true
  quickInsertVertexForm.vType = 'account'
  quickInsertVertexForm.balance = 0
}

// 显示快速连边对话框
const showQuickEdgeDialog = () => {
  // 填充源点和目标点ID
  quickInsertEdgeForm.srcVid = parseInt(selectedNodesForEdge.value[0])
  quickInsertEdgeForm.dstVid = parseInt(selectedNodesForEdge.value[1])
  quickInsertEdgeForm.eid = null
  quickInsertEdgeForm.amount = 1000
  quickInsertEdgeForm.eType = '+'
  quickInsertEdgeForm.occurTime = null
  
  quickEdgeDialogVisible.value = true
}

// 取消快速连边
const cancelQuickEdge = () => {
  quickEdgeDialogVisible.value = false
  selectedNodesForEdge.value = []
  updateNodeSelection()
}

// 确认快速连边
const confirmQuickEdge = async () => {
  if (!quickInsertEdgeForm.amount || quickInsertEdgeForm.amount < 0) {
    ElMessage.warning('请输入有效的交易金额')
    return
  }

  loading.value = true
  try {
    const command = [
      'insert', 'edge',
      '--src', quickInsertEdgeForm.srcVid.toString(),
      '--dst', quickInsertEdgeForm.dstVid.toString(),
      '--amt', quickInsertEdgeForm.amount.toString()
    ]

    if (quickInsertEdgeForm.eid) command.push('--eid', quickInsertEdgeForm.eid.toString())
    if (quickInsertEdgeForm.eType && quickInsertEdgeForm.eType.trim()) {
      command.push('--et', quickInsertEdgeForm.eType.trim())
    }
    if (quickInsertEdgeForm.occurTime) {
      const timestamp = Math.floor(quickInsertEdgeForm.occurTime.getTime() / 1000)
      command.push('--time', timestamp.toString())
    }

    console.log('执行快速连边命令:', command)
    const response = await executeCommand(command)

    if (response.status === 'success') {
      ElMessage.success(`边创建成功: ${quickInsertEdgeForm.srcVid} → ${quickInsertEdgeForm.dstVid}`)
      quickEdgeDialogVisible.value = false
      selectedNodesForEdge.value = []
      // 刷新全图
      await queryFullGraph()
    } else {
      ElMessage.error('创建边失败: ' + (response.message || '未知错误'))
    }
  } catch (error) {
    console.error('快速连边错误:', error)
    ElMessage.error('创建边失败: ' + (error.message || '未知错误'))
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

  // 监听Shift键状态
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Shift') {
      isShiftKeyPressed.value = true
    }
  })
  
  window.addEventListener('keyup', (e) => {
    if (e.key === 'Shift') {
      isShiftKeyPressed.value = false
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
  height: calc(100vh - 140px);
  overflow: hidden;
}

.graph-query :deep(.el-row) {
  height: 100%;
}

.graph-query :deep(.el-col) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.operation-panel {
  border-radius: 12px;
  height: 100%;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.operation-panel :deep(.el-card) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.operation-panel :deep(.el-card__body) {
  flex: 1;
  overflow-y: auto;
}

.visualization-panel {
  border-radius: 12px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.visualization-panel :deep(.el-card) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.visualization-panel :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 12px;
}

.result-stats {
  border-radius: 12px;
  margin-top: 16px;
  margin-bottom: 16px;
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
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  min-height: 400px;
}

/* 底部环路面板 */
.cycle-bottom-panel {
  position: relative;
  background: white;
  border-radius: 12px;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.1);
  margin-top: 8px;
  overflow: hidden;
  transition: height 0.3s ease;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.cycle-bottom-panel.collapsed {
  height: 32px !important;
}

.cycle-panel-header {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eaf6 100%);
  border-bottom: 1px solid #e4e7ed;
  cursor: pointer;
  user-select: none;
  height: 32px;
  flex-shrink: 0;
}

.cycle-panel-header:hover {
  background: linear-gradient(135deg, #e8eaf6 0%, #dce0f5 100%);
}

.cycle-panel-resizer {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 6px;
  background: linear-gradient(to bottom, rgba(102, 126, 234, 0.15), transparent);
  cursor: ns-resize;
  transition: background 0.2s;
  z-index: 10;
}

.cycle-panel-resizer:hover {
  background: linear-gradient(to bottom, rgba(102, 126, 234, 0.3), transparent);
}

.cycle-panel-resizer:active {
  background: rgba(102, 126, 234, 0.5);
}

.cycle-panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 12px 16px;
}

.cycle-panel-content .el-collapse {
  border: none;
}

.cycle-panel-content .el-collapse-item__header {
  background: #f9fafc;
  padding: 8px 12px;
  border-radius: 6px;
  margin-bottom: 8px;
}

.cycle-panel-content .el-collapse-item__wrap {
  border: none;
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

/* 右键菜单浮动窗口样式 */
.context-menu-card {
  position: fixed;
  z-index: 99999 !important;
  min-width: 180px;
  max-width: 250px;
  user-select: none;
}

.context-menu-card :deep(.el-card__header) {
  padding: 12px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-bottom: none;
}

.context-menu-header {
  font-size: 14px;
  font-weight: 600;
  color: white;
  text-align: center;
}

.context-menu-card :deep(.el-card__body) {
  padding: 8px 0;
}

.context-menu-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  color: #606266;
  border-radius: 4px;
  margin: 0 8px;
}

.menu-item:hover {
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eaf6 100%);
  color: #303133;
  transform: translateX(4px);
}

.menu-item .el-icon {
  font-size: 18px;
  transition: transform 0.2s ease;
}

.menu-item:hover .el-icon {
  transform: scale(1.2);
}

/* 右键菜单动画 */
.context-menu-fade-enter-active,
.context-menu-fade-leave-active {
  transition: all 0.3s ease;
}

.context-menu-fade-enter-from {
  opacity: 0;
  transform: scale(0.9) translateY(-10px);
}

.context-menu-fade-leave-to {
  opacity: 0;
  transform: scale(0.9) translateY(10px);
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
