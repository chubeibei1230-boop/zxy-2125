<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">任务详情</span>
      <el-button @click="router.back()">
        <el-icon><Back /></el-icon>
        返回
      </el-button>
    </div>

    <div v-loading="loading" v-if="task">
      <el-row :gutter="20">
        <el-col :span="16">
          <el-card class="mb-20">
            <template #header>
              <div class="card-header">
                <span>基本信息</span>
                <span :class="['status-tag', `status-${task.status}`]">{{ task.status_display }}</span>
              </div>
            </template>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="任务标题">{{ task.title }}</el-descriptions-item>
              <el-descriptions-item label="所属项目">{{ task.project_name }}</el-descriptions-item>
              <el-descriptions-item label="工位">{{ task.station_name }}</el-descriptions-item>
              <el-descriptions-item label="任务模板">{{ task.template_name }}</el-descriptions-item>
              <el-descriptions-item label="执行者">{{ task.executor_name }}</el-descriptions-item>
              <el-descriptions-item label="复核者">{{ task.reviewer_name }}</el-descriptions-item>
              <el-descriptions-item label="计划时间">{{ formatDate(task.scheduled_time) }}</el-descriptions-item>
              <el-descriptions-item label="创建时间">{{ formatDate(task.created_at) }}</el-descriptions-item>
            </el-descriptions>
          </el-card>

          <el-card class="mb-20" v-if="task.preparation">
            <template #header>
              <span>准备记录</span>
            </template>
            <div class="record-content">
              <p style="margin-bottom: 10px;">
                <strong>填写人：</strong>{{ task.preparation.operator_name }}
                <span style="margin-left: 20px; color: #909399;">{{ formatDate(task.preparation.created_at) }}</span>
              </p>
              <pre style="white-space: pre-wrap; background: #f5f7fa; padding: 15px; border-radius: 4px; margin: 0;">{{ task.preparation.content }}</pre>
            </div>
          </el-card>

          <el-card class="mb-20" v-if="task.reception">
            <template #header>
              <span>接待记录</span>
            </template>
            <div class="record-content">
              <p style="margin-bottom: 10px;">
                <strong>填写人：</strong>{{ task.reception.operator_name }}
                <span style="margin-left: 20px; color: #909399;">{{ formatDate(task.reception.created_at) }}</span>
              </p>
              <pre style="white-space: pre-wrap; background: #f5f7fa; padding: 15px; border-radius: 4px; margin: 0;">{{ task.reception.content }}</pre>
            </div>
          </el-card>

          <el-card class="mb-20" v-if="task.closing">
            <template #header>
              <div class="card-header">
                <span>收尾记录</span>
                <el-tag v-if="task.closing.has_exception" type="danger">有异常</el-tag>
              </div>
            </template>
            <div class="record-content">
              <p style="margin-bottom: 10px;">
                <strong>填写人：</strong>{{ task.closing.operator_name }}
                <span style="margin-left: 20px; color: #909399;">{{ formatDate(task.closing.created_at) }}</span>
              </p>
              <pre style="white-space: pre-wrap; background: #f5f7fa; padding: 15px; border-radius: 4px; margin: 0 0 10px 0;">{{ task.closing.content }}</pre>
              <div v-if="task.closing.has_exception" style="background: #fef0f0; padding: 15px; border-radius: 4px;">
                <p style="margin-bottom: 5px;"><strong style="color: #f56c6c;">异常描述：</strong></p>
                <p>{{ task.closing.exception_description }}</p>
              </div>
            </div>
          </el-card>

          <el-card v-if="task.exception_handlings && task.exception_handlings.length > 0" class="mb-20">
            <template #header>
              <span>异常处理记录</span>
            </template>
            <div v-for="(item, index) in task.exception_handlings" :key="item.id" class="exception-item">
              <p style="margin-bottom: 10px;">
                <strong>复核人：</strong>{{ item.reviewer_name }}
                <span style="margin-left: 20px; color: #909399;">{{ formatDate(item.created_at) }}</span>
              </p>
              <pre style="white-space: pre-wrap; background: #f0f9eb; padding: 15px; border-radius: 4px; margin: 0;">{{ item.handling_content }}</pre>
            </div>
          </el-card>

          <el-card v-if="task.rectification_records && task.rectification_records.length > 0">
            <template #header>
              <span>整改历史记录</span>
            </template>
            <div v-for="(item, index) in task.rectification_records" :key="item.id" class="rectification-item">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <div>
                  <el-tag :type="item.status === 'pending' ? 'warning' : item.status === 'rectified' ? 'primary' : 'success'" size="small">
                    {{ item.status_display }}
                  </el-tag>
                  <span style="margin-left: 10px; font-weight: bold;">{{ item.stage_display }}</span>
                </div>
                <span style="color: #909399; font-size: 12px;">创建时间：{{ formatDate(item.created_at) }}</span>
              </div>
              <div style="background: #fff7e6; padding: 12px; border-radius: 4px; margin-bottom: 10px;">
                <p style="margin-bottom: 5px;"><strong style="color: #fa8c16;">整改意见（{{ item.reviewer_name }}）：</strong></p>
                <p style="white-space: pre-wrap; margin: 0;">{{ item.rectification_content }}</p>
              </div>
              <div v-if="item.rectification_note" style="background: #e6f7ff; padding: 12px; border-radius: 4px;">
                <p style="margin-bottom: 5px;"><strong style="color: #1890ff;">整改说明（{{ item.executor_name }}）：</strong></p>
                <p style="white-space: pre-wrap; margin: 0;">{{ item.rectification_note }}</p>
                <p v-if="item.rectified_at" style="margin-top: 5px; color: #909399; font-size: 12px;">整改时间：{{ formatDate(item.rectified_at) }}</p>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card class="mb-20">
            <template #header>
              <span>状态流转</span>
            </template>
            <div class="flow-actions" style="margin-bottom: 20px;">
              <el-alert 
                v-if="getTransitionHint" 
                :title="getTransitionHint" 
                type="warning" 
                :closable="false"
                style="margin-bottom: 10px;"
                size="small"
              />
              <el-select 
                v-model="newStatus" 
                placeholder="选择目标状态" 
                style="width: 100%; margin-bottom: 10px;">
                <el-option 
                  v-for="status in availableTransitions" 
                  :key="status.value" 
                  :label="status.label" 
                  :value="status.value" 
                />
              </el-select>
              <el-input v-model="transitionRemark" placeholder="备注（可选）" style="margin-bottom: 10px;" type="textarea" :rows="2" />
              <el-button 
                type="primary" 
                style="width: 100%;" 
                :disabled="!newStatus || getTransitionHint"
                @click="handleTransition"
              >
                状态流转
              </el-button>
            </div>
            <el-timeline>
              <el-timeline-item
                v-for="record in task.flow_records"
                :key="record.id"
                :timestamp="formatDate(record.created_at)"
              >
                <div>
                  <span :class="['status-tag', `status-${record.old_status}`]" style="margin-right: 5px;">{{ record.old_status_display }}</span>
                  <el-icon><ArrowRight /></el-icon>
                  <span :class="['status-tag', `status-${record.new_status}`]" style="margin-left: 5px;">{{ record.new_status_display }}</span>
                </div>
                <p style="font-size: 12px; color: #909399; margin-top: 5px;">
                  操作人：{{ record.operator_name }}
                </p>
                <p v-if="record.remark" style="font-size: 12px; color: #606266; margin-top: 5px;">
                  备注：{{ record.remark }}
                </p>
              </el-timeline-item>
              <el-timeline-item
                :timestamp="formatDate(task.created_at)"
                placement="top"
                type="primary"
              >
                任务创建
              </el-timeline-item>
            </el-timeline>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { taskApi } from '@/api'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const task = ref(null)
