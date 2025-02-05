"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import LandingPage from "../components/LandingPage";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to landing page if not on home page
    if (window.location.pathname === "/") {
      router.push("/landing");
    }
  }, [router]);

  return (
    
    <LandingPage />
  );
}