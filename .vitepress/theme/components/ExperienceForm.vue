<script setup lang="ts">
import { ref } from 'vue'

type Status = 'idle' | 'submitting' | 'success' | 'error'

const category = ref('')
const content  = ref('')
const alias    = ref('')
const status   = ref<Status>('idle')
const errorMsg = ref('')

async function handleSubmit() {
  status.value = 'submitting'
  errorMsg.value = ''

  const body = new URLSearchParams({
    'form-name': 'experience-submission',
    'bot-field':  '',
    category:    category.value,
    content:     content.value,
    alias:       alias.value,
  })

  try {
    const res = await fetch('/', {
      method:  'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body:    body.toString(),
    })
    await res.body?.cancel()
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
      <label for="ef-category">经验分类 <span aria-hidden="true">*</span></label>
      <select id="ef-category" v-model="category" name="category" required>
        <option value="" disabled>请选择分类</option>
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
        minlength="20"
        required
        placeholder="请描述你的亲身经验（至少 20 字）"
      />
    </div>

    <div class="ef-field">
      <label for="ef-alias">昵称 / 专业（可选）</label>
      <input
        id="ef-alias"
        v-model="alias"
        type="text"
        name="alias"
        placeholder="匿名提交请留空"
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
