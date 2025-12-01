<template>
  <div v-if="maquina">
    <h2>{{ maquina.id }} - {{ maquina.equipamento }}</h2>
    <p>Status: {{ maquina.status_operacional }}</p>

    <h3>Alertas</h3>
    <ul>
      <li
        v-for="(valor, chave) in maquina.alertas"
        :key="chave"
        :style="{ color: valor ? 'red' : 'green' }"
      >
        {{ chave }}: {{ valor ? 'ATIVO' : 'normal' }}
      </li>
    </ul>

    <h3>Gráficos de sensores</h3>
    <div
      v-for="(serie, nome) in historico"
      :key="nome"
      style="margin-bottom: 24px"
    >
      <EChartLine
        :dados="serie"
        :titulo="formatarTitulo(nome)"
        :nomeSerie="formatarTitulo(nome)"
      />
    </div>
  </div>
</template>

<script setup>
/* global defineProps */
import EChartLine from './EChartLine.vue'

defineProps({
  maquina: {
    type: Object,
    required: true
  },
  historico: {
    type: Object,
    required: true
  }
})

function formatarTitulo(chave) {
  return chave
    .replace(/_/g, ' ')
    .replace(/lâmina/gi, 'Lâmina')
    .replace(/\b\w/g, m => m.toUpperCase())
}
</script>
