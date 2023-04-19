import { MaterialIcon } from "material-icons";
import { FC } from "react";

export type IconProps = {
  value: MaterialIcon;
  type?: "material-icons" | "material-icons-outlined";
  className?: string;
};

export const Icon: FC<IconProps> = ({
  value,
  type = "material-icons-outlined",
  className,
}) => <span className={[type, className].join(" ")}>{value}</span>;
