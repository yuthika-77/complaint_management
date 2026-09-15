import  { useState, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { setProcessing, syncCopilotData } from '../store/complaintSlice';
import axios from 'axios';
import { Sparkles, UploadCloud, Send, Bot, Loader2 } from 'lucide-react';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api',
})

function ChatMessage({message}){
  const isUser = message.role === 'user';

  return(
    <div
      className={`p-2.5 rounded-lg max-w-[88%] leading-relaxed whitespace-pre-wrap ${
        isUser
          ? 'bg-blue-600 text-white ml-auto'
          : 'bg-white border border-slate-200 text-slate-800 mr-auto'
      }`}
    >
      {!isUser && (
        <div className="flex items-center gap-1 font-semibold text-[10px] text-blue-600 mb-1">
          <Bot size={12} /> AIVOA Co-Pilot
        </div>
      )}
      {message.text}
    </div>
  )
}
export default function IntakeAssistant() {
  const dispatch = useDispatch();
  const { formData, riskAssessment, isProcessing } = useSelector((state) => state.complaint);

  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: "Hello! I am your AI QMS Co-Pilot. You can log a new complaint, edit specific details (e.g. 'Sorry, the batch number is BMX24602'), or drop a PDF/document above."
    }
  ]);
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  // Auto-scroll chat to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isProcessing]);

  const detectActionType = (text) => {
    const editTriggers = ['sorry', 'change', 'update', 'edit', 'correction', 'replace', 'batch number is', 'batch is', 'quantity is', 'affected quantity'];
    const isEdit = editTriggers.some((kw) => text.toLowerCase().includes(kw));
    return isEdit && Boolean(formData.product_name) ? 'edit_complaint' : 'log_complaint';
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    const cleanText = input.trim();
    if (!cleanText || isProcessing) return;

    const userText = input.trim();
    const actionType = detectActionType(userText);

    setMessages((prev) => [...prev, { role: 'user', text: userText }]);
    setInput('');
    dispatch(setProcessing(true));

    try {
      const res = await api.post('/copilot-chat', {
        message: userText,
        action_type: actionType,
        current_form: formData,
        current_risk: riskAssessment,
      });

      dispatch(syncCopilotData(res.data));
      setMessages((prev) => [...prev, { role: 'assistant', text: res.data.reply }]);
    } catch {
      dispatch(setProcessing(false));
      setMessages((prev) => [...prev, { role: 'assistant', text: "Error communicating with AI engine. Please verify backend." }]);
    }
  };

  const handleFileUpload = async (file) => {
    if (!file) return;
    dispatch(setProcessing(true));
    setMessages((prev) => [...prev, { role: 'user', text: `Uploaded document: ${file.name}` }]);

    const form = new FormData();
    form.append('file', file);
    form.append('current_form', JSON.stringify(formData));
    form.append('current_risk', JSON.stringify(riskAssessment));

    try {
      const res = await api.post('/copilot-upload', form);
      dispatch(syncCopilotData(res.data));
      setMessages((prev) => [...prev, { role: 'assistant', text: res.data.reply }]);
    } catch {
      dispatch(setProcessing(false));
      setMessages((prev) => [...prev, { role: 'assistant', text: `Failed to extract details from ${file.name}.` }]);
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex flex-col h-full overflow-hidden box-border">
      {/*Top Header */}
      <div className="flex justify-between items-center border-b border-slate-100 pb-3 mb-3 shrink-0">
        <div className="flex items-center gap-2">
          <Sparkles className="text-blue-600" size={17} />
          <h2 className="font-semibold text-slate-900 text-sm">AIVOA Co-Pilot AI Assistant</h2>
        </div>
        <span className="text-[10px] font-bold uppercase px-2 py-0.5 bg-blue-50 text-blue-600 rounded">
          QMS Agent
        </span>
      </div>

      {/* File Dropzone */}
      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          if (e.dataTransfer.files?.[0]) handleFileUpload(e.dataTransfer.files[0]);
        }}
        onClick={() => fileInputRef.current?.click()}
        className="border-2 border-dashed border-slate-200 hover:border-blue-400 rounded-xl p-3 text-center cursor-pointer transition-colors bg-slate-50/50 mb-3 shrink-0"
      >
        <input
          type="file"
          ref={fileInputRef}
          className="hidden"
          accept=".pdf,.docx,.txt,.eml"
          onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
        />
        <UploadCloud className="mx-auto text-slate-400 mb-1" size={20} />
        <p className="text-[11px] text-slate-600">
          Drag & drop complaint PDF/Email here or <span className="text-blue-600 underline">browse</span>
        </p>
      </div>

      {/* Dynamic Flexible Chat Area */}
      <div className="flex-1 min-h-0 border border-slate-100 rounded-xl p-3 bg-slate-50/40 flex flex-col justify-between overflow-hidden">
        {/* Scrollable Message History */}
        <div className="flex-1 overflow-y-auto space-y-2 mb-2 pr-1 text-xs">
          {messages.map((m, idx) => (
            <ChatMessage key={idx} message={m} />
          ))}
          {isProcessing && (
            <div className="flex items-center gap-2 p-2 text-xs text-blue-700 bg-blue-50/60 border border-blue-100 rounded-lg">
              <Loader2 className="animate-spin" size={14} />
              <span>Analyzing complaint details and updating form...</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Static Bottom Input Bar */}
        <form onSubmit={handleSendMessage} className="flex gap-2 shrink-0 pt-1">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isProcessing}
            placeholder="Log new complaint or edit (e.g. 'Sorry, batch is BMX...')"
            className="flex-1 px-3 py-2 border border-slate-200 rounded-lg text-xs bg-white focus:outline-none focus:border-blue-500"
          />
          <button
            type="submit"
            disabled={isProcessing || !input.trim()}
            className="p-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg transition-colors shrink-0"
          >
            <Send size={13} />
          </button>
        </form>
      </div>
    </div>
  );
}