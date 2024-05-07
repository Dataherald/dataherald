import { CreditCardBrand } from '@/models/api'
import Image from 'next/image'
import { FC } from 'react'

interface CreditCardLogoProps {
  brand: CreditCardBrand
}

const CreditCardLogo: FC<CreditCardLogoProps> = ({ brand }) => (
  <Image
    src={`/images/billing/${brand}.svg`}
    alt={brand}
    width={35}
    height={35}
  />
)

export default CreditCardLogo
