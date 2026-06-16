<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

interface Experience {
  id: string
  original_text: string
  category: string
  summary: string
  tags: string[]
  alias: string | null
  major: string | null
}

const props = defineProps<{ category?: string }>()

const all      = ref<Experience[]>([])
const selected = ref<string | null>(null)
const loading  = ref(true)

const dialog    = ref<HTMLDialogElement | null>(null)
const activeExp = ref<Experience | null>(null)

onMounted(async () => {
  try {
    const res  = await fetch('/data/experiences.json')
    const data = await res.json()
    all.value  = data.experiences ?? []
  } catch {
    // stays empty — "暂无数据" message covers this
  } finally {
    loading.value = false
  }
})

const pool = computed(() =>
  props.category ? all.value.filter(e => e.category === props.category) : all.value
)

const allTags = computed(() =>
  [...new Set(pool.value.flatMap(e => e.tags ?? []))].sort()
)

const filtered = computed(() =>
  selected.value ? pool.value.filter(e => e.tags?.includes(selected.value!)) : pool.value
)

function toggle(tag: string) {
  selected.value = selected.value === tag ? null : tag
}

function preview(text: string, limit = 200): string {
  return text.length > limit ? text.slice(0, limit) + '…' : text
}

function openModal(exp: Experience) {
  activeExp.value = exp
  dialog.value?.showModal()
}

function closeModal() {
  dialog.value?.close()
  activeExp.value = null
}
</script>

<template>
  <div class="ew">
    <!-- Tag filter bar -->
    <div v-if="allTags.length" class="ew-filters" role="group" aria-label="按标签筛选">
      <button
        class="ew-chip"
        :class="{ active: !selected }"
        @click="selected = null"
      >
        全部 <span class="ew-count">{{ pool.length }}</span>
      </button>
      <button
        v-for="tag in allTags"
        :key="tag"
        class="ew-chip"
        :class="{ active: selected === tag }"
        @click="toggle(tag)"
      >{{ tag }}</button>
    </div>

    <!-- Card wall -->
    <div v-if="filtered.length" class="ew-grid">
      <article
        v-for="exp in filtered"
        :key="exp.id"
        class="ew-card"
        role="button"
        tabindex="0"
        @click="openModal(exp)"
        @keydown.enter="openModal(exp)"
        @keydown.space.prevent="openModal(exp)"
      >
        <p class="ew-preview">{{ exp.summary }}</p>
        <footer class="ew-footer">
          <span v-for="t in exp.tags" :key="t" class="ew-tag">{{ t }}</span>
          <span v-if="exp.alias" class="ew-alias">— {{ exp.alias }}</span>
        </footer>
      </article>
    </div>

    <p v-else-if="loading" class="ew-state">加载中…</p>
    <p v-else class="ew-state">暂无经验数据。</p>

    <!-- Full-content dialog -->
    <dialog ref="dialog" class="ew-modal" @click.self="closeModal">
      <div class="ew-modal-inner">
        <button class="ew-close" aria-label="关闭" @click="closeModal">✕</button>
        <p class="ew-modal-text">{{ activeExp?.original_text }}</p>
        <footer v-if="activeExp" class="ew-footer ew-modal-footer">
          <span v-for="t in activeExp.tags" :key="t" class="ew-tag">{{ t }}</span>
          <span v-if="activeExp.alias" class="ew-alias">— {{ activeExp.alias }}</span>
        </footer>
      </div>
    </dialog>
  </div>
</template>

<style scoped>
.ew {
  margin-top: 2rem;
}

/* ── Filter chips ── */
.ew-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 1.5rem;
}

.ew-chip {
  padding: 4px 12px;
  border-radius: 999px;
  border: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-2);
  font-size: 0.85rem;
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s, background 0.15s;
}

.ew-chip:hover {
  border-color: var(--vp-c-brand-1);
  color: var(--vp-c-brand-1);
}

.ew-chip.active {
  border-color: var(--vp-c-brand-1);
  background: var(--vp-c-brand-soft);
  color: var(--vp-c-brand-1);
  font-weight: 600;
}

.ew-count {
  font-size: 0.75rem;
  opacity: 0.7;
  margin-left: 2px;
}

/* ── Card wall ── */
.ew-grid {
  columns: 1;
  gap: 1rem;
}

@media (min-width: 640px) {
  .ew-grid { columns: 2; }
}

@media (min-width: 1024px) {
  .ew-grid { columns: 3; }
}

.ew-card {
  break-inside: avoid;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  padding: 1rem 1.2rem;
  margin-bottom: 1rem;
  cursor: pointer;
  transition: box-shadow 0.15s, border-color 0.15s;
}

.ew-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  border-color: var(--vp-c-brand-1);
}

.ew-card:focus-visible {
  outline: 2px solid var(--vp-c-brand-1);
  outline-offset: 2px;
}

/* Preview: clamp to 4 lines */
.ew-preview {
  margin: 0 0 0.75rem;
  font-size: 0.92rem;
  line-height: 1.65;
  color: var(--vp-c-text-1);
  white-space: pre-wrap;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
}

.ew-footer {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  margin-top: 0.5rem;
}

.ew-tag {
  padding: 2px 8px;
  border-radius: 4px;
  background: var(--vp-c-brand-soft);
  color: var(--vp-c-brand-1);
  font-size: 0.78rem;
  font-weight: 500;
}

.ew-alias {
  font-size: 0.8rem;
  color: var(--vp-c-text-3);
  margin-left: auto;
}

.ew-state {
  color: var(--vp-c-text-3);
  font-style: italic;
}

/* ── Modal dialog ── */
.ew-modal {
  width: min(720px, 92vw);
  max-height: 80vh;
  border: none;
  border-radius: 12px;
  padding: 0;
  overflow: hidden;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.25);
  /* Fallback: showModal() raises to top layer, but z-index guards
     against VitePress nav bar overlap in edge cases */
  z-index: 1000;
}

.ew-modal::backdrop {
  background: rgba(0, 0, 0, 0.5);
}

.ew-modal-inner {
  padding: 1.5rem;
  overflow-y: auto;
  max-height: 80vh;
  background: var(--vp-c-bg);
}

.ew-modal-text {
  margin: 0 0 1rem;
  font-size: 0.92rem;
  line-height: 1.75;
  color: var(--vp-c-text-1);
  white-space: pre-wrap;
}

.ew-modal-footer {
  border-top: 1px solid var(--vp-c-divider);
  padding-top: 0.75rem;
}

.ew-close {
  float: right;
  background: none;
  border: none;
  font-size: 1.1rem;
  line-height: 1;
  cursor: pointer;
  color: var(--vp-c-text-2);
  padding: 4px 6px;
  border-radius: 4px;
  transition: color 0.15s, background 0.15s;
}

.ew-close:hover {
  color: var(--vp-c-text-1);
  background: var(--vp-c-bg-soft);
}
</style>
