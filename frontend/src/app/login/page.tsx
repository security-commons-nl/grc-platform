'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/providers/auth-provider';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { Button } from '@/components/ui/button';

function generateUUID(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

const ROLE_OPTIONS = [
  { value: 'admin', label: 'Admin' },
  { value: 'sims_lid', label: 'SIMS-lid' },
  { value: 'tims_lid', label: 'TIMS-lid' },
  { value: 'discipline_eigenaar', label: 'Discipline-eigenaar' },
  { value: 'lijnmanager', label: 'Lijnmanager' },
  { value: 'viewer', label: 'Viewer' },
];

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [userId] = useState(generateUUID);
  const [tenantId, setTenantId] = useState('');
  const [role, setRole] = useState('admin');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');

    if (!tenantId.trim()) {
      setError('Tenant ID is verplicht');
      return;
    }

    setLoading(true);
    try {
      await login(userId, tenantId.trim(), role);
      router.push('/inrichten');
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Inloggen mislukt. Controleer of de API beschikbaar is.',
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-neutral-50 px-4">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-primary-600 text-white text-lg font-bold">
            IMS
          </div>
          <h1 className="text-2xl font-semibold text-neutral-900">
            IMS Platform
          </h1>
          <p className="mt-1 text-sm text-neutral-600">Ontwikkelmodus</p>
        </div>

        <Card>
          <form onSubmit={handleSubmit} className="space-y-5">
            <Input
              label="User ID"
              value={userId}
              readOnly
              className="font-mono text-xs bg-neutral-50"
            />

            <Input
              label="Tenant ID"
              placeholder="UUID van de tenant"
              value={tenantId}
              onChange={(e) => setTenantId(e.target.value)}
              className="font-mono text-xs"
            />

            <Select
              label="Rol"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              options={ROLE_OPTIONS}
            />

            {error && (
              <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
                {error}
              </div>
            )}

            <Button
              type="submit"
              disabled={loading}
              className="w-full"
              size="lg"
            >
              {loading ? 'Bezig met inloggen...' : 'Inloggen'}
            </Button>
          </form>
        </Card>

        <p className="mt-4 text-center text-xs text-neutral-400">
          Dit is een ontwikkelomgeving. Gebruik een geldige Tenant UUID.
        </p>
      </div>
    </div>
  );
}
