<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">异常复核</span>
      <el-select v-model="filterStatus" placeholder="状态筛选" clearable style="width: 180px;" @change="loadData">
        <el-option label="待复核" value="pending_review" />
        <el-option label="已整改待复核" value="rectified_pending_review" />
        <el-option label="待整改" value="rectification_pending" />
        <el-option label="已完成" value="completed" />
      </el-select>
    </div>
    <div class="card">
      <el-table :data="tasks" v-loading="loading">
        <el-table-column prop="title" label="任务标题" />
        <el-table-column prop="station_name" label="工位" />
        <el-table-column prop="executor_name" label="执行者" />
        <el-table-column prop="status_display" label="状态" width="100">
          <template #default="{ row }">
            <span :class="['status-tag', `status-${row.status}`]">{{ row.status_display }}</span>
          </template>
        </el-table-column>
        <el-table-column label="是否有异常" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.closing?.has_exception" type="danger">有异常</el-tag>
            <el-tag v-else type="success">正常</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">查看详情</el-button>
            <el-button 
              link 
              type="success" 
              @click="handleReview(row)"
              v-if="row.status === 'pending_review' || row.status === 'rectified_pending_review'"
            >
              复核
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" title="任务复核" width="700px" :close-on-click-modal="false">
      <div v-if="currentTask">
        <el-descriptions :column="2" border style="margin-bottom: 20px;">
          <el-descriptions-item label="任务标题">{{ currentTask.title }}</el-descriptions-item>
          <el-descriptions-item label="工位">{{ currentTask.station_name }}</el-descriptions-item>
          <el-descriptions-item label="执行者">{{ currentTask.executor_name }}</el-descriptions-item>
          <el-descriptions-item label="计划时间">{{ formatDate(currentTask.scheduled_time) }}</el-descriptions-item>
        </el-descriptions>

        <el-tabs v-model="activeTab">
          <el-tab-pane label="准备记录" name="prep">
            <div v-if="currentTask.preparation">
              <p style="margin-bottom: 10px; color: #909399;">
                填写人：{{ currentTask.preparation.operator_name }} | {{ formatDate(currentTask.preparation.created_at) }}
              </p>
              <pre style="white-space: pre-wrap; background: #f5f7fa; padding: 15px; border-radius: 4px; margin: 0;">{{ currentTask.preparation.content }}</pre>
            </div>
            <el-empty v-else description="暂无准备记录" />
          </el-tab-pane>
          <el-tab-pane label="接待记录" name="recep">
            <div v-if="currentTask.reception">
              <p style="margin-bottom: 10px; color: #909399;">
                填写人：{{ currentTask.reception.operator_name }} | {{ formatDate(currentTask.reception.created_at) }}
              </p>
              <pre style="white-space: pre-wrap; background: #f5f7fa; padding: 15px; border-radius: 4px; margin: 0;">{{ currentTask.reception.content }}</pre>
            </div>
            <el-empty v-else description="暂无接待记录" />
          </el-tab-pane>
          <el-tab-pane label="收尾记录" name="close">
            <div v-if="currentTask.closing">
              <p style="margin-bottom: 10px; color: #909399;">
                填写人：{{ currentTask.closing.operator_name }} | {{ formatDate(currentTask.closing.created_at) }}
              </p>
              <pre style="white-space: pre-wrap; background: #f5f7fa; padding: 15px; border-radius: 4px; margin: 0 0 10px 0;">{{ currentTask.closing.content }}</pre>
              <div v-if="currentTask.closing.has_exception" style="background: #fef0f0; padding: 15px; border-radius: 4px;">
                <p style="margin-bottom: 5px;"><strong style="color: #f56c6c;">异常描述：</strong></p>
                <p>{{ currentTask.closing.exception_description }}</p>
              </div>
            </div>
            <el-empty v-else description="暂无收尾记录" />
          </el-tab-pane>
          <el-tab-pane label="异常处理" name="exception">
            <div v-if="currentTask.closing?.has_exception">
              <el-form label-width="100px" style="margin-top: 20px;">
                <el-form-item label="处理意见">
                  <el-input v-model="handlingForm.handling_content" type="textarea" :rows="4" placeholder="请输入异常处理意见..." />
                </el-form-item>
              </el-form>
            </div>
            <el-empty v-else description="该任务无异常" />
          </el-tab-pane>
        </el-tabs>
      </div>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="warning" @click="openRectificationDialog" v-if="currentTask?.status === 'pending_review' || currentTask?.status === 'rectified_pending_review'">
          发起整改
        </el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleApprove" v-if="currentTask?.status === 'pending_review' || currentTask?.status === 'rectified_pending_review'">
          复核通过
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="rectificationDialogVisible" title="发起整改" width="500px" :close-on-click-modal="false">
      <el-form :model="rectificationForm" label-width="100px">
        <el-form-item label="整改环节">
          <el-radio-group v-model="rectificationForm.stage">
            <el-radio label="preparation">准备记录</el-radio>
            <el-radio label="reception">接待记录</el-radio>
            <el-radio label="closing">收尾记录</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="整改意见">
          <el-input v-model="rectificationForm.rectification_content" type="textarea" :rows="4" placeholder="请输入整改意见..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rectificationDialogVisible = false">取消</el-button>
        <el-button type="warning" :loading="rectificationLoading" @click="handleInitiateRectification">
          确认发起整改
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { taskApi } from '@/api'

const router = useRouter()
const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const rectificationDialogVisible = ref(false)
const rectificationLoading = ref(false)
const tasks = ref([])
const currentTask = ref(null)
const filterStatus = ref('pending_review')
const activeTab = ref('prep')

const handlingForm = ref({
  handling_content: ''
})

const rectificationForm = ref({
  stage: 'preparation',
  rectification_content: ''
})

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

const handleReview = async (row) => {
  currentTask.value = await taskApi.detail(row.id)
  handlingForm.value.handling_content = ''
  activeTab.value = 'prep'
  dialogVisible.value = true
}

const openRectificationDialog = () => {
  rectificationForm.value = {
    stage: 'preparation',
    rectification_content: ''
  }
  rectificationDialogVisible.value = true
}

const handleInitiateRectification = async () => {
  if (!rectificationForm.value.stage) {
    ElMessage.warning('请选择整改环节')
    return
  }
  if (!rectificationForm.value.rectification_content) {
    ElMessage.warning('请填写整改意见')
    return
  }

  try {
    rectificationLoading.value = true
    await taskApi.initiateRectification(currentTask.value.id, rectificationForm.value)
    ElMessage.success('整改已发起，任务已退回执行者')
    rectificationDialogVisible.value = false
    dialogVisible.value = false
    loadData()
  } catch (e) {
  } finally {
    rectificationLoading.value = false
  }
}

const handleApprove = async () => {
  if (currentTask.value.closing?.has_exception && !handlingForm.value.handling_content) {
    ElMessage.warning('请填写异常处理意见')
    return
  }
  
  try {
    submitLoading.value = true
    
    if (currentTask.value.closing?.has_exception) {
      await taskApi.handleException(currentTask.value.id, handlingForm.value)
    }
    
    await taskApi.transition(currentTask.value.id, {
      new_status: 'completed',
      remark: '复核通过'
    })
    ElMessage.success('复核通过')
    dialogVisible.value = false
    loadData()
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
