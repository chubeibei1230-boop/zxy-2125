<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">任务执行</span>
      <el-select v-model="filterStatus" placeholder="状态筛选" clearable style="width: 150px;" @change="loadData">
        <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
      </el-select>
    </div>
    <div class="card">
      <el-table :data="tasks" v-loading="loading">
        <el-table-column prop="title" label="任务标题" />
        <el-table-column prop="station_name" label="工位" />
        <el-table-column prop="template_name" label="模板" />
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
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">查看详情</el-button>
            <el-button 
              link 
              type="success" 
              @click="handleExecute(row)"
              v-if="row.status === 'pending_prep' || row.status === 'in_progress'"
            >
              执行
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" title="填写记录" width="700px" :close-on-click-modal="false">
      <div v-if="currentTask">
        <el-alert 
          :title="currentTask.title" 
          type="info" 
          :closable="false"
          style="margin-bottom: 20px;"
        >
          <p>工位：{{ currentTask.station_name }}</p>
          <p>模板：{{ currentTask.template_name }}</p>
        </el-alert>

        <el-steps :active="activeStep" finish-status="success" style="margin-bottom: 30px;">
          <el-step title="准备" />
          <el-step title="接待" />
          <el-step title="收尾" />
        </el-steps>

        <div v-if="activeStep === 0">
          <h4 style="margin-bottom: 15px;">模板要求：</h4>
          <div style="background: #f5f7fa; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
            <p style="white-space: pre-wrap;">{{ currentTask.template_detail?.preparation_content }}</p>
          </div>
          <el-form :model="prepForm" label-width="80px">
            <el-form-item label="准备记录">
              <el-input v-model="prepForm.content" type="textarea" :rows="5" placeholder="请输入准备工作记录..." />
            </el-form-item>
          </el-form>
        </div>

        <div v-if="activeStep === 1">
          <h4 style="margin-bottom: 15px;">模板要求：</h4>
          <div style="background: #f5f7fa; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
            <p style="white-space: pre-wrap;">{{ currentTask.template_detail?.reception_content }}</p>
          </div>
          <el-form :model="recepForm" label-width="80px">
            <el-form-item label="接待记录">
              <el-input v-model="recepForm.content" type="textarea" :rows="5" placeholder="请输入接待过程记录..." />
            </el-form-item>
          </el-form>
        </div>

        <div v-if="activeStep === 2">
          <h4 style="margin-bottom: 15px;">模板要求：</h4>
          <div style="background: #f5f7fa; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
            <p style="white-space: pre-wrap;">{{ currentTask.template_detail?.closing_content }}</p>
          </div>
          <el-form :model="closeForm" label-width="80px">
            <el-form-item label="收尾记录">
              <el-input v-model="closeForm.content" type="textarea" :rows="4" placeholder="请输入收尾工作记录..." />
            </el-form-item>
            <el-form-item label="是否异常">
              <el-switch v-model="closeForm.has_exception" />
            </el-form-item>
            <el-form-item label="异常描述" v-if="closeForm.has_exception">
              <el-input v-model="closeForm.exception_description" type="textarea" :rows="3" placeholder="请描述异常情况..." />
            </el-form-item>
          </el-form>
        </div>
      </div>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button v-if="activeStep > 0" @click="prevStep">上一步</el-button>
        <el-button type="primary" :loading="submitLoading" @click="submitStep">
          {{ activeStep < 2 ? '下一步' : '提交' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { taskApi, templateApi } from '@/api'

const router = useRouter()
const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const tasks = ref([])
const currentTask = ref(null)
const filterStatus = ref('')
const activeStep = ref(0)

const statusOptions = [
  { label: '待准备', value: 'pending_prep' },
  { label: '进行中', value: 'in_progress' },
  { label: '待复核', value: 'pending_review' },
  { label: '已完成', value: 'completed' }
]

const prepForm = ref({ content: '', task: null })
const recepForm = ref({ content: '', task: null })
const closeForm = ref({ content: '', has_exception: false, exception_description: '', task: null })

const loadData = async () => {
  loading.value = true
  try {
    const params = {}
    if (filterStatus.value) params.status = filterStatus.value
    tasks.value = await taskApi.myTasks(params)
  } finally {
    loading.value = false
  }
}

const handleView = (row) => {
  router.push(`/tasks/${row.id}`)
}

const handleExecute = async (row) => {
  currentTask.value = await taskApi.detail(row.id)
  activeStep.value = 0
  
  if (currentTask.value.preparation) {
    prepForm.value.content = currentTask.value.preparation.content
    activeStep.value = 1
  }
  if (currentTask.value.reception) {
    recepForm.value.content = currentTask.value.reception.content
    activeStep.value = 2
  }
  if (currentTask.value.closing) {
    closeForm.value = {
      content: currentTask.value.closing.content,
      has_exception: currentTask.value.closing.has_exception,
      exception_description: currentTask.value.closing.exception_description
    }
  }
  
  dialogVisible.value = true
}

const prevStep = () => {
  if (activeStep.value > 0) {
    activeStep.value--
  }
}

const submitStep = async () => {
  submitLoading.value = true
  try {
    if (activeStep.value === 0) {
      if (!prepForm.value.content) {
        ElMessage.warning('请填写准备记录')
        return
      }
      if (currentTask.value.status === 'pending_prep') {
        await taskApi.transition(currentTask.value.id, { 
          new_status: 'in_progress', 
          remark: '开始执行任务' 
        })
      }
      if (!currentTask.value.preparation) {
        await taskApi.submitPreparation(currentTask.value.id, prepForm.value)
        ElMessage.success('准备记录提交成功')
      }
      currentTask.value = await taskApi.detail(currentTask.value.id)
      activeStep.value = 1
    } else if (activeStep.value === 1) {
      if (!recepForm.value.content) {
        ElMessage.warning('请填写接待记录')
        return
      }
      if (!currentTask.value.reception) {
        await taskApi.submitReception(currentTask.value.id, recepForm.value)
        ElMessage.success('接待记录提交成功')
      }
      currentTask.value = await taskApi.detail(currentTask.value.id)
      activeStep.value = 2
    } else if (activeStep.value === 2) {
      if (!closeForm.value.content) {
        ElMessage.warning('请填写收尾记录')
        return
      }
      if (closeForm.value.has_exception && !closeForm.value.exception_description) {
        ElMessage.warning('请填写异常描述')
        return
      }
      if (!currentTask.value.closing) {
        await taskApi.submitClosing(currentTask.value.id, closeForm.value)
      }
      await taskApi.transition(currentTask.value.id, { 
        new_status: 'pending_review', 
        remark: '任务执行完成，提交复核' 
      })
      ElMessage.success('任务提交复核成功')
      dialogVisible.value = false
      loadData()
    }
  } catch (e) {
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
