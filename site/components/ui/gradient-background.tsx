"use client";

import React from "react";
import { cn } from "../../lib/utils";

interface GradientBackgroundProps {
  children: React.ReactNode;
  className?: string;
  variant?: "hero" | "section" | "card";
}

export function GradientBackground({ children, className, variant = "section" }: GradientBackgroundProps) {
  const gradients = {
    hero: "bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900",
    section: "bg-gradient-to-r from-slate-900 to-slate-800",
    card: "bg-gradient-to-br from-slate-800 to-slate-900"
  };

  return (
    <div className={cn(
      "relative overflow-hidden",
      gradients[variant],
      className
    )}>
      <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent" />
      <div className="relative z-10">
        {children}
      </div>
    </div>
  );
}
