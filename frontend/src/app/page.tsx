"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";


export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to landing page if not on home page
    if (window.location.pathname === "/") {
      router.push("/landing");
    }
  }, [router]);

  return (

    <div>
      <h1>Welcome to HackSphere CodeBreakers</h1>
      <p>
        <Link href="/landing">Go to Landing Page</Link>
      </p>
      <p>
        <Link href="/">Go to Home Page</Link>
      </p>
    </div>
  );
}