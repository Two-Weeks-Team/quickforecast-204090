use client
import Dashboard from '@/components/Dashboard';
import Hero from '@/components/Hero';
import InsightPanel from '@/components/InsightPanel';
import StatePanel from '@/components/StatePanel';
import CollectionPanel from '@/components/CollectionPanel';
import StatsStrip from '@/components/StatsStrip';
import { useEffect, useState } from "react";

export default function Home() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<any>(null);

  useEffect(() => {
    // Simulate loading state
    const timer = setTimeout(() => {
      setLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  if (loading) {
    return <StatePanel state="loading" message="Loading your forecast..." />;
  }

  if (error) {
    return <StatePanel state="error" message={error} />;
  }

  return (
    <main className="min-h-screen bg-background p-4">
      <Hero />
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Dashboard />
        <div className="space-y-6">
          <InsightPanel />
          <CollectionPanel />
          <StatsStrip />
        </div>
      </div>
    </main>
  );
}