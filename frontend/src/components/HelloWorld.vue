<script>
import { onMounted, reactive, ref } from 'vue';
import Chart from 'chart.js/auto';

export default {
  name: 'DashboardIndustrial',
  setup() {
    const activeTab = ref('geral');

    const tabs = [
      { id: 'geral', label: 'Dashboard Geral' },
      { id: 'LASER_001', label: 'Corte Laser' },
      { id: 'PUNC_001', label: 'Puncionadeira' },
      { id: 'SERRA_001', label: 'Serra Fita' },
      { id: 'SOLDA_001', label: 'Solda' },
      { id: 'DOBRA_001', label: 'Dobradeira' },
    ];

    const equipamentos = reactive([
      {
        id: 'LASER_001',
        dados: { temperatura_interna: 42.5, vibracao: 2.1, consumo_energetico: 15.75, porta_seguranca: 1 },
        alertas: { temperatura_alta: false, vibracao_excessiva: true, porta_aberta: false }
      },
      {
        id: 'PUNC_001',
        dados: { pressao_hidraulica: 120.5, golpes_por_minuto: 45, emergencia_acionada: 0 },
        alertas: { pressao_alta: true, emergencia_ativa: false }
      },
      {
        id: 'SERRA_001',
        dados: { velocidade_lâmina: 1250, vibracao: 1.8, temperatura_motor: 65.2 },
        alertas: { motor_superaquecendo: false, vibracao_excessiva: false }
      },
      {
        id: 'SOLDA_001',
        dados: { corrente: 150.0, tensao: 24.0, fumaca_particulas: 12.5, temperatura_solda: 320.0 },
        alertas: { fumaca_excessiva: false, temperatura_alta: true }
      },
      {
        id: 'DOBRA_001',
        dados: { pressao_hidraulica: 85.3, alinhamento_lâmina: 0.05, barreira_optica_ativa: 1 },
        alertas: { alinhamento_fora_especificacao: false, barreira_violada: false }
      }
    ]);

    const simulateData = (value) => {
      const variation = value * 0.05;
      return +(value + (Math.random() * variation * 2 - variation)).toFixed(2);
    };

    const createLineChart = (canvasId, dataObj) => {
      const labels = Array.from({ length: 20 }, (_, i) => `T-${20 - i}`);
      const datasets = Object.entries(dataObj).map(([key, val], idx) => ({
        label: key,
        data: labels.map(() => simulateData(val)),
        borderColor: `hsl(${idx * 60}, 70%, 60%)`,
        backgroundColor: 'transparent',
        tension: 0.3,
        pointRadius: 3
      }));
      new Chart(document.getElementById(canvasId), {
        type: 'line',
        data: { labels, datasets },
        options: {
          responsive: true,
          plugins: { legend: { labels: { color: '#fff' } } },
          scales: {
            x: { ticks: { color: '#fff' }, grid: { color: '#333' } },
            y: { ticks: { color: '#fff' }, grid: { color: '#333' } }
          }
        }
      });
    };

    const createAlerts = () => {
      equipamentos.forEach(eq => {
        const container = document.getElementById(`alerts_${eq.id}`);
        for (const [alertName, active] of Object.entries(eq.alertas)) {
          const div = document.createElement('div');
          div.className = `alert ${active ? 'active' : 'inactive'}`;
          div.innerHTML = `${alertName.replace(/_/g,' ')} <span>${active ? 'ATIVO' : 'OK'}</span>`;
          container.appendChild(div);
        }
      });
    };

    onMounted(() => {
      equipamentos.forEach(eq => {
        createLineChart(`chart_${eq.id}`, eq.dados);
        createLineChart(`chart_ind_${eq.id}`, eq.dados);
      });
      createAlerts();
    });

    return { activeTab, tabs, equipamentos };
  }
};
</script>
<template>
  <div class="dashboard">
    <div class="tabs">
      <div
        v-for="tab in tabs"
        :key="tab.id"
        :class="['tab', { active: activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        {{ tab.label }}
      </div>
    </div>

    <!-- Dashboard Geral -->
    <div class="content" v-show="activeTab === 'geral'">
      <div class="chart-container">
        <div class="chart-box" v-for="eq in equipamentos" :key="eq.id">
          <canvas :id="'chart_' + eq.id"></canvas>
        </div>
      </div>
    </div>

    <!-- Abas individuais -->
    <div
      class="content"
      v-for="eq in equipamentos"
      :key="eq.id + '_content'"
      v-show="activeTab === eq.id"
    >
      <div class="alert-container" :id="'alerts_' + eq.id"></div>
      <div class="chart-box">
        <canvas :id="'chart_ind_' + eq.id"></canvas>
      </div>
    </div>
  </div>
</template>



<style scoped>
body {
  margin: 0;
  font-family: 'Segoe UI', sans-serif;
  background-color: #121212;
  color: #fff;
}
.tabs {
  display: flex;
  background-color: #1f1f2f;
  overflow-x: auto;
}
.tab {
  padding: 15px 25px;
  cursor: pointer;
  flex-shrink: 0;
  border-bottom: 3px solid transparent;
  transition: all 0.3s;
}
.tab.active {
  border-bottom: 3px solid #00e0ff;
  color: #00e0ff;
}
.content {
  padding: 20px;
}
.alert-container {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 20px;
}
.alert {
  flex: 1 1 200px;
  padding: 15px;
  border-radius: 12px;
  font-weight: bold;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #fff;
  box-shadow: 0 4px 15px rgba(0,0,0,0.5);
  transition: transform 0.2s;
}
.alert:hover {
  transform: translateY(-3px);
}
.alert.active { background-color: #ff4d4d; }
.alert.inactive { background-color: #2ecc71; }
.alert span { font-size: 14px; opacity: 0.9; }
.chart-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
}
.chart-box {
  background: linear-gradient(145deg, #1e1e2f, #29293f);
  padding: 20px;
  border-radius: 12px;
  box-shadow: 5px 5px 15px #0a0a15, -5px -5px 15px #22223a;
}
</style>
