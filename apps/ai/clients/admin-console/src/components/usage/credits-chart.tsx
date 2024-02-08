import { toDollars } from '@/lib/utils'
import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  ChartOptions,
  Legend,
  LinearScale,
  Title,
  Tooltip,
} from 'chart.js'
import { FC } from 'react'
import { Bar } from 'react-chartjs-2'

interface CreditsChartProps {
  availableCredits: number
  totalCredits: number
}

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)
const CreditsChart: FC<CreditsChartProps> = ({
  availableCredits,
  totalCredits,
}) => {
  const usedCreditsDollars = toDollars(totalCredits - availableCredits)
  const availableCreditsDollars = toDollars(availableCredits)

  const data = {
    labels: [''],
    datasets: [
      {
        label: 'Available',
        data: [availableCreditsDollars],
        backgroundColor: 'rgba(75, 192, 144, 0.6)', // light green color
        barThickness: 25,
      },
      {
        label: 'Used',
        data: [usedCreditsDollars],
        backgroundColor: 'rgba(255, 159, 164, 0.6)', // light red color
        barThickness: 25,
      },
    ],
  }

  const options: ChartOptions<'bar'> = {
    indexAxis: 'y',
    plugins: {
      legend: {
        position: 'top',
        align: 'start',
        labels: {
          padding: 5,
          textAlign: 'left',
          boxWidth: 18,
          boxHeight: 18,
        },
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            let label = context.dataset.label || ''
            label += ': $' + Number(context.raw).toFixed(2)
            return label
          },
        },
      },
    },
    scales: {
      x: {
        display: false,
        stacked: true,
      },
      y: {
        display: false,
        stacked: true,
      },
    },
    maintainAspectRatio: false,
  }

  return <Bar options={options} data={data} />
}

export default CreditsChart
