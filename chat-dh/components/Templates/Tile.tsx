import { FC } from "react";
import { Icon, IconType, IconValue } from "../Layout/Icon";
import Link from "next/link";

interface TileProps {
  icon: IconValue;
  iconType?: IconType;
  title: string;
  description: string;
  href?: string;
  disabled?: boolean
}

export const Tile: FC<TileProps> = ({ icon, iconType, title, description, href="", disabled=false }) => {
  if (disabled) href = "";
  return (
    <Link href={href} className={`w-54 h-50 bg-white border rounded-2xl border-black border-opacity-40 p-5 hover:shadow-lg ${
      disabled
        ? "opacity-30"
        : ""
    }`}>
      <Icon className="text-5xl" value={icon} type={iconType}></Icon>
      <h2>{title}</h2>
      <p>{description}</p>
    </Link>
  );
};