<template>
  <div class="home">
    <el-card class="welcome-card">
      <h1>欢迎使用 CycleGraph</h1>
      <p class="description">
        专业的图数据库环路检测系统，支持复杂的图结构分析、路径查询和环路检测。
      </p>
      <div class="features">
        <el-row :gutter="24">
          <el-col :span="6">
            <el-card shadow="hover" class="feature-card">
              <template #header>
                <div class="feature-header">
                  <el-icon :size="32" color="#667eea"><Histogram /></el-icon>
                  <span>点查询</span>
                </div>
              </template>
              <p>查询图中的节点，支持多维度过滤条件</p>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="feature-card">
              <template #header>
                <div class="feature-header">
                  <el-icon :size="32" color="#667eea"><Connection /></el-icon>
                  <span>边查询</span>
                </div>
              </template>
              <p>查询节点之间的关系边，分析数据流向</p>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="feature-card">
              <template #header>
                <div class="feature-header">
                  <el-icon :size="32" color="#667eea"><Refresh /></el-icon>
                  <span>环路检测</span>
                </div>
              </template>
              <p>检测图中的环路结构，支持时序分析</p>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="feature-card">
              <template #header>
                <div class="feature-header">
                  <el-icon :size="32" color="#667eea"><DataAnalysis /></el-icon>
                  <span>图可视化</span>
                </div>
              </template>
              <p>直观展示图结构，支持节点拖动交互</p>
            </el-card>
          </el-col>
        </el-row>
      </div>
      <div class="action-buttons">
        <el-button type="primary" size="large" @click="goToQuery">
          <el-icon><Promotion /></el-icon>
          <span>开始查询</span>
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { Histogram, Connection, Refresh, DataAnalysis, Promotion } from '@element-plus/icons-vue'

const router = useRouter()

const goToQuery = () => {
  router.push('/query')
}
</script>

<style scoped>
.home {
  padding: 20px;
}

.welcome-card {
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
}

h1 {
  font-size: 2.5em;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 20px;
  font-weight: 700;
}

.description {
  font-size: 1.1em;
  color: #606266;
  margin-bottom: 50px;
  line-height: 1.6;
}

.features {
  margin: 50px 0;
}

.feature-card {
  height: 180px;
  transition: all 0.3s;
  border-radius: 12px;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.2);
}

.feature-card .el-card__header {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  border-bottom: 2px solid rgba(102, 126, 234, 0.1);
}

.feature-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  font-weight: 600;
  font-size: 16px;
  color: #333;
}

.feature-card p {
  text-align: center;
  color: #666;
  line-height: 1.6;
  font-size: 14px;
  margin-top: 10px;
}

.action-buttons {
  margin-top: 50px;
}

.action-buttons .el-button {
  padding: 16px 48px;
  font-size: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
  transition: all 0.3s;
}

.action-buttons .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(102, 126, 234, 0.4);
}
</style>
