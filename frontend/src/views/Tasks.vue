<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">任务列表</span>
      <div>
        <el-select v-model="filterStatus" placeholder="状态筛选" clearable style="width: 150px; margin-right: 10px;" @change="loadData">
          <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
        <el-button type="primary" @click="handleAdd" v-if="userStore.isManager">
          <el-icon><Plus /></el-icon>
          新建任务
        </el-button>
      </div>
    </div>
    <div class="card">
      <el-table :data="tasks" v-loading="loading">
        <el-table-column prop="title" label="任务标题" />
        <el-table-column prop="project_name" label="所属项目" />
        <el-table-column prop="station_name" label="工位" />
        <el-table-column prop="executor_name" label="执行者" />
        <el-table-column prop="reviewer_name" label="复核者" />
        <el-table-column prop="status_display" label="状态" width="100">
          <template #default="{ row }">
            <span :class="['status-tag', `status-${row.status}`]">{{ row.status_display }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="scheduled_time" label="计划时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.scheduled_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">详情</el-button>
            <el-button link type="primary" @click="handleEdit(row)" v-if="userStore.isManager && row.status === 'pending_prep'">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)" v-if="userStore.isManager">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑任务' : '新建任务'" width="600px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="任务标题" prop="title">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="所属项目" prop="project">
          <el-select v-model="form.project" placeholder="请选择项目" style="width: 100%" @change="onProjectChange">
            <el-option 
              v-for="item in projects" 
              :key="item.id" 
              :label="item.name" 
              :value="item.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="工位" prop="station">
          <el-select v-model="form.station" placeholder="请选择工位" style="width: 100%">
            <el-option 
              v-for="item in filteredStations" 
              :key="item.id" 
              :label="item.name" 
              :value="item.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="任务模板" prop="template">
          <el-select v-model="form.template" placeholder="请选择模板" style="width: 100%">
            <el-option 
              v-for="item in filteredTemplates" 
              :key="item.id" 
              :label="item.name" 
              :value="item.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="执行者" prop="executor">
          <el-select v-model="form.executor" placeholder="请选择执行者" style="width: 100%">
            <el-option 
              v-for="item in executors" 
              :key="item.id" 
              :label="item.username" 
              :value="item.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="复核者" prop="reviewer">
          <el-select v-model="form.reviewer" placeholder="请选择复核者" style="width: 100%">
            <el-option 
              v-for="item in reviewers" 
              :key="item.id" 
              :label="item.username" 
              :value="item.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="计划时间" prop="scheduled_time">
          <el-date-picker
            v-model="form.scheduled_time"
            type="datetime"
            placeholder="选择计划时间"
            style="width: 100%"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DDTHH:mm:ss"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { taskApi, projectApi, stationApi, templateApi, userApi } from '@/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const tasks = ref([])
const projects = ref([])
const stations = ref([])
const templates = ref([])
const executors = ref([])
const reviewers = ref([])
const filterStatus = ref('')

const statusOptions = [
  { label: '待准备', value: 'pending_prep' },
  { label: '进行中', value: 'in_progress' },
  { label: '待复核', value: 'pending_review' },
  { label: '待整改', value: 'rectification_pending' },
  { label: '已整改待复核', value: 'rectified_pending_review' },
  { label: '已完成', value: 'completed' },
  { label: '已取消', value: 'cancelled' }
]

const form = ref({
  id: null,
  title: '',
  project: null,
  station: null,
  template: null,
  executor: null,
  reviewer: null,
  scheduled_time: ''
})

const rules = {
  title: [{ required: true, message: '请输入任务标题', trigger: 'blur' }],
  project: [{ required: true, message: '请选择项目', trigger: 'change' }],
  station: [{ required: true, message: '请选择工位', trigger: 'change' }],
  template: [{ required: true, message: '请选择模板', trigger: 'change' }],
  executor: [{ required: true, message: '请选择执行者', trigger: 'change' }],
  reviewer: [{ required: true, message: '请选择复核者', trigger: 'change' }],
  scheduled_time: [{ required: true, message: '请选择计划时间', trigger: 'change' }]
}

const filteredStations = computed(() => {
  if (!form.value.project) return stations.value
  return stations.value.filter(s => s.project === form.value.project)
})

const filteredTemplates = computed(() => {
  if (!form.value.project) return templates.value
  return templates.value.filter(t => t.project === form.value.project)
})

const loadData = async () => {
  loading.value = true
  try {
    const params = {}
    if (filterStatus.value) params.status = filterStatus.value
    tasks.value = await taskApi.list(params)
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

const loadTemplates = async () => {
  templates.value = await templateApi.list()
}

const loadUsers = async () => {
  executors.value = await userApi.byRole('executor')
  reviewers.value = await userApi.byRole('reviewer')
}

const onProjectChange = () => {
  form.value.station = null
  form.value.template = null
}

const handleAdd = () => {
  isEdit.value = false
  form.value = {
    id: null, title: '', project: null, station: null,
    template: null, executor: null, reviewer: null, scheduled_time: ''
  }
  dialogVisible.value = true
}

const handleView = (row) => {
  router.push(`/tasks/${row.id}`)
}

const handleEdit = (row) => {
  isEdit.value = true
  form.value = {
    ...row,
    project: row.project,
    station: row.station,
    template: row.template,
    executor: row.executor,
    reviewer: row.reviewer
  }
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  const canHard = row.can_hard_delete
  const hint = canHard ? '该任务暂无流转记录，可选择硬删除（彻底删除）或软删除（标记删除）' : '该任务已有流转记录，只能软删除（标记删除）'
  
  try {
    const { value: type } = await ElMessageBox.confirm(
      hint,
      '删除提示',
      {
        confirmButtonText: canHard ? '硬删除' : '确定',
        cancelButtonText: canHard ? '软删除' : '取消',
        type: 'warning',
        distinguishCancelAndClose: true
      }
    )
    
    if (canHard) {
      await taskApi.delete(row.id, true)
    } else {
      await taskApi.delete(row.id, false)
    }
    ElMessage.success('删除成功')
    loadData()
  } catch (action) {
    if (action === 'cancel' && canHard) {
      await taskApi.delete(row.id, false)
      ElMessage.success('软删除成功')
      loadData()
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (isEdit.value) {
          await taskApi.update(form.value.id, form.value)
          ElMessage.success('更新成功')
        } else {
          await taskApi.create(form.value)
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

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  loadData()
  loadProjects()
  loadStations()
  loadTemplates()
  loadUsers()
})
</script>
