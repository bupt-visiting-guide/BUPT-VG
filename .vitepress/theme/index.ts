import DefaultTheme from 'vitepress/theme'
import type { Theme } from 'vitepress'
import './style.css'
import ExperienceForm from './components/ExperienceForm.vue'
import ExperienceWall from './components/ExperienceWall.vue'

const theme: Theme = {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('ExperienceForm', ExperienceForm)
    app.component('ExperienceWall', ExperienceWall)
  },
}

export default theme
