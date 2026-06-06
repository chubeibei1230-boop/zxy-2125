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

          <el-card v-if="task.rectification_records && task.rectification_records.length > 0" class="mb-20">
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

          <el-card>
            <template #header>
              <div class="card-header">
                <span>复盘记录</span>
                <el-button 
                  type="primary" 
                  size="small" 
                  v-if="task.can_initiate_review"
                  @click="handleInitiateReview"
                >
                  <el-icon><Plus /></el-icon>
                  发起复盘
                </el-button>
              </div>
            </template>
            <div v-if="!task.reviews || task.reviews.length === 0" style="text-align: center; padding: 40px 0; color: #909399;">
              暂无复盘记录
            </div>
            <div v-for="(item, index) in task.reviews" :key="item.id" class="review-item">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <div>
                  <el-tag :type="getFollowupStatusType(item.followup_status)" size="small" style="margin-right: 10px;">
                    {{ item.followup_status_display }}
                  </el-tag>
                  <el-tag size="small" type="info">{{ item.problem_type_display }}</el-tag>
                  <span style="margin-left: 10px;">责任环节：{{ item.responsibility_stage_display }}</span>
                </div>
                <span style="color: #909399; font-size: 12px;">
                  发起人：{{ item.initiator_name }} | {{ formatDate(item.created_at) }}
                </span>
              </div>
              <div style="background: #f0f9eb; padding: 12px; border-radius: 4px; margin-bottom: 10px;">
                <p style="margin-bottom: 5px;"><strong style="color: #67c23a;">复盘结论：</strong></p>
                <p style="white-space: pre-wrap; margin: 0;">{{ item.conclusion }}</p>
              </div>
              <div style="background: #fff7e6; padding: 12px; border-radius: 4px; margin-bottom: 10px;">
                <p style="margin-bottom: 5px;"><strong style="color: #fa8c16;">改进建议：</strong></p>
                <p style="white-space: pre-wrap; margin: 0;">{{ item.improvement_suggestion }}</p>
              </div>
              <div v-if="item.rectification_feedback" style="background: #e6f7ff; padding: 12px; border-radius: 4px; margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                  <strong style="color: #1890ff;">整改反馈：</strong>
                  <span style="color: #909399; font-size: 12px;">{{ formatDate(item.rectification_feedback_at) }}</span>
                </div>
                <p style="white-space: pre-wrap; margin: 0;">{{ item.rectification_feedback }}</p>
              </div>
              <div v-if="item.operation_logs && item.operation_logs.length > 0" style="background: #f5f7fa; padding: 12px; border-radius: 4px;">
                <p style="margin-bottom: 10px; font-weight: bold; color: #606266;">操作日志：</p>
                <div v-for="log in item.operation_logs" :key="log.id" style="margin-bottom: 8px; padding-left: 10px; border-left: 2px solid #dcdfe6;">
                  <div style="display: flex; justify-content: space-between; font-size: 12px;">
                    <span>
                      <span style="color: #409eff; font-weight: 500;">{{ log.operator_name }}</span>
                      <span style="color: #606266; margin-left: 5px;">{{ log.operation_type_display }}</span>
                      <span v-if="log.old_followup_status && log.new_followup_status" style="color: #909399; margin-left: 5px;">
                        ({{ log.old_followup_status_display }} → {{ log.new_followup_status_display }})
                      </span>
                    </span>
                    <span style="color: #909399;">{{ formatDate(log.created_at) }}</span>
                  </div>
                </div>
              </div>
              <div style="margin-top: 10px; text-align: right;">
                <el-button 
                  link 
                  type="primary" 
                  size="small" 
                  v-if="item.can_submit_feedback && !item.rectification_feedback"
                  @click="handleSubmitReviewFeedback(item)"
                >
                  提交整改反馈
                </el-button>
                <el-button 
                  link 
                  type="primary" 
                  size="small" 
                  v-if="item.can_edit"
                  @click="handleUpdateReviewStatus(item)"
                >
                  更新跟进状态
                </el-button>
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

    <el-dialog v-model="reviewDialogVisible" title="发起复盘" width="600px">
      <el-form label-width="100px">
        <el-form-item label="复盘结论" required>
          <el-input v-model="reviewForm.conclusion" type="textarea" :rows="3" placeholder="请输入复盘结论" />
        </el-form-item>
        <el-form-item label="问题类型" required>
          <el-select v-model="reviewForm.problem_type" placeholder="请选择问题类型" style="width: 100%">
            <el-option v-for="item in problemTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="责任环节" required>
          <el-select v-model="reviewForm.responsibility_stage" placeholder="请选择责任环节" style="width: 100%">
            <el-option v-for="item in responsibilityStageOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="改进建议" required>
          <el-input v-model="reviewForm.improvement_suggestion" type="textarea" :rows="3" placeholder="请输入改进建议" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reviewDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleReviewSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="feedbackDialogVisible" title="提交整改反馈" width="600px">
      <el-form label-width="100px">
        <el-form-item label="整改反馈">
          <el-input v-model="feedbackForm.rectification_feedback" type="textarea" :rows="4" placeholder="请输入整改反馈内容" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="feedbackDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleFeedbackSubmit">提交</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="statusDialogVisible" title="更新跟进状态" width="500px">
      <el-form label-width="100px">
        <el-form-item label="跟进状态">
          <el-select v-model="statusForm.followup_status" placeholder="请选择跟进状态" style="width: 100%">
            <el-option v-for="item in followupStatusOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="statusDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleStatusSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { taskApi, taskReviewApi } from '@/api'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const task = ref(null)
