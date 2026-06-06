<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">任务模板</span>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        新建模板
      </el-button>
    </div>
    <div class="card">
      <el-table :data="templates" v-loading="loading">
        <el-table-column prop="name" label="模板名称" />
        <el-table-column prop="project_name" label="所属项目" />
        <el-table-column prop="description" label="模板描述" show-overflow-tooltip />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">查看</el-button>
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑模板' : '新建模板'" width="600px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="模板名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="所属项目" prop="project">
          <el-select v-model="form.project" placeholder="请选择项目" style="width: 100%">
            <el-option 
              v-for="item in projects" 
              :key="item.id" 
              :label="item.name" 
              :value="item.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="模板描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="准备内容" prop="preparation_content">
          <el-input v-model="form.preparation_content" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="接待内容" prop="reception_content">
          <el-input v-model="form.reception_content" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="收尾内容" prop="closing_content">
          <el-input v-model="form.closing_content" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="viewDialogVisible" title="模板详情" width="600px">
      <div v-if="viewData">
        <h3>{{ viewData.name }}</h3>
        <p style="color: #909399; margin: 10px 0;">所属项目：{{ viewData.project_name }}</p>
        <p style="margin: 10px 0;"><strong>模板描述：</strong>{{ viewData.description }}</p>
        <div style="margin: 15px 0;">
          <p><strong>准备内容要求：</strong></p>
          <p style="white-space: pre-wrap; background: #f5f7fa; padding: 10px; border-radius: 4px;">{{ viewData.preparation_content }}</p>
        </div>
        <div style="margin: 15px 0;">
          <p><strong>接待内容要求：</strong></p>
          <p style="white-space: pre-wrap; background: #f5f7fa; padding: 10px; border-radius: 4px;">{{ viewData.reception_content }}</p>
        </div>
        <div style="margin: 15px 0;">
          <p><strong>收尾内容要求：</strong></p>
          <p style="white-space: pre-wrap; background: #f5f7fa; padding: 10px; border-radius: 4px;">{{ viewData.closing_content }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { templateApi, projectApi } from '@/api'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const viewDialogVisible = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const templates = ref([])
const projects = ref([])
const viewData = ref(null)

const form = ref({
  id: null,
  name: '',
  project: null,
  description: '',
  preparation_content: '',
  reception_content: '',
  closing_content: ''
})

const rules = {
  name: [{ required: true, message: '请输入模板名称', trigger: 'blur' }],
  project: [{ required: true, message: '请选择所属项目', trigger: 'change' }],
  preparation_content: [{ required: true, message: '请输入准备内容要求', trigger: 'blur' }],
  reception_content: [{ required: true, message: '请输入接待内容要求', trigger: 'blur' }],
  closing_content: [{ required: true, message: '请输入收尾内容要求', trigger: 'blur' }]
}

const loadData = async () => {
  loading.value = true
  try {
    templates.value = await templateApi.list()
  } finally {
    loading.value = false
  }
}

const loadProjects = async () => {
  projects.value = await projectApi.list()
}

const handleAdd = () => {
  isEdit.value = false
  form.value = {
    id: null, name: '', project: null, description: '',
    preparation_content: '', reception_content: '', closing_content: ''
  }
  dialogVisible.value = true
}

const handleView = (row) => {
  viewData.value = row
  viewDialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  form.value = { ...row, project: row.project }
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该模板吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await templateApi.delete(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch {
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (isEdit.value) {
          await templateApi.update(form.value.id, form.value)
          ElMessage.success('更新成功')
        } else {
          await templateApi.create(form.value)
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

onMounted(() => {
  loadData()
  loadProjects()
})
</script>
