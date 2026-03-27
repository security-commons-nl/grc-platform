'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '@/providers/auth-provider';
import { Sidebar } from '@/components/layout/sidebar';
import { Header } from '@/components/layout/header';
import { CardSkeleton } from '@/components/ui/loading-skeleton';

const ROUTE_TITLES: Record<string, string> = {
  '/inrichten': 'Inrichting',
  '/inrichten/besluiten': 'Besluiten',
  '/inrichten/documenten': 'Documenten',
  '/beheer': 'Beheer',
  '/beheer/risicos': "Risico's",
  '/beheer/controls': 'Controls',
  '/beheer/assessments': 'Assessments',
  '/beheer/bewijs': 'Bewijs',
  '/beheer/bevindingen': 'Bevindingen',
  '/beheer/incidenten': 'Incidenten',
  '/admin/gebruikers': 'Gebruikers',
  '/admin/tenant': 'Instellingen',
};

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, isLoading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  useEffect(() => {
    if (!isLoading && !user) {
      router.replace('/login');
    }
  }, [user, isLoading, router]);

  useEffect(() => {
    function checkCollapsed() {
      const stored = localStorage.getItem('ims_sidebar_collapsed');
      setSidebarCollapsed(stored === 'true');
    }
    checkCollapsed();
    window.addEventListener('storage', checkCollapsed);
    return () => window.removeEventListener('storage', checkCollapsed);
  }, []);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-neutral-50">
        <div className="w-full max-w-md space-y-4 px-4">
          <CardSkeleton />
          <CardSkeleton />
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  const pageTitle = ROUTE_TITLES[pathname] || 'IMS Platform';

  return (
    <div className="min-h-screen bg-neutral-50">
      <Sidebar />
      <div
        className={`transition-[margin-left] duration-200 ${sidebarCollapsed ? 'ml-16' : 'ml-60'}`}
      >
        <Header title={pageTitle} />
        <main>{children}</main>
      </div>
    </div>
  );
}
