import ComplaintForm from './components/ComplaintForm';
import IntakeAssistant from './components/IntakeAssistant';

export default function App() {
  return (
    <main className="h-screen w-screen bg-slate-100 p-4 overflow-hidden box-border">
      <div className="w-full h-full max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-5 overflow-hidden">
        {/* Left Column: Form (7 cols) */}
        <section className="lg:col-span-7 h-full overflow-hidden">
          <ComplaintForm />
        </section>

        {/* Right Column: AI Intake Copilot (5 cols) */}
        <aside className="lg:col-span-5 h-full overflow-hidden">
          <IntakeAssistant />
        </aside>
      </div>
    </main>
  );
}