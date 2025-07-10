import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import StoreProvider from "@/components/core/StoreProvider"; // Importar

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
        <StoreProvider>{children}</StoreProvider> {/* Envolver */}
      </body>
    </html>
  );
}

