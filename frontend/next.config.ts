import type { NextConfig } from "next";

const nextConfig = {
    protocol: "https",
    hostname: "firebasestorage.googleapis.com",
    port: "",
    pathname: "/**",


    // protocol: 'https',
    //     hostname: 'lh3.googleusercontent.com',
    // port: '',
    // pathname: '/**',

};
module.exports = {
  distDir: 'out',
};


export default nextConfig;
