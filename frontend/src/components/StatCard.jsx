export default function StatCard({ title, value, trend, icon: Icon }) {
  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
        </div>
        {Icon && <Icon className="w-10 h-10 text-gray-300" />}
      </div>
      {trend && (
        <p className={`mt-2 text-sm font-medium ${trend > 0 ? 'text-red-600' : 'text-green-600'}`}>
          {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}% vs mois dernier
        </p>
      )}
    </div>
  )
}