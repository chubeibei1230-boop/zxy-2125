<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">工位管理</span>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        新建工位
      </el-button>
    </div>
    <div class="card">
      <el-table :data="stations" v-loading="loading">
        <el-table-column prop="code" label="工位编号" width="120" />
        <el-table-column prop="name" label="工位名称" />
        <el-table-column prop="project_name" label="所属项目" />
        <el-table-column prop="description" label="工位描述" show-overflow-tooltip />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑工位' : '新建工位'" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="工位编号" prop="code">
          <el-input v-model="form.code" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="工位名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="所属项目" prop="project">
          <el-select v-model="form.project" placeholder="请选择项目">
            <el-option 
              v-for="item in projects" 
              :key="item.id" 
              :label="item.name" 
              :value="item.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="工位描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" />
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
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { stationApi, projectApi } from '@/api'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const stations = ref([])
const projects = ref([])

const form = ref({
  id: null,
  code: '',
  name: '',
  project: null,
  description: ''
})

const rules = {
  code: [{ required: true, message: '请输入工位编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入工位名称', trigger: 'blur' }],
  project: [{ required: true, message: '请选择所属项目', trigger: 'change' }]
}

const loadData = async () => {
  loading.value = true
  try {
    stations.value = await stationApi.list()
  } finally {
    loading.value = false
  }
}

const loadProjects = async () => {
  projects.value = await projectApi.list()
}

const handleAdd = () => {
  isEdit.value = false
  form.value = { id: null, code: '', name: '', project: null, description: '' }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  form.value = { ...row, project: row.project }
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该工位吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await stationApi.delete(row.id)
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
          await stationApi.update(form.value.id, form.value)
          ElMessage.success('更新成功')
        } else {
          await stationApi.create(form.value)
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
