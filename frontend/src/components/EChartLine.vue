<template>
  <vue-echarts
    class="chart"
    :option="option"
    autoresize
  />
</template>

<script setup>
/* global defineProps */
import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent
} from 'echarts/components'
// Remova esta linha: import VueECharts from 'vue-echarts'

use([
  CanvasRenderer,
  LineChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent
])

const props = defineProps({
  dados: {
    type: Array,
    required: true
  },
  titulo: {
    type: String,
    default: ''
  },
  nomeSerie: {
    type: String,
    default: 'Valor'
  },
  unidadeY: {
    type: String,
    default: ''
  }
})

const option = computed(() => ({
  title: {
    text: props.titulo
  },
  tooltip: {
    trigger: 'axis'
  },
  grid: {
    left: '3%',
    right: '3%',
    bottom: '8%',
    containLabel: true
  },
  xAxis: {
    type: 'time',
    axisLabel: {
      formatter: '{yyyy}-{MM}-{dd} {HH}:{mm}'
    }
  },
  yAxis: {
    type: 'value',
    axisLabel: {
      formatter: value => props.unidadeY ? `${value} ${props.unidadeY}` : value
    }
  },
  series: [
    {
      name: props.nomeSerie,
      type: 'line',
      smooth: true,
      showSymbol: false,
      data: props.dados
    }
  ]
}))
</script>


<style scoped>
.chart {
  width: 100%;
  height: 300px;
}
</style>
