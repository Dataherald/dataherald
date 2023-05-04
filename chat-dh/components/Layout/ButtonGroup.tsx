import React, { CSSProperties, ReactNode } from "react";
import styles from "./ButtonGroup.module.css";

interface ButtonGroupProps {
  children: ReactNode;
  className?: string;
  style?: CSSProperties;
}

const ButtonGroup: React.FC<ButtonGroupProps> = ({
  children,
  className = "",
  style = {},
}) => {
  return (
    <div className={`${styles.buttonGroup} ${className}`} style={style}>
      {children}
    </div>
  );
};

export default ButtonGroup;
