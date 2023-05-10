import Link from "next/link";
import { FC } from "react";
import { Icon, IconType, IconValue } from "../Layout/Icon";

interface TileProps {
  icon: IconValue;
  title: string;
  description: string;
  iconType?: IconType;
  href?: string;
  disabled?: boolean;
}

export const Tile: FC<TileProps> = ({
  icon,
  iconType,
  title,
  description,
  href = "",
  disabled = false,
}) => {
  if (disabled) href = "";
  return (
    <Link
      href={href}
      className={`w-54 h-50 bg-white border rounded-2xl border-black border-opacity-40 p-5 ${
        disabled ? "opacity-30 hover:pointer-events-none" : "hover:shadow-lg"
      }`}
    >
      <Icon className="text-5xl" value={icon} type={iconType}></Icon>
      <h2 className="font-bold text-lg mb-4">{title}</h2>
      <p>{description}</p>
    </Link>
  );
};
