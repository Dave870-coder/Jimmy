'use client';

import { useEffect, useState } from 'react';

const API_BASE = (process.env.NEXT_PUBLIC_API_BASE || '').replace(/\/$/, '');
const apiUrl = (path: string) => `${API_BASE}${path}`;

type User = {
  id: string;
  username: string;
  email: string;
  is_active: boolean;
  created_at: string;
  last_seen: string;
  message_count: number;
};

export default function Users() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filterActive, setFilterActive] = useState('all');
  const [page, setPage] = useState(1);
  const limit = 50;

  useEffect(() => {
    async function loadUsers() {
      try {
        const offset = (page - 1) * limit;
        const response = await fetch(apiUrl(`/api/v1/admin/users?limit=${limit}&offset=${offset}`));
        if (response.ok) {
          const data = await response.json();
          setUsers(data);
        }
      } catch (error) {
        console.error('Failed to load users:', error);
      } finally {
        setLoading(false);
      }
    }

    loadUsers();
  }, [page]);

  const filteredUsers = users.filter((user) => {
    const matchesSearch =
      user.username.toLowerCase().includes(search.toLowerCase()) ||
      user.email.toLowerCase().includes(search.toLowerCase());
    const matchesFilter = filterActive === 'all' || (filterActive === 'active' ? user.is_active : !user.is_active);
    return matchesSearch && matchesFilter;
  });

  const toggleUserActive = async (userId: string, currentStatus: boolean) => {
    try {
      const response = await fetch(apiUrl(`/api/v1/admin/users/${userId}`), {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_active: !currentStatus }),
      });

      if (response.ok) {
        setUsers(users.map((u) => (u.id === userId ? { ...u, is_active: !currentStatus } : u)));
      }
    } catch (error) {
      console.error('Failed to update user:', error);
    }
  };

  const exportUsers = () => {
    const csv = [
      'ID,Username,Email,Active,Created At,Last Seen,Messages',
      ...users.map((u) => `${u.id},${u.username},${u.email},${u.is_active},${u.created_at},${u.last_seen},${u.message_count}`),
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `users-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Loading users...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl">
        <h1 className="text-2xl font-bold text-slate-100">User Management</h1>
        <p className="text-slate-400">View, search, and manage connected users</p>
      </div>

      {/* Search and Filters */}
      <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl space-y-4">
        <div className="flex gap-3 flex-col md:flex-row">
          <input
            type="text"
            placeholder="Search by username or email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 rounded-lg bg-white/10 px-4 py-2 text-slate-100 placeholder-slate-500 border border-white/20 focus:border-cyan-500 focus:outline-none"
          />
          <select
            value={filterActive}
            onChange={(e) => setFilterActive(e.target.value)}
            className="rounded-lg bg-white/10 px-4 py-2 text-slate-100 border border-white/20 focus:border-cyan-500 focus:outline-none"
          >
            <option value="all">All Users</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
          <button
            onClick={exportUsers}
            className="px-6 py-2 rounded-lg bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500/30 transition-all border border-emerald-500/50"
          >
            Export CSV
          </button>
        </div>
        <p className="text-sm text-slate-400">{filteredUsers.length} users found</p>
      </div>

      {/* Users Table */}
      <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-white/10">
              <th className="text-left py-3 px-4 text-slate-300 font-semibold">Username</th>
              <th className="text-left py-3 px-4 text-slate-300 font-semibold">Email</th>
              <th className="text-left py-3 px-4 text-slate-300 font-semibold">Status</th>
              <th className="text-left py-3 px-4 text-slate-300 font-semibold">Messages</th>
              <th className="text-left py-3 px-4 text-slate-300 font-semibold">Last Seen</th>
              <th className="text-left py-3 px-4 text-slate-300 font-semibold">Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredUsers.map((user) => (
              <tr key={user.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                <td className="py-3 px-4 text-slate-100">{user.username}</td>
                <td className="py-3 px-4 text-slate-400">{user.email}</td>
                <td className="py-3 px-4">
                  <span
                    className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
                      user.is_active
                        ? 'bg-emerald-500/20 text-emerald-300'
                        : 'bg-slate-500/20 text-slate-300'
                    }`}
                  >
                    {user.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td className="py-3 px-4 text-slate-100">{user.message_count}</td>
                <td className="py-3 px-4 text-slate-400">{new Date(user.last_seen).toLocaleDateString()}</td>
                <td className="py-3 px-4">
                  <button
                    onClick={() => toggleUserActive(user.id, user.is_active)}
                    className={`px-3 py-1 rounded text-xs font-medium transition-all ${
                      user.is_active
                        ? 'bg-red-500/20 text-red-300 hover:bg-red-500/30'
                        : 'bg-cyan-500/20 text-cyan-300 hover:bg-cyan-500/30'
                    }`}
                  >
                    {user.is_active ? 'Block' : 'Unblock'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl flex justify-between items-center">
        <button
          onClick={() => setPage(Math.max(1, page - 1))}
          disabled={page === 1}
          className="px-4 py-2 rounded-lg bg-white/10 text-slate-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-white/20"
        >
          Previous
        </button>
        <p className="text-slate-400">
          Page <span className="text-slate-100">{page}</span>
        </p>
        <button
          onClick={() => setPage(page + 1)}
          disabled={filteredUsers.length < limit}
          className="px-4 py-2 rounded-lg bg-white/10 text-slate-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-white/20"
        >
          Next
        </button>
      </div>
    </div>
  );
}
