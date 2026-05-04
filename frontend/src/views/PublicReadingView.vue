<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import PalmReport from '../components/PalmReport.vue'
import { getPublicReading } from '../api/palmReadings'

const route = useRoute()
const reading = ref(null)
const errorMessage = ref('')

onMounted(async () => {
  try {
    reading.value = await getPublicReading(route.params.shareToken)
  } catch (error) {
    errorMessage.value = error.status === 410 ? '报告已过期' : error.message
  }
})
</script>

<template>
  <section v-if="errorMessage" class="state-page">
    <div class="state-card">
      <h1>{{ errorMessage }}</h1>
      <p>这份分享报告可能不存在，或已经超过 7 天留存时间。</p>
    </div>
  </section>

  <section v-else-if="!reading || reading.status === 'processing'" class="state-page">
    <div class="state-card">
      <p class="eyebrow">PALM READING</p>
      <h1>报告正在生成中</h1>
      <p>请稍后刷新查看。</p>
    </div>
  </section>

  <section v-else-if="reading.status === 'failed'" class="state-page">
    <div class="state-card">
      <h1>生成失败</h1>
      <p>{{ reading.errorMessage || 'AI 分析暂时不可用。' }}</p>
    </div>
  </section>

  <PalmReport v-else :result="reading.result" />
</template>
