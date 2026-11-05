import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import { cpSync, existsSync, mkdirSync } from 'node:fs'

// Copies ../data/*.json (written by the Python scanner) into the served/built site.
const syncData = () => ({
  name: 'sync-data',
  buildStart() {
    mkdirSync('public/data', { recursive: true })
    for (const f of ['dashboard.json', 'changes.json']) {
      if (existsSync(`../data/${f}`)) cpSync(`../data/${f}`, `public/data/${f}`)
    }
    if (existsSync('../config/site.json')) cpSync('../config/site.json', 'public/data/site.json') // notify_url for sign-ups
  },
})

export default defineConfig({
  base: './', // works at any GitHub Pages sub-path
  plugins: [syncData(), react()],
})
