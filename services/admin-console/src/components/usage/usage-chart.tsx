import { toDollars } from '@/lib/utils'
import { Usage } from '@/models/api'
import { ArcElement, Chart, ChartOptions, Legend, Tooltip } from 'chart.js'
import { FC } from 'react'
import { Doughnut } from 'react-chartjs-2'

interface UsagePieChartProps {
  usage: Usage
}

Chart.register(ArcElement, Tooltip, Legend)

const UsagePieChart: FC<UsagePieChartProps> = ({ usage }) => {
  const {
    spending_limit,
    sql_generation_cost,
    finetuning_gpt_35_cost,
    finetuning_gpt_4_cost,
  } = usage
  const total_cost =
    sql_generation_cost + finetuning_gpt_35_cost + finetuning_gpt_4_cost

  const availableLimit = spending_limit - total_cost

  const chartData = {
    labels: [
      'SQL query generations',
      'Finetuning GPT-3.5',
      'Finetuning GPT-4',
      'Available limit',
    ],
    datasets: [
      {
        data: [
          toDollars(sql_generation_cost),
          toDollars(finetuning_gpt_35_cost),
          toDollars(finetuning_gpt_4_cost),
          toDollars(Math.max(0, availableLimit)),
        ],
        backgroundColor: [
          'rgba(54, 162, 235, 0.6)', // blue
          'rgba(255, 206, 86, 0.6)', // yellow
          'rgba(75, 192, 192, 0.6)', // teal
          'rgba(211, 211, 211, 0.6)', // light gray
        ],
        hoverOffset: 4,
      },
    ],
  }

  const chartOptions: ChartOptions<'doughnut'> = {
    cutout: '80%', // Adjust this value to make the doughnut chart thinner
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          boxWidth: 25,
        },
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            let label = ' $'
            if (context.raw !== null) {
              label += Number(context.raw).toFixed(2)
            }
            return label
          },
        },
      },
    },
    maintainAspectRatio: true,
    aspectRatio: 1, // keeps the chart as a perfect circle
  }

  return <Doughnut data={chartData} options={chartOptions} />
}

export default UsagePieChart
