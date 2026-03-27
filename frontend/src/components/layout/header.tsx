'use client';

import { useState, useRef, useEffect } from 'react';
import { useAuth } from '@/providers/auth-provider';
import { ROLE_LABELS } from '@/lib/constants';
import { Badge } from '@/components/ui/badge';

interface HeaderProps {
  title: string;
}

export function Header({ title }: HeaderProps) {
  const { user, logout } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-neutral-200 bg-white px-6">
      <h1 className="text-lg font-semibold text-neutral-900">{title}</h1>

      {user && (
        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="flex items-center gap-2.5 rounded-lg px-3 py-1.5 hover:bg-neutral-50 transition-colors"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-100 text-primary-700 text-xs font-semibold">
              {user.id.substring(0, 2).toUpperCase()}
            </div>
            <span className="text-sm font-medium text-neutral-800">
              {user.id.substring(0, 8)}
            </span>
            <Badge variant="primary">
              {ROLE_LABELS[user.role] || user.role}
            </Badge>
          </button>

          {dropdownOpen && (
            <div className="absolute right-0 mt-1 w-48 rounded-lg border border-neutral-200 bg-white shadow-lg py-1">
              <div className="px-4 py-2 border-b border-neutral-100">
                <p className="text-xs text-neutral-400">Tenant</p>
                <p className="text-sm font-medium text-neutral-800 truncate">
                  {user.tenant_id.substring(0, 8)}
                </p>
              </div>
              {user.domain && (
                <div className="px-4 py-2 border-b border-neutral-100">
                  <p className="text-xs text-neutral-400">Domein</p>
                  <p className="text-sm font-medium text-neutral-800">
                    {user.domain}
                  </p>
                </div>
              )}
              <button
                onClick={() => {
                  setDropdownOpen(false);
                  logout();
                }}
                className="w-full px-4 py-2 text-left text-sm text-neutral-600 hover:bg-neutral-50 hover:text-neutral-800 transition-colors"
              >
                Uitloggen
              </button>
            </div>
          )}
        </div>
      )}
    </header>
  );
}
