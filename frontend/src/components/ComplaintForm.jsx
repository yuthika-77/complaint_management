import { useSelector, useDispatch } from 'react-redux';
import { resetAll } from '../store/complaintSlice';
import axios from 'axios';
import { RotateCcw, Save, ShieldAlert, Bot } from 'lucide-react';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api',
})


export default function ComplaintForm() {
  const dispatch = useDispatch();
  const formData = useSelector((state) => state.complaint.formData);
  const risk = useSelector((state) => state.complaint.riskAssessment);

  const handleSave = async () => {
    try {
      const res = await api.post('/save-complaint', {
        ...formData,
        root_cause_hypothesis: risk.risk_justification,
        recommended_capa: risk.capa_recommendation,
      });
      alert(`Complaint logged successfully! Record ID: ${res.data.complaint_id}`);
    } catch {
      alert('Error saving complaint. Ensure backend is running.');
    }
  };

  const readOnlyInputClass =
    "w-full px-3 py-2 border border-slate-200 rounded-lg text-slate-800 bg-slate-50/60 placeholder-slate-400 cursor-not-allowed text-xs transition-colors focus:outline-none";

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm flex flex-col h-full overflow-y-auto">
      <div className="flex justify-between items-start border-b border-slate-100 pb-4 mb-5">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Log Customer Complaint</h1>
          <p className="text-xs text-slate-500 font-medium mt-0.5">API & FDF Quality Assurance Module</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-semibold px-2.5 py-1 bg-blue-50 text-blue-700 border border-blue-200 rounded-full flex items-center gap-1">
            <Bot size={12} /> AI Controlled
          </span>
          <span className="text-[11px] font-semibold px-3 py-1 bg-amber-50 text-amber-700 border border-amber-200 rounded-full">
            Pending Triage
          </span>
        </div>
      </div>

      <div className="space-y-5 flex-1 text-xs">
        {/* Origin & Customer Details */}
        <div>
          <h2 className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">1. ORIGIN & CUSTOMER DETAILS</h2>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Complaint Source</label>
              <input readOnly type="text" value={formData.complaint_source} placeholder="Awaiting AI extraction..." className={readOnlyInputClass} />
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Customer Name</label>
              <input readOnly type="text" value={formData.customer_name} placeholder="Awaiting AI extraction..." className={readOnlyInputClass} />
            </div>
          </div>
        </div>

        {/* Product & Batch Identification */}
        <div>
          <h2 className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">2. PRODUCT & BATCH IDENTIFICATION</h2>
          <div className="grid grid-cols-2 gap-3 mb-2">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Product Name</label>
              <input readOnly type="text" value={formData.product_name} placeholder="Awaiting AI extraction..." className={readOnlyInputClass} />
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Product Strength/Grade</label>
              <input readOnly type="text" value={formData.product_strength_grade} placeholder="Awaiting AI extraction..." className={readOnlyInputClass} />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3 mb-2">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Batch/Lot Number</label>
              <input readOnly type="text" value={formData.batch_number} placeholder="Awaiting AI extraction..." className={readOnlyInputClass} />
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Manufacturing Date</label>
              <input readOnly type="text" value={formData.manufacturing_date} placeholder="YYYY-MM-DD" className={readOnlyInputClass} />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Expiry Date</label>
              <input readOnly type="text" value={formData.expiry_date} placeholder="YYYY-MM-DD" className={readOnlyInputClass} />
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Quantity Affected</label>
              <input readOnly type="text" value={formData.quantity_affected} placeholder="e.g. 50 kg or 120 vials" className={readOnlyInputClass} />
            </div>
          </div>
        </div>

        {/* Complaint Details */}
        <div>
          <h2 className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">3. COMPLAINT DETAILS</h2>
          <div className="grid grid-cols-2 gap-3 mb-2">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Complaint Type</label>
              <input readOnly type="text" value={formData.complaint_type} placeholder="Packaging, Contamination, Defect" className={readOnlyInputClass} />
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Complaint Date</label>
              <input readOnly type="text" value={formData.complaint_date} placeholder="YYYY-MM-DD" className={readOnlyInputClass} />
            </div>
          </div>
          <div>
            <label className="block font-semibold text-slate-700 mb-1">Detailed Complaint Description</label>
            <textarea readOnly rows={2} value={formData.detailed_description} placeholder="Awaiting AI extraction..." className={readOnlyInputClass} />
          </div>
        </div>

        {/* Initial Assessment & Priority */}
        <div>
          <h2 className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">4. INITIAL ASSESSMENT & PRIORITY</h2>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Initial Severity</label>
              <input readOnly type="text" value={formData.initial_severity} className={readOnlyInputClass} />
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Priority</label>
              <input readOnly type="text" value={formData.priority} className={readOnlyInputClass} />
            </div>
          </div>
        </div>

        {/* AI Co-Pilot Risk Assessment Box */}
        <div className="p-3.5 bg-blue-50/70 border border-blue-100 rounded-xl space-y-2">
          <div className="flex items-center gap-1.5 text-blue-900 font-bold text-xs">
            <ShieldAlert size={15} /> AI Co-Pilot Risk Assessment
          </div>
          <div className="text-xs grid grid-cols-2 gap-2 pt-1 border-t border-blue-100 text-blue-950">
            <div>
              <span className="font-semibold block text-[10px] text-blue-700 uppercase">Suggested Action:</span>
              <span>{risk.suggested_next_action}</span>
            </div>
            <div>
              <span className="font-semibold block text-[10px] text-blue-700 uppercase">Regulatory Impact:</span>
              <span>{risk.regulatory_impact}</span>
            </div>
          </div>

          {/* Root Cause Hypothesis Row */}
          <div className="pt-1 border-t border-blue-100 text-xs text-blue-950">
            <span className="font-semibold block text-[10px] text-blue-700 uppercase tracking-wide">
              Root Cause Hypothesis:
            </span>
            <p className="mt-0.5 leading-relaxed text-slate-800">
              {risk.risk_justification || 'Awaiting AI copilot risk assessment...'}
            </p>
          </div>
          
          {/* Recommended CAPA */}
          {risk.capa_recommendation && (
            <div className="pt-1.5 border-t border-blue-100 text-[11px] text-blue-900">
              <span className="font-semibold block text-[10px] text-blue-700 uppercase tracking-wide mb-1">
                Recommended CAPA:
              </span>
              <ul className="space-y-1 pl-1">
                {risk.capa_recommendation
                  .split(/(?=\b\d+\.\s)/) // Splits on "1. ", "2. ", "3. ", etc.
                  .filter((item) => item.trim().length > 0)
                  .map((step, idx) => {
                    const cleanStep = step.trim().replace(/^\d+\.\s*/, '');
                    return (
                      <li key={idx} className="flex items-start gap-1.5 text-slate-800 leading-relaxed">
                        <span className="shrink-0 flex items-center justify-center w-4 h-4 rounded-full bg-blue-100 text-blue-800 font-bold text-[9px] mt-0.5">
                          {idx + 1}
                        </span>
                        <span>{cleanStep}</span>
                      </li>
                    );
                  })}
              </ul>
            </div>
          )}
        </div>
      </div>

      <div className="flex justify-between items-center pt-3 border-t border-slate-100 mt-3">
        <button
          type="button"
          onClick={() => dispatch(resetAll())}
          className="flex items-center gap-1.5 px-3 py-1.5 border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-lg text-xs font-medium"
        >
          <RotateCcw size={13} /> Reset Form
        </button>
        <button
          type="button"
          onClick={handleSave}
          className="flex items-center gap-1.5 px-4 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-medium shadow-sm"
        >
          <Save size={13} /> Save Complaint
        </button>
      </div>
    </div>
  );
}