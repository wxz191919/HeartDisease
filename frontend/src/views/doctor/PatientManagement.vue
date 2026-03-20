<template>
  <div class="patient-management">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <h2>病人管理</h2>
          <el-button type="primary" @click="showAddDialog">添加病人</el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索病人姓名/电话/地址"
          clearable
          @clear="handleSearch"
          style="width: 300px;"
        >
          <template #append>
            <el-button @click="handleSearch">
              <el-icon><Search /></el-icon>
            </el-button>
          </template>
        </el-input>
      </div>

      <!-- 病人列表 -->
      <el-table :data="patients" style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="gender" label="性别" width="80" />
        <el-table-column prop="age" label="年龄" width="80" />
        <el-table-column prop="phone" label="电话" />
        <el-table-column prop="address" label="地址" show-overflow-tooltip />
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button size="small" @click="showEditDialog(scope.row)">编辑</el-button>
            <el-button
              size="small"
              type="danger"
              @click="handleDelete(scope.row)"
            >删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="500px"
      @close="handleDialogClose"
    >
      <el-form
        ref="patientFormRef"
        :model="patientForm"
        :rules="rules"
        label-width="80px"
      >
        <el-form-item label="姓名" prop="name">
          <el-input v-model="patientForm.name" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-select v-model="patientForm.gender" placeholder="请选择性别">
            <el-option label="男" value="male" />
            <el-option label="女" value="female" />
          </el-select>
        </el-form-item>
        <el-form-item label="年龄" prop="age">
          <el-input-number v-model="patientForm.age" :min="0" :max="150" />
        </el-form-item>
        <el-form-item label="电话" prop="phone">
          <el-input v-model="patientForm.phone" />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input v-model="patientForm.address" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import axios from 'axios'

export default {
  name: 'PatientManagement',
  components: {
    Search
  },
  setup() {
    const patients = ref([])
    const loading = ref(false)
    const currentPage = ref(1)
    const pageSize = ref(10)
    const total = ref(0)
    const searchQuery = ref('')
    const dialogVisible = ref(false)
    const dialogTitle = ref('')
    const isEdit = ref(false)
    const patientFormRef = ref(null)

    const patientForm = ref({
      id: null,
      name: '',
      gender: '',
      age: 0,
      phone: '',
      address: '',
    })

    const rules = {
      name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
      gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
      age: [{ required: true, message: '请输入年龄', trigger: 'blur' }]
    }

    // 获取病人列表
    const fetchPatients = async () => {
      loading.value = true
      try {
        const response = await axios.get('/api/patients', {
          params: {
            page: currentPage.value,
            per_page: pageSize.value,
            search: searchQuery.value
          }
        })

        patients.value = response.data.patients
        total.value = response.data.total
      } catch (error) {
        console.error('Error fetching patients:', error)
        const message = error.response && error.response.data && error.response.data.message
        ElMessage.error(message || '获取病人列表失败')
      } finally {
        loading.value = false
      }
    }

    // 显示添加对话框
    const showAddDialog = () => {
      isEdit.value = false
      dialogTitle.value = '添加病人'
      patientForm.value = {
        id: null,
        name: '',
        gender: '',
        age: 0,
        phone: '',
        address: '',
      }
      dialogVisible.value = true
    }

    // 显示编辑对话框
    const showEditDialog = (row) => {
      isEdit.value = true
      dialogTitle.value = '编辑病人'
      patientForm.value = { ...row }
      dialogVisible.value = true
    }

    // 关闭对话框时重置表单
    const handleDialogClose = () => {
      if (patientFormRef.value) {
        patientFormRef.value.resetFields()
      }
    }

    // 提交表单
    const handleSubmit = async () => {
      if (!patientFormRef.value) return

      try {
        await patientFormRef.value.validate()

        if (isEdit.value) {
          await axios.put(`/api/patients/${patientForm.value.id}`, patientForm.value)
          ElMessage.success('更新成功')
        } else {
          await axios.post('/api/patients', patientForm.value)
          ElMessage.success('添加成功')
        }

        dialogVisible.value = false
        fetchPatients()
      } catch (error) {
        console.error('Error submitting form:', error)
        if (error.response && error.response.data) {
          const message = error.response.data.message
          ElMessage.error(message || (isEdit.value ? '更新失败' : '添加失败'))
        } else if (error.name === 'ValidationError') {
          ElMessage.error('请填写必要的信息')
        } else {
          ElMessage.error(isEdit.value ? '更新失败' : '添加失败')
        }
      }
    }

    // 删除病人
    const handleDelete = (row) => {
      ElMessageBox.confirm('确定要删除该病人吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await axios.delete(`/api/patients/${row.id}`)
          ElMessage.success('删除成功')
          fetchPatients()
        } catch (error) {
          console.error('Error deleting patient:', error)
          const message = error.response && error.response.data && error.response.data.message
          ElMessage.error(message || '删除失败')
        }
      }).catch(() => {})
    }

    // 搜索
    const handleSearch = () => {
      currentPage.value = 1
      fetchPatients()
    }

    // 分页大小变化
    const handleSizeChange = (size) => {
      pageSize.value = size
      fetchPatients()
    }

    // 页码变化
    const handleCurrentChange = (page) => {
      currentPage.value = page
      fetchPatients()
    }

    onMounted(() => {
      fetchPatients()
    })

    return {
      patients,
      loading,
      currentPage,
      pageSize,
      total,
      searchQuery,
      dialogVisible,
      dialogTitle,
      patientForm,
      patientFormRef,
      rules,
      showAddDialog,
      showEditDialog,
      handleDialogClose,
      handleSubmit,
      handleDelete,
      handleSearch,
      handleSizeChange,
      handleCurrentChange
    }
  }
}
</script>

<style scoped>
.patient-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-bar {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>