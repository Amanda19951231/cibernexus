<template>
  <div id="app" class="container-fluid">
    <div class="navbar-custom">
      <h1>🏭 Dashboard de Monitoramento de Máquinas</h1>
    </div>

    <div class="main-content">
      <ul class="nav nav-tabs" role="tablist">
        <li class="nav-item">
          <button class="nav-link" :class="{ active: activeTab === 'general' }" @click="activeTab = 'general'">
            📊 Visão Geral
          </button>
        </li>
        <li class="nav-item" v-for="machine in machines" :key="machine.id">
          <button class="nav-link" :class="{ active: activeTab === machine.id }" @click="activeTab = machine.id">
            🔧 {{ getMachineName(machine.equipamento) }}
          </button>
        </li>
      </ul>

      <!-- ABA GERAL -->
      <div v-if="activeTab === 'general'">
        <h2 class="mb-4">Resumo Geral do Sistema</h2>
        <div class="general-grid row">
          <div class="metric-card col-md-12">
            <div class="metric-label">Máquinas em Operação</div>
            <div class="metric-value">{{ machinesRunning }}<span class="metric-unit">/ {{ machines.length }}</span></div>
          </div>
          <div class="metric-card col-md-12">
            <div class="metric-label">Alertas Críticos</div>
            <div class="metric-value" style="color: var(--danger-color);">{{ totalCriticalAlerts }}</div>
          </div>
          <div class="metric-card col-md-12">
            <div class="metric-label">Alertas de Aviso</div>
            <div class="metric-value" style="color: var(--warning-color);">{{ totalWarningAlerts }}</div>
          </div>
          <div class="metric-card col-md-12">
            <div class="metric-label">Taxa de Saúde</div>
            <div class="metric-value" style="color: var(--success-color);">{{ systemHealth }}%</div>
          </div>
        </div>

        <div class="chart-container">
          <h3 class="chart-title">Status de Todas as Máquinas</h3>
          <div class="chart-wrapper" ref="statusChart"></div>
        </div>

        <div class="row">
          <div class="col-md-6">
            <div class="chart-container">
              <h3 class="chart-title">Distribuição de Alertas</h3>
              <div class="chart-wrapper" ref="alertsChart"></div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="chart-container">
              <h3 class="chart-title">Últimos Alertas</h3>
              <div style="max-height: 350px; overflow-y: auto;">
                <div v-if="recentAlerts.length === 0" class="p-3 text-center text-muted">
                  Nenhum alerta recente
                </div>
                <div v-for="alert in recentAlerts" :key="alert.key" class="alert-card" :class="alert.type">
                  <div class="alert-title">{{ alert.machine }}</div>
                  <div style="font-size: 0.9rem;">{{ alert.message }}</div>
                  <div style="font-size: 0.8rem; color: #999; margin-top: 0.5rem;">{{ alert.timestamp }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ABAS INDIVIDUAIS DAS MÁQUINAS -->
      <div v-for="machine in machines" :key="machine.id" v-show="activeTab === machine.id">
        <div class="machine-header d-flex justify-content-between align-items-center">
          <div>
            <h2 class="machine-title">{{ getMachineName(machine.equipamento) }}</h2>
            <div style="font-size: 0.9rem; color: #666; margin-top: 0.5rem;">
              ID: {{ machine.id }} | Última atualização: {{ formatTime(machine.timestamp) }}
            </div>
          </div>
          <div class="alert-summary">
            <span class="status-badge" :class="machine.status_operacional === 'executando' ? 'active' : 'inactive'">
              {{ machine.status_operacional.toUpperCase() }}
            </span>
          </div>
        </div>

        <div class="chart-container">
          <h3 class="chart-title">⚠️ Alertas e Status</h3>
          <div class="row">
            <div class="col-md-12">
              <div v-if="hasAlerts(machine)" style="display: flex; flex-wrap: wrap; gap: 1rem;">
                <div v-for="alert in getActiveAlerts(machine)" :key="alert.key" class="alert-card">
                  <div class="alert-title">🚨 {{ formatAlertName(alert.key) }}</div>
                  <div style="font-size: 0.9rem; color: #666;">Ativo desde última atualização</div>
                </div>
              </div>
              <div v-else style="padding: 1rem; background: rgba(76, 175, 80, 0.1); border-radius: 4px; color: var(--success-color); font-weight: 600;">
                ✓ Nenhum alerta ativo - Sistema operacional
              </div>
            </div>
          </div>
        </div>

        <div class="row">
          <div v-for="(sensor, sensorName) in getSensorCharts(machine)" :key="sensorName" class="col-md-6">
            <div class="chart-container">
              <h3 class="chart-title">{{ sensor.label }}</h3>
              <div class="chart-wrapper" :ref="machine.id + '_' + sensorName"></div>
            </div>
          </div>
        </div>

        <div class="chart-container">
          <h3 class="chart-title">Dados Atuais dos Sensores</h3>
          <div class="row">
            <div v-for="(sensor, sensorName) in getSensorData(machine)" :key="sensorName" class="col-md-3">
              <div class="metric-card" style="margin-bottom: 1rem;">
                <div class="metric-label">{{ sensor.label }}</div>
                <div class="metric-value">{{ sensor.value }}<span class="metric-unit">{{ sensor.unit }}</span></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

export default {
  name: 'App',
  setup() {
    const activeTab = ref('general')
    const machines = ref([
      {
        equipamento: "corte_laser",
        id: "LASER_001",
        timestamp: "2024-01-15T14:30:00Z",
        status_operacional: "executando",
        dados_sensores: {
          temperatura_interna: 42.5,
          vibracao: 2.1,
          consumo_energetico: 15.75,
          porta_seguranca: true
        },
        alertas: {
          temperatura_alta: false,
          vibracao_excessiva: false,
          porta_aberta: false
        }
      },
      {
        equipamento: "puncionadeira",
        id: "PUNC_001",
        timestamp: "2024-01-15T14:30:00Z",
        status_operacional: "executando",
        dados_sensores: {
          pressao_hidraulica: 120.5,
          golpes_por_minuto: 45,
          emergencia_acionada: false
        },
        metricas_producao: {
          ciclos_hora: 2700,
          eficiencia: 92.5
        },
        alertas: {
          pressao_alta: false,
          emergencia_ativa: false
        }
      },
      {
        equipamento: "serra_fita",
        id: "SERRA_001",
        timestamp: "2024-01-15T14:30:00Z",
        status_operacional: "executando",
        dados_sensores: {
          velocidade_lâmina: 1250,
          vibracao: 1.8,
          temperatura_motor: 65.2
        },
        alertas: {
          motor_superaquecendo: false,
          vibracao_excessiva: false
        }
      },
      {
        equipamento: "solda",
        id: "SOLDA_001",
        timestamp: "2024-01-15T14:30:00Z",
        status_operacional: "executando",
        dados_sensores: {
          corrente: 150.0,
          tensao: 24.0,
          fumaca_particulas: 12.5,
          temperatura_solda: 320.0
        },
        qualidade_solda: {
          estabilidade_arco: 95.2,
          qualidade_media: "excelente"
        },
        alertas: {
          fumaca_excessiva: false,
          temperatura_alta: false
        }
      },
      {
        equipamento: "dobradeira",
        id: "DOBRA_001",
        timestamp: "2024-01-15T14:30:00Z",
        status_operacional: "executando",
        dados_sensores: {
          pressao_hidraulica: 85.3,
          alinhamento_lâmina: 0.05,
          barreira_optica_ativa: true
        },
        precisao: {
          tolerancia_atual: 0.02,
          desvio_medio: 0.01
        },
        alertas: {
          alinhamento_fora_especificacao: false,
          barreira_violada: false
        }
      }
    ])

    const charts = ref({})

    // Declaração correta dos refs para os gráficos principais
    const statusChart = ref(null)
    const alertsChart = ref(null)

    const getMachineName = (equipamento) => {
      const names = {
        'corte_laser': 'Corte a Laser',
        'puncionadeira': 'Puncionadeira',
        'serra_fita': 'Serra de Fita',
        'solda': 'Máquina de Solda',
        'dobradeira': 'Dobradeira'
      }
      return names[equipamento] || equipamento
    }

    const formatAlertName = (alertKey) => {
      return alertKey
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ')
    }

    const formatTime = (isoString) => {
      return new Date(isoString).toLocaleString('pt-BR')
    }

    const hasAlerts = (machine) => {
      return Object.values(machine.alertas).some(a => a === true)
    }

    const getSensorData = (machine) => {
      const sensors = []
      const sensorMappings = {
        'temperatura_interna': { label: '🌡️ Temperatura Interna', unit: '°C' },
        'vibracao': { label: '📳 Vibração', unit: 'mm/s' },
        'consumo_energetico': { label: '⚡ Consumo Energético', unit: 'kW' },
        'pressao_hidraulica': { label: '💧 Pressão Hidráulica', unit: 'bar' },
        'golpes_por_minuto': { label: '⚙️ Golpes/min', unit: 'gpm' },
        'velocidade_lâmina': { label: '⚡ Velocidade Lâmina', unit: 'm/min' },
        'temperatura_motor': { label: '🌡️ Temperatura Motor', unit: '°C' },
        'corrente': { label: '⚡ Corrente', unit: 'A' },
        'tensao': { label: '📊 Tensão', unit: 'V' },
        'fumaca_particulas': { label: '💨 Fumaça/Partículas', unit: 'mg/m³' },
        'temperatura_solda': { label: '🔥 Temperatura Solda', unit: '°C' },
        'alinhamento_lâmina': { label: '📐 Alinhamento Lâmina', unit: 'mm' },
        'estabilidade_arco': { label: '✨ Estabilidade Arco', unit: '%' },
        'ciclos_hora': { label: '⚙️ Ciclos/Hora', unit: 'ciclos' },
        'eficiencia': { label: '📈 Eficiência', unit: '%' },
        'tolerancia_atual': { label: '📏 Tolerância Atual', unit: 'mm' },
        'desvio_medio': { label: '📊 Desvio Médio', unit: 'mm' }
      }

      Object.entries(machine.dados_sensores).forEach(([key, value]) => {
        if (typeof value === 'number' && sensorMappings[key]) {
          sensors.push({
            key: key,
            label: sensorMappings[key].label,
            value: typeof value === 'number' ? value.toFixed(2) : value,
            unit: sensorMappings[key].unit
          })
        }
      })

      Object.entries(machine.metricas_producao || {}).forEach(([key, value]) => {
        if (typeof value === 'number' && sensorMappings[key]) {
          sensors.push({
            key: key,
            label: sensorMappings[key].label,
            value: typeof value === 'number' ? value.toFixed(2) : value,
            unit: sensorMappings[key].unit
          })
        }
      })

      Object.entries(machine.qualidade_solda || {}).forEach(([key, value]) => {
        if (typeof value === 'number' && sensorMappings[key]) {
          sensors.push({
            key: key,
            label: sensorMappings[key].label,
            value: typeof value === 'number' ? value.toFixed(2) : value,
            unit: sensorMappings[key].unit
          })
        }
      })

      Object.entries(machine.precisao || {}).forEach(([key, value]) => {
        if (typeof value === 'number' && sensorMappings[key]) {
          sensors.push({
            key: key,
            label: sensorMappings[key].label,
            value: typeof value === 'number' ? value.toFixed(3) : value,
            unit: sensorMappings[key].unit
          })
        }
      })

      return sensors
    }

    const getSensorCharts = (machine) => {
      const charts = []
      const sensorMappings = {
        'temperatura_interna': { label: '🌡️ Temperatura Interna (°C)', unit: '°C' },
        'vibracao': { label: '📳 Vibração (mm/s)', unit: 'mm/s' },
        'consumo_energetico': { label: '⚡ Consumo Energético (kW)', unit: 'kW' },
        'pressao_hidraulica': { label: '💧 Pressão Hidráulica (bar)', unit: 'bar' },
        'golpes_por_minuto': { label: '⚙️ Golpes por Minuto', unit: 'gpm' },
        'velocidade_lâmina': { label: '⚡ Velocidade Lâmina (m/min)', unit: 'm/min' },
        'temperatura_motor': { label: '🌡️ Temperatura Motor (°C)', unit: '°C' },
        'corrente': { label: '⚡ Corrente (A)', unit: 'A' },
        'tensao': { label: '📊 Tensão (V)', unit: 'V' },
        'fumaca_particulas': { label: '💨 Fumaça/Partículas (mg/m³)', unit: 'mg/m³' },
        'temperatura_solda': { label: '🔥 Temperatura Solda (°C)', unit: '°C' },
        'alinhamento_lâmina': { label: '📐 Alinhamento Lâmina (mm)', unit: 'mm' },
        'estabilidade_arco': { label: '✨ Estabilidade Arco (%)', unit: '%' },
        'ciclos_hora': { label: '⚙️ Ciclos por Hora', unit: 'ciclos' },
        'eficiencia': { label: '📈 Eficiência (%)', unit: '%' },
        'tolerancia_atual': { label: '📏 Tolerância Atual (mm)', unit: 'mm' },
        'desvio_medio': { label: '📊 Desvio Médio (mm)', unit: 'mm' }
      }

      Object.entries(machine.dados_sensores).forEach(([key, value]) => {
        if (typeof value === 'number' && sensorMappings[key]) {
          charts.push({
            key: key,
            label: sensorMappings[key].label,
            unit: sensorMappings[key].unit
          })
        }
      })

      Object.entries(machine.metricas_producao || {}).forEach(([key, value]) => {
        if (typeof value === 'number' && sensorMappings[key]) {
          charts.push({
            key: key,
            label: sensorMappings[key].label,
            unit: sensorMappings[key].unit
          })
        }
      })

      Object.entries(machine.qualidade_solda || {}).forEach(([key, value]) => {
        if (typeof value === 'number' && sensorMappings[key]) {
          charts.push({
            key: key,
            label: sensorMappings[key].label,
            unit: sensorMappings[key].unit
          })
        }
      })

      Object.entries(machine.precisao || {}).forEach(([key, value]) => {
        if (typeof value === 'number' && sensorMappings[key]) {
          charts.push({
            key: key,
            label: sensorMappings[key].label,
            unit: sensorMappings[key].unit
          })
        }
      })

      return charts
    }

    const machinesRunning = computed(() => {
      return machines.value.filter(m => m.status_operacional === 'executando').length
    })

    const totalCriticalAlerts = computed(() => {
      return machines.value.reduce((sum, machine) => {
        return sum + Object.values(machine.alertas).filter(a => a).length
      }, 0)
    })

    const totalWarningAlerts = computed(() => 0)

    const systemHealth = computed(() => {
      const alertsCount = totalCriticalAlerts.value
      return Math.max(0, 100 - (alertsCount * 10))
    })

    const recentAlerts = computed(() => {
      const alerts = []
      machines.value.forEach(machine => {
        Object.entries(machine.alertas).forEach(([key, value]) => {
          if (value) {
            alerts.push({
              key: machine.id + '_' + key,
              machine: getMachineName(machine.equipamento),
              message: formatAlertName(key),
              timestamp: formatTime(machine.timestamp),
              type: 'warning'
            })
          }
        })
      })
      return alerts.slice(0, 5)
    })

    const initCharts = () => {
      nextTick(() => {
        // Gráfico de Status Geral
        if (statusChart.value && !charts.value['statusChart']) {
          const chart = echarts.init(statusChart.value)
          chart.setOption({
            tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
            grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
            xAxis: {
              type: 'category',
              data: machines.value.map(m => getMachineName(m.equipamento)),
              axisLabel: { interval: 0, rotate: 45 }
            },
            yAxis: { type: 'value' },
            series: [{
              name: 'Status',
              data: machines.value.map(m => m.status_operacional === 'executando' ? 1 : 0),
              type: 'bar',
              itemStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  { offset: 0, color: '#83bff6' },
                  { offset: 0.5, color: '#188df0' },
                  { offset: 1, color: '#188df0' }
                ])
              }
            }]
          })
          charts.value['statusChart'] = chart
        }

        // Gráfico de Alertas
        if (alertsChart.value && !charts.value['alertsChart']) {
          const chart = echarts.init(alertsChart.value)
          chart.setOption({
            tooltip: { trigger: 'item', formatter: '{b}: {c}' },
            series: [{
              name: 'Alertas',
              type: 'pie',
              radius: '50%',
              data: [
                { value: totalCriticalAlerts.value, name: 'Críticos' },
                { value: machinesRunning.value - totalCriticalAlerts.value, name: 'Normais' }
              ],
              itemStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 1, 1, [
                  { offset: 0, color: '#fccb05' },
                  { offset: 1, color: '#d81b60' }
                ])
              }
            }]
          })
          charts.value['alertsChart'] = chart
        }

        // Gráficos de Sensores por Máquina
        machines.value.forEach(machine => {
          getSensorCharts(machine).forEach(sensor => {
            const chartId = machine.id + '_' + sensor.key
            const chartDom = document.getElementById(chartId)
            if (chartDom && !charts.value[chartId]) {
              const chart = echarts.init(chartDom)
              const value = machine.dados_sensores[sensor.key] || 
                  machine.metricas_producao?.[sensor.key] ||
                  machine.qualidade_solda?.[sensor.key] ||
                  machine.precisao?.[sensor.key] || 0

              // Gerar dados históricos simulados
              const now = new Date(machine.timestamp)
              const timeLabels = []
              const dataPoints = []

              for (let i = 11; i >= 0; i--) {
                const time = new Date(now.getTime() - i * 5 * 60000)
                timeLabels.push(time.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }))
                const variance = (Math.random() - 0.5) * value * 0.1
                dataPoints.push(parseFloat((value + variance).toFixed(2)))
              }

              chart.setOption({
                tooltip: { trigger: 'axis', formatter: '{b}: {c} ' + sensor.unit },
                grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
                xAxis: {
                  type: 'category',
                  data: timeLabels,
                  axisLabel: { rotate: 45 }
                },
                yAxis: { type: 'value' },
                series: [{
                  name: sensor.label,
                  data: dataPoints,
                  type: 'line',
                  smooth: true,
                  itemStyle: { color: '#2196F3' },
                  areaStyle: { color: 'rgba(33, 150, 243, 0.3)' }
                }]
              })
              charts.value[chartId] = chart
            }
          })
        })
      })
    }

    const handleResize = () => {
      Object.values(charts.value).forEach(chart => {
        if (chart) chart.resize()
      })
    }

    onMounted(() => {
      initCharts()
      window.addEventListener('resize', handleResize)
    })

    onUnmounted(() => {
      window.removeEventListener('resize', handleResize)
    })

    watch(activeTab, () => {
      initCharts()
    })

    return {
      activeTab,
      machines,
      machinesRunning,
      totalCriticalAlerts,
      totalWarningAlerts,
      systemHealth,
      recentAlerts,
      getMachineName,
      formatAlertName,
      formatTime,
      hasAlerts,
      getSensorData,
      getSensorCharts,
      statusChart,
      alertsChart
    }
  }
}
</script>

