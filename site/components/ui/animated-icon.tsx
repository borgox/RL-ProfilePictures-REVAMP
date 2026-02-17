"use client";

import React from "react";
import { motion } from "framer-motion";
import { cn } from "../../lib/utils";

interface AnimatedIconProps {
  children: React.ReactNode;
  className?: string;
  delay?: number;
  hover?: boolean;
}

export function AnimatedIcon({ children, className, delay = 0, hover = true }: AnimatedIconProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3, delay }}
      whileHover={hover ? { scale: 1.1 } : undefined}
      className={cn("inline-block", className)}
    >
      {children}
    </motion.div>
  );
}
