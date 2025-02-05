import type { NextConfig } from "next";

const nextConfig = {
  protocol: "https",
  hostname: "firebasestorage.googleapis.com",
  port: "",
  pathname: "/**",
  output: "export",
  distDir: "out",
  images: {
    domains: ["firebasestorage.googleapis.com", "lh3.googleusercontent.com"],
  },
  // protocol: 'https',
  //     hostname: 'lh3.googleusercontent.com',
  // port: '',
  // pathname: '/**',
};

export default nextConfig;
