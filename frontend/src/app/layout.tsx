import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Insurance Pricing",
  description:
    "Estimate insurance costs with ML-powered predictions and explainable AI insights",
  keywords: [
    "insurance pricing",
    "machine learning",
    "explainable AI",
    "SHAP",
    "health insurance",
    "cost prediction",
  ],
  authors: [{ name: "Viacheslav Danilov" }, { name: "Mikhail Vinogradov" }],
  openGraph: {
    title: "Insurance Pricing",
    description:
      "Estimate insurance costs with ML-powered predictions and explainable AI insights.",
    type: "website",
    locale: "en_US",
    siteName: "Insurance Pricing",
  },
  twitter: {
    card: "summary_large_image",
    title: "Insurance Pricing",
    description:
      "Estimate insurance costs with ML-powered predictions and explainable AI insights.",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
