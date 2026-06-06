<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">任务复盘记录</span>
      <div>
        <el-button type="primary" @click="handleAdd" v-if="userStore.isManager || userStore.isReviewer">
          <el-icon><Plus /></el-icon>
          新建复盘
        </el-button>
      </div>
    </div>

    <el-card class="mb-20">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="所属项目">
          <el-select v-model="filters.project" placeholder="全部" clearable style="width: 150px" @change="loadData">
            <el-option v-for="item in projects" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="工位">
          <el-select v-model="filters.station" placeholder="全部" clearable style="width: 150px" @change="loadData">
            <el-option v-for="item in filteredStations" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="任务状态">
          <el-select v-model="filters.task_status" placeholder="全部" clearable style="width: 150px" @change="loadData">
            <el-option v-for="item in taskStatusOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="问题类型">
          <el-select v-model="filters.problem_type" placeholder="全部" clearable style="width: 150px" @change="loadData">
            <el-option v-for="item in problemTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="跟进状态">
          <el-select v-model="filters.followup_status" placeholder="全部" clearable style="width: 150px" @change="loadData">
            <el-option v-for="item in followupStatusOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <div class="card">
      <el-table :data="reviews" v-loading="loading">
        <el-table-column prop="task_title" label="任务标题" min-width="180" />
        <el-table-column prop="project_name" label="所属项目" width="120" />
        <el-table-column prop="station_name" label="工位" width="120" />
        <el-table-column prop="problem_type_display" label="问题类型" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.problem_type_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="responsibility_stage_display" label="责任环节" width="100" />
        <el-table-column prop="followup_status_display" label="跟进状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getFollowupStatusType(row.followup_status)" size="small">
              {{ row.followup_status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="initiator_name" label="发起人" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">查看详情</el-button>
            <el-button link type="primary" @click="handleViewTask(row)">查看任务</el-button>
            <el-button link type="primary" @click="handleEdit(row)" v-if="row.can_edit">编辑</el-button>
            <el-button link type="primary" @click="handleSubmitFeedback(row)" v-if="row.can_submit_feedback && !row.rectification_feedback">
              提交反馈
            </el-button>
            <el-button link type="primary" @click="handleUpdateStatus(row)" v-if="row.can_edit">
              更新状态
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="700px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="关联任务" prop="task">
          <el-select v-model="form.task" placeholder="请选择任务" style="width: 100%" filterable :disabled="isEdit">
            <el-option 
              v-for="item in availableTasks" 
              :key="item.id" 
              :label="item.title" 
              :value="item.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="复盘结论" prop="conclusion">
          <el-input v-model="form.conclusion" type="textarea" :rows="3" placeholder="请输入复盘结论" />
        </el-form-item>
        <el-form-item label="问题类型" prop="problem_type">
          <el-select v-model="form.problem_type" placeholder="请选择问题类型" style="width: 100%">
            <el-option v-for="item in problemTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="责任环节" prop="responsibility_stage">
          <el-select v-model="form.responsibility_stage" placeholder="请选择责任环节" style="width: 100%">
            <el-option v-for="item in responsibilityStageOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="改进建议" prop="improvement_suggestion">
          <el-input v-model="form.improvement_suggestion" type="textarea" :rows="3" placeholder="请输入改进建议" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="feedbackDialogVisible" title="提交整改反馈" width="600px">
      <el-form :model="feedbackForm" label-width="100px">
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

    <el-drawer v-model="detailDrawerVisible" title="复盘详情" size="50%">
      <div v-if="currentReview">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务标题">{{ currentReview.task_title }}</el-descriptions-item>
          <el-descriptions-item label="所属项目">{{ currentReview.project_name }}</el-descriptions-item>
          <el-descriptions-item label="工位">{{ currentReview.station_name }}</el-descriptions-item>
          <el-descriptions-item label="问题类型">
            <el-tag size="small">{{ currentReview.problem_type_display }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="责任环节">{{ currentReview.responsibility_stage_display }}</el-descriptions-item>
          <el-descriptions-item label="跟进状态">
            <el-tag :type="getFollowupStatusType(currentReview.followup_status)" size="small">
              {{ currentReview.followup_status_display }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="发起人">{{ currentReview.initiator_name }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(currentReview.created_at) }}</el-descriptions-item>
        </el-descriptions>

        <el-card style="margin-top: 20px;">
          <template #header><span>复盘结论</span></template>
          <div style="white-space: pre-wrap;">{{ currentReview.conclusion }}</div>
        </el-card>

        <el-card style="margin-top: 20px;">
          <template #header><span>改进建议</span></template>
          <div style="white-space: pre-wrap;">{{ currentReview.improvement_suggestion }}</div>
        </el-card>

        <el-card style="margin-top: 20px;" v-if="currentReview.rectification_feedback">
          <template #header>
            <div class="card-header">
              <span>整改反馈</span>
              <span style="color: #909399; font-size: 12px;">{{ formatDate(currentReview.rectification_feedback_at) }}</span>
            </div>
          </template>
          <div style="white-space: pre-wrap;">{{ currentReview.rectification_feedback }}</div>
        </el-card>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { taskReviewApi, projectApi, stationApi, taskApi } from '@/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const submitLoading = ref(false)
const reviews = ref([])
const projects = ref([])
const stations = ref([])
const availableTasks = ref([])

const dialogVisible = ref(false)
const feedbackDialogVisible = ref(false)
const statusDialogVisible = ref(false)
const detailDrawerVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const currentReview = ref(null)
const currentReviewId = ref(null)

const filters = ref({
  project: '',
  station: '',
  task_status: '',
  problem_type: '',
  followup_status: ''
})

const form = ref({
  task: null,
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

const rules = {
  task: [{ required: true, message: '请选择任务', trigger: 'change' }],
  conclusion: [{ required: true, message: '请输入复盘结论', trigger: 'blur' }],
  problem_type: [{ required: true, message: '请选择问题类型', trigger: 'change' }],
  responsibility_stage: [{ required: true, message: '请选择责任环节', trigger: 'change' }],
  improvement_suggestion: [{ required: true, message: '请输入改进建议', trigger: 'blur' }]
}

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

const taskStatusOptions = [
  { label: '已完成', value: 'completed' },
  { label: '已取消', value: 'cancelled' }
]

const dialogTitle = computed(() => isEdit.value ? '编辑复盘' : '新建复盘')

const filteredStations = computed(() => {
  if (!filters.value.project) return stations.value
  return stations.value.filter(s => s.project === filters.value.project)
})

const getFollowupStatusType = (status) => {
  const typeMap = {
    'pending': 'warning',
    'processing': 'primary',
    'completed': 'success',
    'closed': 'info'
  }
  return typeMap[status] || 'info'
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.project) params.project = filters.value.project
    if (filters.value.station) params.station = filters.value.station
    if (filters.value.task_status) params.task_status = filters.value.task_status
    if (filters.value.problem_type) params.problem_type = filters.value.problem_type
    if (filters.value.followup_status) params.followup_status = filters.value.followup_status
    reviews.value = await taskReviewApi.list(params)
  } finally {
    loading.value = false
  }
}

const loadProjects = async () => {
  projects.value = await projectApi.list()
}

const loadStations = async () => {
  stations.value = await stationApi.list()
}

const loadAvailableTasks = async () => {
  const tasks = await taskApi.list({ status: 'completed' })
  const cancelledTasks = await taskApi.list({ status: 'cancelled' })
  availableTasks.value = [...tasks, ...cancelledTasks]
}

const resetFilters = () => {
  filters.value = {
    project: '',
    station: '',
    task_status: '',
    problem_type: '',
    followup_status: ''
  }
  loadData()
}

const handleAdd = async () => {
  await loadAvailableTasks()
  isEdit.value = false
  form.value = {
    task: null,
    conclusion: '',
    problem_type: '',
    responsibility_stage: '',
    improvement_suggestion: ''
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  currentReviewId.value = row.id
  form.value = {
    task: row.task,
    conclusion: row.conclusion,
    problem_type: row.problem_type,
    responsibility_stage: row.responsibility_stage,
    improvement_suggestion: row.improvement_suggestion
  }
  dialogVisible.value = true
}

const handleView = (row) => {
  currentReview.value = row
  detailDrawerVisible.value = true
}

const handleViewTask = (row) => {
  router.push(`/tasks/${row.task}`)
}

const handleSubmitFeedback = (row) => {
  currentReviewId.value = row.id
  feedbackForm.value = { rectification_feedback: '' }
  feedbackDialogVisible.value = true
}

const handleUpdateStatus = (row) => {
  currentReviewId.value = row.id
  statusForm.value = { followup_status: row.followup_status }
  statusDialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (isEdit.value) {
          await taskReviewApi.update(currentReviewId.value, form.value)
          ElMessage.success('更新成功')
        } else {
          await taskReviewApi.create(form.value)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        loadData()
      } finally {
        submitLoading.value = false
      }
    }
  })
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
  loadProjects()
  loadStations()
})
</script>

<style scoped>
.mb-20 {
  margin-bottom: 20px;
}

.filter-form {
  margin: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
