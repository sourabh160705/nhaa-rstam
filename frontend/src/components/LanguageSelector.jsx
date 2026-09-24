import React from 'react';

const languages = [
  { code: 'en', english: 'English', native: 'English' },
  { code: 'hi', english: 'Hindi', native: 'हिन्दी' },
  { code: 'ta', english: 'Tamil', native: 'தமிழ்' },
  { code: 'te', english: 'Telugu', native: 'తెలుగు' },
  { code: 'mr', english: 'Marathi', native: 'मराठी' },
  { code: 'bn', english: 'Bengali', native: 'বাংলা' },
  { code: 'kn', english: 'Kannada', native: 'ಕನ್ನಡ' },
  { code: 'gu', english: 'Gujarati', native: 'ગુજરાતી' },
  { code: 'ml', english: 'Malayalam', native: 'മലയാളം' },
  { code: 'pa', english: 'Punjabi', native: 'ਪੰਜਾਬੀ' },
  { code: 'or', english: 'Odia', native: 'ଓଡ଼ିଆ' },
  { code: 'ur', english: 'Urdu', native: 'اردو' }
];

export default function LanguageSelector({ value, onChange }) {
  return (
    <div className="w-full">
      <label className="block text-sm font-medium text-slate-700 mb-1">Primary Language</label>
      <select 
        value={value} 
        onChange={(e) => onChange(e.target.value)}
        className="w-full border border-slate-300 rounded-md shadow-sm p-2 bg-white focus:ring-nhaa-blue focus:border-nhaa-blue outline-none"
      >
        <option value="" disabled>Select language...</option>
        {languages.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.english} ({lang.native})
          </option>
        ))}
      </select>
    </div>
  );
}
