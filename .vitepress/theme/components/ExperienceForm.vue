<script setup lang="ts">
import { ref } from 'vue'

type Status = 'idle' | 'submitting' | 'success' | 'error'

const category   = ref('')
const content    = ref('')
const alias      = ref('')
const attachFile = ref<File | null>(null)
const fileError  = ref('')
const contentError = ref('')
const status     = ref<Status>('idle')
const errorMsg   = ref('')

const MIN_CONTENT_LENGTH = 20
const MAX_FILE_BYTES = 5 * 1024 * 1024

function handleFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0] ?? null
  if (file && file.size > MAX_FILE_BYTES) {
    fileError.value = `文件过大（${(file.size / 1024 / 1024).toFixed(1)} MB），请上传 5 MB 以内的文件`
    attachFile.value = null
    ;(e.target as HTMLInputElement).value = ''
    return
  }
  fileError.value = ''
  attachFile.value = file
}

async function handleSubmit() {
  // 至少需要文本内容或文件附件之一
  contentError.value = ''
  if (content.value.trim().length < MIN_CONTENT_LENGTH && !attachFile.value) {
    contentError.value = `请填写经验内容（至少 ${MIN_CONTENT_LENGTH} 字），或上传文件附件`
    return
  }

  status.value = 'submitting'
  errorMsg.value = ''

  const fd = new FormData()
  fd.append('form-name', 'experience-submission')
  fd.append('bot-field', '')
  fd.append('category', category.value)
  fd.append('content', content.value)
  fd.append('alias', alias.value)
  if (attachFile.value) fd.append('attachment', attachFile.value)

  try {
    // 不设置 Content-Type，让浏览器自动生成带 boundary 的 multipart/form-data 头
    const res = await fetch('/', { method: 'POST', body: fd })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    status.value = 'success'
  } catch (e) {
    errorMsg.value = `提交失败：${(e as Error).message}`
    status.value = 'error'
  }
}
</script>

<template>
  <form
    v-if="status !== 'success'"
    class="ef-form"
    @submit.prevent="handleSubmit"
  >
    <div class="ef-field">
      <label for="ef-category">经验分类（选填）</label>
      <select id="ef-category" v-model="category" name="category">
        <option value="">请选择分类</option>
        <option value="行前准备">行前准备</option>
        <option value="学业与科研">学业与科研</option>
        <option value="生活与心态">生活与心态</option>
      </select>
    </div>

    <div class="ef-field">
      <label for="ef-content">经验内容 <span aria-hidden="true">*</span></label>
      <textarea
        id="ef-content"
        v-model="content"
        name="content"
        rows="6"
        placeholder="请描述你的亲身经验，或上传文件附件（二选一即可）"
      />
      <p v-if="contentError" class="ef-error" role="alert">{{ contentError }}</p>
    </div>

    <div class="ef-field">
      <label for="ef-attachment">文件附件（PDF / Word / TXT，≤ 5 MB，选填）</label>
      <input
        id="ef-attachment"
        type="file"
        name="attachment"
        accept=".pdf,.txt,.doc,.docx"
        class="ef-file-input"
        @change="handleFileChange"
      />
      <p v-if="fileError" class="ef-error" role="alert">{{ fileError }}</p>
    </div>

    <div class="ef-field">
      <label for="ef-alias">化名（选填）</label>
      <input
        id="ef-alias"
        v-model="alias"
        type="text"
        name="alias"
        placeholder="例如：沙河老学长 / 匿名理工妹"
      />
    </div>

    <p v-if="status === 'error'" class="ef-error" role="alert">{{ errorMsg }}</p>

    <button type="submit" class="ef-submit" :disabled="status === 'submitting'">
      {{ status === 'submitting' ? '提交中…' : '提交经验' }}
    </button>
  </form>

  <div v-else class="ef-success" role="status">
    感谢你的分享！你的经验已成功提交，将在审核后收录到本指南中。
  </div>
</template>

<style scoped>
.ef-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  max-width: 600px;
  margin: 1.5rem 0;
}
.ef-field {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.ef-field label {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--vp-c-text-1);
}
.ef-field label span {
  color: var(--vp-c-danger-1);
  margin-left: 2px;
}
.ef-field select,
.ef-field textarea,
.ef-field input[type="text"] {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-1);
  font-size: 0.95rem;
  font-family: inherit;
  transition: border-color 0.2s;
}
.ef-field select:focus,
.ef-field textarea:focus,
.ef-field input[type="text"]:focus {
  outline: none;
  border-color: var(--vp-c-brand-1);
}
.ef-field textarea {
  resize: vertical;
  min-height: 120px;
}
.ef-file-input {
  font-size: 0.9rem;
  color: var(--vp-c-text-1);
}
.ef-submit {
  align-self: flex-start;
  padding: 0.55rem 1.5rem;
  background: var(--vp-c-brand-1);
  color: var(--vp-button-brand-text);
  border: none;
  border-radius: 20px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s, opacity 0.2s;
}
.ef-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.ef-submit:not(:disabled):hover {
  background: var(--vp-c-brand-2);
}
.ef-error {
  color: var(--vp-c-danger-1);
  font-size: 0.9rem;
  margin: 0;
}
.ef-success {
  padding: 1rem 1.25rem;
  border-left: 4px solid var(--vp-c-brand-1);
  background: var(--vp-c-brand-soft);
  color: var(--vp-c-text-1);
  border-radius: 4px;
  font-size: 0.95rem;
  margin: 1.5rem 0;
}
</style>
