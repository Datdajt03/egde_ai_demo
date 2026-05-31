"use client";

import React, { useState, useEffect, useRef } from 'react';
import { 
  Users, 
  Brain, 
  CheckCircle, 
  RefreshCw, 
  Cpu, 
  Sparkles, 
  Activity, 
  TrendingUp, 
  Layers, 
  Calendar,
  AlertTriangle
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  Legend
} from 'recharts';
import { api, getAiServiceUrl } from '../utils/api';

interface RealtimeStats {
  present_count: number;
  attendance_rate: number;
  focused_count: number;
  neutral_count: number;
  distracted_count: number;
  focus_score: number;
}

interface SummaryStats {
  average_attendance_rate: number;
  average_focus_score: number;
  peak_students: number;
  classroom_capacity: number;
}

interface ClassroomMeta {
  name: string;
  capacity: number;
  subject: string;
  instructor: string;
}

interface HistoryData {
  timestamp: string;
  present_count: number;
  attendance_rate: number;
  focused_count: number;
  neutral_count: number;
  distracted_count: number;
  focus_score: number;
}

export default function Dashboard() {
  const [classroom, setClassroom] = useState<ClassroomMeta | null>(null);
  const [realtime, setRealtime] = useState<RealtimeStats>({
    present_count: 0,
    attendance_rate: 0,
    focused_count: 0,
    neutral_count: 0,
    distracted_count: 0,
    focus_score: 0
  });
  const [summary, setSummary] = useState<SummaryStats>({
    average_attendance_rate: 0,
    average_focus_score: 0,
    peak_students: 0,
    classroom_capacity: 30
  });
  const [history, setHistory] = useState<HistoryData[]>([]);
  const [report, setReport] = useState<string>('');
  const [aiMetadata, setAiMetadata] = useState<any>(null);
  const [generatingReport, setGeneratingReport] = useState(false);
  const [activeTab, setActiveTab] = useState<'video' | 'history'>('video');
  const [streamError, setStreamError] = useState(false);
  const [loading, setLoading] = useState(true);

  // Poll intervals
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch classroom metadata
        const classroomResp = await api.get('/classrooms/room_101');
        setClassroom(classroomResp.data);

        // Fetch realtime metrics
        const realtimeResp = await api.get('/analytics/room_101/realtime');
        setRealtime(realtimeResp.data);

        // Fetch aggregated summary
        const summaryResp = await api.get('/analytics/room_101/summary');
        setSummary(summaryResp.data);

        // Fetch historical logs
        const historyResp = await api.get('/analytics/room_101/history');
        setHistory(historyResp.data);

        setLoading(false);
      } catch (err) {
        console.error('Error fetching dashboard telemetry:', err);
      }
    };

    const fetchReport = async () => {
      try {
        const reportResp = await api.get('/reports/room_101');
        setReport(reportResp.data.report_content);
        setAiMetadata(reportResp.data.metadata);
      } catch (err) {
        console.log('No report generated yet. Request one below.');
      }
    };

    fetchData();
    fetchReport();
    
    // Poll data every 2.5 seconds
    const interval = setInterval(fetchData, 2500);
    return () => clearInterval(interval);
  }, []);

  const handleGenerateReport = async () => {
    setGeneratingReport(true);
    try {
      const resp = await api.post('/reports/room_101/generate');
      setReport(resp.data.report.report_content);
      setAiMetadata(resp.data.report.metadata);
    } catch (err) {
      console.error('Error generating AI report:', err);
      alert('Không thể tạo báo cáo AI lúc này. Vui lòng kiểm tra kết nối API backend.');
    } finally {
      setGeneratingReport(false);
    }
  };

  // Simple clean markdown parser to HTML tags
  const renderMarkdown = (text: string) => {
    if (!text) return <p className="text-gray-400 italic">Nhấp vào nút "Phát sinh Báo cáo AI" bên dưới để tạo phản hồi sư phạm.</p>;
    
    return text.split('\n').map((line, idx) => {
      if (line.startsWith('# ')) {
        return <h1 key={idx} className="text-2xl font-bold text-white mt-6 mb-3 border-b border-gray-800 pb-2">{line.replace('# ', '')}</h1>;
      }
      if (line.startsWith('## ')) {
        return <h2 key={idx} className="text-xl font-semibold text-glowGreen mt-5 mb-2">{line.replace('## ', '')}</h2>;
      }
      if (line.startsWith('### ')) {
        return <h3 key={idx} className="text-lg font-medium text-white mt-4 mb-2">{line.replace('### ', '')}</h3>;
      }
      if (line.startsWith('* ') || line.startsWith('- ')) {
        return <li key={idx} className="text-gray-300 ml-4 list-disc mb-1">{line.replace(/^[\*\-]\s+/, '')}</li>;
      }
      if (line.trim() === '---') {
        return <hr key={idx} className="border-gray-800 my-4" />;
      }
      return <p key={idx} className="text-gray-300 mb-2 leading-relaxed">{line}</p>;
    });
  };

  const aiStreamUrl = `${getAiServiceUrl()}/video_feed`;

  return (
    <div className="flex flex-col min-h-screen bg-[#070A0F] text-[#E2E8F0] font-sans">
      {/* Top Banner Navigation */}
      <header className="sticky top-0 z-40 bg-[#0B0F17]/90 backdrop-blur-md border-b border-techBorder px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="bg-glowGreen/10 p-2 rounded-lg border border-glowGreen/30 animate-pulse">
            <Cpu className="w-6 h-6 text-glowGreen" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-gray-300 to-gray-500 bg-clip-text text-transparent">
              Smart Classroom Analytics
            </h1>
            <p className="text-xs text-glowGreen flex items-center gap-1 font-mono">
              <span className="inline-block w-2 h-2 rounded-full bg-glowGreen"></span>
              Edge AI Edition • Local Processing
            </p>
          </div>
        </div>

        {classroom && (
          <div className="hidden md:flex items-center gap-6 text-sm text-gray-400">
            <div className="bg-[#121824] px-4 py-1.5 rounded-lg border border-techBorder">
              <span className="text-xs text-gray-500 block font-mono">MÔN HỌC</span>
              <span className="font-semibold text-white">{classroom.subject}</span>
            </div>
            <div className="bg-[#121824] px-4 py-1.5 rounded-lg border border-techBorder">
              <span className="text-xs text-gray-500 block font-mono">GIẢNG VIÊN</span>
              <span className="font-semibold text-white">{classroom.instructor}</span>
            </div>
            <div className="bg-[#121824] px-4 py-1.5 rounded-lg border border-techBorder">
              <span className="text-xs text-gray-500 block font-mono">PHÒNG HỌC</span>
              <span className="font-semibold text-glowGreen">{classroom.name}</span>
            </div>
          </div>
        )}
      </header>

      {/* Main Container */}
      <main className="flex-1 p-6 md:p-8 space-y-6 max-w-7xl mx-auto w-full">
        {loading ? (
          <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-4">
            <RefreshCw className="w-8 h-8 text-glowGreen animate-spin" />
            <p className="text-gray-400 text-sm">Đang tải cấu hình Edge telemetry và kết nối MongoDB...</p>
          </div>
        ) : (
          <>
            {/* Realtime KPI Banner */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {/* Card 1: Live Presence */}
              <div className="bg-[#0B0F17] border border-techBorder rounded-xl p-5 relative overflow-hidden transition-all duration-300 hover:border-glowGreen/30 hover:shadow-glow group">
                <div className="absolute top-0 right-0 w-24 h-24 bg-glowGreen/5 rounded-full blur-2xl group-hover:bg-glowGreen/10 transition-colors"></div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-mono text-gray-500 font-bold">LỚP HỌC HIỆN TẠI</span>
                  <div className="bg-glowGreen/15 p-2 rounded-lg">
                    <Users className="w-5 h-5 text-glowGreen" />
                  </div>
                </div>
                <div className="mt-4 flex items-baseline gap-2">
                  <span className="text-3xl font-extrabold tracking-tight text-white">
                    {realtime.present_count}
                  </span>
                  <span className="text-sm text-gray-500 font-medium">
                    / {classroom?.capacity || 30} sinh viên
                  </span>
                </div>
                <p className="mt-2 text-xs text-gray-400 flex items-center gap-1">
                  <TrendingUp className="w-3.5 h-3.5 text-glowGreen" />
                  Sức chứa khai thác đạt {realtime.attendance_rate}%
                </p>
              </div>

              {/* Card 2: Attendance Rate */}
              <div className="bg-[#0B0F17] border border-techBorder rounded-xl p-5 relative overflow-hidden transition-all duration-300 hover:border-glowBlue/30 hover:shadow-glowBlue group">
                <div className="absolute top-0 right-0 w-24 h-24 bg-glowBlue/5 rounded-full blur-2xl group-hover:bg-glowBlue/10 transition-colors"></div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-mono text-gray-500 font-bold">TỶ LỆ HIỆN DIỆN TB</span>
                  <div className="bg-glowBlue/15 p-2 rounded-lg">
                    <CheckCircle className="w-5 h-5 text-glowBlue" />
                  </div>
                </div>
                <div className="mt-4 flex items-baseline gap-2">
                  <span className="text-3xl font-extrabold tracking-tight text-white">
                    {summary.average_attendance_rate}%
                  </span>
                </div>
                <p className="mt-2 text-xs text-gray-400">
                  Cao nhất buổi học: <span className="text-white font-semibold font-mono">{summary.peak_students}</span> sinh viên
                </p>
              </div>

              {/* Card 3: Focus Score */}
              <div className="bg-[#0B0F17] border border-techBorder rounded-xl p-5 relative overflow-hidden transition-all duration-300 hover:border-glowYellow/30 hover:shadow-glowYellow group">
                <div className="absolute top-0 right-0 w-24 h-24 bg-glowYellow/5 rounded-full blur-2xl group-hover:bg-glowYellow/10 transition-colors"></div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-mono text-gray-500 font-bold">ĐIỂM TẬP TRUNG LIVE</span>
                  <div className="bg-glowYellow/15 p-2 rounded-lg">
                    <Brain className="w-5 h-5 text-glowYellow" />
                  </div>
                </div>
                <div className="mt-4 flex items-baseline gap-2">
                  <span className="text-3xl font-extrabold tracking-tight text-white">
                    {realtime.focus_score}%
                  </span>
                </div>
                <p className="mt-2 text-xs text-gray-400">
                  Điểm trung bình buổi học: <span className="text-white font-semibold font-mono">{summary.average_focus_score}%</span>
                </p>
              </div>

              {/* Card 4: Focus Distribution */}
              <div className="bg-[#0B0F17] border border-techBorder rounded-xl p-4 flex flex-col justify-between">
                <span className="text-xs font-mono text-gray-500 font-bold block mb-2">PHÂN PHỐI TRẠNG THÁI TRỰC TIẾP</span>
                <div className="space-y-2">
                  <div className="flex justify-between items-center text-xs">
                    <span className="flex items-center gap-1.5 text-gray-400">
                      <span className="w-2.5 h-2.5 rounded-full bg-glowGreen inline-block"></span>
                      Focused
                    </span>
                    <span className="font-semibold text-white font-mono">{realtime.focused_count} sinh viên</span>
                  </div>
                  <div className="flex justify-between items-center text-xs">
                    <span className="flex items-center gap-1.5 text-gray-400">
                      <span className="w-2.5 h-2.5 rounded-full bg-glowYellow inline-block"></span>
                      Neutral
                    </span>
                    <span className="font-semibold text-white font-mono">{realtime.neutral_count} sinh viên</span>
                  </div>
                  <div className="flex justify-between items-center text-xs">
                    <span className="flex items-center gap-1.5 text-gray-400">
                      <span className="w-2.5 h-2.5 rounded-full bg-glowRed inline-block"></span>
                      Distracted
                    </span>
                    <span className="font-semibold text-white font-mono">{realtime.distracted_count} sinh viên</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Video Feed and Focus Chart Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Live Video Panel (8 columns) */}
              <div className="lg:col-span-8 bg-[#0B0F17] border border-techBorder rounded-xl overflow-hidden flex flex-col">
                <div className="px-5 py-4 border-b border-techBorder flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-red-600 animate-ping"></span>
                    <span className="font-bold text-sm text-white tracking-wider flex items-center gap-2">
                      LIVE STREAM: EDGE CAMERA FEED
                    </span>
                  </div>
                  <div className="flex items-center bg-[#131B2A] rounded-lg p-0.5 border border-techBorder">
                    <button 
                      onClick={() => setActiveTab('video')} 
                      className={`px-3 py-1 text-xs font-medium rounded-md transition-all ${activeTab === 'video' ? 'bg-glowGreen text-black font-semibold' : 'text-gray-400 hover:text-white'}`}
                    >
                      Camera Realtime
                    </button>
                    <button 
                      onClick={() => setActiveTab('history')} 
                      className={`px-3 py-1 text-xs font-medium rounded-md transition-all ${activeTab === 'history' ? 'bg-glowGreen text-black font-semibold' : 'text-gray-400 hover:text-white'}`}
                    >
                      Bảng Số Liệu
                    </button>
                  </div>
                </div>

                <div className="flex-1 bg-black aspect-video flex items-center justify-center relative overflow-hidden min-h-[350px]">
                  {activeTab === 'video' ? (
                    !streamError ? (
                      <img 
                        src={aiStreamUrl} 
                        alt="Edge AI Live Classroom Telemetry Feed" 
                        className="w-full h-full object-cover"
                        onError={() => setStreamError(true)}
                      />
                    ) : (
                      <div className="flex flex-col items-center justify-center p-8 space-y-3 text-center">
                        <AlertTriangle className="w-12 h-12 text-glowYellow animate-bounce" />
                        <h4 className="text-white font-semibold text-lg">Lỗi tải luồng video AI Service</h4>
                        <p className="text-gray-500 text-sm max-w-md">
                          Không thể kết nối đến luồng MJPEG tại `{aiStreamUrl}`. 
                          Vui lòng đảm bảo container `ai-service` đang chạy trên cổng `8001`.
                        </p>
                        <button 
                          onClick={() => setStreamError(false)}
                          className="px-4 py-2 bg-[#121A28] border border-techBorder rounded-lg text-sm text-white hover:border-glowGreen/40 transition-colors"
                        >
                          Thử tải lại luồng camera
                        </button>
                      </div>
                    )
                  ) : (
                    <div className="w-full h-full p-6 overflow-y-auto bg-[#070A0F]">
                      <h4 className="text-glowGreen font-bold font-mono text-sm mb-4">LỊCH SỬ TELEMETRY THỜI GIAN THỰC (MONGODB)</h4>
                      <table className="w-full text-xs text-left border-collapse">
                        <thead>
                          <tr className="border-b border-techBorder text-gray-500 uppercase font-mono">
                            <th className="py-2">Thời gian</th>
                            <th className="py-2">Hiện diện (%)</th>
                            <th className="py-2">Focused</th>
                            <th className="py-2">Neutral</th>
                            <th className="py-2">Distracted</th>
                            <th className="py-2">Điểm tập trung</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-techBorder">
                          {history.slice().reverse().map((h, i) => (
                            <tr key={i} className="text-gray-300 hover:bg-[#121B2A]/40">
                              <td className="py-2.5 font-mono text-gray-500">{h.timestamp}</td>
                              <td className="py-2.5 font-semibold text-white">{h.attendance_rate}% ({h.present_count} SV)</td>
                              <td className="py-2.5 text-glowGreen">{h.focused_count}</td>
                              <td className="py-2.5 text-glowYellow">{h.neutral_count}</td>
                              <td className="py-2.5 text-glowRed">{h.distracted_count}</td>
                              <td className="py-2.5 font-mono font-bold text-glowYellow">{h.focus_score}%</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              </div>

              {/* Engagement Status Realtime Chart (4 columns) */}
              <div className="lg:col-span-4 bg-[#0B0F17] border border-techBorder rounded-xl p-5 flex flex-col justify-between">
                <div>
                  <h3 className="text-sm font-bold tracking-wider text-white mb-1 uppercase">Xu Hướng Tập Trung (Realtime)</h3>
                  <p className="text-xs text-gray-500 mb-4">Biểu diễn biến động mức độ tập trung của cả lớp qua thời gian.</p>
                </div>

                <div className="h-[250px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={history}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                      <XAxis dataKey="timestamp" stroke="#4B5563" fontSize={10} tickLine={false} />
                      <YAxis domain={[0, 100]} stroke="#4B5563" fontSize={10} tickLine={false} />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#0B0F17', borderColor: '#1F2937', color: '#fff' }}
                        itemStyle={{ color: '#F1C40F' }}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="focus_score" 
                        stroke="#F1C40F" 
                        strokeWidth={2}
                        dot={false}
                        name="Điểm tập trung" 
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>

                <div className="bg-[#121B2A]/40 border border-techBorder rounded-lg p-3 text-xs text-gray-400 mt-4">
                  <div className="flex gap-2">
                    <Sparkles className="w-5 h-5 text-glowYellow shrink-0" />
                    <p>
                      Mức độ tập trung hiện tại đạt <span className="text-white font-bold">{realtime.focus_score}%</span>. 
                      Đa số sinh viên đang chú ý nghe giảng và ghi chép bài học tích cực.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Attendance & Focus Stats charts */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Chart 1: Attendance History */}
              <div className="bg-[#0B0F17] border border-techBorder rounded-xl p-5">
                <div className="mb-4">
                  <h3 className="text-sm font-bold tracking-wider text-white uppercase flex items-center gap-2">
                    <Activity className="w-4 h-4 text-glowBlue" /> Lịch sử Điểm Danh & Sĩ Số Lớp
                  </h3>
                  <p className="text-xs text-gray-500">Tần suất và số lượng sinh viên tham gia lớp học.</p>
                </div>
                <div className="h-[250px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={history}>
                      <defs>
                        <linearGradient id="colorAtt" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#3498DB" stopOpacity={0.3}/>
                          <stop offset="95%" stopColor="#3498DB" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                      <XAxis dataKey="timestamp" stroke="#4B5563" fontSize={10} />
                      <YAxis domain={[0, 35]} stroke="#4B5563" fontSize={10} />
                      <Tooltip contentStyle={{ backgroundColor: '#0B0F17', borderColor: '#1F2937' }} />
                      <Area 
                        type="monotone" 
                        dataKey="present_count" 
                        stroke="#3498DB" 
                        strokeWidth={2}
                        fillOpacity={1}
                        fill="url(#colorAtt)"
                        name="Số lượng sinh viên" 
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Chart 2: Focus States Area Chart */}
              <div className="bg-[#0B0F17] border border-techBorder rounded-xl p-5">
                <div className="mb-4">
                  <h3 className="text-sm font-bold tracking-wider text-white uppercase flex items-center gap-2">
                    <Layers className="w-4 h-4 text-glowGreen" /> Phân Tích Mức Độ Tập Trung
                  </h3>
                  <p className="text-xs text-gray-500">Phân bố tỷ lệ trạng thái (Focused, Neutral, Distracted).</p>
                </div>
                <div className="h-[250px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={history}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                      <XAxis dataKey="timestamp" stroke="#4B5563" fontSize={10} />
                      <YAxis stroke="#4B5563" fontSize={10} />
                      <Tooltip contentStyle={{ backgroundColor: '#0B0F17', borderColor: '#1F2937' }} />
                      <Legend verticalAlign="top" height={36} iconSize={8} wrapperStyle={{ fontSize: 10 }} />
                      <Bar dataKey="focused_count" stackId="a" fill="#2ECC71" name="Focused" />
                      <Bar dataKey="neutral_count" stackId="a" fill="#F1C40F" name="Neutral" />
                      <Bar dataKey="distracted_count" stackId="a" fill="#E74C3C" name="Distracted" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* AI Classroom Report Component */}
            <div className="bg-[#0B0F17] border border-techBorder rounded-xl overflow-hidden">
              <div className="px-6 py-5 border-b border-techBorder bg-gradient-to-r from-[#0E1523] to-[#0B0F17] flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="bg-glowYellow/15 p-2 rounded-xl border border-glowYellow/30">
                    <Sparkles className="w-6 h-6 text-glowYellow animate-pulse" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white uppercase tracking-wide">Báo Cáo Sư Phạm Tự Động (Gemini AI)</h3>
                    <p className="text-xs text-gray-400">
                      Hệ thống tự động đồng bộ dữ liệu MongoDB qua Gemini API để phân tích đề xuất giảng dạy.
                    </p>
                  </div>
                </div>

                <button 
                  onClick={handleGenerateReport}
                  disabled={generatingReport}
                  className="bg-gradient-to-r from-glowYellow via-amber-500 to-yellow-600 hover:from-yellow-400 hover:to-amber-500 text-black font-extrabold px-6 py-2.5 rounded-xl flex items-center justify-center gap-2 transition-all shadow-md active:scale-95 disabled:opacity-60 disabled:pointer-events-none"
                >
                  <RefreshCw className={`w-4 h-4 ${generatingReport ? 'animate-spin' : ''}`} />
                  {generatingReport ? 'Đang phân tích dữ liệu...' : 'Phát Sinh Báo Cáo AI'}
                </button>
              </div>

              {/* AI Report Markdown display panel */}
              <div className="p-6 md:p-8 bg-[#0D121F]/30 max-h-[500px] overflow-y-auto border-b border-techBorder font-sans prose prose-invert max-w-none">
                {renderMarkdown(report)}
              </div>

              {aiMetadata && (
                <div className="px-6 py-4 bg-[#090D14] flex items-center justify-between text-xs text-gray-500 border-t border-techBorder">
                  <span className="flex items-center gap-1">
                    <Cpu className="w-3.5 h-3.5" /> Engine: <span className="text-gray-300 font-mono font-semibold">{aiMetadata.generated_by}</span>
                  </span>
                  <span>
                    Báo cáo tạo lúc: <span className="text-gray-300 font-mono">{new Date(aiMetadata.generated_at || Date.now()).toLocaleString('vi-VN')}</span>
                  </span>
                </div>
              )}
            </div>
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-auto py-6 border-t border-techBorder bg-[#070A0F] text-center text-xs text-gray-600">
        <p>© 2026 Smart Classroom Analytics • Edge AI, MongoDB, and Gemini API Demonstration</p>
      </footer>
    </div>
  );
}
