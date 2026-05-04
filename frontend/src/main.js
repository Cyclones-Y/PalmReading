import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import HomeView from './views/HomeView.vue'
import ReadingView from './views/ReadingView.vue'
import PublicReadingView from './views/PublicReadingView.vue'
import './styles.css'

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/reading/:readingId', name: 'reading', component: ReadingView },
  { path: '/r/:shareToken', name: 'public-reading', component: PublicReadingView }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

createApp(App).use(router).mount('#app')
