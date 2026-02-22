import type { Metadata } from "next";
import "./globals.css";
import StoreProvider from "@/redux/provider";
import { ThemeProvider } from "@/redux/theme-provider";

const platformName = process.env.NEXT_PUBLIC_PLATFORM_NAME || "Project Boilerplate";

export const metadata: Metadata = {
  title: platformName,
  description: "Reusable Next.js boilerplate starter.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <StoreProvider>
          <ThemeProvider>{children}</ThemeProvider>
        </StoreProvider>
      </body>
    </html>
  );
}
