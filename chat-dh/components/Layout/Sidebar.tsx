import { useUser } from "@auth0/nextjs-auth0/client";
import { MaterialIcon } from "material-icons";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/router";
import { FC } from "react";
import { Icon } from "./Icon";

export type MenuItem = {
  hide?: boolean;
  label: string;
  href: string;
  icon?: MaterialIcon;
};
export type MenuItems = MenuItem[];
export type SidebarProps = {
  className?: string;
};

export const Sidebar: FC<SidebarProps> = ({ className = "" }) => {
  const { user } = useUser();
  const router = useRouter();
  const TOP_MENU_ITEMS: MenuItems = [
    { label: "Chat", href: "/chat", icon: "chat" },
  ];
  const BOTTOM_MENU_ITEMS: MenuItems = [
    {
      label: "Quick Start Guide",
      href: "/quick-start-guide",
      hide: true,
      icon: "menu_book",
    },
    {
      label: "Logout",
      hide: !user,
      href: "/api/auth/logout",
      icon: "logout",
    },
  ];

  const renderMenuItems = (menuItems: MenuItems): JSX.Element => (
    <nav className="flex flex-col gap-2">
      {menuItems.map(({ label, href, icon, hide }, idx) => {
        if (hide) return;
        const isActive = router.pathname === href;
        return (
          <Link
            key={idx}
            href={href}
            className={`flex items-center p-2 rounded-lg ${
              isActive
                ? "bg-black bg-opacity-10 text-primary"
                : "hover:bg-black hover:bg-opacity-10"
            }`}
          >
            <Icon value={icon as MaterialIcon} />
            <span className="hidden sm:flex ml-3">{label}</span>
          </Link>
        );
      })}
    </nav>
  );

  return (
    <div
      className={[
        "bg-gray-100 text-secondary-dark font-bold flex flex-col justify-between min-w-fit px-1 sm:px-2 md:px-4 pb-4",
        className,
      ].join(" ")}
    >
      <div className="flex flex-col">
        <div className="flex items-center justify-center h-20">
          <Link href="/">
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
          </Link>
        </div>
        {renderMenuItems(TOP_MENU_ITEMS)}
      </div>
      <div className="flex flex-col gap-2">
        {renderMenuItems(BOTTOM_MENU_ITEMS)}
        {user && (
          <div className="flex flex-row items-center gap-2">
            {user.picture ? (
              <Image
                className="rounded-full"
                src={user.picture}
                alt="User Profile Picture"
                width={35}
                height={35}
              />
            ) : (
              <Icon value="person"></Icon>
            )}
            <span className="hidden sm:flex font-normal">{user.name}</span>
          </div>
        )}
      </div>
    </div>
  );
};
