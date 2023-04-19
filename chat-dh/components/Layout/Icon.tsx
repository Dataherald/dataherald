import { MaterialIcon } from "material-icons";
import { FC } from "react";

export type IconValue = MaterialIcon;

export type IconType = "filled" | "outlined" | "round";

type MaterialIconClass =
  | "material-icons"
  | "material-icons-outlined"
  | "material-icons-round";

type IconClassMapping = { [K in IconType]: MaterialIconClass };

interface IconProps {
  value: MaterialIcon;
  type?: IconType;
  className?: string;
}

const iconClassMap: IconClassMapping = {
  filled: "material-icons",
  outlined: "material-icons-outlined",
  round: "material-icons-round",
};

export const Icon: FC<IconProps> = ({
  value,
  type = "outlined",
  className,
}) => (
  <span className={[iconClassMap[type], className].join(" ")}>{value}</span>
);
