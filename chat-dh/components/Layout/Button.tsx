import { CSSProperties, FC, ReactNode } from "react";
import { Icon, IconType, IconValue } from "./Icon";

interface ButtonProps {
  children: ReactNode;
  onClick?: () => void;
  className?: string;
  style?: CSSProperties;
  icon?: IconValue;
  iconType?: IconType;
  color?: "primary" | "primary-light" | "secondary";
}

const Button: FC<ButtonProps> = ({
  children,
  onClick,
  className,
  style,
  icon,
  iconType,
  color = "primary",
}) => {
  const bgColor = `bg-${color}`;

  return (
    <button
      className={`${className} rounded-lg px-4 py-2 ${bgColor} hover:bg-opacity-90 text-white transition-colors duration-200`}
      style={style}
      onClick={onClick}
    >
      <div className="flex items-center gap-2">
        {icon && <Icon value={icon} type={iconType} />}
        {children}
      </div>
    </button>
  );
};

export default Button;
