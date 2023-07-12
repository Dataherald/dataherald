import { CSSProperties, FC, ReactNode, memo } from 'react';
import { Icon, IconType, IconValue } from './Icon';

interface ButtonProps {
  children?: ReactNode;
  onClick?: () => void;
  className?: string;
  style?: CSSProperties;
  icon?: IconValue;
  iconType?: IconType;
  color?: 'primary' | 'primary-light' | 'secondary';
}

const Button: FC<ButtonProps> = ({
  children,
  onClick,
  icon,
  iconType,
  color = 'primary',
  className = '',
  style = {},
}) => {
  const colorClasses = {
    primary: 'bg-primary',
    'primary-light': 'bg-primary-light',
    secondary: 'bg-secondary',
  };

  const bgColor = colorClasses[color];

  return (
    <div className="text-white" style={style}>
      <button
        className={`rounded-lg px-4 py-2 ${bgColor} hover:bg-opacity-90 active:bg-opacity-80 active:scale-95 transition-all duration-200 ${className}`}
        onClick={onClick}
      >
        <div className="flex items-center gap-2">
          {icon && <Icon value={icon} type={iconType} />}
          {children}
        </div>
      </button>
    </div>
  );
};

export default memo(Button);
