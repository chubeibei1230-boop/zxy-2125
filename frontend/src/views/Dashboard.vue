<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6" v-for="stat in stats" :key="stat.label">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" :style="{ backgroundColor: stat.color }">
              <el-icon :size="24"><component :is="stat.icon" /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>最近任务</span>
          </template>
          <el-table :data="recentTasks" style="width: 100%">
            <el-table-column prop="title" label="任务标题" />
            <el-table-column prop="status_display" label="状态">
              <template #default="{ row }">
                <span :class="['status-tag', `status-${row.status}`]">{{ row.status_display }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="scheduled_time" label="计划时间">
              <template #default="{ row }">
                {{ formatDate(row.scheduled_time) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>任务状态分布</span>
          </template>
          <div class="status-distribution">
            <div v-for="item in statusDistribution" :key="item.status" class="status-item">
              <span class="status-label">{{ item.label }}</span>
              <div class="status-bar">
                <div 
                  class="status-fill" 
                  :class="`status-${item.status}`"
                  :style="{ width: `${item.percentage}%` }"
                ></div>
              </div>
              <span class="status-count">{{ item.count }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { taskApi } from '@/api'
import { 
  List, Clock, Check, Warning, 
  DataAnalysis, Files, CircleCheck, Timer
} from '@element-plus/icons-vue'

const tasks = ref([])

const loadData = async () => {
  try {
    tasks.value = await taskApi.myTasks()
  } catch (error) {
    console.error('加载数据失败', error)
  }
}

const stats = computed(() => {
  const total = tasks.value.length
  const pending = tasks.value.filter(t => t.status === 'pending_prep').length
  const inProgress = tasks.value.filter(t => t.status === 'in_progress').length
  const completed = tasks.value.filter(t => t.status === 'completed').length
  
  return [
    { label: '任务总数', value: total, icon: List, color: '#409eff' },
    { label: '待准备', value: pending, icon: Clock, color: '#e6a23c' },
    { label: '进行中', value: inProgress, icon: Timer, color: '#67c23a' },
    { label: '已完成', value: completed, icon: Check, color: '#909399' }
  ]
})

const recentTasks = computed(() => {
  return tasks.value.slice(0, 5)
})

const statusDistribution = computed(() => {
  const statusMap = {
    'pending_prep': { label: '待准备', color: '#409eff' },
    'in_progress': { label: '进行中', color: '#e6a23c' },
    'pending_review': { label: '待复核', color: '#f56c6c' },
    'completed': { label: '已完成', color: '#67c23a' },
    'cancelled': { label: '已取消', color: '#909399' }
  }
  
  const total = tasks.value.length || 1
  
  return Object.entries(statusMap).map(([status, info]) => {
    const count = tasks.value.filter(t => t.status === status).length
    return {
      status,
      label: info.label,
      count,
      percentage: Math.round((count / total) * 100)
    }
  })
})

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.stat-card {
  margin-bottom: 20px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.status-distribution {
  padding: 10px 0;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.status-item:last-child {
  margin-bottom: 0;
}

.status-label {
  width: 60px;
  font-size: 14px;
  color: #606266;
}

.status-bar {
  flex: 1;
  height: 12px;
  background: #f0f2f5;
  border-radius: 6px;
  overflow: hidden;
}

.status-fill {
  height: 100%;
  border-radius: 6px;
  transition: width 0.3s;
}

.status-count {
  width: 40px;
  text-align: right;
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}
</style>
