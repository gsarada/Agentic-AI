"use client";

import {
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { Summary } from "@/lib/analytics";
import {
  CATEGORY_COLORS,
  formatCurrency,
  formatCurrencyCompact,
} from "@/lib/format";

export function SpendingCharts({ summary }: { summary: Summary }) {
  const hasData = summary.count > 0;

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-5">
      <ChartCard title="Spending by category" className="lg:col-span-2">
        {hasData ? (
          <div className="flex flex-col items-center gap-4 sm:flex-row">
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={summary.byCategory}
                  dataKey="total"
                  nameKey="category"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={2}
                  stroke="none"
                >
                  {summary.byCategory.map((c) => (
                    <Cell
                      key={c.category}
                      fill={CATEGORY_COLORS[c.category]}
                    />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value: number) => formatCurrency(value)}
                  contentStyle={tooltipStyle}
                />
              </PieChart>
            </ResponsiveContainer>
            <ul className="w-full space-y-2 sm:w-44">
              {summary.byCategory.map((c) => (
                <li
                  key={c.category}
                  className="flex items-center justify-between gap-2 text-sm"
                >
                  <span className="flex items-center gap-2 text-slate-600">
                    <span
                      className="h-2.5 w-2.5 rounded-full"
                      style={{ background: CATEGORY_COLORS[c.category] }}
                    />
                    {c.category}
                  </span>
                  <span className="font-medium text-slate-800">
                    {formatCurrency(c.total)}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <EmptyChart />
        )}
      </ChartCard>

      <ChartCard title="Monthly spending" className="lg:col-span-3">
        {hasData ? (
          <ResponsiveContainer width="100%" height={240}>
            <BarChart
              data={summary.byMonth}
              margin={{ top: 8, right: 8, left: 0, bottom: 0 }}
            >
              <XAxis
                dataKey="label"
                tickLine={false}
                axisLine={false}
                tick={{ fontSize: 12, fill: "#94a3b8" }}
              />
              <YAxis
                tickFormatter={(v) => formatCurrencyCompact(v)}
                tickLine={false}
                axisLine={false}
                width={56}
                tick={{ fontSize: 12, fill: "#94a3b8" }}
              />
              <Tooltip
                cursor={{ fill: "#f1f5f9" }}
                formatter={(value: number) => formatCurrency(value)}
                contentStyle={tooltipStyle}
              />
              <Bar dataKey="total" fill="#3b66f5" radius={[6, 6, 0, 0]} maxBarSize={48} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <EmptyChart />
        )}
      </ChartCard>
    </div>
  );
}

const tooltipStyle = {
  borderRadius: 10,
  border: "1px solid #e2e8f0",
  boxShadow: "0 8px 24px -6px rgb(0 0 0 / 0.12)",
  fontSize: 13,
};

function ChartCard({
  title,
  className = "",
  children,
}: {
  title: string;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <div className={`card p-5 ${className}`}>
      <h3 className="mb-4 text-sm font-semibold text-slate-700">{title}</h3>
      {children}
    </div>
  );
}

function EmptyChart() {
  return (
    <div className="flex h-[220px] items-center justify-center text-sm text-slate-400">
      Add expenses to see this chart.
    </div>
  );
}
