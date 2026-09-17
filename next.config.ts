import type { NextConfig } from "next";
const config: NextConfig = {
  trailingSlash: true,
  images: { unoptimized: true },
  poweredByHeader: false,
  // Allow dev requests from other devices on the LAN (npm run dev:lan).
  allowedDevOrigins: ["192.168.2.*"],
};
export default config;
