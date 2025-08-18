import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import StoreProvider from "@/components/core/StoreProvider"; 
import Notifications from "@/components/core/Notifications";
import AppLayout from "@/components/core/AppLayout";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ChemsTools",
  description: "Herramientas químicas integradas",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
  
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <StoreProvider>
          <AppLayout>
            {children}
          </AppLayout>
          <Notifications />
        </StoreProvider>
      </body>
    </html>
  );
}

