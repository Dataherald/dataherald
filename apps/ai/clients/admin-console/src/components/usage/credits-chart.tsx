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
  className?: string
}

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const CreditsChart: FC<CreditsChartProps> = ({
  availableCredits,
  totalCredits,
  className,
}) => {
  // Use percentages for the visual representation
  const usedCredits = totalCredits - availableCredits
  const availableCreditsPercentage = (availableCredits / totalCredits) * 100
  const usedCreditsPercentage = (usedCredits / totalCredits) * 100

  const data = {
    labels: [''],
    datasets: [
      {
        label: 'Available',
        data: [availableCreditsPercentage], // For bar length
        backgroundColor: 'rgba(75, 192, 144, 0.6)', // light green color
        barThickness: 25,
      },
      {
        label: 'Used',
        data: [usedCreditsPercentage], // For bar length
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
            if (label === 'Available') {
              label += ': $' + toDollars(availableCredits)
            } else if (label === 'Used') {
              label += ': $' + toDollars(usedCredits)
            }
            return label
          },
        },
      },
    },
    scales: {
      x: {
        display: false,
        stacked: true,
        min: 0,
        max: 100,
      },
      y: {
        display: false,
        stacked: true,
      },
    },
    maintainAspectRatio: false,
  }

  return <Bar className={className} options={options} data={data} />
}

export default CreditsChart
