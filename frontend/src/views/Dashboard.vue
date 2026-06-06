<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6" v-for="stat in stats" :key="stat.label">
        <el-card class="stat-card" :class="{ 'clickable': stat.action }" @click="stat.action && stat.action()">
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
            <div class="card-header">
              <span>最近任务</span>
              <el-button type="primary" link @click="$router.push('/tasks')">查看全部</el-button>
            </div>
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
            <div class="card-header">
              <span>最近复盘问题</span>
              <el-button type="primary" link @click="$router.push('/reviews')">查看全部</el-button>
            </div>
          </template>
          <div v-if="!recentReviews || recentReviews.length === 0" style="text-align: center; padding: 40px 0; color: #909399;">
            暂无复盘记录
          </div>
          <div v-else>
            <div 
              v-for="item in recentReviews" 
              :key="item.id" 
              class="review-item"
              @click="$router.push(`/tasks/${item.task}`)"
            >
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: 500; color: #303133;">{{ item.task_title }}</span>
                <div style="display: flex; gap: 4px;">
                  <el-tag v-if="item.is_overdue" type="danger" size="small">已逾期</el-tag>
                  <el-tag :type="getFollowupStatusType(item.followup_status, item.is_overdue)" size="small">
                    {{ item.followup_status_display }}
                  </el-tag>
                </div>
              </div>
              <div style="display: flex; gap: 10px; margin-bottom: 8px;">
                <el-tag size="small" type="info">{{ item.problem_type_display }}</el-tag>
                <span style="color: #909399; font-size: 12px;">{{ item.responsibility_stage_display }}</span>
              </div>
              <p style="color: #606266; font-size: 13px; margin: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                {{ item.conclusion }}
              </p>
              <div style="text-align: right; margin-top: 8px;">
                <span style="color: #909399; font-size: 12px;">{{ formatDate(item.created_at) }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
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
import { useRouter } from 'vue-router'
import { taskApi, taskReviewApi } from '@/api'
import { 
  List, Clock, Check, Warning, 
  DataAnalysis, Files, CircleCheck, Timer,
  DocumentCopy, Bell
} from '@element-plus/icons-vue'

const router = useRouter()
const tasks = ref([])
const reviewStats = ref({})
const recentReviews = ref([])

const loadData = async () => {
  try {
    tasks.value = await taskApi.myTasks()
    reviewStats.value = await taskReviewApi.stats()
    const reviews = await taskReviewApi.myReviews()
    recentReviews.value = Array.isArray(reviews) ? reviews.slice(0, 5) : []
  } catch (error) {
    console.error('加载数据失败', error)
  }
}

const stats = computed(() => {
  const total = tasks.value.length
  const pending = tasks.value.filter(t => t.status === 'pending_prep').length
  const inProgress = tasks.value.filter(t => t.status === 'in_progress').length
  const completed = tasks.value.filter(t => t.status === 'completed').length
  
  const result = [
    { label: '任务总数', value: total, icon: List, color: '#409eff' },
    { label: '待准备', value: pending, icon: Clock, color: '#e6a23c' },
    { label: '进行中', value: inProgress, icon: Timer, color: '#67c23a' },
    { label: '已完成', value: completed, icon: Check, color: '#909399' }
  ]
  
  if (reviewStats.value && reviewStats.value.pending !== undefined) {
    result.push(
      { 
        label: '复盘待处理', 
        value: reviewStats.value.pending_feedback || reviewStats.value.pending, 
        icon: Bell, 
        color: '#e6a23c',
        action: () => router.push('/reviews')
      }
    )
    if (reviewStats.value.overdue > 0) {
      result.push(
        { 
          label: '复盘已逾期', 
          value: reviewStats.value.overdue, 
          icon: Warning, 
          color: '#f56c6c',
          action: () => router.push('/reviews?is_overdue=true')
        }
      )
    }
  }
  
  return result
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

const getFollowupStatusType = (status, isOverdue) => {
  if (isOverdue) {
    return 'danger'
  }
  const typeMap = {
    'pending': 'warning',
    'processing': 'primary',
    'completed': 'success',
    'closed': 'info'
  }
  return typeMap[status] || 'info'
}

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

.stat-card.clickable {
  cursor: pointer;
  transition: all 0.3s;
}

.stat-card.clickable:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.review-item {
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
  cursor: pointer;
  transition: background-color 0.3s;
}

.review-item:hover {
  background-color: #f5f7fa;
}

.review-item:last-child {
  border-bottom: none;
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
