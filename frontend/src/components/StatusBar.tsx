import React, { useEffect, useState, useCallback } from 'react';
import { RefreshCw, RotateCcw } from 'lucide-react';
import clsx from 'clsx';
import { apiClient } from '../api/client';
import type { HealthResponse } from '../types';

interface Props {
  onLog?: (msg: string, type: 'error' | 'warning' | 'info') => void;
}

export const StatusBar: React.FC<Props> = ({ onLog }) => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [offline, setOffline] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [restarting, setRestarting] = useState(false);

  const check = useCallback(async () => {
    try {
      const h = await apiClient.getHealth();
      setHealth(h);
      setOffline(false);
      return true;
    } catch {
      setOffline(true);
      return false;
    }
  }, []);

  // Initial check + 30s polling
  useEffect(() => {
    check();
    const t = setInterval(check, 30_000);
    return () => clearInterval(t);
  }, [check]);

  const handleRefresh = useCallback(async () => {
    setRefreshing(true);
    const ok = await check();
    if (!ok) onLog?.('Health check failed — backend may be offline', 'error');
    else onLog?.('Server status refreshed', 'info');
    setRefreshing(false);
  }, [check, onLog]);

  const handleRestart = useCallback(async () => {
    if (restarting) return;
    setRestarting(true);
    onLog?.('Restart requested — waiting for server to come back…', 'info');
    try {
      await apiClient.restartServer();
    } catch {
      // Expected — server dies before responding
    }

    // Poll until healthy (up to 30s)
    await new Promise<void>((resolve) => {
      let attempts = 0;
      const poll = setInterval(async () => {
        attempts++;
        const ok = await check();
        if (ok || attempts >= 30) {
          clearInterval(poll);
          if (ok) onLog?.('Server restarted successfully', 'info');
          else onLog?.('Server did not come back after 30s — check your terminal', 'error');
          resolve();
        }
      }, 1_000);
    });

    setRestarting(false);
  }, [restarting, check, onLog]);

  return (
    <div className="flex items-center gap-2">
      {/* Status indicator */}
      <div className="flex items-center gap-3 text-xs text-gray-500">
        {offline ? (
          <div className="flex items-center gap-1.5 text-red-400">
            <span className="w-1.5 h-1.5 rounded-full bg-red-500" />
            API offline
          </div>
        ) : health ? (
          <>
            <div className="flex items-center gap-1.5">
              <span className={clsx(
                'w-1.5 h-1.5 rounded-full',
                health.status === 'healthy' ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'
              )} />
              <span className={health.status === 'healthy' ? 'text-emerald-400' : 'text-amber-400'}>
                {restarting ? 'Restarting…' : health.status === 'healthy' ? 'Healthy' : 'Degraded'}
              </span>
            </div>
            <span className="text-gray-700">·</span>
            <span className="flex items-center gap-1">
              {health.llm_adapter}
              <span className={health.llm_available ? 'text-emerald-500' : 'text-red-500'}>●</span>
            </span>
            <span className="text-gray-700 hidden sm:inline">·</span>
            <span className="hidden sm:inline">
              {health.embedding_available ? health.embedding_model : 'jaccard fallback'}
            </span>
            <span className="text-gray-700">·</span>
            <span className="text-gray-600">v{health.version}</span>
          </>
        ) : null}
      </div>

      {/* Refresh */}
      <button
        onClick={handleRefresh}
        disabled={refreshing || restarting}
        title="Refresh server status"
        className={clsx(
          'flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium border transition-all disabled:opacity-40',
          refreshing
            ? 'bg-sky-500/15 border-sky-500/30 text-sky-400 cursor-wait'
            : 'bg-[#1a1d26] border-[#2a2d38] text-gray-400 hover:text-sky-400 hover:bg-sky-500/10 hover:border-sky-500/30'
        )}
      >
        <RefreshCw className={clsx('w-3.5 h-3.5', refreshing && 'animate-spin')} />
        {refreshing ? 'Refreshing…' : 'Refresh'}
      </button>

      {/* Restart */}
      <button
        onClick={handleRestart}
        disabled={restarting}
        title="Restart backend server"
        className={clsx(
          'flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium border transition-all',
          restarting
            ? 'bg-amber-500/15 border-amber-500/30 text-amber-400 cursor-wait'
            : 'bg-[#1a1d26] border-[#2a2d38] text-gray-400 hover:text-red-400 hover:bg-red-500/10 hover:border-red-500/30'
        )}
      >
        <RotateCcw className={clsx('w-3.5 h-3.5', restarting && 'animate-spin')} />
        {restarting ? 'Restarting…' : 'Restart'}
      </button>
    </div>
  );
};
