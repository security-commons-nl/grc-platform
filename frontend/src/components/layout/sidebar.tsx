'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import clsx from 'clsx';
import {
  HomeIcon,
  DocumentTextIcon,
  FolderOpenIcon,
  ChartBarSquareIcon,
  ShieldExclamationIcon,
  CheckCircleIcon,
  ClipboardDocumentCheckIcon,
  DocumentCheckIcon,
  ExclamationTriangleIcon,
  BoltIcon,
  UsersIcon,
  CogIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
} from '@heroicons/react/24/outline';
import { useAuth } from '@/providers/auth-provider';
import { hasMinRole, ROLE_LABELS } from '@/lib/constants';
import { Badge } from '@/components/ui/badge';
import { Tooltip } from '@/components/ui/tooltip';

interface NavItem {
  label: string;
  href: string;
  icon: React.ElementType;
  minRole: string;
}

interface NavSection {
  title: string;
  items: NavItem[];
}

const NAV_SECTIONS: NavSection[] = [
  {
    title: 'INRICHTEN',
    items: [
      { label: 'Overzicht', href: '/inrichten', icon: HomeIcon, minRole: 'viewer' },
      { label: 'Besluiten', href: '/inrichten/besluiten', icon: DocumentTextIcon, minRole: 'viewer' },
      { label: 'Documenten', href: '/inrichten/documenten', icon: FolderOpenIcon, minRole: 'viewer' },
    ],
  },
  {
    title: 'BEHEER',
    items: [
      { label: 'Dashboard', href: '/beheer', icon: ChartBarSquareIcon, minRole: 'viewer' },
      { label: "Risico's", href: '/beheer/risicos', icon: ShieldExclamationIcon, minRole: 'lijnmanager' },
      { label: 'Controls', href: '/beheer/controls', icon: CheckCircleIcon, minRole: 'discipline_eigenaar' },
      { label: 'Assessments', href: '/beheer/assessments', icon: ClipboardDocumentCheckIcon, minRole: 'discipline_eigenaar' },
      { label: 'Bewijs', href: '/beheer/bewijs', icon: DocumentCheckIcon, minRole: 'lijnmanager' },
      { label: 'Bevindingen', href: '/beheer/bevindingen', icon: ExclamationTriangleIcon, minRole: 'discipline_eigenaar' },
      { label: 'Incidenten', href: '/beheer/incidenten', icon: BoltIcon, minRole: 'lijnmanager' },
    ],
  },
  {
    title: 'ADMIN',
    items: [
      { label: 'Gebruikers', href: '/admin/gebruikers', icon: UsersIcon, minRole: 'admin' },
      { label: 'Instellingen', href: '/admin/tenant', icon: CogIcon, minRole: 'admin' },
    ],
  },
];

const COLLAPSED_KEY = 'ims_sidebar_collapsed';

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem(COLLAPSED_KEY);
    if (stored === 'true') setCollapsed(true);
  }, []);

  function toggleCollapsed() {
    const next = !collapsed;
    setCollapsed(next);
    localStorage.setItem(COLLAPSED_KEY, String(next));
  }

  const userRole = user?.role || 'viewer';

  return (
    <aside
      className={clsx(
        'fixed left-0 top-0 bottom-0 z-40 flex flex-col border-r border-neutral-200 bg-white transition-[width] duration-200',
        collapsed ? 'w-16' : 'w-60',
      )}
    >
      {/* Logo */}
      <div
        className={clsx(
          'flex h-16 items-center border-b border-neutral-200 px-4',
          collapsed ? 'justify-center' : 'gap-3',
        )}
      >
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary-600 text-white text-sm font-bold">
          IMS
        </div>
        {!collapsed && (
          <span className="text-base font-semibold text-neutral-900">
            Platform
          </span>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4">
        {NAV_SECTIONS.map((section) => {
          const visibleItems = section.items.filter((item) =>
            hasMinRole(userRole, item.minRole),
          );
          if (visibleItems.length === 0) return null;

          return (
            <div key={section.title} className="mb-4">
              {!collapsed && (
                <div className="px-4 pb-1.5 text-[11px] font-semibold tracking-wider text-neutral-400 uppercase">
                  {section.title}
                </div>
              )}
              <ul className="space-y-0.5 px-2">
                {visibleItems.map((item) => {
                  const isActive =
                    pathname === item.href ||
                    (item.href !== '/inrichten' &&
                      item.href !== '/beheer' &&
                      pathname.startsWith(item.href));
                  const Icon = item.icon;

                  const linkContent = (
                    <Link
                      href={item.href}
                      className={clsx(
                        'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                        isActive
                          ? 'bg-primary-50 text-primary-700'
                          : 'text-neutral-600 hover:bg-neutral-50 hover:text-neutral-800',
                        collapsed && 'justify-center',
                      )}
                    >
                      <Icon className="h-5 w-5 shrink-0" />
                      {!collapsed && <span>{item.label}</span>}
                    </Link>
                  );

                  return (
                    <li key={item.href}>
                      {collapsed ? (
                        <Tooltip content={item.label} position="right">
                          {linkContent}
                        </Tooltip>
                      ) : (
                        linkContent
                      )}
                    </li>
                  );
                })}
              </ul>
            </div>
          );
        })}
      </nav>

      {/* User info */}
      {user && !collapsed && (
        <div className="border-t border-neutral-200 p-4">
          <div className="flex items-center gap-2 mb-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-100 text-primary-700 text-xs font-semibold">
              {user.id.substring(0, 2).toUpperCase()}
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-neutral-800">
                {user.id.substring(0, 8)}
              </p>
              <Badge variant="primary">
                {ROLE_LABELS[user.role] || user.role}
              </Badge>
            </div>
          </div>
          <button
            onClick={logout}
            className="w-full rounded-lg px-3 py-1.5 text-left text-sm text-neutral-600 hover:bg-neutral-50 hover:text-neutral-800 transition-colors"
          >
            Uitloggen
          </button>
        </div>
      )}

      {/* Collapse toggle */}
      <div className="border-t border-neutral-200 p-2">
        <button
          onClick={toggleCollapsed}
          className="flex w-full items-center justify-center rounded-lg p-2 text-neutral-400 hover:bg-neutral-50 hover:text-neutral-600 transition-colors"
          aria-label={collapsed ? 'Sidebar uitklappen' : 'Sidebar inklappen'}
        >
          {collapsed ? (
            <ChevronRightIcon className="h-4 w-4" />
          ) : (
            <ChevronLeftIcon className="h-4 w-4" />
          )}
        </button>
      </div>
    </aside>
  );
}