const newStatus = ref('')
const transitionRemark = ref('')

const statusTransitionMap = {
  'pending_prep': [
    { value: 'in_progress', label: '开始执行（进行中）', roles: ['manager', 'executor'] },
    { value: 'cancelled', label: '取消任务', roles: ['manager'] }
  ],
  'in_progress': [
    { value: 'pending_review', label: '提交复核', roles: ['manager', 'executor'], requireRecords: true },
    { value: 'cancelled', label: '取消任务', roles: ['manager'] }
  ],
  'pending_review': [
    { value: 'completed', label: '复核通过（已完成）', roles: ['manager', 'reviewer'], requireRecords: true },
    { value: 'rectification_pending', label: '发起整改（待整改）', roles: ['manager', 'reviewer'] }
  ],
  'rectification_pending': [
    { value: 'rectified_pending_review', label: '提交整改（已整改待复核）', roles: ['manager', 'executor'] }
  ],
  'rectified_pending_review': [
    { value: 'completed', label: '复核通过（已完成）', roles: ['manager', 'reviewer'], requireRecords: true },
    { value: 'rectification_pending', label: '再次发起整改', roles: ['manager', 'reviewer'] }
  ],
  'completed': [],
  'cancelled': []
}

const availableTransitions = computed(() => {
  if (!task.value) return []
  const allTransitions = statusTransitionMap[task.value.status] || []
  return allTransitions.filter(t => {
    if (t.roles && !t.roles.includes(userStore.userRole)) {
      return false
    }
    return true
  })
})

const getTransitionHint = computed(() => {
  if (!task.value) return ''
  const status = task.value.status
  if (status === 'in_progress') {
    const missing = []
    if (!task.value.preparation) missing.push('准备记录')
    if (!task.value.reception) missing.push('接待记录')
    if (!task.value.closing) missing.push('收尾记录')
    if (missing.length > 0) {
      return `提交复核前需先填写：${missing.join('、')}`
    }
  }
  if (status === 'pending_review' && task.value.closing?.has_exception) {
    if (!task.value.exception_handlings || task.value.exception_handlings.length === 0) {
      return '该任务存在异常，需先填写异常处理意见'
    }
  }
  return ''
})

const loadData = async () => {
  loading.value = true
  try {
    task.value = await taskApi.detail(route.params.id)
  } finally {
    loading.value = false
  }
}

const handleTransition = async () => {
  if (!newStatus.value) return
  
  try {
    await taskApi.transition(task.value.id, {
      new_status: newStatus.value,
      remark: transitionRemark.value
    })
    ElMessage.success('状态流转成功')
    newStatus.value = ''
    transitionRemark.value = ''
    loadData()
  } catch (error) {
  }
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
.mb-20 {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.exception-item {
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}

.exception-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.rectification-item {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

.rectification-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}
</style>
