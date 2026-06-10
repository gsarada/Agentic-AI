export function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="card h-[116px] animate-pulse p-5">
            <div className="h-4 w-24 rounded bg-slate-200" />
            <div className="mt-4 h-7 w-32 rounded bg-slate-200" />
          </div>
        ))}
      </div>
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-5">
        <div className="card h-[280px] animate-pulse lg:col-span-2" />
        <div className="card h-[280px] animate-pulse lg:col-span-3" />
      </div>
    </div>
  );
}

export function ListSkeleton() {
  return (
    <div className="card divide-y divide-slate-100">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="flex animate-pulse items-center gap-4 p-4">
          <div className="h-4 w-24 rounded bg-slate-200" />
          <div className="h-4 flex-1 rounded bg-slate-200" />
          <div className="h-4 w-16 rounded bg-slate-200" />
        </div>
      ))}
    </div>
  );
}
