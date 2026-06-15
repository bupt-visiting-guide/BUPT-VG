import DefaultTheme from 'vitepress/theme'
import type { Theme } from 'vitepress'
import ExperienceForm from './components/ExperienceForm.vue'

const theme: Theme = {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('ExperienceForm', ExperienceForm)
  },
}

export default theme
