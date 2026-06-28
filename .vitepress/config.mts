import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'BUPT 访学指南',
  description: '北邮学生交流访学经验与建议聚合',
  lang: 'zh-CN',

  srcDir: 'docs',
  outDir: 'docs/.vitepress/dist',

  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/logo.svg' }],
  ],

  themeConfig: {
    logo: '/logo.svg',

    nav: [
      { text: '首页', link: '/' },
      { text: '行前准备', link: '/pre-departure/' },
      { text: '学业与科研', link: '/academics/' },
      { text: '生活与心态', link: '/life-and-mindset/' },
      { text: '贡献经验', link: '/contribute/' },
      { text: '资源导航', link: '/resources/' },
    ],

    sidebar: {
      '/pre-departure/': [
        {
          text: '行前准备',
          items: [
            { text: '概览', link: '/pre-departure/' },
            { text: '报到与手续', link: '/pre-departure/registration-and-credits' },
            { text: '行李清单', link: '/pre-departure/packing-checklist' },
          ],
        },
      ],
      '/academics/': [
        {
          text: '学业与科研',
          items: [
            { text: '概览', link: '/academics/' },
            { text: '选课策略', link: '/academics/course-selection' },
            { text: '实验室与科研', link: '/academics/lab-and-research' },
          ],
        },
      ],
      '/life-and-mindset/': [
        {
          text: '生活与心态',
          items: [
            { text: '概览', link: '/life-and-mindset/' },
            { text: '日常生活', link: '/life-and-mindset/daily-life' },
            { text: '心态调整', link: '/life-and-mindset/mental-health' },
          ],
        },
      ],
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/bupt-visiting-guide/BUPT-VG' },
    ],

    editLink: {
      pattern: 'https://github.com/bupt-visiting-guide/BUPT-VG/edit/main/docs/:path',
      text: '在 GitHub 上编辑此页',
    },

    footer: {
      message: '基于 VitePress 构建 · 内容来自北邮访学同学贡献',
      copyright: 'Copyright © 2026–present BUPT Visiting Guide Contributors',
    },

    search: {
      provider: 'local',
    },
  },
})
