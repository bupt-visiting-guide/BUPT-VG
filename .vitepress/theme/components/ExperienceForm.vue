<script setup lang="ts">
import { ref } from 'vue'

type Status = 'idle' | 'submitting' | 'success' | 'error'
type Mode   = 'structured' | 'bulk'

const mode       = ref<Mode>('structured')
const category   = ref('')
const content    = ref('')
const major      = ref('')
const rawContent = ref('')
const attachFile = ref<File | null>(null)
const fileError  = ref('')
const status     = ref<Status>('idle')
const errorMsg   = ref('')

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
  if (mode.value === 'bulk' && !rawContent.value.trim() && !attachFile.value) {
    errorMsg.value = '请填写原始文本或上传附件（至少提供其中一项）'
    return
  }

  status.value = 'submitting'
  errorMsg.value = ''

  const fd = new FormData()
  fd.append('form-name', 'experience-submission')
  fd.append('bot-field', '')

  if (mode.value === 'structured') {
    fd.append('category', category.value)
    fd.append('content',  content.value)
    fd.append('major',    major.value)
  } else {
    fd.append('raw_content', rawContent.value)
    if (attachFile.value) fd.append('attachment', attachFile.value)
  }

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
    <!-- 模式切换 -->
    <div class="ef-mode-switch" role="group" aria-label="提交模式">
      <label :class="['ef-mode-btn', { 'ef-mode-btn--active': mode === 'structured' }]">
        <input type="radio" v-model="mode" name="ef-mode" value="structured" class="ef-sr-only" />
        结构化提交
      </label>
      <label :class="['ef-mode-btn', { 'ef-mode-btn--active': mode === 'bulk' }]">
        <input type="radio" v-model="mode" name="ef-mode" value="bulk" class="ef-sr-only" />
        历史数据灌入
      </label>
    </div>

    <!-- 模式 A：结构化字段 -->
    <div v-show="mode === 'structured'" class="ef-field">
      <label for="ef-category">经验分类 <span aria-hidden="true">*</span></label>
      <select id="ef-category" v-model="category" name="category" :required="mode === 'structured'">
        <option value="" disabled>请选择分类</option>
        <option value="行前准备">行前准备</option>
        <option value="学业与科研">学业与科研</option>
        <option value="生活与心态">生活与心态</option>
      </select>
    </div>

    <div v-show="mode === 'structured'" class="ef-field">
      <label for="ef-content">经验内容 <span aria-hidden="true">*</span></label>
      <textarea
        id="ef-content"
        v-model="content"
        name="content"
        rows="6"
        :minlength="mode === 'structured' ? 20 : undefined"
        :required="mode === 'structured'"
        placeholder="请描述你的亲身经验（至少 20 字）"
      />
    </div>

    <div v-show="mode === 'structured'" class="ef-field">
      <label for="ef-major">专业（可选）</label>
      <input
        id="ef-major"
        v-model="major"
        type="text"
        name="major"
        placeholder="例如：计算机科学 / 通信工程"
      />
    </div>

    <!-- 模式 B：非结构化字段 -->
    <div v-show="mode === 'bulk'">
      <div class="ef-field">
        <label for="ef-raw-content">原始文本（粘贴微信记录 / 邮件等）</label>
        <textarea
          id="ef-raw-content"
          v-model="rawContent"
          name="raw_content"
          rows="10"
          placeholder="将非结构化文本直接粘贴于此"
        />
      </div>

      <div class="ef-field">
        <label for="ef-attachment">文件附件（PDF / Word / TXT，≤ 5 MB）</label>
        <input
          id="ef-attachment"
          type="file"
          name="attachment"
          accept=".pdf,.doc,.docx,.txt"
          class="ef-file-input"
          @change="handleFileChange"
        />
        <p v-if="fileError" class="ef-error" role="alert">{{ fileError }}</p>
      </div>
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
.ef-mode-switch {
  display: flex;
  gap: 0;
  border: 1px solid var(--vp-c-divider);
  border-radius: 20px;
  overflow: hidden;
  width: fit-content;
}
.ef-mode-btn {
  padding: 0.4rem 1.1rem;
  font-size: 0.88rem;
  font-weight: 500;
  cursor: pointer;
  color: var(--vp-c-text-2);
  background: transparent;
  transition: background 0.15s, color 0.15s;
  user-select: none;
}
.ef-mode-btn--active {
  background: var(--vp-c-brand-1);
  color: var(--vp-button-brand-text);
}
.ef-sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
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
