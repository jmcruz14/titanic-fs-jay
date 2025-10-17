import { usePaginatedApi } from '../hooks/useApi';
import { Passenger, PaginatedResponse, Filters } from '../types/passenger'; 
import { useEffect, useRef, useState, useMemo } from 'react';
import * as d3 from 'd3';

export function SurvivalChart() {
  const svgRef = useRef<SVGSVGElement>(null);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(100);
  const [filters, setFilters] = useState<Filters>({});

  const { data, loading, error } = usePaginatedApi(page, pageSize, filters);

  // Memoize aggregated chart data
  const chartData = useMemo(() => {
    if (!data?.passengers.length) return [];

    const aggregated = d3.rollup(
      data.passengers,
      v => v.length,
      d => `Class ${d.Pclass}`,
      d => d.Survived === 1 ? 'Survived' : 'Died'
    );

    const result: Array<{ category: string; survived: number; died: number }> = [];
    aggregated.forEach((survivalMap, category) => {
      result.push({
        category,
        survived: survivalMap.get('Survived') || 0,
        died: survivalMap.get('Died') || 0,
      });
    });

    return result.sort((a, b) => a.category.localeCompare(b.category));
  }, [data]);

  useEffect(() => {
    if (!data?.passengers.length || !svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const width = 800;
    const height = 400;
    const margin = { top: 50, right: 120, bottom: 80, left: 60 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const g = svg
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Aggregate data by class and survival
    const aggregated = d3.rollup(
      data.passengers,
      v => v.length,
      d => `Class ${d.Pclass}`,
      d => d.Survived === 1 ? 'Survived' : 'Died'
    );

    const chartData: Array<{ category: string; survived: number; died: number }> = [];
    aggregated.forEach((survivalMap, category) => {
      chartData.push({
        category,
        survived: survivalMap.get('Survived') || 0,
        died: survivalMap.get('Died') || 0,
      });
    });

    chartData.sort((a, b) => a.category.localeCompare(b.category));

    // Scales
    const x0 = d3.scaleBand()
      .domain(chartData.map(d => d.category))
      .range([0, innerWidth])
      .padding(0.2);

    const x1 = d3.scaleBand()
      .domain(['Survived', 'Died'])
      .range([0, x0.bandwidth()])
      .padding(0.05);

    const y = d3.scaleLinear()
      .domain([0, d3.max(chartData, d => Math.max(d.survived, d.died)) || 0])
      .nice()
      .range([innerHeight, 0]);

    const color = d3.scaleOrdinal()
      .domain(['Survived', 'Died'])
      .range(['#22c55e', '#ef4444']);

    // X Axis
    g.append('g')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(d3.axisBottom(x0))
      .selectAll('text')
      .style('font-size', '13px')
      .style('font-weight', '600');

    // Y Axis
    g.append('g')
      .call(d3.axisLeft(y).ticks(5))
      .selectAll('text')
      .style('font-size', '12px');

    // Y Axis Label
    g.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', -45)
      .attr('x', -innerHeight / 2)
      .attr('text-anchor', 'middle')
      .style('font-size', '12px')
      .style('font-weight', 'bold')
      .text('Number of Passengers');

    // Draw grouped bars
    const categoryGroups = g.selectAll('.category-group')
      .data(chartData)
      .enter()
      .append('g')
      .attr('class', 'category-group')
      .attr('transform', d => `translate(${x0(d.category)},0)`);

    // Survived bars
    categoryGroups.append('rect')
      .attr('x', x1('Survived')!)
      .attr('y', d => y(d.survived))
      .attr('width', x1.bandwidth())
      .attr('height', d => innerHeight - y(d.survived))
      .attr('fill', color('Survived') as string)
      .attr('rx', 2);

    // Died bars
    categoryGroups.append('rect')
      .attr('x', x1('Died')!)
      .attr('y', d => y(d.died))
      .attr('width', x1.bandwidth())
      .attr('height', d => innerHeight - y(d.died))
      .attr('fill', color('Died') as string)
      .attr('rx', 2);

    // Value labels on bars
    categoryGroups.selectAll('.label-survived')
      .data(d => [d])
      .enter()
      .append('text')
      .attr('class', 'label-survived')
      .attr('x', x1('Survived')! + x1.bandwidth() / 2)
      .attr('y', d => y(d.survived) - 5)
      .attr('text-anchor', 'middle')
      .style('font-size', '11px')
      .style('font-weight', 'bold')
      .style('fill', '#22c55e')
      .text(d => d.survived);

    categoryGroups.selectAll('.label-died')
      .data(d => [d])
      .enter()
      .append('text')
      .attr('class', 'label-died')
      .attr('x', x1('Died')! + x1.bandwidth() / 2)
      .attr('y', d => y(d.died) - 5)
      .attr('text-anchor', 'middle')
      .style('font-size', '11px')
      .style('font-weight', 'bold')
      .style('fill', '#ef4444')
      .text(d => d.died);

    // Legend
    const legend = svg.append('g')
      .attr('transform', `translate(${width - 100}, ${margin.top})`);

    ['Survived', 'Died'].forEach((status, i) => {
      const legendRow = legend.append('g')
        .attr('transform', `translate(0, ${i * 25})`);

      legendRow.append('rect')
        .attr('width', 18)
        .attr('height', 18)
        .attr('fill', color(status) as string)
        .attr('rx', 2);

      legendRow.append('text')
        .attr('x', 25)
        .attr('y', 13)
        .style('font-size', '13px')
        .text(status);
    });

    // Title
    svg.append('text')
      .attr('x', width / 2)
      .attr('y', 25)
      .attr('text-anchor', 'middle')
      .style('font-size', '18px')
      .style('font-weight', 'bold')
      .text('Survival Distribution by Passenger Class');

  }, [data]);

  const handleFilterChange = (key: keyof Filters, value: any) => {
    setFilters(prev => ({
      ...prev,
      [key]: value === '' ? undefined : value,
    }));
    setPage(1); // Reset to first page when filters change
  };

  const clearFilters = () => {
    setFilters({});
    setPage(1);
  };

  return (
    <div className="card bg-base-100 shadow-xl">
      <div className="card-body">
        <h2 className="card-title mb-4">Survival Analysis</h2>

        {/* Filters */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
          <div className="form-control">
            <label className="label"><span className="label-text">Survived</span></label>
            <select
              className="select select-bordered select-sm"
              value={filters.survived ?? ''}
              onChange={(e) => handleFilterChange('survived', e.target.value ? parseInt(e.target.value) : '')}
            >
              <option value="">All</option>
              <option value="1">Yes</option>
              <option value="0">No</option>
            </select>
          </div>

          <div className="form-control">
            <label className="label"><span className="label-text">Sex</span></label>
            <select
              className="select select-bordered select-sm"
              value={filters.sex ?? ''}
              onChange={(e) => handleFilterChange('sex', e.target.value)}
            >
              <option value="">All</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
            </select>
          </div>

          <div className="form-control">
            <label className="label"><span className="label-text">Class</span></label>
            <select
              className="select select-bordered select-sm"
              value={filters.pclass ?? ''}
              onChange={(e) => handleFilterChange('pclass', e.target.value ? parseInt(e.target.value) : '')}
            >
              <option value="">All</option>
              <option value="1">1st</option>
              <option value="2">2nd</option>
              <option value="3">3rd</option>
            </select>
          </div>

          <div className="form-control">
            <label className="label"><span className="label-text">Embarked</span></label>
            <select
              className="select select-bordered select-sm"
              value={filters.embarked ?? ''}
              onChange={(e) => handleFilterChange('embarked', e.target.value)}
            >
              <option value="">All</option>
              <option value="C">Cherbourg</option>
              <option value="Q">Queenstown</option>
              <option value="S">Southampton</option>
            </select>
          </div>

          <div className="form-control">
            <label className="label"><span className="label-text">Siblings/Spouses</span></label>
            <input
              type="number"
              className="input input-bordered input-sm"
              placeholder="All"
              min="0"
              value={filters.sibsp ?? ''}
              onChange={(e) => handleFilterChange('sibsp', e.target.value ? parseInt(e.target.value) : '')}
            />
          </div>

          <div className="form-control">
            <label className="label"><span className="label-text">Parents/Children</span></label>
            <input
              type="number"
              className="input input-bordered input-sm"
              placeholder="All"
              min="0"
              value={filters.parch ?? ''}
              onChange={(e) => handleFilterChange('parch', e.target.value ? parseInt(e.target.value) : '')}
            />
          </div>

          <div className="form-control">
            <label className="label"><span className="label-text">Page Size</span></label>
            <select
              className="select select-bordered select-sm"
              value={pageSize}
              onChange={(e) => {
                setPageSize(parseInt(e.target.value));
                setPage(1);
              }}
            >
              <option value="20">20</option>
              <option value="50">50</option>
              <option value="100">100</option>
            </select>
          </div>

          <div className="form-control">
            <label className="label"><span className="label-text opacity-0">Clear</span></label>
            <button className="btn btn-sm btn-outline" onClick={clearFilters}>
              Clear Filters
            </button>
          </div>
        </div>

        {/* Chart */}
        {loading ? (
          <div className="flex justify-center items-center h-96">
            <span className="loading loading-spinner loading-lg"></span>
          </div>
        ) : (
          <>
            <svg ref={svgRef} width={800} height={400} className="mx-auto" />
            
            {/* Pagination */}
            <div className="flex justify-between items-center mt-6">
              <div className="text-sm">
                Showing {data?.returned || 0} of {data?.count || 0} passengers
              </div>
              <div className="join">
                <button
                  className="join-item btn btn-sm"
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                >
                  «
                </button>
                <button className="join-item btn btn-sm">
                  Page {page} of {data?.total_pages || 1}
                </button>
                <button
                  className="join-item btn btn-sm"
                  onClick={() => setPage(p => p + 1)}
                  disabled={page === (data?.total_pages || 1)}
                >
                  »
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
