import { SurvivalChart } from './components/SurvivalChart';
import { SummaryCards } from './components/SummaryCards';
import "./index.css";

import logo from "./logo.svg";
import reactLogo from "./react.svg";

export function App() {
  return (
    <div className="min-h-screen bg-base-200 p-8">
      <h1 className="text-4xl font-bold text-center mb-8">Titanic Dataset Analysis</h1>
      <SummaryCards />
      <div className="mt-8">
        <SurvivalChart />
      </div>
    </div>
  );
}

export default App;
