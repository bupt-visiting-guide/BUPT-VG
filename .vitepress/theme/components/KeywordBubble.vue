<script setup lang="ts">
import { ref, onMounted } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import 'echarts-wordcloud'

use([CanvasRenderer])

interface KeywordEntry {
  name: string
  value: number
}

interface KeywordsJson {
  generated: string
  keywords: KeywordEntry[]
}

const loading = ref(true)
const error = ref<string | null>(null)
const option = ref<Record<string, unknown>>({})

function buildOption(keywords: KeywordEntry[]): Record<string, unknown> {
  return {
    tooltip: {
      show: true,
      formatter: (params: { name: string; value: number }) =>
        `${params.name}: ${params.value} 次提及`,
    },
    series: [
      {
        type: 'wordCloud',
        shape: 'circle',
        keepAspect: false,
        width: '100%',
        height: '100%',
        sizeRange: [14, 72],
        rotationRange: [-45, 45],
        rotationStep: 15,
        gridSize: 8,
        drawOutOfBound: false,
        textStyle: {
          fontFamily: '"PingFang SC", "Microsoft YaHei", sans-serif',
          fontWeight: 'bold',
          color() {
            const palette = [
              '#1a6fcf', '#2e86de', '#54a0ff',
              '#e74c3c', '#e67e22', '#27ae60',
              '#8e44ad', '#16a085',
            ]
            return palette[Math.floor(Math.random() * palette.length)]
          },
        },
        emphasis: {
          focus: 'self',
          textStyle: { shadowBlur: 10, shadowColor: '#333' },
        },
        data: keywords,
      },
    ],
  }
}

onMounted(async () => {
  try {
    const res = await fetch('/data/keywords.json')
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const json: KeywordsJson = await res.json()
    option.value = buildOption(json.keywords)
  } catch (e) {
    error.value = `无法加载关键词数据：${(e as Error).message}`
    console.error('[KeywordBubble]', e)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="keyword-bubble-wrapper">
    <div v-if="loading" class="kb-placeholder">关键词图谱加载中…</div>
    <div v-else-if="error" class="kb-error">{{ error }}</div>
    <VChart
      v-else
      class="kb-chart"
      :option="option"
      autoresize
    />
  </div>
</template>

<style scoped>
.keyword-bubble-wrapper {
  width: 100%;
  margin: 2rem 0;
}

.kb-chart {
  width: 100%;
  height: 480px;
}

.kb-placeholder,
.kb-error {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: var(--vp-c-text-2);
  font-size: 0.9rem;
}

.kb-error {
  color: var(--vp-c-danger-1);
}
</style>
