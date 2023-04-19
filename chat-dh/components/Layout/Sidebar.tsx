import { MaterialIcon } from "material-icons";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/router";
import { FC } from "react";
import { Icon } from "./Icon";

export type MenuItem = {
  label: string;
  href: string;
  icon?: MaterialIcon;
};
export type MenuItems = MenuItem[];

export const Sidebar: FC = () => {
  const router = useRouter();
  const menuItems = [
    { label: "Chat", href: "/chat", icon: "chat" },
    {
      label: "Quick Start Guide",
      href: "/quick-start-guide",
      icon: "menu_book",
    },
  ];

  return (
    <div className="h-full bg-black bg-opacity-5 border-r border-black border-opacity-10 text-primary flex flex-col">
      <div className="flex items-center justify-center h-20">
        <div className="hidden sm:block">
          <Image
            src="/images/dh-logo-color.svg"
            alt="Dataherald company logo"
            width={150}
            height={50}
          />
        </div>
        <div className="block sm:hidden">
          <Image
            src="/images/dh-logo-symbol-color.svg"
            alt="Dataherald company logo narrow"
            width={35}
            height={35}
          />
        </div>
      </div>
      <nav className="flex flex-col px-1 sm:px-2 md:px-4">
        {menuItems.map(({ label, href, icon }, idx) => {
          const isActive = router.pathname === href;
          return (
            <Link
              key={idx}
              href={href}
              className={`flex items-center p-2 font-bold my-1 rounded-lg text-primary ${
                isActive
                  ? "bg-black bg-opacity-20"
                  : "hover:bg-black hover:bg-opacity-20"
              }`}
            >
              <Icon value={icon as MaterialIcon} />
              <span className="hidden sm:flex ml-2">{label}</span>
            </Link>
          );
        })}
      </nav>
    </div>
  );
};
