import { useApi } from '../hooks/useApi';
import { Summary } from '../types/passenger';

export function SummaryCards() {
  const { data, loading } = useApi<Summary>('/passengers/summary');

  if (loading) return <div className="loading loading-spinner loading-lg" />;

  return (
    <div className="stats shadow">
      <div className="stat">
        <div className="stat-title">Total Passengers</div>
        <div className="stat-value">{data?.total_passengers}</div>
      </div>
      <div className="stat">
        <div className="stat-title">Survived</div>
        <div className="stat-value text-success">{data?.survived}</div>
      </div>
      <div className="stat">
        <div className="stat-title">Died</div>
        <div className="stat-value text-error">{data?.died}</div>
      </div>
      <div className="stat">
        <div className="stat-title">Survival Rate</div>
        <div className="stat-value">{((data?.survival_rate || 0) * 100).toFixed(1)}%</div>
      </div>
    </div>
  );
}
