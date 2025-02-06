"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { HiHome, HiCurrencyDollar } from "react-icons/hi";
import Image from "next/image";
import { useTheme } from "next-themes";

export const NavbarComponent = () => {
  const { theme, setTheme } = useTheme();
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 0);
    };
    window.addEventListener("scroll", handleScroll);
    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, []);

  return (
    <nav
      className={`fixed w-full z-50 transition-all ${
        isScrolled ? "bg-white dark:bg-gray-900 shadow-lg" : "bg-transparent"
      }`}
    >
      <div className="container mx-auto px-4 py-2 flex justify-between items-center">
        <Link href="/" className="flex items-center">
          <Image
            src="/logo-light.svg"
            width={32}
            height={32}
            className="mr-3 h-6 sm:h-8"
            alt="EmailGuard Logo"
          />
          <span className="self-center whitespace-nowrap text-xl font-semibold bg-gradient-to-r from-cyan-500 to-blue-500 text-transparent bg-clip-text">
            EmailGuard
          </span>
        </Link>
        <div className="flex items-center gap-4">
          <button
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            className="focus:ring-cyan-500 p-2 rounded-full"
          >
            {theme === "dark" ? "🌞" : "🌜"}
          </button>
          <Link href="/profile">
            <div className="relative w-8 h-8 rounded-full overflow-hidden cursor-pointer">
              <Image
                src="https://flowbite.com/docs/images/people/profile-picture-5.jpg"
                alt="Profile"
                layout="fill"
                objectFit="cover"
              />
              <span className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-white dark:border-gray-900 rounded-full" />
            </div>
          </Link>
          <button
            className="md:hidden p-2 rounded focus:outline-none focus:ring-2 focus:ring-cyan-500"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            ☰
          </button>
        </div>
        <div className="hidden md:flex items-center space-x-4">
          <Link
            href="/home"
            className="flex items-center gap-2 text-black dark:text-white hover:text-cyan-500 dark:hover:text-cyan-500"
          >
            <HiHome className="w-5 h-5" />
            Home
          </Link>
          <Link
            href="/pricing"
            className="flex items-center gap-2 text-black dark:text-white hover:text-cyan-500 dark:hover:text-cyan-500"
          >
            <HiCurrencyDollar className="w-5 h-5" />
            Pricing
          </Link>
        </div>
      </div>
      <div className={`md:hidden ${isMenuOpen ? "block" : "hidden"} bg-white dark:bg-gray-900`}>
        <Link
          href="/home"
          className="block px-4 py-2 text-black dark:text-white hover:bg-gray-200 dark:hover:bg-gray-700"
        >
          Home
        </Link>
        <Link
          href="/pricing"
          className="block px-4 py-2 text-black dark:text-white hover:bg-gray-200 dark:hover:bg-gray-700"
        >
          Pricing
        </Link>
      </div>
    </nav>
  );
};
