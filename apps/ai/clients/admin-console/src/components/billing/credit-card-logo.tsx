import { CreditCardBrand } from '@/models/api'
import Image from 'next/image'
import { FC } from 'react'

interface CreditCardLogoProps {
  brand: CreditCardBrand
}

const CreditCardLogo: FC<CreditCardLogoProps> = ({ brand }) => (
  <Image
    src={`https://hi-george.s3.amazonaws.com/DataheraldAI/Payment%20Processor%20Logos/${brand}.svg`}
    alt={brand}
    width={35}
    height={35}
  />
)

export default CreditCardLogo
