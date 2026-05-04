<script setup>
import { computed } from 'vue'
import { fallbackReading } from '../data/fallbackReading'

const props = defineProps({
  illustration: {
    type: Object,
    default: () => fallbackReading.illustration
  }
})

const illustration = computed(() => ({
  ...fallbackReading.illustration,
  ...props.illustration
}))
</script>

<template>
  <svg class="palm-figure" :viewBox="illustration.viewBox" role="img" aria-labelledby="svg-title svg-desc">
    <title id="svg-title">主要掌纹小插图</title>
    <desc id="svg-desc">黑白细线绘制的手掌轮廓，并标出感情线、智慧线、生命线和事业线。</desc>
    <rect width="420" height="520" fill="#fbfaf7" />
    <g fill="none" stroke="#1f1d1a" stroke-linecap="round" stroke-linejoin="round">
      <path
        d="M86 488 C81 435 57 391 31 342 C3 291 -16 221 9 198 C27 181 51 196 50 230 C49 253 69 257 79 238 C88 221 84 139 87 103 C90 72 113 62 129 80 C143 96 137 209 142 233 C145 249 166 249 168 231 C171 204 166 87 177 57 C185 35 211 32 223 54 C236 78 224 207 230 234 C234 251 256 251 259 233 C263 206 263 126 274 104 C284 84 309 89 316 113 C323 139 305 220 310 247 C315 275 350 246 378 236 C404 226 428 248 418 277 C408 306 361 319 327 339 C290 361 264 403 258 488"
      />
      <path d="M87 488 C106 498 163 500 188 488" opacity=".72" />
      <path :d="illustration.heartLine" stroke-width="1.7" />
      <path :d="illustration.headLine" stroke-width="1.8" />
      <path :d="illustration.lifeLine" stroke-width="1.8" />
      <path :d="illustration.fateLine" stroke-width="1.3" opacity=".78" />
      <path
        v-for="minorLine in illustration.minorLines"
        :key="minorLine"
        :d="minorLine"
        stroke-width=".75"
        opacity=".32"
      />
    </g>
    <g font-family="Georgia, 'Times New Roman', serif" font-size="13" text-anchor="middle">
      <circle cx="279" cy="253" r="13" fill="#1f1d1a" />
      <text x="279" y="258" fill="#fbfaf7">1</text>
      <circle cx="105" cy="359" r="13" fill="#1f1d1a" />
      <text x="105" y="364" fill="#fbfaf7">2</text>
      <circle cx="252" cy="428" r="13" fill="#1f1d1a" />
      <text x="252" y="433" fill="#fbfaf7">3</text>
      <circle cx="210" cy="438" r="13" fill="#1f1d1a" />
      <text x="210" y="443" fill="#fbfaf7">4</text>
    </g>
  </svg>
</template>
