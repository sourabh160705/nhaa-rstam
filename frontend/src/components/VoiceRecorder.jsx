import React, { useState, useRef, useCallback, useEffect } from 'react';
import { UploadCloud, FileAudio, Play, X, Mic, Square, Pause, Circle } from 'lucide-react';

export default function VoiceRecorder({ onAnalyze }) {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [mode, setMode] = useState('choose'); // 'choose' | 'recording' | 'paused' | 'recorded' | 'uploaded'
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioURL, setAudioURL] = useState(null);
  const [waveform, setWaveform] = useState(new Array(40).fill(5));

  const fileInputRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerRef = useRef(null);
  const analyserRef = useRef(null);
  const animFrameRef = useRef(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      clearInterval(timerRef.current);
      cancelAnimationFrame(animFrameRef.current);
      if (audioURL) URL.revokeObjectURL(audioURL);
    };
  }, [audioURL]);

  // ─── Waveform visualizer ───
  const updateWaveform = useCallback(() => {
    if (!analyserRef.current) return;
    const data = new Uint8Array(analyserRef.current.frequencyBinCount);
    analyserRef.current.getByteFrequencyData(data);
    const bars = 40;
    const step = Math.floor(data.length / bars);
    const newWave = [];
    for (let i = 0; i < bars; i++) {
      const val = data[i * step] || 0;
      newWave.push(Math.max(3, (val / 255) * 48));
    }
    setWaveform(newWave);
    animFrameRef.current = requestAnimationFrame(updateWaveform);
  }, []);

  // ─── Start recording ───
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioChunksRef.current = [];

      // Set up analyser for waveform
      const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      const source = audioCtx.createMediaStreamSource(stream);
      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      analyserRef.current = analyser;

      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = () => {
        stream.getTracks().forEach(t => t.stop());
        audioCtx.close();
        cancelAnimationFrame(animFrameRef.current);

        const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const url = URL.createObjectURL(blob);
        const recordedFile = new File([blob], `recording-${Date.now()}.webm`, { type: 'audio/webm' });

        setAudioURL(url);
        setFile(recordedFile);
        setMode('recorded');
        setWaveform(new Array(40).fill(5));
      };

      mediaRecorder.start(100);
      setMode('recording');
      setRecordingTime(0);
      timerRef.current = setInterval(() => setRecordingTime(t => t + 1), 1000);
      updateWaveform();
    } catch (err) {
      console.error('Microphone access denied:', err);
      alert('Microphone access is required to record audio. Please allow microphone access and try again.');
    }
  };

  // ─── Pause / Resume ───
  const pauseRecording = () => {
    if (mediaRecorderRef.current?.state === 'recording') {
      mediaRecorderRef.current.pause();
      clearInterval(timerRef.current);
      cancelAnimationFrame(animFrameRef.current);
      setMode('paused');
    }
  };

  const resumeRecording = () => {
    if (mediaRecorderRef.current?.state === 'paused') {
      mediaRecorderRef.current.resume();
      timerRef.current = setInterval(() => setRecordingTime(t => t + 1), 1000);
      updateWaveform();
      setMode('recording');
    }
  };

  // ─── Stop recording ───
  const stopRecording = () => {
    clearInterval(timerRef.current);
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
  };

  // ─── File drag & drop ───
  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files?.[0]) handleFileSelect(e.dataTransfer.files[0]);
  };

  const handleFileSelect = (selectedFile) => {
    if (selectedFile && (selectedFile.type.includes('audio/') || selectedFile.name.match(/\.(wav|mp3|ogg|webm|m4a)$/i))) {
      setFile(selectedFile);
      setAudioURL(URL.createObjectURL(selectedFile));
      setMode('uploaded');
    } else {
      alert('Please select a valid audio file (WAV, MP3, OGG, WebM, M4A)');
    }
  };

  // ─── Reset ───
  const reset = () => {
    clearInterval(timerRef.current);
    cancelAnimationFrame(animFrameRef.current);
    if (audioURL) URL.revokeObjectURL(audioURL);
    if (mediaRecorderRef.current?.state !== 'inactive') {
      try { mediaRecorderRef.current?.stop(); } catch {}
    }
    setFile(null);
    setAudioURL(null);
    setMode('choose');
    setRecordingTime(0);
    setWaveform(new Array(40).fill(5));
  };

  const formatTime = (s) => `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;

  // ─── Choose mode: Record or Upload ───
  if (mode === 'choose') {
    return (
      <div className="w-full max-w-lg mx-auto space-y-4">
        {/* Record button */}
        <button
          onClick={startRecording}
          className="w-full p-6 bg-white border-2 border-slate-200 rounded-xl hover:border-red-400 hover:bg-red-50 transition-all group flex items-center gap-5"
        >
          <div className="p-4 bg-red-100 rounded-full group-hover:bg-red-200 transition-colors">
            <Mic className="h-7 w-7 text-red-600" />
          </div>
          <div className="text-left">
            <p className="font-semibold text-slate-800 text-base">Record Voice</p>
            <p className="text-sm text-slate-500">Use microphone to record victim's statement</p>
          </div>
        </button>

        {/* Divider */}
        <div className="flex items-center gap-3">
          <div className="flex-1 h-px bg-slate-200" />
          <span className="text-xs text-slate-400 font-medium uppercase">or</span>
          <div className="flex-1 h-px bg-slate-200" />
        </div>

        {/* Upload / Drag & Drop */}
        <div
          className={`w-full p-8 border-2 border-dashed rounded-xl text-center cursor-pointer transition-all ${
            isDragging
              ? 'border-nhaa-blue bg-blue-50 scale-[1.01]'
              : 'border-slate-300 hover:border-nhaa-blue hover:bg-slate-50 bg-white'
          }`}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <UploadCloud className={`mx-auto h-10 w-10 mb-3 ${isDragging ? 'text-nhaa-blue' : 'text-slate-400'}`} />
          <p className="text-slate-600 font-medium mb-1">
            {isDragging ? 'Drop audio file here' : 'Click to upload or drag and drop'}
          </p>
          <p className="text-slate-400 text-sm">WAV, MP3, OGG, WebM, M4A (Max 50MB)</p>
          <input
            type="file"
            ref={fileInputRef}
            className="hidden"
            accept=".wav,.mp3,.ogg,.webm,.m4a,audio/*"
            onChange={(e) => handleFileSelect(e.target.files[0])}
          />
        </div>
      </div>
    );
  }

  // ─── Recording in progress ───
  if (mode === 'recording' || mode === 'paused') {
    return (
      <div className="w-full max-w-lg mx-auto">
        <div className="bg-white border-2 border-red-200 rounded-xl p-6 space-y-5">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Circle className={`h-3 w-3 fill-red-500 text-red-500 ${mode === 'recording' ? 'animate-pulse' : ''}`} />
              <span className="font-semibold text-slate-800">
                {mode === 'recording' ? 'Recording...' : 'Paused'}
              </span>
            </div>
            <span className="font-mono text-lg text-red-600 font-bold">{formatTime(recordingTime)}</span>
          </div>

          {/* Waveform visualization */}
          <div className="flex items-center justify-center gap-[3px] h-16 bg-slate-50 rounded-lg px-3">
            {waveform.map((h, i) => (
              <div
                key={i}
                className={`w-[5px] rounded-full transition-all duration-75 ${
                  mode === 'recording' ? 'bg-red-500' : 'bg-slate-300'
                }`}
                style={{ height: `${h}px` }}
              />
            ))}
          </div>

          {/* Controls */}
          <div className="flex items-center justify-center gap-4">
            {/* Discard */}
            <button
              onClick={reset}
              className="p-3 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-full transition-colors"
              title="Discard"
            >
              <X size={22} />
            </button>

            {/* Pause / Resume */}
            {mode === 'recording' ? (
              <button
                onClick={pauseRecording}
                className="p-3 bg-amber-100 text-amber-700 rounded-full hover:bg-amber-200 transition-colors"
                title="Pause"
              >
                <Pause size={22} />
              </button>
            ) : (
              <button
                onClick={resumeRecording}
                className="p-3 bg-red-100 text-red-600 rounded-full hover:bg-red-200 transition-colors"
                title="Resume"
              >
                <Mic size={22} />
              </button>
            )}

            {/* Stop */}
            <button
              onClick={stopRecording}
              className="p-4 bg-red-600 text-white rounded-full hover:bg-red-700 transition-colors shadow-md"
              title="Stop & Save"
            >
              <Square size={22} fill="white" />
            </button>
          </div>

          <p className="text-center text-xs text-slate-400">
            Click the square button to stop recording
          </p>
        </div>
      </div>
    );
  }

  // ─── Recorded or Uploaded: preview & submit ───
  return (
    <div className="w-full max-w-lg mx-auto">
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
        {/* File info */}
        <div className="flex items-center gap-4">
          <div className="bg-blue-100 p-3 rounded-full">
            <FileAudio className="h-6 w-6 text-nhaa-blue" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="font-medium text-slate-800 truncate">{file?.name}</p>
            <p className="text-xs text-slate-500">
              {file ? `${(file.size / (1024 * 1024)).toFixed(2)} MB` : ''}
              {mode === 'recorded' && ` • ${formatTime(recordingTime)} recorded`}
            </p>
          </div>
        </div>

        {/* Audio player */}
        {audioURL && (
          <audio controls src={audioURL} className="w-full h-10 rounded" />
        )}

        {/* Actions */}
        <div className="flex items-center justify-between pt-1">
          <button
            onClick={reset}
            className="flex items-center gap-2 text-sm text-slate-500 hover:text-red-500 px-3 py-2 rounded-lg hover:bg-red-50 transition-colors"
          >
            <X size={16} />
            {mode === 'recorded' ? 'Re-record' : 'Remove'}
          </button>
          <button
            onClick={() => onAnalyze(file)}
            className="flex items-center gap-2 bg-nhaa-blue text-white px-5 py-2.5 rounded-lg hover:bg-blue-700 transition-colors shadow-sm font-medium"
          >
            <Play size={16} />
            Analyze Voice
          </button>
        </div>
      </div>
    </div>
  );
}