<style scoped>
:root {
  --primary-color: #2196F3;
  --success-color: #4CAF50;
  --warning-color: #FF9800;
  --danger-color: #F44336;
  --dark-bg: #1a1a1a;
  --light-bg: #f5f5f5;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: var(--light-bg);
  color: #333;
}

.navbar-custom {
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
  color: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.navbar-custom h1 {
  font-size: 1.8rem;
  font-weight: 600;
  margin: 0;
}

.main-content {
  flex: 1;
  padding: 2rem;
}

.nav-link {
  color: #666;
  font-weight: 500;
  border: none;
  border-bottom: 3px solid transparent;
  transition: all 0.3s ease;
}

.nav-link:hover {
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
}

.nav-link.active {
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
  background: none;
}

.chart-container {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.chart-title {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #2c3e50;
}

.chart-wrapper {
  width: 100%;
  height: 350px;
  border-radius: 4px;
  overflow: hidden;
}

.alert-card {
  background: white;
  border-left: 4px solid var(--danger-color);
  padding: 1rem;
  margin-bottom: 1rem;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.alert-card.warning {
  border-left-color: var(--warning-color);
}

.alert-card.success {
  border-left-color: var(--success-color);
}

.alert-title {
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.status-badge {
  display: inline-block;
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
}

.status-badge.active {
  background-color: var(--success-color);
  color: white;
}

.status-badge.inactive {
  background-color: #ccc;
  color: #333;
}

.metric-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  border-top: 4px solid var(--primary-color);
}

.metric-label {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.metric-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--primary-color);
}

.metric-unit {
  font-size: 0.9rem;
  color: #999;
  margin-left: 0.5rem;
}

.general-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.machine-header {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.machine-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2c3e50;
}

.alert-summary {
  display: flex;
  gap: 1rem;
}

.alert-count {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.9rem;
}

.alert-count.error {
  background-color: rgba(244, 67, 54, 0.15);
  color: var(--danger-color);
}

.alert-count.warning {
  background-color: rgba(255, 152, 0, 0.15);
  color: var(--warning-color);
}

.alert-count.ok {
  background-color: rgba(76, 175, 80, 0.15);
  color: var(--success-color);
}

@media (max-width: 768px) {
  .main-content {
    padding: 1rem;
  }

  .chart-wrapper {
    height: 250px;
  }

  .general-grid {
    grid-template-columns: 1fr;
  }

  .machine-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
}
</style>