const newStatus = ref('')
const transitionRemark = ref('')

const reviewDialogVisible = ref(false)
const feedbackDialogVisible = ref(false)
const statusDialogVisible = ref(false)
const currentReviewId = ref(null)
const submitLoading = ref(false)

const reviewForm = ref({
  conclusion: '',
  problem_type: '',
  responsibility_stage: '',
  improvement_suggestion: ''
})

const feedbackForm = ref({
  rectification_feedback: ''
})

const statusForm = ref({
  followup_status: ''
})

const problemTypeOptions = [
  { label: '流程问题', value: 'process' },
  { label: '执行问题', value: 'execution' },
  { label: '沟通问题', value: 'communication' },
  { label: '资源问题', value: 'resource' },
  { label: '质量问题', value: 'quality' },
  { label: '其他问题', value: 'other' }
]

const responsibilityStageOptions = [
  { label: '准备环节', value: 'preparation' },
  { label: '接待环节', value: 'reception' },
  { label: '收尾环节', value: 'closing' },
  { label: '复核环节', value: 'review' },
  { label: '管理环节', value: 'management' },
  { label: '其他环节', value: 'other' }
]

const followupStatusOptions = [
  { label: '待处理', value: 'pending' },
  { label: '处理中', value: 'processing' },
  { label: '已完成', value: 'completed' },
  { label: '已闭环', value: 'closed' }
]

const getFollowupStatusType = (status) => {
  const typeMap = {
    'pending': 'warning',
    'processing': 'primary',
    'completed': 'success',
    'closed': 'info'
  }
  return typeMap[status] || 'info'
}

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
    { value: 'completed', label: '复核通过（已完成）', roles: ['manager', 'reviewer'], requireRecords: true }
  ],
  'rectification_pending': [],
  'rectified_pending_review': [
    { value: 'completed', label: '复核通过（已完成）', roles: ['manager', 'reviewer'], requireRecords: true }
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

const handleInitiateReview = () => {
  reviewForm.value = {
    conclusion: '',
    problem_type: '',
    responsibility_stage: '',
    improvement_suggestion: ''
  }
  reviewDialogVisible.value = true
}

const handleReviewSubmit = async () => {
  if (!reviewForm.value.conclusion || !reviewForm.value.problem_type || 
      !reviewForm.value.responsibility_stage || !reviewForm.value.improvement_suggestion) {
    ElMessage.warning('请填写所有必填项')
    return
  }
  
  submitLoading.value = true
  try {
    await taskReviewApi.create({
      task: task.value.id,
      ...reviewForm.value
    })
    ElMessage.success('复盘创建成功')
    reviewDialogVisible.value = false
    loadData()
  } finally {
    submitLoading.value = false
  }
}

const handleSubmitReviewFeedback = (item) => {
  currentReviewId.value = item.id
  feedbackForm.value = { rectification_feedback: '' }
  feedbackDialogVisible.value = true
}

const handleFeedbackSubmit = async () => {
  if (!feedbackForm.value.rectification_feedback) {
    ElMessage.warning('请输入整改反馈内容')
    return
  }
  
  submitLoading.value = true
  try {
    await taskReviewApi.submitFeedback(currentReviewId.value, feedbackForm.value)
    ElMessage.success('提交成功')
    feedbackDialogVisible.value = false
    loadData()
  } finally {
    submitLoading.value = false
  }
}

const handleUpdateReviewStatus = (item) => {
  currentReviewId.value = item.id
  statusForm.value = { followup_status: item.followup_status }
  statusDialogVisible.value = true
}

const handleStatusSubmit = async () => {
  if (!statusForm.value.followup_status) {
    ElMessage.warning('请选择跟进状态')
    return
  }
  
  submitLoading.value = true
  try {
    await taskReviewApi.updateStatus(currentReviewId.value, statusForm.value)
    ElMessage.success('更新成功')
    statusDialogVisible.value = false
    loadData()
  } finally {
    submitLoading.value = false
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

.review-item {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

.review-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}
</style>
