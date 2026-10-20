'use client';

import { useEffect } from 'react';

// AdminLTE's fixed/expand sidebar behavior is driven by classes on <body>,
// but the root layout owns <body> across routes (including the classless
// login/register pages), so portal/admin layouts apply their classes here.
export default function BodyClass({ className }) {
  useEffect(() => {
    const classes = className.split(' ').filter(Boolean);
    document.body.classList.add(...classes);
    return () => document.body.classList.remove(...classes);
  }, [className]);

  return null;
}
