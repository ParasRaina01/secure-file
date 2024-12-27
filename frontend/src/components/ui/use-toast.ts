import * as React from 'react';
import { toast as sonnerToast } from 'sonner';

export interface ToastProps {
  title?: string;
  description?: string;
  variant?: 'default' | 'destructive';
}

export function toast({ title, description, variant = 'default' }: ToastProps) {
  sonnerToast[variant === 'destructive' ? 'error' : 'success'](title, {
    description,
  });
} 