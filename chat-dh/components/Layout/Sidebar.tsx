import { useUser } from "@auth0/nextjs-auth0/client";
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
  const { user } = useUser();
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
    <div className="h-full bg-black bg-opacity-5 border-r border-black border-opacity-10 text-secondary-dark font-bold flex flex-col justify-between px-1 sm:px-2 md:px-4 pb-4">
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
        <nav className="flex flex-col gap-2">
          {menuItems.map(({ label, href, icon }, idx) => {
            const isActive = router.pathname === href;
            return (
              <Link
                key={idx}
                href={href}
                className={`flex items-center p-2 rounded-lg text-secondary-dark ${
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
      {user && (
        <div className="flex flex-col gap-2">
          <Link
            href="/api/auth/logout"
            className="flex items-center gap-3 p-2 my-1 rounded-lg text-secondary-dark hover:bg-black hover:bg-opacity-20"
          >
            <Icon value="logout" />
            <span className="hidden sm:flex">Logout</span>
          </Link>
          <div className="flex flex-row items-center gap-2">
            {user.picture ? (
              <Image
                className="rounded-full"
                src={user.picture}
                alt="User Picture"
                width={35}
                height={35}
              />
            ) : (
              <Icon value="person"></Icon>
            )}
            <span className="hidden sm:flex">{user.name}</span>
          </div>
        </div>
      )}
    </div>
  );
};
