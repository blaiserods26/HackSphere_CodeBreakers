import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { NavbarComponent } from "@/components/NavbarComponent";
import  Footer  from "@/components/Footer";

export const metadata: Metadata = {
  title: "Create Next App",
  description: "Generated by create next app",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <NavbarComponent />
        {children}
        <Footer />
      </body>
    </html>
  );
}
