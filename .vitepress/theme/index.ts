import DefaultTheme from 'vitepress/theme'
import type { Theme } from 'vitepress'
import { defineAsyncComponent } from 'vue'

// echarts-wordcloud accesses `document` at import time — SSR-unsafe.
// defineAsyncComponent defers the import to client hydration, avoiding
// "ReferenceError: document is not defined" during vitepress build.
const KeywordBubble = defineAsyncComponent(
  () => import('./components/KeywordBubble.vue')
)

const theme: Theme = {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('KeywordBubble', KeywordBubble)
  },
}

export default theme
