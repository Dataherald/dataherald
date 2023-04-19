import { MaterialIcon } from "material-icons";
import { FC } from "react";

interface IconProps {
  value: MaterialIcon;
  type?: "filled" | "outlined";
  className?: string;
}

export const Icon: FC<IconProps> = ({
  value,
  type = "outlined",
  className,
}) => (
  <span
    className={[
      type === "filled" ? "material-icons" : "material-icons-outlined",
      className,
    ].join(" ")}
  >
    {value}
  </span>
);
